import os
import pandas as pd
import argparse
from rich.pretty import pprint
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Prompt to year')
parser.add_argument('--base-dir', type=str, required=True, help='Base directory')
parser.add_argument('--start-year', type=int, default=1947, help='Start year')
parser.add_argument('--end-year', type=int, default=2022, help='End year')
parser.add_argument('--random-samples', type=int, default=-1, help='If we take random 100 samples or so while creating yearwise data.')
args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip('/')
OUTDIR = BASE_DIR + '_yearly_prompt'
START_YEAR = args.start_year
END_YEAR = args.end_year

# os.makedirs(OUTDIR, exist_ok=True)

yearly_freq = {}
os.makedirs(f"{OUTDIR}", exist_ok=True)
dirs = os.listdir(BASE_DIR)
files = []
for i in dirs:
    temp = os.listdir(f"{BASE_DIR}/{i}")
    file_path = [f"{BASE_DIR}/{i}/{j}" for j in temp]
    files.extend(file_path)
print(f"Total files: {len(files)}")

for y in tqdm(range(START_YEAR, END_YEAR + 1)):
    yearly_data = []
    for file in tqdm(files, leave=False):
        if file.endswith(".csv"):
            df = pd.read_csv(file)
            df["year"] = df["id"].str.split("-").str[-1]
            df = df[df["year"] == str(y)]
            yearly_data += df.to_dict(orient="records")
            # print(len(yearly_data))

    if len(yearly_data) == 0:
        continue

    data = pd.DataFrame(yearly_data)
    data = data.loc[:,['id','query','answer']]
    if args.random_samples > 0:
        data = data.sample(args.random_samples, random_state=1)
    yearly_freq[y] = data.shape[0]
    data.to_csv(f"{OUTDIR}/{y}.csv", index=False)

with open(f"{OUTDIR}/yearly_freq.csv", "w") as f:
    f.write("year,frequency\n")
    for key in sorted(yearly_freq.keys()):
        f.write(f"{key},{yearly_freq[key]}\n")
        
