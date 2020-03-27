# SolverWrapperAbaqus

This is the documentation for all Abaqus SolverWrappers.
Currently only FSI simulations are supported, no other multiphysics problems. 
Subcycling within the structural solver is possible.

## Terminology
`Main directory`: Directory where the Python code will be executed  
`Source directory`(for wrapper): <span style="color:red">Kratos/applications/CoSimulationApplication/python_scripts/solver_wrappers/abaqus/</span>  
`Extra directory`: Subdirectory of the source directory with some files to assist with the setup  
`Working directory`: Subdirectory of the main directory where Abaqus will be running   
`Geometrical nodes`: Nodes in Abaqus related to the geometry of the elements. At these nodes the displacement data is exported.   
`Loadpoints`: Every element has load points. This is where the loads (input to Abaqus) are applied.  

## Environment

## Input File

## Parameters 
This section describes the Parameters in the JSON file, listed in alphabetical order. A distinction is made between mandatory and optional parameters.
### Mandatory
parameter|type|description
---:|:---:|---
`arraysize`|integer|Size specification for array in FORTRAN part of the code. Should be large enough and depends on the number of load points in the structural model.
`cores`|integer|Number of cores to be used by Abaqus
`delta_t`|float|Size of the time step in Abaqus (Should be synchronized with the flow solver). This parameter is usually specified in a higher CoSimulationObject.
`dimensions`|integer|Dimensionality of the problem (2 or 3)
`interface_input`|dict|Should contain `surfaces` keys. Keys are names of ModelParts for Abaqus load points. Each name (key) must be the contain an entry from `surfaceIDs`. The list that follows specifies the historical variables that should be included in this modelpart. (Note the comma) <br> <br> <b>Example:</b> <br> &emsp;"NODESETA_load_points": ["PRESSURE", "TRACTION"],<br>&emsp;"NODESETB_load_points": ["PRESSURE", "TRACTION"]
`interface_output`|dict|Similar to interface_input but for Abaqus load points.
`input_file`|string|Name of the input file provided by the user. <br> <b>Example:</b> “Base.inp”
`mp_mode`|string|Determines how Abaqus is executed in parallel. Should be “THREADS” as “MPI”  is currently not implemented
`save_iterations`|integer|Determines what files are kept by Abaqus. All files are saved, but files not corresponding to the save_iterations are removed at the end of a time step. Important for restart options (also in correspondence with the save interval of the flow solver).
`surfaceIDs`|list of strings|Comma-separated list with the names of the node sets associated with the geometrical nodes on the interface surfaces. <br><br> <b>Example:</b>  [“NODESETA”, “NODESETB”] <br> <br> <b>Important notes:</b><br> &emsp;•	The sequence of these surfaces has to correspond with the integer specified in the corresponding load-surface (See the Input file section)<br>&emsp;•	The names of these surfaces should be all UPPERCASE as Abaqus recasts these when opening the .inp file.
`surfaces`|integer|Number of surfaces on the FSI interface. Should correspond with the number of elements in `surfaceIDs`.
`timestep_start`|integer|Time step to start from [data should be available at this time step. For a new simulation this value will typically be 0] (Should be synchronized with the flow solver). This parameter is usually specified in a higher CoSimulationObject. 
`working_directory`|string|Relative path to the directory in which Abaqus will be executed and where all structural information will be stored. <br> Should be created before execution and contain an `AbaqusHosts.txt` file.

`timestep_start` and `delta_t` are necessary parameters, but are usually defined in a higher CoSimulationObject. However, they can also be given directly as parameter of the solver wrapper (e.g. for standalone testing). If they are defined both in higher object and in the solver wrapper, then the former value is used and a warning is printed.

If different parameters are used with different Abaqus versions, this should be specified both in this section and in the version specific documentation section.

### Optional
parameter|type|description
---:|:---:|---
`initialInc`|float|Required when subcycling is enabled. Contains the size of the first substep attempted Abaqus
`maxInc`|float|Required when subcycling is enabled. Contains the maximal size allowed for a substep
`maxNumInc`|integer|Required when subcycling is enabled. Contains the maximum number of increments that Abaqus is allowed to perform for one time step 
`minInc`|float|Required when subcycling is enabled. Contains the minimal size allowed for a substep
`ramp`|integer| Only important when subcycling is enabled in Abaqus. <br> <b>0</b>: Load is considered to be constant throughout the time step <br><b>1</b>: [Default] Load is applied in a ramped fashion throughout the time step 
`subcycling`|integer|<b>0</b>: [Default] Abaqus solves the requested time step using one increment <br> <b>1</b>: Abaqus is allowed to solve the time step using multiple increments, often required when contact is involved 

