from __future__ import print_function, absolute_import, division  # makes KratosMultiphysics backward compatible with python 2.6 and 2.7

# Importing the Kratos Library
import KratosMultiphysics

# Import base class file
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_solver import MechanicalSolver

def CreateSolver(model, custom_settings):
    return StaticMechanicalSolver(model, custom_settings)

class StaticMechanicalSolver(MechanicalSolver):
    """The structural mechanics static solver.

    This class creates the mechanical solvers for static analysis.

    See structural_mechanics_solver.py for more information.
    """
    def __init__(self, model, custom_settings):
        # Construct the base solver.
        super(StaticMechanicalSolver, self).__init__(model, custom_settings)
        KratosMultiphysics.Logger.PrintInfo("::[StaticMechanicalSolver]:: ", "Construction finished")

    def _create_solution_scheme(self):
        return KratosMultiphysics.ResidualBasedIncrementalUpdateStaticScheme()
