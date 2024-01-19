import os
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, default=1950)
parser.add_argument("--end", type=int, default=2023)

args = parser.parse_args()

txts = os.listdir("./freq")

freq = {}
for txt in txts:
    if not txt.endswith(".txt"):
        continue
    with open(f"./freq/{txt}", "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line == "":
                continue
            k, v = line.split("\t")
            freq[int(k)] = freq.get(int(k), 0) + int(v)

values = list(freq.items())
values.sort(key=lambda x: x[1], reverse=True)
values = [(k, v) for k, v in values if k >= args.start and k <= args.end]

with open("./freq.txt", "w") as f:
    for k, v in values:
        f.write(f"{k}\t{v}\n")

values = values[:100]

x = [v[0] for v in values]
y = [v[1] for v in values]
# print(values)

plt.figure(figsize=(20, 10))
plt.bar(x, y)
plt.xticks(rotation=90)
plt.xlabel("Year")
plt.ylabel("Frequency")
plt.title(f"Total Samples: {sum(y)}")
plt.savefig(f"./freq.png")
