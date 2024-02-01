
import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True, help="Model Eval Path")
# parser.add_argument("--start-year", type=int, default=1947)
# parser.add_argument("--end-year", type=int, default=2022)

# parser.add_argument("--out-dir", type=str, required=True)

args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip("/")
# os.makedirs(OUT_DIR, exist_ok=True)
# SPAN = args.year_span



eval_category = os.listdir(f"{BASE_DIR}")
eval_category = [d for d in eval_category if os.path.isdir(f"{BASE_DIR}/{d}")]
eval_category.sort()

for cate in tqdm(eval_category):
    out_dir = f"{BASE_DIR}/{cate}"
    dirs = os.listdir(f"{BASE_DIR}/{cate}")
    dirs = [f"{BASE_DIR}/{cate}/{d}" for d in dirs if os.path.isdir(f"{BASE_DIR}/{cate}/{d}")]
    freq = {}
    counts = []
    for i in dirs:
        csvs = os.listdir(i)
        csvs = [f"{i}/{csv}" for csv in csvs if csv.endswith(".csv")]
        per_dir_count = {}
        for csv in csvs:
            df = pd.read_csv(csv)
            last_col = df.columns[-1]

            true_values = df[df['answer'] == df[last_col]].shape[0]
            empty_values = df[df[last_col].isnull()].shape[0]
            false_values = df.shape[0] - true_values - empty_values

            per_dir_count["true"] = per_dir_count.get("true", 0) + true_values
            per_dir_count["false"] = per_dir_count.get("false", 0) + false_values
            per_dir_count["empty"] = per_dir_count.get("empty", 0) + empty_values
        
        per_dir_count["dir"] = i.split("/")[-1]
        total = per_dir_count["true"] + per_dir_count["false"] + per_dir_count["empty"]
        
        per_dir_count["true_percent"] = round(per_dir_count["true"] / total, 2) * 100
        per_dir_count["false_percent"] = round(per_dir_count["false"] / total, 2) * 100
        per_dir_count["empty_percent"] = round(per_dir_count["empty"] / total, 2) * 100
        counts.append(per_dir_count)
    # print(counts)

    if len(counts) == 0:
        continue

    df = pd.DataFrame(counts)
    # Total row
    cols = ['dir', 'true', 'false', 'empty', 'true_percent', 'false_percent', 'empty_percent']
    df = df[cols]
    df.loc['Total'] = df[cols[1:]].sum()
    df.to_csv(f"{out_dir}/count.csv", index=False)



def category_map(cate):
    mp = ["date", "range", "window", "trend", "min", "relative", "other"]
    sp = cate.split("_")
    if len(sp) == 1:
        return mp[-1]
    for i in mp:
        if i in sp:
            x = i
            if i == "min":
                x = "min max"
            return x + " based"


combined_df = pd.DataFrame()
for cate in tqdm(eval_category):
    out_dir = f"{BASE_DIR}/{cate}"
    count_csv = f"{out_dir}/count.csv"
    if not os.path.exists(count_csv):
        continue
    df = pd.read_csv(count_csv)
    c = category_map(cate)
    df["category"] = c
    # Add Empty row
    empty_row = pd.DataFrame([["", "", "", "", "", "", "", ""]], columns=df.columns)
    df = pd.concat([df, empty_row], ignore_index=True)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

combined_df = combined_df[['category', 'dir', 'true', 'false', 'empty', 'true_percent', 'false_percent', 'empty_percent']]
combined_df.to_csv(f"{BASE_DIR}/combined_count.csv", index=False)
