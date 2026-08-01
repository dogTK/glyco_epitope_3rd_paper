"""cp_predicted_RNAseq_profiles.gctx (171GB, S3) の行・列メタだけを読む。

本体をDLせず ros3 で部分読みし、遺伝子名と (細胞, 薬剤, 時間, 用量) を取得する。
出力の gctx_colmeta.parquet から抽出対象を選んで sel_idx*.npy を作り、
gctx_02_extract_absolute.py に渡す。
"""
import h5py, boto3, time, numpy as np, pandas as pd, os

S = os.environ.get(
    "GLYCO_WORK",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "data", "processed", "gctx_work")) + "/"
os.makedirs(S, exist_ok=True)
c=boto3.Session().get_credentials().get_frozen_credentials()
url="https://snowflake-bioinformatics-clinicfor.s3.ap-northeast-1.amazonaws.com/LINCS/cp_predicted_RNAseq_profiles.gctx"
f=h5py.File(url,'r',driver='ros3',aws_region=b'ap-northeast-1',
            secret_id=c.access_key.encode(),secret_key=c.secret_key.encode())
t=time.time(); genes=np.array([x.decode() for x in f['/0/META/ROW/id'][:]])
print(f"genes {len(genes)} ({time.time()-t:.1f}s)")
np.save(S+"gctx_genes.npy",genes)
meta={}
for k in ['cell','pertname','timepoint','dose']:
    t=time.time(); v=f[f'/0/META/COL/{k}'][:]
    meta[k]=np.array([x.decode() if isinstance(x,bytes) else x for x in v])
    print(f"  {k}: {time.time()-t:.1f}s")
df=pd.DataFrame(meta); df['idx']=np.arange(len(df))
df.to_parquet(S+"gctx_colmeta.parquet")
print("\n細胞株 上位20:"); print(df.cell.value_counts().head(20).to_string())
print("\ntimepoint:",df.timepoint.value_counts().head(6).to_dict())
print("dose 上位:",df.dose.value_counts().head(6).to_dict())
