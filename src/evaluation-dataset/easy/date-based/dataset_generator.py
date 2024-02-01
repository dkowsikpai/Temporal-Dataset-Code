# For Accuracy and Temporal Awareness

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
from rich.pretty import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
# parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--start-year", type=int, default=1947)
parser.add_argument("--end-year", type=int, default=2022)
parser.add_argument("--suffix", type=str, default="")


countries = pd.read_csv(os.getcwd()+"/src/utils/country _code.csv")
c_code_to_name = {countries["A3"][i]: countries["Name"][i] for i in range(len(countries))}
c_code = list(c_code_to_name.keys())

args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip("/")
OUT_DIR = BASE_DIR + "_acc_prompt"
END_YEAR = args.end_year
START_YEAR = args.start_year

sample_counter = 0
dirs = os.listdir(f"{BASE_DIR}")
unique_set = set()
dirs = dirs[::-1]
per_category_count = {}
for i in tqdm(dirs):
    os.makedirs(f"{OUT_DIR}/{i}/", exist_ok=True)

    jsons = os.listdir(f"{BASE_DIR}/{i}")
    jsons = [f"{BASE_DIR}/{i}/{json}" for json in jsons if json.endswith(".json")]


    for json in tqdm(jsons, leave=False, desc=f"Processing {i}"):
        with jsonlines.open(json) as reader:
            objs = []
            for obj in reader:

                for idx in range(len(obj["answer"])):
                    item = {
                        "query": obj["query"],
                        "id": str(obj["id"]) + "-" + str(idx),
                        "answer": ""
                    }
                    # if 'answer' not in obj["answer"][idx]:
                    #     print(json)
                    #     exit()
                    #     continue

                    if obj["answer"][idx]["date"] != "nan" and obj["answer"][idx]["answer"] != "0" and START_YEAR <= int(obj["answer"][idx]["date"]) <= END_YEAR: # 
                        q = item['query'].replace("?", "")
                        item["query"] = f"In {obj['answer'][idx]['date']}, {q}" + args.suffix
                        for c in c_code:
                            if c in obj["query"]:
                                item["query"] = item["query"].replace(c, c_code_to_name[c])
                                break
                        if item["query"] in unique_set:
                            continue

                        unique_set.add(item["query"])
                        
                        item["id"] = f"{item['id']}-{obj['answer'][idx]['date']}"
                        item["answer"] += f"""{obj["answer"][idx]["answer"]}"""
                        objs.append(item)
                    
            if len(objs) == 0:
                continue

            data = pd.DataFrame(objs)
            data = data.loc[:,['id','query','answer']]
            sample_counter += data.shape[0]
            per_category_count[i] = per_category_count.get(i, 0) + data.shape[0]
            data.to_csv(f"{OUT_DIR}/{i}/{json.split('/')[-1].split('.')[0]}.csv", index=False)
            # print(sample_counter)
           

print(f"Total samples: {sample_counter}")
pprint(per_category_count)
