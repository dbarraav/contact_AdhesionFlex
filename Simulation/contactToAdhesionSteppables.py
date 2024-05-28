from cc3d.cpp.PlayerPython import * 
from cc3d import CompuCellSetup
from cc3d.core.PySteppables import *
import numpy as np
import csv 
import os

JCC = 5
JCM = 10

class contactToAdhesionSteppable(SteppableBasePy):

    def __init__(self, frequency=1):

        SteppableBasePy.__init__(self,frequency)
        self.create_scalar_field_cell_level_py("adh_C")
        

    def start(self):
        """
        Called before MCS=0 while building the initial simulation
        """
    
        
        cellCOMs = np.zeros((len(self.cell_list), 4))
        
        for cellNum, cell in enumerate(self.cell_list):
            cell.targetVolume = cell.volume
            cell.lambdaVolume = 1.0
            
            cell.targetSurface = cell.surface
            cell.lambdaSurface = 1.0
            
            # Make sure AdhesionFlex plugin is loaded
            # setting adhesion molecule density using its name
            # self.adhesionFlexPlugin.setAdhesionMoleculeDensity(cell, "adh_C", cell.surface)
            # self.adhesionFlexPlugin.setAdhesionMoleculeDensity(cell, "adh_C", cell.surface)
            cellCOMs[cellNum, :] = [cell.id, cell.xCOM, cell.yCOM, cell.zCOM]
            
        spheroidCOM = np.mean(cellCOMs[1:], axis = 0)
        nearHorizPlane = np.abs(cellCOMs[:, -1] - spheroidCOM[-1]) < 5 # cells X pixels away from horizontal plane
        nearVertPlane = np.abs(cellCOMs[:, 2] - spheroidCOM[2]) < 5 # cells X pixels away from vertical plane
        
        cellIDsNearEq = cellCOMs[nearHorizPlane & nearVertPlane, :]
        
        self.shared_steppable_vars['leadCellID'] = int(cellIDsNearEq[np.argmax(cellIDsNearEq[:,1]), 0])
        leadCellID = self.shared_steppable_vars['leadCellID']
        leadCell = self.fetch_cell_by_id(leadCellID)
        leadCell.type = self.cell_type.leader

    def step(self, mcs):
        """
        Called every frequency MCS while executing the simulation
        :param mcs: current Monte Carlo step
        """
        adh_CField = self.field.adh_C
        adh_CField.clear()
        
        if mcs == 0:
            leadCellID = self.shared_steppable_vars['leadCellID']
            leadCell = self.fetch_cell_by_id(leadCellID)
            self.adhesionFlexPlugin.setAdhesionMoleculeDensity(leadCell, "adh_C", 2.5)
            print("The adh_C molecule density of the leader cell was increased")

        for cell in self.cell_list:
            axes = np.round(self.momentOfInertiaPlugin.getSemiaxes(cell), 3)
            maxAxis = np.max(axes)
            minAxis = np.min(axes)
            elongIdx = maxAxis/minAxis
            # if elongIdx > 1.75:
                # self.adhesionFlexPlugin.setAdhesionMoleculeDensity(cell, "adh_C", 5)
                # print("Cell with {} has increased their molecule density".format(cell.id))
        
        # self.adhesionFlexPlugin.setMediumAdhesionMoleculeDensity("adh_M", total_surface)
        if mcs in [0, 200, 400, 600, 800]:
            print("Step {} is completed".format(mcs))
            for cell in self.cell_list:
                axes = np.round(self.momentOfInertiaPlugin.getSemiaxes(cell), 3)
                
                maxAxis = np.max(axes)
                minAxis = np.min(axes)
                elongIdx = maxAxis/minAxis

                if cell.type == self.cell_type.leader:
                    print("Leader cell {} has a moment of Inertia: [{}, {}, {}], and EI of {}".format(cell.id, axes[0], axes[1], axes[2], elongIdx))
                else:
                    print("Cell {} has a moment of Inertia: [{}, {}, {}], and EI of {}".format(cell.id, axes[0], axes[1], axes[2], elongIdx))
                    
                    
        for cell in self.cell_list:
            adh_CField[cell] = self.adhesionFlexPlugin.getAdhesionMoleculeDensity(cell, "adh_C")
        
        
        
        outputDir = self.output_dir
        # print("The current directory is \n {}".format(outputDir))
        
        cellDataFilePath = os.path.join(outputDir, "cellData.csv")
        
        if  not os.path.isfile(cellDataFilePath):  
            # print('cellData.csv DOES NOT EXIST. IT WILL BE CREATED.')
            with open(cellDataFilePath, 'a', newline='') as fout:
                writer = csv.writer(fout, delimiter=',')
                writer.writerow(['cellID', 'cell.xCOM', 'cell.yCOM', 'cell.zCOM'])
                for cell in self.cell_list:
                    writer.writerow([cell.id, cell.xCOM, cell.yCOM, cell.zCOM])
        else:
            if mcs % 50 == 0:
                with open(cellDataFilePath, 'a', newline='') as fout:
                    writer = csv.writer(fout, delimiter=',')
                    for cell in self.cell_list:
                        writer.writerow([cell.id, cell.xCOM, cell.yCOM, cell.zCOM])
        
        
                
    def finish(self):
        """
        Called after the last MCS to wrap up the simulation
        """

    def on_stop(self):
        """
        Called if the simulation is stopped before the last MCS
        """
