import os
import jsonlines
import argparse
from tqdm import tqdm
import time

parser = argparse.ArgumentParser(description='Filter file')
parser.add_argument('--base-dir', type=str, required=True, help='Base directory')
parser.add_argument('--word', type=str, required=True, help='Word to search')
parser.add_argument('--outdir', type=str, required=True, help='Output directory')


args = parser.parse_args()

files = os.listdir(args.base_dir)
WORD = args.word.lower()

counter = 0
for file in tqdm(files):
    if file.endswith(".json"):
        with jsonlines.open(f"{args.base_dir}/{file}") as reader:
            for obj in reader:
                if WORD in obj["query"].lower():
                    # Copy file to new directory
                    os.system(f"""cp \"{args.base_dir}/{file}\" \"{args.outdir}/{file}\"""")
                    counter += 1
                    break

time.sleep(3)
print(f"Total files: {counter}")
