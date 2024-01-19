import jsonlines
import os
from rich.pretty import pprint
import sys
from tqdm import tqdm
import pandas as pd
import time
import shutil

####################################################################################################
BASE_DIR = "./raw"
NON_NUMERICAL_DIR = "./non-numerical"
NUMERICAL_DIR = "./numerical"
START_YEAR = 1947
END_YEAR = 2022
exclude = [".git", "manual_csv", "space-exploration", "zzz_redundant", "worldometer_population"]
####################################################################################################

directories = os.listdir(BASE_DIR)
pprint(directories)

for e in exclude:
    if e in directories:
        directories.remove(e)
directories.sort()

# pprint(len(directories))
# exit()

dir_code_map = {}
with open("./rnd_code.txt", "r") as f:
    codes = f.readlines()

for code, directory in zip(codes, directories):
    dir_code_map[directory] = code.strip()

pprint(dir_code_map)
# for k, v in dir_code_map.items():
#     print(k)

# exit()

category_count = dir_code_map.copy()
for k in category_count.keys():
    category_count[k] = 0
    
# dir_data = {}
# ct_files = set()
# category_counter = {}

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def prepare_dataset(out_dir, is_numerical=False, just_run=False):
    category_freq = {}
    unique_set = set()
    for directory in tqdm(directories):
        if not os.path.isdir(f"{BASE_DIR}/{directory}"):
            continue
        files = os.listdir(f"{BASE_DIR}/{directory}")
        for file in files:
            if file.endswith(".json"):
                file_path = f"{BASE_DIR}/{directory}/{file}"
                with jsonlines.open(file_path) as reader:
                    objs = []
                    for obj in reader:

                        if obj["query"] in unique_set:
                            continue
                        unique_set.add(obj["query"])

                        item = {
                            "query": obj["query"],
                            "id": dir_code_map[directory] + "-" + str(obj["id"]),
                            "answer": []
                        }

                        # answers = obj["answer"]

                        for answer in obj["answer"]:
                            if "/" in answer["date"]:
                                answer["date"] = answer["date"].split("/")[-1]
                            if "-" in answer["date"] and "-" != answer["date"][0]:
                                answer["date"] = answer["date"].split("-")[0]
                            if "." in answer["date"]:
                                answer["date"] = answer["date"].split(".")[0]
                            if answer["date"] == "nan":
                                continue

                            if not is_numerical:
                                if answer["answer"] != "nan" and answer["answer"].isalpha(): # START_YEAR <= int(answer["date"]) <= END_YEAR and
                                    item["answer"].append(answer)
                            else:
                                if answer["answer"] != "nan" and is_number(answer["answer"]): # START_YEAR <= int(answer["date"]) <= END_YEAR and 
                                    item["answer"].append(answer)

                        if len(item["answer"]) > 0:
                            objs.append(item)

                        # if len(obj["answer"]) > 0:
                        #     for ans in obj["answer"]:
                        #         if ans["answer"] != "nan" and ans["answer"].isalpha():
                        #             ct_files.add(file_path)
                        #             break

                if len(objs) == 0:
                    continue
                
                category_freq[directory] = category_freq.get(directory, 0) + len(objs)

                if just_run:
                    continue
                os.makedirs(f"{out_dir}/{directory}/", exist_ok=True) # {directory}
                # time.sleep(3)
                with jsonlines.open(f"{out_dir}/{directory}/{file}", mode="w") as writer: # {directory}
                    writer.write_all(objs)
                # category_count[directory] = category_count[directory] + len(objs)

    return category_freq


if __name__ == "__main__":
    JUST_RUN = True
    category_freq_non_num = prepare_dataset(NON_NUMERICAL_DIR, is_numerical=False, just_run=JUST_RUN)
    category_count_num = prepare_dataset(NUMERICAL_DIR, is_numerical=True, just_run=JUST_RUN)

    df = pd.DataFrame(category_freq_non_num.items(), columns=["Category", "non_num_count"])
    df.to_csv("./non_numerical_values.csv")

    df = pd.DataFrame(category_count_num.items(), columns=["Category", "num_count"])
    df.to_csv("./numerical_values.csv")















# for file in ct_files:
#     directory = file.split("/")[-2]
#     with open(file, "r") as f:
#         category_counter[directory] = category_counter.get(directory, 0) + sum(1 for _ in f)
    
#     # Copy file to output directory
#     os.makedirs(f"{OUTPUT_DIR}/{directory}", exist_ok=True)
#     shutil.copy(file, f"{OUTPUT_DIR}/{directory}")


# # for directory in directories:
# #     if not os.path.isdir(f"{BASE_DIR}/{directory}"):
# #         continue
# #     if directory not in category_counter.keys():
# #         category_counter[directory] = 0


# data = []
# for k, v in category_counter.items():
#     data.append({
#         "Category": k,
#         "cat_count": v 
#     })

# df = pd.DataFrame(data)
# df.to_csv("./categorical_values.csv")          

# with open("./categorical_files.txt", "w") as f:
#     for file in ct_files:
#         f.write(file + "\n")

#------------------------------------------------------------

# For Numerical dataset
# nu_files = set()
# for directory in tqdm(directories):
#     if not os.path.isdir(f"{BASE_DIR}/{directory}"):
#         continue
#     files = os.listdir(f"{BASE_DIR}/{directory}")
#     for file in files:
#         if file.endswith(".json"):
#             file_path = f"{BASE_DIR}/{directory}/{file}"
#             if file_path in ct_files:
#                 continue
#             nu_files.add(file_path)

# numerical_counter = {}
# for file in nu_files:
#     directory = file.split("/")[-2]
#     with open(file, "r") as f:
#         numerical_counter[directory] = numerical_counter.get(directory, 0) + sum(1 for _ in f)

#     # Copy file to output directory
#     os.makedirs(f"{NUMERICAL_DIR}/{directory}", exist_ok=True)
#     shutil.copy(file, f"{NUMERICAL_DIR}/{directory}")

# data = []
# for k, v in numerical_counter.items():
#     data.append({
#         "Category": k,
#         "num_count": v 
#     })

# df = pd.DataFrame(data)
# df.to_csv("./numerical_values.csv")

# with open("./numerical_files.txt", "w") as f:
#     for file in nu_files:
#         f.write(file + "\n")

