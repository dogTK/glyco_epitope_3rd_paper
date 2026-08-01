"""全遺伝子ブロックを結合して保存する。

23,614列を parquet にすると列指向のメタデータが肥大するので、
行列は .npy、メタと遺伝子名は別ファイルに分ける。
"""
import numpy as np, pandas as pd, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.environ.get("GLYCO_WORK",
                   os.path.join(ROOT, "data", "processed", "gctx_work")) + "/"
OUT = os.path.join(ROOT, "data", "processed") + "/"
genes = np.load(S + "gctx_genes.npy", allow_pickle=True)
np.save(OUT + "abs_full_genes.npy", genes)

JOBS = [("blocks_full_liver", "sel_meta_liver.parquet", "abs_full_liver_24h"),
        ("blocks_full_6h",    "sel_meta_6h.parquet",    "abs_full_core9_6h"),
        ("blocks_full_24h",   "sel_meta.parquet",       "abs_full_16cell_24h")]

for blockdir, metafile, out in JOBS:
    files = sorted(glob.glob(S + blockdir + "/blk_*.npz"))
    arrs, rows = [], []
    for f in files:
        z = np.load(f)
        if z['arr'].shape[0]:
            arrs.append(z['arr']); rows.append(z['rows'])
    A = np.vstack(arrs); R = np.concatenate(rows)
    order = np.argsort(R)
    A, R = A[order], R[order]
    meta = pd.read_parquet(S + metafile).set_index('idx').loc[R].reset_index()
    np.save(OUT + out + ".npy", A)
    meta.to_parquet(OUT + out + "_meta.parquet", index=False)
    print(f"{out}: {A.shape[0]:,} 試料 x {A.shape[1]:,} 遺伝子  "
          f"({os.path.getsize(OUT + out + '.npy')/1024**3:.1f} GB)  "
          f"細胞 {meta.cell.nunique()} / 薬剤 {meta.pertname.nunique():,}", flush=True)
