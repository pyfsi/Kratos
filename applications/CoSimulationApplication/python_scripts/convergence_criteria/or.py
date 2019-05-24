from KratosMultiphysics.CoSimulationApplication.co_simulation_component import CoSimulationComponent
import KratosMultiphysics.CoSimulationApplication.co_simulation_tools as cs_tools
cs_data_structure = cs_tools.cs_data_structure


def Create(parameters):
    return ConvergenceCriterionOr(parameters)


class ConvergenceCriterionOr(CoSimulationComponent):
    def __init__(self, parameters):
        super().__init__()

        settings = parameters["settings"]
        self._convergence_criteria = []
        index = 0
        while True:
            key = "convergence_criterion" + str(index)
            if key in settings.keys():
                self._convergence_criteria.append(cs_tools.CreateInstance(settings[key]))
                index += 1
            else:
                break

    def Update(self, r):
        for convergence_criterion in self._convergence_criteria:
            convergence_criterion.Update(r)

    def IsSatisfied(self):
        is_satisfied = False
        for convergence_criterion in self._convergence_criteria:
            is_satisfied = is_satisfied or convergence_criterion.IsSatisfied()

        return is_satisfied

    def PrintInfo(self):
        super().PrintInfo()

        for convergence_criterion in self._convergence_criteria:
            convergence_criterion.PrintInfo()