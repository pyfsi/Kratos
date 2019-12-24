import KratosMultiphysics as KM
import KratosMultiphysics.KratosUnittest as KratosUnittest
from KratosMultiphysics.CoSimulationApplication.co_simulation_interface import CoSimulationInterface
from KratosMultiphysics.CoSimulationApplication.co_simulation_tools import ImportDataStructure
import KratosMultiphysics.CoSimulationApplication.co_simulation_tools as cs_tools

class TestPredictorLinear(KratosUnittest.TestCase):
    def test_predictor_linear(self):
        parameter_file_name = "test_parameters.json"
        cs_data_structure = ImportDataStructure(parameter_file_name)

        m = 10
        dz = 3.0
        a0 = 1.0
        p1 = 1.0
        a1 = 2.0
        p2 = 3.0
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

        # Create predictor
        parameter_file_name = "predictors/test_linear.json"
        with open(parameter_file_name, 'r') as parameter_file:
            settings = cs_data_structure.Parameters(parameter_file.read())

        predictor_linear = cs_tools.CreateInstance(settings)
        predictor_linear.Initialize(interface)

        # Test predictor: first prediction needs to be equal to initialized value
        predictor_linear.InitializeSolutionStep()
        prediction = predictor_linear.Predict(interface)
        self.assertIsInstance(prediction, CoSimulationInterface)
        prediction_as_array = prediction.GetNumpyArray()
        for i in range(m):
            self.assertAlmostEqual(p1, prediction_as_array[i])
        interface_as_array = a1 * prediction_as_array
        interface.SetNumpyArray(interface_as_array)
        predictor_linear.Update(interface)
        predictor_linear.FinalizeSolutionStep()

        # Test predictor: second prediction needs to be linear
        predictor_linear.InitializeSolutionStep()
        prediction = predictor_linear.Predict(interface)
        self.assertIsInstance(prediction, CoSimulationInterface)
        prediction_as_array = prediction.GetNumpyArray()
        for i in range(m):
            self.assertAlmostEqual(p2, prediction_as_array[i])


if __name__ == '__main__':
    KratosUnittest.main()
