import jsonlines
import os
from rich.pretty import pprint
import sys
from tqdm import tqdm
import pandas as pd
import time
import sys

BASE_DIR = "./raw"
OUTPUT_DIR = "./processed"

directories = os.listdir(BASE_DIR)
pprint(directories)

exclude = [".git", "manual_csv", "space-exploration", "zzz_redundant", "worldometer_population"]
for e in exclude:
    if e in directories:
        directories.remove(e)
directories.sort()

dir_code_map = {}
with open("./rnd_code.txt", "r") as f:
    codes = f.readlines()

for code, directory in zip(codes, directories):
    dir_code_map[directory] = code.strip()

pprint(dir_code_map)

category_count = dir_code_map.copy()
for k in category_count.keys():
    category_count[k] = 0
    
data = []

unique_set = set()

nname = 0
count = 0
for directory in tqdm(directories):
    if not os.path.isdir(f"{BASE_DIR}/{directory}"):
        continue
    files = os.listdir(f"{BASE_DIR}/{directory}")
    for file in files:
        if file.endswith(".json"):
            with jsonlines.open(f"{BASE_DIR}/{directory}/{file}") as reader:
                objs = []
                for obj in reader:

                    if obj["query"] in unique_set:
                        continue
                    unique_set.add(obj["query"])

                    for answer in obj["answer"]:
                        if "/" in answer["date"]:
                            answer["date"] = answer["date"].split("/")[-1]
                        if "-" in answer["date"] and "-" != answer["date"][0]:
                            answer["date"] = answer["date"].split("-")[0]
                        if "." in answer["date"]:
                            answer["date"] = answer["date"].split(".")[0]
                        if answer["date"] == "nan":
                            continue
                    
                        data.append({
                            "query": obj["query"],
                            "answer": answer["answer"],
                            "date": answer["date"]
                        })

                        count += 1

                    if sys.getsizeof(data) > 5e+7:
                        df = pd.DataFrame(data)
                        df.to_csv(f"./all/all-{nname}.csv", index=False)
                        print(f"Saved {nname} with {count} rows")
                        # exit()
                        nname += 1
                        data = []
                        count = 0

df = pd.DataFrame(data)
df.to_csv(f"./all/all-{nname}.csv", index=False)
