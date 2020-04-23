import KratosMultiphysics as KM
import KratosMultiphysics.KratosUnittest as KratosUnittest
from KratosMultiphysics.CoSimulationApplication.co_simulation_interface import CoSimulationInterface
from KratosMultiphysics.CoSimulationApplication.co_simulation_tools import ImportDataStructure
import KratosMultiphysics.CoSimulationApplication.co_simulation_tools as cs_tools


class TestConvergenceCriterionOr(KratosUnittest.TestCase):
    def test_convergence_criterion_or(self):
        parameter_file_name = "test_parameters.json"
        cs_data_structure = ImportDataStructure(parameter_file_name)

        m = 10
        dz = 2.0
        a0 = 1.0
        interface_settings = cs_data_structure.Parameters('{"wall": "AREA"}')

        # Create interface
        variable = vars(KM)["AREA"]
        model = cs_data_structure.Model()
        model_part = model.CreateModelPart("wall")
        model_part.AddNodalSolutionStepVariable(variable)
        for i in range(m):
            model_part.CreateNewNode(i, 0.0, 0.0, i * dz)
        step = 0
        for node in model_part.Nodes:
            node.SetSolutionStepValue(variable, step, a0)
        interface = CoSimulationInterface(model, interface_settings)

        parameter_file_name = "convergence_criteria/test_or.json"
        with open(parameter_file_name, 'r') as parameter_file:
            settings = cs_data_structure.Parameters(parameter_file.read())

        convergence_criterion_or = cs_tools.CreateInstance(settings)
        convergence_criterion_or.Initialize()
        for i in range(3):
            convergence_criterion_or.InitializeSolutionStep()
            is_satisfied = convergence_criterion_or.IsSatisfied()
            self.assertFalse(is_satisfied)
            convergence_criterion_or.Update(interface)
            is_satisfied = convergence_criterion_or.IsSatisfied()
            self.assertFalse(is_satisfied)
            convergence_criterion_or.Update(interface)
            is_satisfied = convergence_criterion_or.IsSatisfied()
            self.assertTrue(is_satisfied)
            convergence_criterion_or.Update(interface)
            is_satisfied = convergence_criterion_or.IsSatisfied()
            self.assertTrue(is_satisfied)
            convergence_criterion_or.Update(interface)
            is_satisfied = convergence_criterion_or.IsSatisfied()
            self.assertTrue(is_satisfied)
            convergence_criterion_or.Update(interface)
            is_satisfied = convergence_criterion_or.IsSatisfied()
            self.assertTrue(is_satisfied)
            convergence_criterion_or.FinalizeSolutionStep()


if __name__ == '__main__':
    KratosUnittest.main()