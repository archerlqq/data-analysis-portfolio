# 合并导出的10条查询结果
import pandas as pd, glob
import os

files = sorted(glob.glob("results/Q*.csv"))
with pd.ExcelWriter("SQL_Results.xlsx") as writer:
    for f in files:
        filename = os.path.basename(f)  
        sheet_name = filename.replace(".csv", "")
        df = pd.read_csv(f)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("SQL_Results.xlsx has been created successfully.")
