from KratosMultiphysics.CoSimulationApplication.co_simulation_component import CoSimulationComponent
from KratosMultiphysics.CoSimulationApplication.co_simulation_interface import CoSimulationInterface
import KratosMultiphysics.CoSimulationApplication.co_simulation_tools as cs_tools
cs_data_structure = cs_tools.cs_data_structure
import matplotlib.pyplot as plt

def Create(parameters):
    return CoupledSolverGaussSeidel(parameters)


class CoupledSolverGaussSeidel(CoSimulationComponent):
    def __init__(self, parameters):
        super().__init__()

        self.parameters = parameters
        self.settings = parameters["settings"]

        self.echo_level = self.settings["echo_level"].GetInt()

        self.predictor = cs_tools.CreateInstance(self.parameters["predictor"])
        self.convergence_accelerator = cs_tools.CreateInstance(self.parameters["convergence_accelerator"])
        self.convergence_criterion = cs_tools.CreateInstance(self.parameters["convergence_criterion"])
        self.solver_wrappers = []
        self.solver_wrappers.append(cs_tools.CreateInstance(self.parameters["solver_wrappers"][0]))
        self.solver_wrappers.append(cs_tools.CreateInstance(self.parameters["solver_wrappers"][1]))
        self.components = [self.predictor, self.convergence_accelerator, self.convergence_criterion,
                            self.solver_wrappers[0], self.solver_wrappers[1]]

        self.x = []

    def Initialize(self):
        super().Initialize()

        for component in self.components[1:]:
            component.Initialize()

        # Construct mappers if required
        index_mapped = None
        index_other = None
        for i in range(2):
            type = self.parameters["solver_wrappers"][i]["type"].GetString()
            if type == "solver_wrappers.mapped":
                index_mapped = i
            else:
                index_other = i
        if index_other is None:
            raise ValueError("Not both solvers may be mapped solvers.")
        if index_mapped is not None:
            # Construct input mapper
            interface_input_from = self.solver_wrappers[index_other].GetInterfaceOutput()
            self.solver_wrappers[index_mapped].SetInterfaceInput(interface_input_from)

            # Construct output mapper
            interface_output_to = self.solver_wrappers[index_other].GetInterfaceInput()
            self.solver_wrappers[index_mapped].SetInterfaceOutput(interface_output_to)

        # Initialize variables with deepcopy
        self.x = self.solver_wrappers[1].GetInterfaceOutput().deepcopy()
        self.r = self.x.deepcopy()
        self.xt = self.x.deepcopy()
        self.dx = self.x.deepcopy()

        self.predictor.Initialize(self.x)

    def Finalize(self):
        super().Finalize()

        for component in self.components:
            component.Finalize()

    def InitializeSolutionStep(self):
        super().InitializeSolutionStep()

        for component in self.components:
            component.InitializeSolutionStep()

    def SolveSolutionStep(self):
        # Coupling iteration loop
        while not self.convergence_criterion.IsSatisfied():
            if not self.convergence_accelerator.IsReady():
                self.x.CopyDataFrom(self.predictor.Predict(self.x))
            else:
                self.dx.CopyDataFrom(self.convergence_accelerator.Predict(self.r))
                self.x += self.dx
            y_tmp = self.solver_wrappers[0].SolveSolutionStep(self.x)
            self.xt.CopyDataFrom(self.solver_wrappers[1].SolveSolutionStep(y_tmp))
            self.r = self.xt - self.x

            self.convergence_accelerator.Update(self.x, self.xt)
            self.convergence_criterion.Update(self.r)

    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()

        self.predictor.Update(self.x)
        for component in self.components:
            component.FinalizeSolutionStep()

    def OutputSolutionStep(self):
        super().OutputSolutionStep()

        for component in self.components:
            component.OutputSolutionStep()

    def Check(self):
        super().Check()

        for component in self.components:
            component.Check()

    def PrintInfo(self):
        cs_tools.PrintInfo("The coupled solver ", self.__class__.__name__, " has the following components:")
        for component in self.components:
            component.PrintInfo()
