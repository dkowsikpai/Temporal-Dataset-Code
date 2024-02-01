# python src/exact_order/dataset_generator.py --base-dir ./non-numerical/exact_odering --out-dir ./non-numerical/exact_ordring_prompt --year-span 10

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from rich.pretty import pprint
import random

random.seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
parser.add_argument("--start-year", type=int, default=1947)
parser.add_argument("--end-year", type=int, default=2022)
# parser.add_argument("--per-category-sample", type=int, default=100)

# parser.add_argument("--out-dir", type=str, required=True)

args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip("/")
OUT_DIR = BASE_DIR+"_micro_shrunk"
os.makedirs(OUT_DIR, exist_ok=True)
# SPAN = args.year_span


dirs = os.listdir(f"{BASE_DIR}")

# per_file_freq = {}
# for i in tqdm(dirs):
#     jsons = os.listdir(f"{BASE_DIR}/{i}")
#     jsons = [f"{BASE_DIR}/{i}/{json}" for json in jsons if json.endswith(".json")]
#     jsons.sort()
    
#     cate_freq = []
#     for json in tqdm(jsons, leave=False):
#         with open(json, 'r') as fp:
#             lines = sum(1 for line in fp)
#             cate_freq.append(lines)
#     per_file_freq[i] = cate_freq

# sampling_freq = {}    
# for key in per_file_freq.keys():
#     percentage = [i/sum(per_file_freq[key]) for i in per_file_freq[key]]
#     inverse = [1/i for i in percentage]
#     inverse_percentage = [i/sum(inverse) for i in inverse]
#     num_samples = [round(args.per_category_sample * i) for i in inverse_percentage]
#     # Make sure sum is equal to args.per_category_sample
#     sm = sum(num_samples)
#     if sm < args.per_category_sample:
#         # Count the number of samples that are 0
#         num_zero = num_samples.count(0)
#         # Add 1 to the first num_zero samples
#         for i in range(len(num_samples)):
#             if sum(num_samples) == args.per_category_sample:
#                 break
#             if num_samples[i] == 0:
#                 num_samples[i] += 1
#     sampling_freq[key] = num_samples

# # pprint(sampling_freq)
# # print(len(sampling_freq.keys()))
# # for i in sampling_freq.keys():
# #     print(i)
# #     print(sum(sampling_freq[i]))
# # exit()

freq = {}
count_75 = 0
for di in tqdm(dirs):
    jsons = os.listdir(f"{BASE_DIR}/{di}")
    jsons = [f"{BASE_DIR}/{di}/{json}" for json in jsons if json.endswith(".json")]
    jsons.sort()

    # cate_freq = []
    # for json in tqdm(jsons, leave=False):
    #     with open(json, 'r') as fp:
    #         lines = sum(1 for line in fp)
    #         cate_freq.append(lines)

    # percentage = [i/sum(cate_freq) for i in cate_freq]
    # inverse = [1/i for i in percentage]
    # inverse_percentage = [i/sum(inverse) for i in inverse]
    # num_samples = [round(args.per_category_sample * i) for i in inverse_percentage]
    # # Make sure sum is equal to args.per_category_sample
    # sm = sum(num_samples)
    # if sm < args.per_category_sample:
    #     # Count the number of samples that are 0
    #     num_zero = num_samples.count(0)
    #     # Add 1 to the first num_zero samples
    #     for i in range(len(num_samples)):
    #         if sum(num_samples) == args.per_category_sample:
    #             break
    #         if num_samples[i] == 0:
    #             num_samples[i] += 1
    # elif sm > args.per_category_sample:
    #     # Remove 1 from heighest num_samples
    #     while sum(num_samples) > args.per_category_sample:
    #         max_idx = num_samples.index(max(num_samples))
    #         num_samples[max_idx] -= 1

    sample_counter = 0
    check_freq = 0
    # print(f"{di}: {sum(num_samples)}")
    for file_idx in tqdm(range(len(jsons)), leave=False):
        json = jsons[file_idx]
        objs = []
        with jsonlines.open(json) as reader:
            for obj in reader:
                item = {
                    "query": obj["query"],
                    "id": obj["id"],
                    "answer": []
                }

                # Clip the answers to the given year range
                obj["answer"].sort(key=lambda x: int(x["date"]))
                while len(obj["answer"]) > 0 and int(obj["answer"][0]["date"]) < args.start_year:
                    obj["answer"].pop(0)
                while len(obj["answer"]) > 0 and int(obj["answer"][-1]["date"]) > args.end_year:
                    obj["answer"].pop(-1)

                if len(obj["answer"]) == 0:
                    # print(f"Skipped  {json}")
                    continue

                # Shrink to change in events
                prev = obj["answer"][0]["answer"]
                item["answer"].append(obj["answer"][0])
                for idx in range(1, len(obj["answer"])):
                    if obj["answer"][idx]["answer"] != prev:
                        item["answer"].append(obj["answer"][idx])
                        prev = obj["answer"][idx]["answer"]

                count_75 += 1 if len(item["answer"]) >= 75 else 0
                freq[len(item["answer"])] = freq.get(len(item["answer"]), 0) + 1
                objs.append(item)

        # random.shuffle(objs)
        # objs = objs[:num_samples[file_idx]]

        if len(objs) == 0:
            # print(f"Skipped {json}")
            continue

        check_freq += len(objs)

        os.makedirs(f"{OUT_DIR}/{di}/", exist_ok=True)
        with jsonlines.open(f"{OUT_DIR}/{di}/{json.split('/')[-1].split('.')[0]}.json", "w") as writer:
            writer.write_all(objs)
    
    # print(f"{di}: {check_freq}")

print("Count 75: ", count_75)
print("Total samples: ", sum(freq.values()))

# print(freq)
with open("change_dist_energy.csv", "w") as f:
    f.write("freq,count\n")
    for k, v in freq.items():
        f.write(f"{k},{v}\n")


def addlabels(x,y):
    for i in range(len(x)):
        if y[i] > 10000:
            ax.text(x[i], y[i], f"{(x[i], y[i])}", ha = 'center', fontsize=8)
        else:
            ax.text(x[i], y[i]+5, f"{y[i]}", ha = 'center', fontsize=8)

l = list(freq.items())
l.sort(key=lambda x: x[0])
x = [i[0] for i in l]
y = [i[1] for i in l]

plt.figure(figsize=(10, 5))
ax = plt.subplot(111)
# Hide the right and top spines
import pandas as pd
df = pd.DataFrame({'x': x, 'y': y})
ax.spines[['right', 'top']].set_visible(False)
ax.bar(x, y, color=["#3DC6C3", "#50E3C2", "#1891C3", "#016FC4", "#016FC4","#3A30DA", "#3A30DA", "#50E3C2", "#00589C",])
ax.grid(axis = 'y')
ax.set_xlabel("Frequency of change over the year")
ax.set_ylabel("Number of samples")
addlabels(x, y)
plt.savefig("change_dist_energy.pdf")
# plt.show()
df.to_csv("change_dist_energy.csv", index=False)