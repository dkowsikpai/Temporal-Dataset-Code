# Dataset
The whole dataset has been provided in the repository [TempUN](https://github.com/dkowsikpai/TempUN).

# Processing Steps

1. Categorizing to `numerical` and `non-numerical` using `./src/categorical.py` > Outputs folder `numerical` and `non-numerical`
2. Manually select the evaluation category
3. Shrink JSON files to have only the changes; remove non-changing facts per instance `./src/shrink_jsons.py` > Outputs folder with same name as input folder but with `_shrunk` at the end.
4. Convert to prompts per category `./src/date_time_metric/dataset_generator.py`; Generates CSVs > Outputs folder with same name as input folder but with `_acc_prompt` at the end.
5. Prepare MCQ query using `./src/date_time_metric/mcq_data_generator.py`; Generates CSVs > Outputs folder with same name as input folder but with `_mcq_acc_prompt` at the end.
6. Prepare Exact Ordering dataset using `./src/exact_order/dataset_generator.py`; Also provide `--end-year` to the script. If we pass 2023, the questions will asking cronological order of events from start year (say 1947) to 2022. > Outputs folder with same name as input folder but with `_exact_ordering_prompt` at the end.
7. Preparing Exact ordering for the MCQ dataset use `./src/exact_order/mcq_dataset_generator.py` Also provide `--end-year` to the script. If we pass 2023, the questions will asking cronological order of events from start year (say 1947) to 2022. > Outputs folder with same name as input folder but with `_mcq_exact_ordering_prompt` at the end.
8. Segregate prompts to year `./src/prompt_to_year/prompt_year.py` NOTE: Must be havingig files with csvs > Outputs folder with same name as input folder but with `_yearly_prompt` at the end.

<!-- 1. Assign 4 character Random Code for each category using `./src/rnd_code.py`
2. Remove redundant query and assign globally-unique-id using `./src/uniqify.py` (Input folder: `./raw` Output folder: `./processed`)
3. Category wise start and end year; Sample wise start and end date - `./src/analysis.py` (Output: `category_start_end.csv`, `start_end_per_sample.csv`, `category_count.csv`)
4. Combing all instances to trainable format using `./src/all-in-one.py` (Output: Sequence of csvs in `./all` folder) 
5. From `./all` gets year-wise frequency of sample using `./src/freq/year_freq.py` (Output is per file frequency: `./freq` png and txt)
6. Combine frequency using `./src/freq/combine_freq.py` (Output: `freq.txt`, `freq.png`) -->


Recursive wc counter
```term
find /home/dkowsik/temporal-dataset/categorical/ -type f -exec wc -l {} \; | awk '{total += $1} END{print total}'
```

# Exact Ordering
## Dataset Generator

```term
python src/exact_order/dataset_generator.py --base-dir ./non-numerical/exact_odering --out-dir ./non-numerical/exact_ordring_prompt --year-span 10
```
