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

def create_dlubal_from_fea_input_tower(fea_input_tower_nodes):
    for node in fea_input_tower_nodes:
        Node(node['number'], node['x'], node['y'], float(node['z'])*-1)
        #print(f"Node {node['number']} created at ({node['x']}, {node['y']}, {node['z']})")

def create_dlubal_fea_members(fea_input_tower_frame_elements):
    for member in fea_input_tower_frame_elements:
        #print(f"Member {member['member_number']} created from {member['start_node']['number']} to {member['end_node']['number']} with material 1 and section 1")
        Member(member['member_number'], member['start_node']['number'], member['end_node']['number'], 0.0, 1, 1)

def create_dlubal_nodal_supports(fea_input_tower_supports):
    for support in fea_input_tower_supports:
        #print(f"Support created at node {support['node']['number']}")
        NodalSupport(support['node']['number'], str(support['node']['number']), NodalSupportType.HINGED)


# Step 1: Model initiation
Model(new_model=True, model_name='first_example_rfem')
Model.clientModel.service.begin_modification('new')



# Step 2: Nodes
# Node(1000, 0, 0, 0)
# Node(2000, 5.0, 0, 0)

#Get FEA input
lattice_file = '01-examples-nils/01_fea_input_S5_empty.json'
fea_input = get_fea_input(lattice_file)

create_dlubal_from_fea_input_tower(fea_input['fea_input_tower']['nodes'])

# Step 3: Materials
Material(1, 'S235')

# Step 4: Sections
Section(1, 'R 100')

# Step 5: Elements
# Member(1, 1000, 2000, 0.0, 1, 1,)

create_dlubal_fea_members(fea_input['fea_input_tower']['frame_elements'])

# Step 6: Supports
# NodalSupport(1000, '1000', NodalSupportType.FIXED)

create_dlubal_nodal_supports(fea_input['fea_input_tower']['tower_supports'])

# Step 7: Load Case
LoadCase(1, 'Name1',[False])

# Step 8: Adding Loads
NodalLoad(1, 1, '100', magnitude=1000)

# Step 9: Analysis Settings
StaticAnalysisSettings.GeometricallyLinear(1, "Linear")

# Step 10: Running Analysis
Calculate_all()

# Step 11: Save and End modifications
Model.clientModel.service.finish_modification()