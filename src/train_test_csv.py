import os 
import pandas as pd
import random
import argparse
import sys
from tqdm import tqdm
random.seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--percent", type=float, default=0.8)

args = parser.parse_args()

data = pd.DataFrame()
for file in tqdm(os.listdir(args.base_dir)):
    if file.endswith(".csv"):
        df = pd.read_csv(f"{args.base_dir}/{file}")
        data = pd.concat([data, df], ignore_index=True)
        
data = data.sample(frac=1).reset_index(drop=True)
print(data.shape)

data.to_csv(f"{args.out_dir}/train.csv", index=False)

test = data.sample(frac=0.2).reset_index(drop=True)
test.to_csv(f"{args.out_dir}/test.csv", index=False)
print(test.shape)


# test_ids = ids[int(args.percent*len(ids)):]

# data = {}
# train_data = []
# counter = 0
# done_ids = set()
# for id in tqdm(train_ids):
#     if id in done_ids:
#         continue
#     for csv in os.listdir(args.base_dir):
#         if csv.endswith(".csv"):
#             df = pd.read_csv(f"{args.base_dir}/{csv}")
#             for idx, row in df.iterrows():
#                 if row["id"] == id:
#                     train_data.append(row)
#                     done_ids.add(id)
#                     counter += 1
#                     break
        
                




