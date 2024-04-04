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
from RFEM.baseSettings import BaseSettings
from RFEM.Loads.imposedNodalDeformation import ImposedNodalDeformation
import json


# Functions
def get_fea_input(json_file):
    with open(json_file) as file:
        data = json.load(file)
    return data


def create_dlubal_nodes_from_fea_input_tower(fea_input_tower_nodes):
    for node in fea_input_tower_nodes:
        Node(node['number'], node['x'], node['y'], float(node['z']))


def create_dlubal_fea_members(fea_input_tower_frame_elements, section_dict):
    for member in fea_input_tower_frame_elements:
        section_number = section_dict[member['cross_section']['name']]["section_number_dlubal"]
        if member['member_type'] == 'GuyWire':
            Member.Cable(
                no=member['member_number'],
                start_node_no=member['start_node']['number'],
                end_node_no=member['end_node']['number'],
                section_no=section_number,
                )
        else:
            Member(
                no=member['member_number'],
                start_node_no=member['start_node']['number'],
                end_node_no=member['end_node']['number'],
                rotation_angle=0.0,
                start_section_no=section_number,
                end_section_no=section_number,
                )


def create_dlubal_nodal_supports(fea_input_tower_supports):
    for support in fea_input_tower_supports:
        NodalSupport(support['node']['number'], str(support['node']['number']), NodalSupportType.HINGED)


def create_dlubal_load_cases(fea_load_cases, predefined_node_displacements):
    nodal_load_number = 1
    for load_case in fea_load_cases:
        if load_case['gravitional_constant'] != 0.0:
            self_weight_factor = load_case['gravitional_constant'] / 9810.0
            self_weight_list = [True, 0, 0, self_weight_factor]
        else:
             self_weight_list = [False]
        LoadCase(load_case["number"], load_case["name"], self_weight_list)
        create_dlubal_nodal_loads(load_case['nodal_loads'], nodal_load_number, load_case["number"])
        create_dlubal_predefined_node_displacements(predefined_node_displacements, load_case["number"])


def create_dlubal_nodal_loads(nodal_loads, nodal_load_number: int, load_case_number: int):
    for nodal_load in nodal_loads:
        x_force = nodal_load['force']['x']
        y_force = nodal_load['force']['y']
        z_force = nodal_load['force']['z']
        x_moment = 0.0
        y_moment = 0.0
        z_moment = 0.0
        load_magnitude = (x_force**2 + y_force**2 + z_force**2)**0.5
        if 0.0 < load_magnitude:
            force_components_N = [x_force, y_force, z_force, x_moment, y_moment, z_moment]
            NodalLoad.Components(no=nodal_load_number, load_case_no=load_case_number, nodes_no=str(nodal_load['node_number']), components=force_components_N)
            nodal_load_number += 1


def create_dlubal_predefined_node_displacements(predefined_node_displacements, load_case_number: int):
    for pre_disp in predefined_node_displacements:
        load_parameter = [pre_disp['x'], pre_disp['y'], pre_disp['z'], 0.0, 0.0, 0.0]
        ImposedNodalDeformation(no=pre_disp['node_number'], load_case_no=load_case_number, node_no=str(pre_disp['node_number']), load_parameter=load_parameter)


def create_dlubal_sections(fea_input_tower_frame_elements):
    section_dict = {}
    section_number = 1
    for frame_element in fea_input_tower_frame_elements:
        cross_section_name = frame_element['cross_section']['name']
        if cross_section_name not in section_dict:
            section_name = dlubal_section_name(cross_section_name)
            Section(no=section_number, name=section_name, comment=cross_section_name)
            section_dict[cross_section_name] = {"section_number_dlubal": section_number}
            section_number += 1
    return section_dict




def dlubal_section_name(cross_section_name: str):
    default_name = 'IPE 300'
    if cross_section_name == "D32":
        dlubal_name = "R 32"
    elif cross_section_name == "D14":
        dlubal_name = "R 14"
    elif cross_section_name == "D25":
        dlubal_name = "R 25"
    elif cross_section_name == "D16":
        dlubal_name = "R 16"
    elif cross_section_name == "SWR_1x7_D9":
        dlubal_name = "Cable 10.00"
    else:
        dlubal_name = default_name
    return dlubal_name


# Step 1: Model initiation
Model(new_model=True, model_name='guyed_mast_example')
Model.clientModel.service.begin_modification('new')
#Basic settings
BaseSettings(
    gravitational_acceleration=9.81,
    global_axes_orientation=GlobalAxesOrientationType.E_GLOBAL_AXES_ORIENTATION_ZUP,
    local_axes_orientation=LocalAxesOrientationType.E_LOCAL_AXES_ORIENTATION_ZDOWN,
    tolerances=[0.0005, 0.0005, 0.0005, 0.0005],
    )


#Get FEA input
lattice_file = '01-examples-nils/03_fea_input_B1.json'
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
create_dlubal_load_cases(fea_input['fea_load_cases'], fea_input['fea_input_tower']['predefined_node_displacements'])


# Step 9: Analysis Settings
StaticAnalysisSettings.LargeDeformation(3, "LargeDeformation")

# Step 10: Running Analysis
#Calculate_all()


# Step 11: Save and End modifications
Model.clientModel.service.finish_modification()
