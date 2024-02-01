# python src/exact_order/dataset_generator.py --base-dir ./non-numerical/exact_odering --out-dir ./non-numerical/exact_ordring_prompt --year-span 10

import os
import jsonlines
import argparse
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", type=str, required=True)
parser.add_argument("--start-year", type=int, default=1947)
parser.add_argument("--end-year", type=int, default=2022)

# parser.add_argument("--out-dir", type=str, required=True)

args = parser.parse_args()

BASE_DIR = args.base_dir.rstrip("/")
OUT_DIR = BASE_DIR+"_shrunk"
os.makedirs(OUT_DIR, exist_ok=True)
# SPAN = args.year_span

dirs = os.listdir(f"{BASE_DIR}")
freq = {}
for i in tqdm(dirs):
    jsons = os.listdir(f"{BASE_DIR}/{i}")
    jsons = [f"{BASE_DIR}/{i}/{json}" for json in jsons if json.endswith(".json")]

    sample_counter = 0

    for json in tqdm(jsons, leave=False):
        objs = []
        with jsonlines.open(json) as reader:
            for obj in reader:
                item = {
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

        if len(objs) == 0:
            print(json)
            continue

        os.makedirs(f"{OUT_DIR}/{i}/", exist_ok=True)
        with jsonlines.open(f"{OUT_DIR}/{i}/{json.split('/')[-1].split('.')[0]}.json", "w") as writer:
            writer.write_all(objs)

print(freq)
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