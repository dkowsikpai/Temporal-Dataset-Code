# For MCQ dataset

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import random
import math

random.seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
# parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--end-year", type=int, default=2022)
parser.add_argument("--suffix", type=str, default="")


countries = pd.read_csv(os.getcwd()+"/src/utils/country _code.csv")
c_code_to_name = {countries["A3"][i]: countries["Name"][i] for i in range(len(countries))}
c_code = list(c_code_to_name.keys())

args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip("/")
OUT_DIR = BASE_DIR + "_easy_date_based_mcq_prompt"
END_YEAR = args.end_year

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_options(idx, ans):
    options = []
    n = len(ans)
    options.append(ans[idx]["answer"])

    if idx - 1 >= 0 and ans[idx -1]["date"] != "nan" and ans[idx - 1]["answer"] != "0":
        options.append(ans[idx - 1]["answer"])
        if idx - 2 >= 0 and ans[idx -2]["date"] != "nan" and ans[idx - 2]["answer"] != "0":
            options.append(ans[idx - 2]["answer"])
    else:
        if idx + 3 < n and ans[idx + 3]["date"] != "nan" and ans[idx + 3]["answer"] != "0":
            options.append(ans[idx + 3]["answer"])
            if idx + 4 < n and ans[idx + 4]["date"] != "nan" and ans[idx + 4]["answer"] != "0":
                options.append(ans[idx + 4]["answer"])

    if idx + 1 < n and ans[idx + 1]["date"] != "nan" and ans[idx + 1]["answer"] != "0":
        options.append(ans[idx + 1]["answer"])
        if idx + 2 < n and ans[idx + 2]["date"] != "nan" and ans[idx + 2]["answer"] != "0":
            options.append(ans[idx + 2]["answer"])
    else:
        if idx - 3 >= 0 and ans[idx - 3]["date"] != "nan" and ans[idx - 3]["answer"] != "0":
            options.append(ans[idx - 3]["answer"])
            if idx - 4 >= 0 and ans[idx - 4]["date"] != "nan" and ans[idx - 4]["answer"] != "0":
                options.append(ans[idx - 4]["answer"])   
    # print(options)

    while len(options) < 4:
        if is_number(options[0]):
            if "." in options[0]:
                after_decimal = len(options[0].split(".")[1])
            else:
                after_decimal = 0
            rn = random.uniform(0, 1)
            lnm = nm = float(options[0]) 
            if nm < 0:
                lnm = -nm
            d = math.floor(math.log10(lnm+1))
            t = nm + rn * (10 ** d)
            t = round(t, after_decimal)
            options.append(str(t))
        else:
            options.append("0")

    while len(options) > 4:
        options.pop()

    # Round off the options
    options = [round(float(x), 2) for x in options]
    correct_option = options[0]
    random.shuffle(options)
    labeled_options = []
    for i in range(len(options)):
        labeled_options.append(f"({chr(97+i)}) {options[i]}")
    correct_option = chr(97 + options.index(correct_option))
    labeled_options = " ".join(labeled_options)
    return labeled_options, correct_option


sample_counter = 0
dirs = os.listdir(f"{BASE_DIR}")
unique_set = set()
for i in tqdm(dirs):
    os.makedirs(f"{OUT_DIR}/{i}/", exist_ok=True)

    jsons = os.listdir(f"{BASE_DIR}/{i}")
    jsons = [f"{BASE_DIR}/{i}/{json}" for json in jsons if json.endswith(".json")]


    for json in tqdm(jsons, leave=False):
        with jsonlines.open(json) as reader:
            objs = []
            for obj in reader:

                ans_len = len(obj["answer"])
                for idx in range(ans_len):
                    item = {
                        "query": obj["query"],
                        "id": str(obj["id"]) + "-" + str(idx),
                        "answer": ""
                    }

                    if obj["answer"][idx]["date"] != "nan" and obj["answer"][idx]["answer"] != "0": # and int(obj["answer"][idx]["date"]) < END_YEAR :
                        q = item['query'].replace("?", "")
                        item["query"] = f"Which option is correct for the question: In {obj['answer'][idx]['date']}, {q}" + args.suffix
                        for c in c_code:
                            if c in obj["query"]:
                                item["query"] = item["query"].replace(c, c_code_to_name[c])
                                break
                        if item["query"] in unique_set:
                            continue
                        unique_set.add(item["query"])

                        options, correct_answer = get_options(idx, obj["answer"])
                        item["query"] += f""". Options: {options}"""
                        
                        item["id"] = f"{item['id']}-{obj['answer'][idx]['date']}"
                        item["answer"] += f"""{correct_answer}"""
                        # print(item["query"], item["answer"])
                        objs.append(item)
                    
            if len(objs) == 0:
                continue

            data = pd.DataFrame(objs)
            data = data.loc[:,['id','query','answer']]
            sample_counter += data.shape[0]
            data.to_csv(f"{OUT_DIR}/{i}/{json.split('/')[-1].split('.')[0]}.csv", index=False)

print(f"Total samples: {sample_counter}")
