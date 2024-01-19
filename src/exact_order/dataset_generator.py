# python src/exact_order/dataset_generator.py --base-dir ./non-numerical/exact_odering --end-year 2012

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
# parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--end-year", type=int, default=5)

args = parser.parse_args()

countries = pd.read_csv(os.getcwd()+"/src/utils/country _code.csv")
c_code_to_name = {countries["A3"][i]: countries["Name"][i] for i in range(len(countries))}
c_code = list(c_code_to_name.keys())

BASE_DIR = args.base_dir
OUT_DIR = BASE_DIR + "_exact_ordering_prompt"
END_YEAR = args.end_year

# os.makedirs(OUT_DIR, exist_ok=True)

sample_counter = 0
dirs = os.listdir(BASE_DIR)
unique_set = set()
for dir in tqdm(dirs):
    os.makedirs(f"{OUT_DIR}/{dir}", exist_ok=True)

    jsons = os.listdir(f"{BASE_DIR}/{dir}")
    jsons = [f"{BASE_DIR}/{dir}/{json}" for json in jsons if json.endswith(".json")]

    for json in tqdm(jsons, leave=False):
        with jsonlines.open(json) as reader:
            objs = []
            for obj in reader:
                item = {
                    "query": obj["query"],
                    "id": obj["id"],
                    "answer": ""
                }
                first_year = obj["answer"][0]["date"]
                last_year = str(END_YEAR)
                if last_year < first_year:
                    continue

                if "[start date]" in item["query"]:
                    item["query"] = item["query"].replace("[start date]", first_year).replace("[end date]", last_year)
                else:
                    item["query"] = f"From {first_year} to {last_year}, {item['query']}"

                for c in c_code:
                    if c in obj["query"]:
                        item["query"] = item["query"].replace(c, c_code_to_name[c])
                        break

                if item["query"] in unique_set:
                    continue
                unique_set.add(item["query"])

                for idx in range(len(obj["answer"])):
                    if int(obj["answer"][idx]["date"]) < END_YEAR:
                        item["answer"] += f"""In {obj["answer"][idx]["date"]} {obj["answer"][idx]["answer"]},"""
                item["answer"] = item["answer"].strip(",")

                if item["answer"].count("In ") == 1:
                    item["answer"] = item["answer"].replace("In ", "From ") 

                objs.append(item)
                sample_counter += 1
                    
            if len(objs) == 0:
                continue

            data = pd.DataFrame(objs)
            data = data.loc[:,['id','query','answer']]
            data.to_csv(f"{OUT_DIR}/{dir}/{json.split('/')[-1].split('.')[0]}.csv", index=False)

print(f"Total samples: {sample_counter}")
