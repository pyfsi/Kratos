import numpy as np
import math as m
import os.path as path

import KratosMultiphysics as KM
from KratosMultiphysics.CoSimulationApplication.co_simulation_component import CoSimulationComponent
from KratosMultiphysics.CoSimulationApplication.co_simulation_interface import CoSimulationInterface
import KratosMultiphysics.CoSimulationApplication.co_simulation_tools as cs_tools
cs_data_structure = cs_tools.cs_data_structure

def print_colored(string, color):
    if color=='green':
        print('\x1b[0;30;42m'+string+'\x1b[0m')
    elif color=='orange':
        print('\x1b[0;30;43m' + string + '\x1b[0m')
    elif color=='red':
        print('\x1b[0;30;41m' + string + '\x1b[0m')
    else:
        print(string+f'(color {color} not implemented)')

def Create(parameters):
    return SolverWrapperPipeStructure(parameters)


class SolverWrapperPipeStructure(CoSimulationComponent):
    def __init__(self, parameters):
        super().__init__()

        # Reading
        self.parameters = parameters
        self.settings = parameters["settings"]
        working_directory = self.settings["working_directory"].GetString()
        input_file = self.settings["input_file"].GetString()
        settings_file_name = path.join(working_directory, input_file)
        with open(settings_file_name, 'r') as settings_file:
            self.settings.AddMissingParameters(cs_data_structure.Parameters(settings_file.read()))

        # Settings
        l = self.settings["l"].GetDouble()  # Length
        start = self.settings["start"].GetDouble()
        self.d = self.settings["d"].GetDouble()  # Diameter
        self.rhof = self.settings["rhof"].GetDouble()  # Density

        e = self.settings["e"].GetDouble()  # Young"s modulus of structure
        h = self.settings["h"].GetDouble()  # Thickness of structure
        self.cmk2 = (e * h) / (self.rhof * self.d)  # Wave speed squared

        self.m = self.settings["m"].GetInt()  # Number of segments
        self.dz = l / self.m  # Segment length
        self.z = np.arange(start+self.dz / 2.0, start+l, self.dz)  # Data is stored in cell centers

        self.n = 0  # Time step

        # Initialization
        self.p = np.ones(self.m) * 2.0 * self.cmk2  # Pressure
        self.a = np.ones(self.m) * m.pi * self.d ** 2 / 4.0  # Area of cross section
        self.disp = np.zeros((self.m,3)) # Displacement
        self.traction = np.zeros((self.m, 3))  # Traction always zero
        self.p0 = 0.0  # Reference pressure
        self.a0 = m.pi * self.d ** 2 / 4.0  # Reference area of cross section
        self.c02 = self.cmk2 - self.p0 / 2.0  # Wave speed squared with reference pressure

        # ModelParts
        self.variable_pres = vars(KM)["PRESSURE"]
        self.variable_disp = vars(KM)["DISPLACEMENT"]
        self.variable_traction = vars(KM)["TRACTION"]
        self.model = cs_data_structure.Model()
        self.model_part = self.model.CreateModelPart("wall")
        self.model_part.AddNodalSolutionStepVariable(self.variable_pres)
        self.model_part.AddNodalSolutionStepVariable(self.variable_disp)
        self.model_part.AddNodalSolutionStepVariable(self.variable_traction)
        for i in range(len(self.z)):
            self.model_part.CreateNewNode(i, 0.0, self.d/2.0, self.z[i])
        step = 0
        for node in self.model_part.Nodes:
            node.SetSolutionStepValue(self.variable_pres, step, self.p[0])
            node.SetSolutionStepValue(self.variable_disp, step, self.disp[0,:].tolist())
            node.SetSolutionStepValue(self.variable_traction, step, self.traction[0, :].tolist())

        # Interfaces
        self.interface_input = CoSimulationInterface(self.model, self.settings["interface_input"])
        self.interface_output = CoSimulationInterface(self.model, self.settings["interface_output"])

        #Write start
        file_name = f"CSD/Area_TS0"
        with open(file_name, 'w') as file:
            for i in range(len(self.a)):
                file.write(f'{self.z[i]}\t{self.a[i]}\n')

    def Initialize(self):
        super().Initialize()
        self.timestep=0

    def InitializeSolutionStep(self):
        super().InitializeSolutionStep()
        self.iter = 0

        self.n += 1
        self.timestep += 1

    def SolveSolutionStep(self, interface_input):
        self.iter += 1

        self.interface_input = interface_input.deepcopy()
        self.p = self.interface_input.GetNumpyArray()/self.rhof

        # Independent rings model
        for i in range(len(self.p)):
            if self.p[i] > 2.0 * self.c02 + self.p0:
                # raise ValueError("Unphysical pressure")
                print_colored("Warning unphysical pressure detected, setting p to highest allowed value","red")
                self.p[i] = 2.0 * self.c02 + self.p0 - 1e-03


        tmp_list = self.interface_output.GetPythonList()

        file_name = f"CSD/Area_TS{self.timestep}_iter{self.iter}"
        with open(file_name, 'w') as file:
            for i in range(len(self.a)):
                self.a[i] = self.a0 * (2.0 / (2.0 + (self.p0 - self.p[i]) / self.c02)) ** 2
                tmp_list[1+i*3] = ((np.sqrt(4*self.a[i]/m.pi)-np.sqrt(4*self.a0/m.pi))/2.0)
                file.write(f'{self.z[i]}\t{self.a[i]}\n')



        self.interface_output.SetPythonList(tmp_list)

        #
        # print("END_SOLVE_SOL_STEP_STRUCTURE")
        return self.interface_output.deepcopy()

    def FinalizeSolutionStep(self):
        file_name = f"CSD/Area_TS{self.timestep}"
        with open(file_name, 'w') as file:
            for i in range(len(self.a)):
                file.write(f'{self.z[i]}\t{self.a[i]}\n')
        super().FinalizeSolutionStep()

    def Finalize(self):
        super().Finalize()

    def GetInterfaceInput(self):
        return self.interface_input.deepcopy()

    def SetInterfaceInput(self):
        Exception("This solver wrapper provides no mapping.")

    def GetInterfaceOutput(self):
        return self.interface_output.deepcopy()

    def SetInterfaceOutput(self):
        Exception("This solver wrapper provides no mapping.")
