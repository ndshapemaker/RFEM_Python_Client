import json


def get_input_file_data(json_file):
    with open(json_file) as file:
        data = json.load(file)
    return data


file_path = '01-examples-nils/04_fea_output_B1.json'
fea_output = get_input_file_data(file_path)

load_case_id = "C37"
node_number = "94"
member_number = "1"



# Print the selected results
for load_case in fea_output['fea_load_case_results']:
    if load_case['load_case_id'] == load_case_id:
        print(load_case['node_displacements'][node_number])
        print(load_case['internal_forces'][member_number])
