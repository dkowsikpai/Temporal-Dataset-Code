import os 
import argparse
from rich.pretty import pprint
import time
import jsonlines
from tqdm import tqdm

parser = argparse.ArgumentParser("Daily Task")
parser.add_argument("--jsons", type=str, help="Dir of jsons")
parser.add_argument("--per-day", type=int, help="Number of files per day", default=200)
parser.add_argument("--persons", type=int, help="Number of person", default=3)

args = parser.parse_args()

dirs = os.listdir(args.jsons)
dirs = [x for x in dirs if x.endswith(".json")]
dirs.sort()
print("Total number of files:", len(dirs))

per_person_files = []
n = len(dirs) // args.persons
start = 0
for _ in range(args.persons):
    per_person_files.append(dirs[start:start+n])
    start = start + n

# # Check duplicate
# l = set()
# for x in per_person_files:
#     l.update(x)
# print(len(l))

# pprint([len(x) for x in per_person_files])
    
OUTDIR = "./numerical-daily-task"
os.makedirs(OUTDIR, exist_ok=True)
for p_idx, x in enumerate(per_person_files):
    os.makedirs(f"{OUTDIR}/person_{p_idx+1}", exist_ok=True)
    start = 0
    day = 1
    os.makedirs(f"{OUTDIR}/person_{p_idx+1}/day-{day}", exist_ok=True)
    time.sleep(1)
    for file in tqdm(x, leave=False):
        # os.system(f'cp \"{args.jsons}/{file}\" \"{OUTDIR}/person_{p_idx+1}/day-{day}/{file}\"') 
        with jsonlines.open(f"{args.jsons}/{file}") as reader:
            objs = []
            for obj in reader:
                objs.append(obj)

        s = '[@_!#$%^&*()<>?/\|}{~:]'
        new_name = ''.join([fn for fn in file if fn not in s])
        with jsonlines.open(f"{OUTDIR}/person_{p_idx+1}/day-{day}/{new_name}", mode="w") as writer: # {directory}
                    writer.write_all(objs)

        start += 1
        if start >= 200:
            day += 1
            os.makedirs(f"{OUTDIR}/person_{p_idx+1}/day-{day}", exist_ok=True)
            time.sleep(1)
            start = 0

time.sleep(5)
print("Done")
