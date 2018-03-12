# ==============================================================================
#  KratosShapeOptimizationApplication
#
#  License:         BSD License
#                   license: ShapeOptimizationApplication/license.txt
#
#  Main authors:    Baumgaertner Daniel, https://github.com/dbaumgaertner
#
# ==============================================================================

# Making KratosMultiphysics backward compatible with python 2.6 and 2.7
from __future__ import print_function, absolute_import, division

# importing the Kratos Library
from KratosMultiphysics import *
from KratosMultiphysics.ALEApplication import *
from KratosMultiphysics.ShapeOptimizationApplication import *

# check that KratosMultiphysics was imported in the main script
CheckForPreviousImport()

# Additional imports
import time as timer

from mesh_controller_base import MeshController
from ale_analysis import ALEAnalysis

# # ==============================================================================
class MeshControllerUsingALESolver( MeshController) :
    # --------------------------------------------------------------------------
    def __init__( self, OptimizationModelPart, MeshSolverSettings ):
        self.OptimizationModelPart = OptimizationModelPart

        default_settings = Parameters("""
        {
            "apply_ale_mesh_solver" : true,
            "problem_data" : {
                "echo_level" : 0,
                "time_step" : 1.1,
                "start_time" : 0.0,
                "end_time" : 1.0,
                "parallel_type" : "OpenMP"
            },
            "solver_settings" : {
                "solver_type" : "mesh_solver_structural_similarity",
                "ale_linear_solver_settings" : {
                    "solver_type" : "AMGCL",
                    "smoother_type":"ilu0",
                    "krylov_type": "gmres",
                    "coarsening_type": "aggregation",
                    "max_iteration": 200,
                    "verbosity" : 0,
                    "tolerance": 1e-7
                },
                "compute_reactions"         : false,
                "calculate_mesh_velocities" : false
            }
        }""")
        self.MeshSolverSettings = MeshSolverSettings
        self.MeshSolverSettings.ValidateAndAssignDefaults(default_settings)

        self.MeshSolverSettings["problem_data"].AddEmptyValue("domain_size")
        self.MeshSolverSettings["problem_data"]["domain_size"].SetInt( self.OptimizationModelPart.ProcessInfo[DOMAIN_SIZE] )

        self.mesh_solver = ALEAnalysis( self.MeshSolverSettings, self.OptimizationModelPart )

    # --------------------------------------------------------------------------
    def Initialize( self ):
        self.mesh_solver.Initialize()

    # --------------------------------------------------------------------------
    def UpdateMeshAccordingInputVariable( self, InputVariable ):
        print("\n> Starting to update the mesh...")
        startTime = timer.time()

        VariableUtils().SetToZero_VectorVar(MESH_DISPLACEMENT,self.OptimizationModelPart.Nodes)

        sub_model_part_name = "surface_nodes"
        GeometryUtilities(self.OptimizationModelPart).ExtractSurfaceNodes(sub_model_part_name)
        surface_nodes = self.OptimizationModelPart.GetSubModelPart(sub_model_part_name).Nodes

        VariableUtils().ApplyFixity(MESH_DISPLACEMENT_X, True, surface_nodes)
        VariableUtils().ApplyFixity(MESH_DISPLACEMENT_Y, True, surface_nodes)
        VariableUtils().ApplyFixity(MESH_DISPLACEMENT_Z, True, surface_nodes)
        VariableUtils().CopyVectorVar(SHAPE_UPDATE, MESH_DISPLACEMENT, surface_nodes)

        self.mesh_solver.InitializeTimeStep()
        self.mesh_solver.SolveTimeStep()
        self.mesh_solver.FinalizeTimeStep()

        MeshControllerUtilities( self.OptimizationModelPart ).LogMeshChangeAccordingInputVariable( MESH_DISPLACEMENT )

        print("> Time needed for updating the mesh = ",round(timer.time() - startTime,2),"s")

    # --------------------------------------------------------------------------
    def Finalize( self ):
        self.mesh_solver.Finalize()

# ==============================================================================