
from cc3d import CompuCellSetup
        

from contactToAdhesionSteppables import contactToAdhesionSteppable

CompuCellSetup.register_steppable(steppable=contactToAdhesionSteppable(frequency=1))


CompuCellSetup.run()
