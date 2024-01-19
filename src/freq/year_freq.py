import os
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint
from tqdm import tqdm

csvs = os.listdir("./all")
csvs.sort()

nname = 0
for csv in csvs:
    print(csv)
    freq = {}
    df = pd.read_csv(f"./all/{csv}", dtype={"date": int, "answer": str, "query": str})
    # print(df.head())
    # exit()
    for idx in tqdm(range(df.shape[0])):
        row = df.iloc[idx]
        freq[row["date"]] = freq.get(row["date"], 0) + 1
        # if idx % 10000 == 0:
        #     print(idx)


    plt.figure(figsize=(20, 10))
    plt.bar(freq.keys(), freq.values())
    plt.xticks(rotation=90)
    plt.xlabel("Year")
    plt.ylabel("Frequency")
    plt.title(f"Total Samples: {sum(freq.values())}")
    plt.savefig(f"./freq/freq-{nname}.png")

    with open(f"./freq/freq-{nname}.txt", "w") as f:
        for k, v in freq.items():
            f.write(f"{k}\t{v}\n")    
    
    nname += 1
