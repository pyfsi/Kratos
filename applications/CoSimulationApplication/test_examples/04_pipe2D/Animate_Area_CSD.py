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

fig, ax = plt.subplots()
file = f"CSD/Area_TS0"
A = np.array(pd.read_csv(file, sep="\s+"))
x = A[:,0]
line, = ax.plot(x, A[:,1])
plt.ylim([1.5e-05,2.5e-05])



def init():  # only required for blitting to give a clean slate.
    line.set_ydata([np.nan] * len(x))
    return line,


def animate(i):
    # print(i)
    file = f"CSD/Area_TS{i}"
    A = np.array(pd.read_csv(file,sep="\s+"))
    line.set_ydata(A[:,1])  # update the data.
    return line,

ani = animation.FuncAnimation(
    fig, animate, init_func=init, interval=100, blit=True, save_count=50,repeat=True,frames=range(1,101))

plt.show()