import argparse
import os
import pandas as pd
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Combine yearly data')
parser.add_argument('--base-dir', type=str, help='Input file')
parser.add_argument('--out-dir', type=str, help='Output file')
args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip('/')
categories = os.listdir(BASE_DIR)
categories = [c for c in categories if os.path.isdir(f'{BASE_DIR}/{c}')]
categories = sorted(categories)


for category in tqdm(categories):
    df = pd.DataFrame()
    files = os.listdir(f'{BASE_DIR}/{category}')
    files = [f for f in files if f.endswith('.csv')]
    files = sorted(files)
    for file in tqdm(files, leave=True, desc=category):
        year = file.split('.')[0]
        df_year = pd.read_csv(f'{BASE_DIR}/{category}/{file}')
        df = pd.concat([df, df_year], ignore_index=True, axis=0)
    os.makedirs(f'{args.out_dir}/{category}', exist_ok=True)
    df.drop(columns=['frequency'], inplace=True)
    cols = ["id", "query", "answer"]
    df = df[cols]
    df.to_csv(f'{args.out_dir}/{category}/{files[0]}', index=False)
