#Import of utilities
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.pyplot import xticks, yticks
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import sys
import os  # to be able to run Linux terminal commands
from matplotlib import cm
import warnings
import pickle
import matplotlib.animation as animation

matplotlib.rcParams['font.size'] = 20
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['lines.linewidth'] = 2
matplotlib.rcParams['axes.labelweight'] = 'bold'
matplotlib.rcParams['xtick.major.size'] = 6
matplotlib.rcParams['xtick.minor.size'] = 2.4
matplotlib.rcParams['ytick.major.size'] = 6
matplotlib.rcParams['ytick.minor.size'] = 2.4
matplotlib.rcParams['savefig.dpi'] = 300

it = 1
TS = 1


file_load_F = f"CFD/pressure_traction_timestep{TS}_thread3_Iter{it}.dat" #WSSx WSSy p
file_load_A = f"CSM/CSM_Time{TS}Surface0Cpu0Input_Iter{it}.dat"

file_pos_F = f"CFD/nodes_update_timestep{TS}_thread3_Iter{it-1}.dat" #xpos ypos id
file_pos_F2 = f"CFD/nodes_update_timestep{TS}_thread3_Iter{it}.dat" #xpos ypos id
file_pos_A = f"CSM/CSM_Time{TS}Surface0Output_Iter{it}.dat"

F_nodes_file = f"CFD/nodes_timestep0_thread3.dat" #x y id
F_faces_file = f"CFD/faces_timestep0_thread3.dat" #x y id1 id2 (id3 id4)

A_nodes_file = f""
A_faces_file = f"CSM/CSM_Time0Surface0Cpu0Faces.dat" #elem_num lp_id x y

F_nodes = np.array(pd.read_csv(F_nodes_file,sep="\s+",header=None,skiprows=1))
F_lp = np.array(pd.read_csv(F_faces_file,sep="\s+",header=None,skiprows=1))
F_pos = np.array(pd.read_csv(file_pos_F,sep="\s+",header=None,skiprows=1))
F_pos0 = np.array(pd.read_csv(F_nodes_file,sep="\s+",header=None,skiprows=1))
F_pos2 = np.array(pd.read_csv(file_pos_F2,sep="\s+",header=None,skiprows=1))
F_load = np.array(pd.read_csv(file_load_F,sep="\s+",header=None,skiprows=1))

A_pos = np.array(pd.read_csv(file_pos_A,sep="\s+",header=None,skiprows=1))
A_load = np.array(pd.read_csv(file_load_A,sep="\s+",header=None,skiprows=1))

file_A_pos0 = f"CSM/CSM_Time0Surface0Nodes.dat"
A_pos0 = np.array(pd.read_csv(file_A_pos0,sep="\s+",header=None,skiprows=1))

plt.figure(1)

#Fluent position
A = F_pos0[np.argsort(F_pos0[:,0]),:]
plt.plot(A[:,0],A[:,1], label = "Initial")
A = F_pos[np.argsort(F_pos[:,0]),:]
plt.plot(A[:,0],A[:,1], label = f"Iter{it-1}")
A = F_pos2[np.argsort(F_pos2[:,0]),:]
plt.plot(A[:,0],A[:,1], label = f"Iter{it}")
plt.legend()

#Abaqus position
A = A_pos0 + A_pos
B = A[np.argsort(A[:,1]),:]
plt.plot(B[:,1],B[:,0],label = f"Abaq_Iter{it}")
plt.legend()

#Tango position
file = f"/cfdfile2/data/fm/lucas/Tango_Test/Data/FluentSolver0/FSI1Refine0Time{TS}Surface0Input_Iter{it}.dat"
pos = np.array(pd.read_csv(file,header=None,skiprows=1,sep="\s+"))
sort_id = np.argsort(pos[:,0])
plt.plot(pos[sort_id,0],pos[sort_id,1],':',label="Pos_Tango_Fluent")

file = f"/cfdfile2/data/fm/lucas/Tango_Test/Data/AbaqusSolver0/FSI1Refine0Time{TS}Surface0Output_Iter{it}.dat"
file0 = f"/cfdfile2/data/fm/lucas/Tango_Test/Data/AbaqusSolver0/FSI1Refine0Time0Surface0Nodes.dat"
pos0 = np.array(pd.read_csv(file0,header=None,skiprows=1,sep="\s+"))
pos = pos0+np.array(pd.read_csv(file,header=None,skiprows=1,sep="\s+"))
sort_id = np.argsort(pos[:,0])
plt.plot(pos[sort_id,0],pos[sort_id,1],':',label="Pos_Tango_Abaqus")
plt.legend()


#Abaqus load
file = f"CSM/CSM_Time0Surface0Elements.dat"
temp = np.array(pd.read_csv(file,header=None))
A_lp = np.array(pd.read_csv(A_faces_file,sep="\s+",header=None,skiprows=0))[:int(temp[0]*temp[1]),[2,3]]
sort_id = np.argsort(A_lp[:,1])

plt.figure(4)
plt.plot(A_lp[sort_id,1],A_load[sort_id,0],'--', label="CoCo_Abaq",marker='o')
B = A_load[sort_id,0]
plt.figure(5)
plt.plot(A_lp[sort_id,1],A_load[sort_id,2],'--', label="CoCo_Abaq")
plt.figure(6)
plt.plot(A_lp[sort_id,1],A_load[sort_id,1],'--', label="CoCo_Abaq")


#Fluent load
sort_id = np.argsort(F_lp[:,0])
plt.figure(4)
plt.ylabel("pressure")
plt.plot(F_lp[sort_id ,0],F_load[sort_id,2], label="CoCo_Fluent",marker='o')
CCx = F_load[sort_id, 2]
CCy = F_load[sort_id, 0]
CCz = F_load[sort_id, 1]
plt.figure(5)
plt.ylabel("axial shear")
plt.plot(F_lp[sort_id ,0],F_load[sort_id,0], label="CoCo_Fluent")
plt.figure(6)
plt.plot(F_lp[sort_id ,0],F_load[sort_id,1], label="CoCo_Fluent")
plt.ylabel("radial shear")

#Tango load
if True:
    file = f"/cfdfile2/data/fm/lucas/Tango_Test/Data/AbaqusSolver0/FSI1Refine0Time{TS}Surface0Cpu0Input_Iter{it}.dat"
    load = np.array(pd.read_csv(file,sep="\s+",header=None,skiprows=1))

    file = "/cfdfile2/data/fm/lucas/Tango_Test/Data/AbaqusSolver0/FSI1Refine0Time0Surface0Faces.dat"
    lp = np.array(pd.read_csv(file,sep="\s+",header=None,skiprows=1))[:,[2,3]]
    sort_id = np.argsort(lp[:,0])

    plt.figure(4)
    plt.plot(lp[sort_id,0],load[sort_id,0],':', label="Tango_Abaq",marker='o')
    plt.legend()
    plt.figure(5)
    plt.plot(lp[sort_id,0],load[sort_id,1],':', label="Tango_Abaq")
    plt.legend()
    plt.figure(6)
    plt.plot(lp[sort_id,0],load[sort_id,2],':', label="Tango_Abaq")

    plt.figure(7)
    plt.plot(lp[sort_id,0],load[sort_id,0]-B,label="diff_load_Abaqus")

    file = f"/cfdfile2/data/fm/lucas/Tango_Test/Data/FluentSolver0/FSI1Refine0Time{TS}Surface0Output_Iter{it}.dat"
    load = np.array(pd.read_csv(file,sep="\s+",header=None,skiprows=1))

    file = "/cfdfile2/data/fm/lucas/Tango_Test/Data/FluentSolver0/FSI1Refine0Time0Surface0Faces.dat"
    lp = np.array(pd.read_csv(file,sep="\s+",header=None,skiprows=1))
    sort_id = np.argsort(lp[:,0])
    Cx = load[sort_id,0]
    Cy = load[sort_id,1]
    Cz = load[sort_id,2]

    plt.plot(lp[sort_id,0],Cx-CCx,label="diff_pressure_Fluent")
    plt.plot(lp[sort_id,0],Cy-CCy,label="diff_WSSx_Fluent")
    plt.plot(lp[sort_id,0],Cz-CCz,label="diff_WSSy_Fluent")

    plt.legend()


plt.show()
