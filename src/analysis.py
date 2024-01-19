import jsonlines
import os
from rich.pretty import pprint
import sys
from tqdm import tqdm
import pandas as pd

BASE_DIR = "./raw"

directories = os.listdir(BASE_DIR)
pprint(directories)

exclude = [".git", "manual_csv", "space-exploration", "zzz_redundant"]

dir_data = {}

for directory in tqdm(directories):
    start = sys.maxsize
    end = -sys.maxsize - 1
    if not os.path.isdir(f"{BASE_DIR}/{directory}") or directory in exclude:
        continue
    files = os.listdir(f"{BASE_DIR}/{directory}")
    for file in files:
        if file.endswith(".json"):
            with jsonlines.open(f"{BASE_DIR}/{directory}/{file}") as reader:
                for obj in reader:
                    answers = obj["answer"]

                    for answer in answers:
                        if "/" in answer["date"]:
                            answer["date"] = answer["date"].split("/")[-1]
                        if "-" in answer["date"] and "-" != answer["date"][0]:
                            answer["date"] = answer["date"].split("-")[0]
                        if "." in answer["date"]:
                            answer["date"] = answer["date"].split(".")[0]
                        if answer["date"] == "nan":
                            continue

                        start = min(start, int(answer["date"]))
                        end = max(end, int(answer["date"]))

    dir_data[directory] = {
        "start": start,
        "end": end,
    }

pprint(dir_data)
dir_data = [{"category": k, "start": v["start"], "end": v["end"]} for k, v in dir_data.items()]
df = pd.DataFrame(dir_data)
df.to_csv("./category_start_end.csv")



start_end_per_sample = []

start = -10000
end = 2100

for directory in tqdm(directories):

    if not os.path.isdir(f"{BASE_DIR}/{directory}") or directory in exclude:
        continue
    files = os.listdir(f"{BASE_DIR}/{directory}")
    for file in files:
        if file.endswith(".json"):
            with jsonlines.open(f"{BASE_DIR}/{directory}/{file}") as reader:
                for obj in reader:
                    answers = obj["answer"]

                    for answer in answers:
                        if "/" in answer["date"]:
                            answer["date"] = answer["date"].split("/")[-1]
                        if "-" in answer["date"] and "-" != answer["date"][0]:
                            answer["date"] = answer["date"].split("-")[0]
                        if "." in answer["date"]:
                            answer["date"] = answer["date"].split(".")[0]
                        if answer["date"] == "nan":
                            continue

                        start = max(start, int(answer["date"]))
                        end = min(end, int(answer["date"]))
                    
                    start_end_per_sample.append({
                        "category": directory,
                        "start": start,
                        "end": end,
                    })


df = pd.DataFrame(start_end_per_sample)
df.to_csv("./start_end_per_sample.csv")

# Category count
category_count = {}
df.groupby("category").count().to_csv("./category_count.csv")
