# python src/exact_order/dataset_generator.py --base-dir ./non-numerical/exact_odering --end-year 2012

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import random
import math
from rich.pretty import pprint

random.seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
# parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--start-year", type=int, default=1947)
parser.add_argument("--end-year", type=int, default=2022)
parser.add_argument("--k", type=int, default=5)
parser.add_argument("--number-of-samples-per-instance", type=int, default=10 , help="Number of samples to be generated per instance aka p")


args = parser.parse_args()

countries = pd.read_csv(os.getcwd()+"/src/utils/country _code.csv")
c_code_to_name = {countries["A3"][i]: countries["Name"][i] for i in range(len(countries))}
c_code = list(c_code_to_name.keys())

K = args.k
BASE_DIR = args.base_dir
OUT_DIR = BASE_DIR + "_hard_trend_based_mcq_prompt"
END_YEAR = args.end_year
START_YEAR = args.start_year

# os.makedirs(OUT_DIR, exist_ok=True)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_options(idx, answer):
    options = []
    options.append(answer)

    while len(options) < 4:
        num = answer
        if is_number(num):
            if "." in num:
                after_decimal = len(num.split(".")[1])
            else:
                after_decimal = 0
            rn = random.uniform(0, 1)
            lnm = nm = float(num) 
            if nm < 0:
                lnm = -nm
            d = math.floor(math.log10(lnm+1))
            t = nm + rn * (10 ** d)
            t = round(t, after_decimal)
            options.append(t)
        else:
            options.append("0")


    # Round off the options
    options = [round(float(x), 2) for x in options]
    correct_option = options[0]
    random.shuffle(options)
    labeled_options = []
    for i in range(len(options)):
        label = "(" + chr(97 + i) + ") "
        labeled_options.append(label + str(options[i]))

    correct_option = chr(97 + options.index(correct_option))
    labeled_options = " ".join(labeled_options)
    return labeled_options, correct_option


sample_counter = 0
dirs = os.listdir(BASE_DIR)
unique_set = set()
per_category_counter = {}
for dir in tqdm(dirs):
    os.makedirs(f"{OUT_DIR}/{dir}", exist_ok=True)

    jsons = os.listdir(f"{BASE_DIR}/{dir}")
    jsons = [f"{BASE_DIR}/{dir}/{json}" for json in jsons if json.endswith(".json")]

    for json in tqdm(jsons, leave=False):
        with jsonlines.open(json) as reader:
            objs = []
            for obj in reader:
                per_sample_answers = []
                for idx in range(K, len(obj["answer"])):
                    item = {
                        "query": obj["query"],
                        "id": obj["id"],
                        "answer": ""
                    }
                    first_year = int(obj["answer"][idx-K]["date"])
                    last_year = int(obj["answer"][idx]["date"])
                    answers = obj["answer"][idx-K:idx]

                    # if last_year < first_year:
                    #     continue

                    if last_year > END_YEAR or last_year < first_year or first_year < START_YEAR:
                        continue

                    if "[start date]" in item["query"]:
                        item["query"] = item["query"].replace("[start date]", first_year).replace("[end date]", last_year)
                    else:
                        item["query"] = f"In {first_year}-{last_year}, what is the highest rate of change for {item['query']}? Out of the option?"

                    # item["query"] = "What is the correct option for the following query? " + item["query"]

                    for c in c_code:
                        if c in obj["query"]:
                            item["query"] = item["query"].replace(c, c_code_to_name[c])
                            break

                    if item["query"] in unique_set:
                        continue
                    unique_set.add(item["query"])

                    # Rate of change of the window of the answers
                    window = []
                    for ans in answers:
                        if first_year <= int(ans["date"]) <= last_year:
                            if len(window) == 0:
                                window.append(float(ans["answer"]))
                            else:
                                window.append(float(ans["answer"]))

                    rate_change = []
                    for i in range(1, len(window)):
                        rate_change.append(window[i] - window[i-1])                    
                    if len(rate_change) <= 1:
                        continue
                    rate_change = max([abs(x) for x in rate_change[1:]]) # Ignore the first value

                    item["answer"] = str(rate_change)
                    
                    if len(item["answer"]) == 0:
                        continue

                    options, correct_option = get_options(idx, item["answer"])
                    # pprint(options)
                    # pprint(correct_option)
                    # exit()

                    item["query"] += f""": Options: {options}"""
                    item["answer"] = correct_option

                    # if item["answer"].count("In ") == 1:
                    #     item["answer"] = item["answer"].replace("In ", "From ") 

                    per_sample_answers.append(item)

                if len(per_sample_answers) == 0:
                    continue
                elif len(per_sample_answers) > args.number_of_samples_per_instance:
                    per_sample_answers = random.sample(per_sample_answers, args.number_of_samples_per_instance)
                objs.extend(per_sample_answers)
                sample_counter += len(per_sample_answers)
                    
            if len(objs) == 0:
                continue

            data = pd.DataFrame(objs)
            data = data.loc[:,['id','query','answer']]
            per_category_counter[dir] = per_category_counter.get(dir, 0) + len(data)
            data.to_csv(f"{OUT_DIR}/{dir}/{json.split('/')[-1].split('.')[0]}.csv", index=False)

print(f"Total samples: {sample_counter}")
pprint(per_category_counter)
