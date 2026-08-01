"""cp_predicted_RNAseq_profiles.gctx から **全 23,614 遺伝子** を抽出する。

前回（extract.py）は glycogene 385 列だけ保存したが、HDF5 のチャンクが
(32サンプル x 738遺伝子) で 23,614 遺伝子が 32 チャンクに分かれており、
385 個が全体に散在するため結局 32 チャンク全部を読んでいた＝全遺伝子を読んで98.4%捨てていた。
通信量は同じなので、今回は捨てずに保存する。

前回との差分:
  - 全列を保存（[:,cols] の絞り込みをしない）
  - **選択サンプルの行だけ**保存（前回はブロック範囲の全行を保存していた）→ 容量が約1/8
使い方: python gctx_02_extract_absolute.py <sel_idx.npy> <出力ディレクトリ名>
  例: python gctx_02_extract_absolute.py sel_idx.npy blocks_full_24h

入力（data/processed/gctx_work/ にある。gctx_01_fetch_metadata.py が作る）:
  sel_idx.npy / sel_idx_6h.npy / sel_idx_liver.npy  抽出対象サンプルの行番号
出力: <work>/<出力ディレクトリ名>/blk_*.npz → gctx_03_combine_blocks.py で結合

所要: 24h全16株で約3時間（16並列 / 118,900試料 / 失敗0 の実績が2026-08-01）。
"""
import h5py, boto3, time, numpy as np, os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed

S = os.environ.get(
    "GLYCO_WORK",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "data", "processed", "gctx_work")) + "/"
URL = ("https://snowflake-bioinformatics-clinicfor.s3.ap-northeast-1.amazonaws.com/"
       "LINCS/cp_predicted_RNAseq_profiles.gctx")

IDXFILE = sys.argv[1] if len(sys.argv) > 1 else "sel_idx.npy"
OUTNAME = sys.argv[2] if len(sys.argv) > 2 else "blocks_full"
OUT = S + OUTNAME + "/"
os.makedirs(OUT, exist_ok=True)

idx = np.load(S + IDXFILE)
selset = set(int(v) for v in idx)

# 連続ブロックにまとめる（64未満の隙間は結合してチャンク境界を活かす）
blocks = []
s = p = idx[0]
for i in idx[1:]:
    if i - p > 64:
        blocks.append((s, p + 1)); s = i
    p = i
blocks.append((s, p + 1))
B = []
for a, b in blocks:
    while b - a > 2048:
        B.append((a, a + 2048)); a += 2048
    B.append((a, b))


def work(k):
    a, b = B[k]
    f = OUT + f"blk_{k:06d}.npz"
    if os.path.exists(f):
        return k, 0
    for attempt in range(4):
        try:
            c = boto3.Session().get_credentials().get_frozen_credentials()
            h = h5py.File(URL, 'r', driver='ros3',
                          aws_region='ap-northeast-1'.encode(),
                          secret_id=c.access_key.encode(),
                          secret_key=c.secret_key.encode())
            arr = h['/0/DATA/0/matrix'][a:b, :].astype('float32')
            h.close()
            rows = np.arange(a, b)
            m = np.array([int(r) in selset for r in rows])   # 選択サンプルの行だけ残す
            if m.sum() == 0:
                np.savez_compressed(f, arr=np.zeros((0, arr.shape[1]), 'float32'),
                                    rows=np.zeros(0, 'int64'))
                return k, 0
            arr, rows = arr[m], rows[m]
            np.savez_compressed(f, arr=arr, rows=rows)
            return k, arr.nbytes
        except Exception:
            if attempt == 3:
                return k, -1
            time.sleep(5 * (attempt + 1))
    return k, -1


if __name__ == "__main__":
    print(f"[{OUTNAME}] ブロック {len(B)} 本 / 選択サンプル {len(idx):,}", flush=True)
    t0 = time.time(); done = nbytes = fail = 0
    with ProcessPoolExecutor(16) as ex:
        futs = [ex.submit(work, k) for k in range(len(B))]
        for fu in as_completed(futs):
            k, nb = fu.result(); done += 1
            if nb < 0: fail += 1
            else: nbytes += nb
            if done % 50 == 0 or done == len(B):
                el = time.time() - t0
                print(f"  {done}/{len(B)} blocks  {el/60:.1f}min  失敗{fail}  "
                      f"保存{nbytes/1024**3:.1f}GB  残り約{el/done*(len(B)-done)/60:.0f}min",
                      flush=True)
    print(f"[{OUTNAME}] 完了 {done} blocks / 失敗 {fail} / {(time.time()-t0)/60:.1f}min", flush=True)
