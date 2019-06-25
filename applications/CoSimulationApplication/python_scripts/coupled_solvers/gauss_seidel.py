from KratosMultiphysics.CoSimulationApplication.co_simulation_component import CoSimulationComponent
from KratosMultiphysics.CoSimulationApplication.co_simulation_interface import CoSimulationInterface
import KratosMultiphysics.CoSimulationApplication.co_simulation_tools as cs_tools
cs_data_structure = cs_tools.cs_data_structure


def Create(parameters):
    return CoupledSolverGaussSeidel(parameters)


class CoupledSolverGaussSeidel(CoSimulationComponent):
    def __init__(self, parameters):
        super().__init__()

        self.parameters = parameters
        self.settings = parameters["settings"]

        self.echo_level = self.settings["echo_level"].GetInt()
        self.master_solver_interface = self.settings["master_solver_interface"].GetInt()

        self._predictor = cs_tools.CreateInstance(self.parameters["predictor"])
        self._convergence_accelerator = cs_tools.CreateInstance(self.parameters["convergence_accelerator"])
        self._convergence_criterion = cs_tools.CreateInstance(self.parameters["convergence_criterion"])
        self._solver_interfaces = []
        self._solver_interfaces.append(cs_tools.CreateInstance(self.parameters["wrappers"][0]))
        self._solver_interfaces.append(cs_tools.CreateInstance(self.parameters["wrappers"][1]))
        self._components = [self._predictor, self._convergence_accelerator, self._convergence_criterion,
                            self._solver_interfaces[0], self._solver_interfaces[1]]

        self.x = []

    def Initialize(self):
        super().Initialize()

        for component in self._components[1:-1]:
            component.Initialize()

        self.x = self._solver_interfaces[self.master_solver_interface].GetInterfaceIn()
        self._predictor.Initialize(self.x)

    def Finalize(self):
        super().Finalize()

        for component in self._components:
            component.Finalize()

    def InitializeSolutionStep(self):
        super().InitializeSolutionStep()

        for component in self._components:
            component.InitializeSolutionStep()

    def SolveSolutionStep(self):
        # Coupling iteration loop
        while not self._convergence_criterion.IsSatisfied():
            if not self._convergence_accelerator.IsReady():
                self.x = self._predictor.Predict()
            else:
                dx = self._convergence_accelerator.Predict(r)
                self.x += dx
            y = self._solver_interfaces[0].SolveSolutionStep(self.x)
            xt = self._solver_interfaces[1].SolveSolutionStep(y)
            r = xt - self.x
            self._convergence_accelerator.Update(self.x, xt)
            self._convergence_criterion.Update(r)

    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()

        self._predictor.Update(self.x)
        for component in self._components:
            component.FinalizeSolutionStep()

    def OutputSolutionStep(self):
        super().OutputSolutionStep()

        for component in self._components:
            component.OutputSolutionStep()

    def Check(self):
        super().Check()

        for component in self._components:
            component.Check()

    def PrintInfo(self):
        cs_tools.PrintInfo("The coupled solver ", self.__class__.__name__, " has the following components:")
        for component in self._components:
            component.PrintInfo()
