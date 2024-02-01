import os
import jsonlines

# Function to count lines in a file
def count_lines(file_path):
    with open(file_path, 'r') as file:
        return sum(1 for line in file)

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

# Find top 100 JSONlines files with the most lines
def find_top_100_files(root_directory):
    jsonlines_files = []
    unique_set = set()
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.json'):
                file_path = os.path.join(dirpath, filename)
                # The 'date' is for more than 4 entries.
                data_read = []
                print(file_path)
                list_of_answers = []
                
                with jsonlines.open(file_path) as reader:
                    for item in reader:

                        if item["query"] in unique_set:
                            continue
                        unique_set.add(item["query"])

                        list_of_answers.append(len(item['answer']))
                        
                        # print(item) 
                    
                        # if mean(list_of_answers)>4:
                        data_read.append(item)
                # list_of_answers.append(data_read[0]['answer']).mean()>4 
                line_count = count_lines(file_path)
                mean_value = mean(list_of_answers)
                line_count = line_count * mean_value
                jsonlines_files.append((file_path, line_count))

    top_100_files = sorted(jsonlines_files, key=lambda x: x[1], reverse=True)[:100]
    return top_100_files

# Move the top 100 files to a different directory
def move_top_100_files(top_files, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for i, (file_path, _) in enumerate(top_files):
        new_file_path = os.path.join(output_directory, f'top_{i + 1}.json')
        os.rename(file_path, new_file_path)


if __name__ == "__main__":
    for cate in ["""Energy, Climate change, and Enviornmental Impact""", """Health""", """Human Rights""", """Innovation and Technological Change""", """Migration""", """Poverty, Economic Development, and Community""", """War""", """Food and Agriculture"""]:  # 
        root_directory = '/home/dkowsik/temporal-dataset/data/final_full_dataset_shrunk/'+cate
        output_directory = '/home/dkowsik/temporal-dataset/data/micro_dataset/'+cate

        top_files = find_top_100_files(root_directory)
        move_top_100_files(top_files, output_directory)
