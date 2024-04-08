# python src/exact_order/dataset_generator.py --base-dir ./non-numerical/exact_odering --out-dir ./non-numerical/exact_ordring_prompt --year-span 10

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import random

random.seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
parser.add_argument("--start-year", type=int, default=1947)
parser.add_argument("--end-year", type=int, default=2022)

# parser.add_argument("--out-dir", type=str, required=True)

args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip("/")
OUT_DIR = BASE_DIR+"_annotate"
os.makedirs(OUT_DIR, exist_ok=True)
# SPAN = args.year_span

dirs = os.listdir(f"{BASE_DIR}")
freq = {}
for i in tqdm(dirs):
    jsons = os.listdir(f"{BASE_DIR}/{i}")
    jsons = [f"{BASE_DIR}/{i}/{json}" for json in jsons if json.endswith(".json")]

    sample_counter = 0
    dir_samples = []

    for json in tqdm(jsons, leave=False):
        objs = []
        try:
            with jsonlines.open(json) as reader:
                for obj in reader:
                    if "_" in obj["query"]:
                        continue
                    item = {
                        "category": i,
                        "query": obj["query"],
                        "id": obj["id"],
                        "answer": []
                    }

                    temp_ans = []
                    for idx in range(len(obj["answer"])):
                        if args.start_year <= int(obj["answer"][idx]["date"]) <= args.end_year:
                            temp_ans.append(obj["answer"][idx])

                    if len(temp_ans) == 0:
                        continue

                    obj["answer"] = temp_ans
                    prev = obj["answer"][0]["answer"]
                    item["answer"].append(obj["answer"][0])
                    for idx in range(1, len(obj["answer"])):
                        if obj["answer"][idx]["answer"] != prev:
                            item["answer"].append(obj["answer"][idx])
                            prev = obj["answer"][idx]["answer"]

                    freq[len(item["answer"])] = freq.get(len(item["answer"]), 0) + 1
                    objs.append(item)
        except:
            print(f"Error in {json}")
            continue

        if len(objs) == 0:
            print(json)
            continue

        unique = set()
        append_data = []
        for obj in objs:
            q = ' '.join(obj["query"].split(" ")[:4])
            if q not in unique:
                unique.add(q)
                append_data.append(obj)
        
        dir_samples.extend(append_data)
        
    os.makedirs(f"{OUT_DIR}/{i}/", exist_ok=True)
    # Convert to csv
    data = []
    for inst in dir_samples:
        item = {
            "category": inst["category"],
            "query": inst["query"],
            "id": inst["id"]
        }
        for ans in inst["answer"]:
            item[ans["date"]] = ans["answer"]
        data.append(item)
            

    df = pd.DataFrame(data)
    df.to_csv(f"{OUT_DIR}/{i}/data.csv", index=False)

combined_sampled = pd.DataFrame()
for i in dirs:
    df = pd.read_csv(f"{OUT_DIR}/{i}/data.csv")
    combined_sampled = pd.concat([combined_sampled, df])

print(combined_sampled.head())

sample = combined_sampled.sample(250) if len(combined_sampled) > 100 else combined_sampled
sample.to_csv(f"{OUT_DIR}/combined_sample.csv", index=False)

