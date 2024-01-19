# For MCQ dataset

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import random
import math
from pprint import pprint

random.seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
# parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--end-year", type=int, default=2022)
parser.add_argument("--k", type=int, default=5)
parser.add_argument("--suffix", type=str, default="")
parser.add_argument("--number-of-samples-per-instance", type=int, default=2)


args = parser.parse_args()

countries = pd.read_csv(os.getcwd()+"/src/utils/country _code.csv")
c_code_to_name = {countries["A3"][i]: countries["Name"][i] for i in range(len(countries))}
c_code = list(c_code_to_name.keys())


K = args.k
BASE_DIR = args.base_dir.rstrip("/")
OUT_DIR = BASE_DIR + "_med_relative_based_mcq_prompt"
END_YEAR = args.end_year


def get_correct_answer(idx, answers, K):
    next_year = int(answers[idx]["date"]) + K
    i = idx + 1
    while i < len(answers) and next_year >= int(answers[i]["date"]):
        i += 1
    
    # print(answers[idx]["answer"], answers[i]["answer"])
    if i < len(answers) and answers[idx]["answer"] < answers[i]["answer"]:
        return "Yes"
    else:
        return "No"


sample_counter = 0
dirs = os.listdir(f"{BASE_DIR}")
unique_set = set()
test = 0
for i in tqdm(dirs):
    os.makedirs(f"{OUT_DIR}/{i}/", exist_ok=True)

    jsons = os.listdir(f"{BASE_DIR}/{i}")
    jsons = [f"{BASE_DIR}/{i}/{json}" for json in jsons if json.endswith(".json")]


    for json in tqdm(jsons, leave=False):
        with jsonlines.open(json) as reader:
            objs = []
            for obj in reader:
                per_sample_answers = []
                ans_len = len(obj["answer"])
                for idx in range(ans_len):
                    item = {
                        "query": obj["query"],
                        "id": str(obj["id"]) + "-" + str(idx),
                        "answer": ""
                    }

                    if obj["answer"][idx]["date"] != "nan" and obj["answer"][idx]["answer"] != "0": # and int(obj["answer"][idx]["date"]) < END_YEAR :
                        q = item['query'].replace("?", "")
                        next_year = int(obj['answer'][idx]['date']) + K
                        item["query"] = f"In {obj['answer'][idx]['date']}, {q}, higher than {next_year}? Yes or No" + args.suffix
                        for c in c_code:
                            if c in obj["query"]:
                                item["query"] = item["query"].replace(c, c_code_to_name[c])
                                break
                        if item["query"] in unique_set:
                            continue
                        unique_set.add(item["query"])

                        correct_answer = get_correct_answer(idx, obj["answer"], K)
                       
                        item["id"] = f"{item['id']}-{obj['answer'][idx]['date']}"
                        item["answer"] += f"""{correct_answer}"""
                        # print(item["query"], item["answer"])
                        per_sample_answers.append(item)
                        # pprint(item)
                        # if test == 2:
                        #     exit()
                        # test += 1 

                if len(per_sample_answers) == 0:
                    continue
                elif len(per_sample_answers) > args.number_of_samples_per_instance:
                    per_sample_answers = random.sample(per_sample_answers, args.number_of_samples_per_instance)
                objs.extend(per_sample_answers)
                    
            if len(objs) == 0:
                continue

            data = pd.DataFrame(objs)
            data = data.loc[:,['id','query','answer']]
            sample_counter += data.shape[0]
            data.to_csv(f"{OUT_DIR}/{i}/{json.split('/')[-1].split('.')[0]}.csv", index=False)

print(f"Total samples: {sample_counter}")
