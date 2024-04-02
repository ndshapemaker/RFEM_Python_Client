# Step 1: importing libraries
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

# Step 2: Model initiation
Model(new_model=True, model_name='first_example_rfem')
Model.clientModel.service.begin_modification('new')

# Step 3: Nodes
Node(1, 0, 0, 0)
Node(2, 5.0, 0, 0)

# Step 4: Materials
Material(1, 'S235')

# Step 5: Sections
Section(1, 'IPE 300')

# Step 6: Elements
Member(1, 1, 2, 0.0, 1, 1,)

# Step 7: Supports
NodalSupport(1, '1', NodalSupportType.FIXED)

# Step 8: Load Case
LoadCase(1, 'Name1',[False])

# Step 9: Adding Loads
NodalLoad(1, 1, '2', magnitude=1000)

# Step 10: Analysis Settings
StaticAnalysisSettings.GeometricallyLinear(1, "Linear")

# Step 11: Running Analysis
Calculate_all()

# Step 12: Save and End modifications
Model.clientModel.service.finish_modification()