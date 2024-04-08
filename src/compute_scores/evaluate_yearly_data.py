
import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from rich.pretty import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True, help="Model Eval Path")
# parser.add_argument("--start-year", type=int, default=1947)
# parser.add_argument("--end-year", type=int, default=2022)

# parser.add_argument("--out-dir", type=str, required=True)

args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip("/")
# os.makedirs(OUT_DIR, exist_ok=True)
# SPAN = args.year_span


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


eval_category = os.listdir(f"{BASE_DIR}")
eval_category = [d for d in eval_category if os.path.isdir(f"{BASE_DIR}/{d}")]
eval_category.sort()

category_counts = {}
for cate in tqdm(eval_category):
    out_dir = f"{BASE_DIR}/{cate}"
    dirs = os.listdir(f"{BASE_DIR}/{cate}")
    csvs = [f"{BASE_DIR}/{cate}/{csv}" for csv in dirs if csv.endswith(".csv") and "yearly_freq.csv" not in csv]
    csvs.sort()
    yearly_counts = {}
    for csv in tqdm(csvs, leave=False, desc=cate):
        df = pd.read_csv(csv)
        last_col = df.columns[-1]

        # try:
        true_values = df[df['answer'] == df[last_col]].shape[0]
        empty_values = df[df[last_col].isnull()].shape[0]
        false_values = df.shape[0] - true_values - empty_values
        # except:
        #     print(csv)
        #     exit()

        csv_name = csv.split("/")[-1]
        csv_name = csv_name.split(".")[0]
        yearly_counts[csv_name] = {
            "true": true_values,
            "false": false_values,
            "empty": empty_values,
            "total": df.shape[0]
        }

    category_counts[category_map(cate)] = yearly_counts

# pprint(category_counts)

# Save yearly counts to csv based on category
for cate, yearly_counts in category_counts.items():
    yearly_counts_df = pd.DataFrame(yearly_counts).T
    yearly_counts_df = yearly_counts_df.reset_index()
    yearly_counts_df = yearly_counts_df.rename(columns={"index": "year"})
    # Reorder columns
    yearly_counts_df = yearly_counts_df[['year', 'true', 'false', 'empty', 'total']]
    yearly_counts_df.to_csv(f"{BASE_DIR}/{cate}_yearly_freq.csv", index=False)

# combined_df = pd.DataFrame()
# for cate in tqdm(eval_category):
#     out_dir = f"{BASE_DIR}/{cate}"
#     count_csv = f"{out_dir}/count.csv"
#     if not os.path.exists(count_csv):
#         continue
#     df = pd.read_csv(count_csv)
#     c = category_map(cate)
#     df["category"] = c
#     # Add Empty row
#     empty_row = pd.DataFrame([["", "", "", "", "", "", "", ""]], columns=df.columns)
#     df = pd.concat([df, empty_row], ignore_index=True)
#     combined_df = pd.concat([combined_df, df], ignore_index=True)

# combined_df = combined_df[['category', 'dir', 'true', 'false', 'empty', 'true_percent', 'false_percent', 'empty_percent']]
# combined_df.to_csv(f"{BASE_DIR}/combined_count.csv", index=False)
