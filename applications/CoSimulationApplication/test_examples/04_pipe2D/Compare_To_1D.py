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

diff = []
for i in range(0,101):
    file = f"CSD/Area_TS{i}"
    A = np.array(pd.read_csv(file,sep="\s+"))

    file = f"../04_tube/CSD/Area_TS{i}"
    B = np.array(pd.read_csv(file,sep="\s+"))

    diff.append(np.max(np.abs(B[:,1]-A[:,1])))

plt.plot(range(0,101),diff)

i = 50

file = f"CSD/Area_TS{i}"
A = np.array(pd.read_csv(file, sep="\s+"))

file = f"../04_tube/CSD/Area_TS{i}"
B = np.array(pd.read_csv(file, sep="\s+"))

plt.figure()
plt.plot(A[:,0],A[:,1])
plt.plot(B[:,0],B[:,1])

plt.show()