# importing libraries
from RFEM.enums import *
from RFEM.initModel import *
from RFEM.BasicObjects.node import Node
from RFEM.BasicObjects.section import Section
from RFEM.BasicObjects.material import Material
from RFEM.BasicObjects.member import Member
from RFEM.TypesForNodes.nodalSupport import *
from RFEM.Loads.nodalLoad import *
from RFEM.LoadCasesAndCombinations.loadCase import *
from RFEM.LoadCasesAndCombinations.staticAnalysisSettings import *
import json


# Functions
def get_fea_input(json_file):
    with open(json_file) as file:
        data = json.load(file)
    return data


def create_dlubal_nodes_from_fea_input_tower(fea_input_tower_nodes):
    for node in fea_input_tower_nodes:
        Node(node['number'], node['x'], node['y'], float(node['z'])*-1)


def create_dlubal_fea_members(fea_input_tower_frame_elements, section_dict):
    for member in fea_input_tower_frame_elements:
        section_number = section_dict[member['cross_section']['name']]["section_number_dlubal"]
        Member(member['member_number'], member['start_node']['number'], member['end_node']['number'], 0.0, section_number, section_number)


def create_dlubal_nodal_supports(fea_input_tower_supports):
    for support in fea_input_tower_supports:
        NodalSupport(support['node']['number'], str(support['node']['number']), NodalSupportType.HINGED)


def create_dlubal_load_cases(fea_load_cases):
    nodal_load_number = 1
    for load_case in fea_load_cases:
        if load_case['gravitional_constant'] != 0.0:
            self_weight_factor = load_case['gravitional_constant'] / -9810.0
            self_weight_list = [True, 0, 0, self_weight_factor]
        else:
             self_weight_list = [False]
        LoadCase(load_case["number"], load_case["name"], self_weight_list)
        create_dlubal_nodal_loads(load_case['nodal_loads'], nodal_load_number, load_case["number"])


def create_dlubal_nodal_loads(nodal_loads, nodal_load_number: int, load_case_number: int):
    for nodal_load in nodal_loads:
        force_components_N = [nodal_load['force']['x']*-1, nodal_load['force']['y'], nodal_load['force']['z']*-1, 0.0, 0.0, 0.0]
        NodalLoad.Components(no=nodal_load_number, load_case_no=load_case_number, nodes_no=str(nodal_load['node_number']), components=force_components_N)
        nodal_load_number += 1


def create_dlubal_sections(fea_input_tower_frame_elements):
    section_dict = {}
    section_number = 1
    for frame_element in fea_input_tower_frame_elements:
        section_name = frame_element['cross_section']['name']
        if section_name not in section_dict:
            Section(no=section_number, name='IPE 300', comment=section_name)
            section_dict[section_name] = {"section_number_dlubal": section_number}
            section_number += 1
    return section_dict



# Step 1: Model initiation
Model(new_model=True, model_name='first_example_rfem')
Model.clientModel.service.begin_modification('new')


#Get FEA input
lattice_file = '01-examples-nils/02_fea_input_3legg_empty.json'
fea_input = get_fea_input(lattice_file)

create_dlubal_nodes_from_fea_input_tower(fea_input['fea_input_tower']['nodes'])


# Step 3: Materials
Material(1, 'S235')


# Step 4: Sections
section_dict = create_dlubal_sections(fea_input['fea_input_tower']['frame_elements'])


# Step 5: Elements
create_dlubal_fea_members(fea_input['fea_input_tower']['frame_elements'], section_dict)


# Step 6: Supports
create_dlubal_nodal_supports(fea_input['fea_input_tower']['tower_supports'])


# Step 7: Load Case
create_dlubal_load_cases(fea_input['fea_load_cases'])


# Step 9: Analysis Settings
StaticAnalysisSettings.GeometricallyLinear(1, "Linear")


# Step 10: Running Analysis
Calculate_all()


# Step 11: Save and End modifications
Model.clientModel.service.finish_modification()
