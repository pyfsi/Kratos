from __future__ import print_function, absolute_import, division  # makes KratosMultiphysics backward compatible with python 2.6 and 2.7

# Importing the Kratos Library
import KratosMultiphysics

# other imports
import os
from file_handler_utility import FileHandlerUtility

def Factory(settings, Model):
    if(type(settings) != KratosMultiphysics.Parameters):
        raise Exception("expected input shall be a Parameters object, encapsulating a json string")
    return PointOutputProcess(Model, settings["Parameters"])

class PointOutputProcess(KratosMultiphysics.Process):
    """This process writes results from a geometrical position (point) in the model to a file
    It first searches the entity containing the requested output location and then interpolates
    the requested variable(s)
    The output can be requested for elements, conditions and nodes. For nodes no geometrical
    interpolation is performed, the exact coordinates have to be specified.

    This process works in MPI as well as with restarts

    It can serve as a basis for other processes (e.g. MultiplePointsOutputProcess)
    Furthermore it can be used for testing in MPI where the node numbers can change
    """
    def __init__(self, model, params):

        default_settings = KratosMultiphysics.Parameters('''{
            "model_part_name"             : "",
            "entity_type"                 : "element",
            "position"                    : [],
            "output_variables"            : [],
            "flush_frequency"             : "",
            "output_file_name"            : ""
        }''')

        self.model = model

        self.params = params
        self.params.ValidateAndAssignDefaults(default_settings)

        # These quantites are lists such that they can be looped
        # => needed for mpi in case the point is in a different partition
        self.output_file = []
        self.entity = []
        self.area_coordinates = []
        self.output_variables = []

    def ExecuteInitialize(self):
        # getting the ModelPart from the Model
        model_part_name = self.params["model_part_name"].GetString()
        if model_part_name == "":
            raise Exception('No "model_part_name" was specified!')
        self.model_part = self.model[model_part_name]

        # retrieving the position of the entity
        point_position = self.params["position"].GetVector()
        if point_position.Size() != 3:
            raise Exception('The position has to be provided with 3 coordinates!')
        point = KratosMultiphysics.Point(point_position[0],
                                         point_position[1],
                                         point_position[2])

        # retrieving the output variables
        output_var_names = self.params["output_variables"]
        variable_names = [ output_var_names[i].GetString() for i in range( output_var_names.size() ) ]
        output_vars = [ KratosMultiphysics.KratosGlobals.GetVariable( var ) for var in variable_names ]
        if len(output_vars) == 0:
            raise Exception('No variables specified for output!')
        self.output_variables.append(output_vars)
        # validate types of variables
        for var in self.output_variables[0]:
            self.__CheckVariableIsSolutionStepVariable(var)
            if type(var) == KratosMultiphysics.DoubleVariable:
                continue
            elif type(var) == KratosMultiphysics.Array1DVariable3:
                continue
            elif type(var) == KratosMultiphysics.Array1DComponentVariable:
                continue
            else:
                err_msg  = 'Type of variable "' + var.Name() + '" is not valid\n'
                err_msg += 'It can only be double, component or array3d!'
                raise Exception(err_msg)

        # retrieving the entity type
        entity_type = self.params["entity_type"].GetString()

        if entity_type == "node":
            tol = 1e-12
            found_id = KratosMultiphysics.PointLocator(self.model_part).FindNode(point, tol)
            if found_id > -1:
                self.entity.append(self.model_part.Nodes[found_id]) # note that this is a find!
                self.area_coordinates.append("dummy") # needed for looping later
        elif entity_type == "element":
            self.sf_values = KratosMultiphysics.Vector()
            found_id = KratosMultiphysics.PointLocator(self.model_part).FindElement(point, self.sf_values)
            if found_id > -1:
                self.entity.append(self.model_part.Elements[found_id]) # note that this is a find!
                self.area_coordinates.append(self.sf_values)
        elif entity_type == "condition":
            self.sf_values = KratosMultiphysics.Vector()
            found_id = KratosMultiphysics.PointLocator(self.model_part).FindCondition(point, self.sf_values)
            if found_id > -1:
                self.entity.append(self.model_part.Conditions[found_id]) # note that this is a find!
                self.area_coordinates.append(self.sf_values)
        else:
            err_msg  = 'Invalid "entity_type" specified, it can only be:\n'
            err_msg += '"node", "element", "condition"'
            raise Exception(err_msg)

        # Check if a point was found, and initalize output
        # NOTE: If the search was not successful (i.e. found_id = -1), we fail silently and
        # do nothing. This is BY DESIGN, as we are supposed to work on MPI too, and the point
        # in question might lie on a different partition.
        # Here we also check if the point has been found in more than one partition
        # In sich a case only one rank (the one with the larger PID) writes the output!
        my_rank = -1 # dummy to indicate that the point is not in my partition
        if found_id > -1: # the point lies in my partition
            my_rank = self.model_part.GetCommunicator().MyPID()
        writing_rank = self.model_part.GetCommunicator().MaxAll(my_rank) # The partition with the larger rank writes

        if my_rank == writing_rank:
            # setting up the output_file
            output_file_name = self.params["output_file_name"].GetString()
            if not output_file_name.endswith(".dat"):
                output_file_name += ".dat"

            file_handler_params = KratosMultiphysics.Parameters('''{ "output_file_name" : "" }''')
            file_handler_params["output_file_name"].SetString(output_file_name)
            file_handler_params.AddValue("flush_frequency", self.params["flush_frequency"])

            file_header = GetFileHeader(entity_type, found_id, point, self.output_variables[0])
            self.output_file.append(FileHandlerUtility(self.model_part, file_handler_params, file_header))

    def ExecuteBeforeSolutionLoop(self):
        pass

    def ExecuteInitializeSolutionStep(self):
        pass

    def ExecuteFinalizeSolutionStep(self):
        time = self.model_part.ProcessInfo[KratosMultiphysics.TIME]

        # zip works with the shortes list, which is what we want here
        # i.e. if no entity was found then also no output_file will be
        # initialized which means that the loop body will never be executed
        for var_list,ent,coord,f in zip(self.output_variables, self.entity, self.area_coordinates, self.output_file):
            out = "{0:.12g}".format(time) # making the format more readable
            for var in var_list:
                value = Interpolate(var, ent, coord)

                if IsArrayVariable(var):
                    out += " " + " ".join( "{0:.16g}".format(v) for v in value )
                else:
                    out += " " + "{0:.16g}".format(value)

            out += "\n"
            f.write(out)

    def ExecuteBeforeOutputStep(self):
        pass

    def ExecuteAfterOutputStep(self):
        pass

    def ExecuteFinalize(self):
        for f in self.output_file:
            f.close()

    def __CheckVariableIsSolutionStepVariable(self, var):
        # if the requested Variable is a component we check the source Variable
        if type(var) == KratosMultiphysics.Array1DComponentVariable:
            var = var.GetSourceVariable()

        if not self.model_part.HasNodalSolutionStepVariable(var):
            err_msg  = 'ModelPart "' + self.model_part.Name + '" does not have'
            err_msg += ' "' + var.Name() + '" as SolutionStepVariable!'
            raise Exception(err_msg)


def GetFileHeader(entity_type, entity_id, point, output_variables):
    header  = '# Results for "' + entity_type + '" '
    header += 'with Id # ' + str(entity_id) + ' at position: '
    header += 'x: ' + "{0:.12g}".format(point.X) + '; '
    header += 'y: ' + "{0:.12g}".format(point.Y) + '; '
    header += 'z: ' + "{0:.12g}".format(point.Z) + '\n'
    header += '# time'
    for var in output_variables:
        # if this is a Variable< array_1d< double,3 > >
        if IsArrayVariable(var):
            header += " {0}_X {0}_Y {0}_Z".format(var.Name())
        else:
            header += " " + var.Name()

    header += "\n"

    return header

def Interpolate(variable, entity, sf_values):
    if type(entity) == KratosMultiphysics.Node:
        return entity.GetSolutionStepValue(variable)
    else: # entity is element or condition
        nodes = entity.GetNodes()
        # Initializing 'value' like this, i don't need to know its type
        # => this way it works both for scalar and array3 variables
        value = nodes[0].GetSolutionStepValue(variable) * sf_values[0]
        for n,c in zip(nodes[1:], sf_values[1:]):
            value = value + c * n.GetSolutionStepValue(variable)

        return value

def IsArrayVariable(var):
    return type(var) == KratosMultiphysics.Array1DVariable3
