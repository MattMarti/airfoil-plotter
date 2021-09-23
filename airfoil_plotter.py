import tkinter as tk
from tkinter import filedialog
import logging

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

def thickness(x, t):
    """
    x - horizontal position (0 to 1)
    t - max thickness divided by chord length (0 to 1)
    """
    dyt_dt = 5 * (0.2969 * np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
    yt = t * dyt_dt
    return yt


def camber(x, m, p):
    """
    x - horizontal position (0 to 1)
    m - max camber
    p - location of max camber
    """
    dum = x <= p
    
    dyc_dm = np.zeros(x.shape)
    dyc_dm[dum] = 1/p**2 * (2*p*x[dum] - x[dum]**2)
    dyc_dm[~dum] = 1/(1-p)**2 * ((1-2*p)+2*p*x[~dum]-x[~dum]**2)
    
    yc = m*dyc_dm
    
    return yc

   
def camber_angle(x, m, p):
    dum = x <= p
    dyc_dx = np.zeros(x.shape)
    dyc_dx[dum] = 2*m/p**2 * (p-x[dum])
    dyc_dx[~dum] = 2*m/(1-p**2)*(p-x[~dum])
    return np.arctan(dyc_dx)


def upper(x, m, p, t):
    yt = thickness(x, t)
    yc = camber(x, m, p)
    y = yc + 0.5*yt
    
    theta = camber_angle(x, m, p)
    xu = x - yt*np.sin(theta)
    yu = yc + yt*np.cos(theta)
    
    return yu, xu
    

def lower(x, m, p, t):
    yt = thickness(x, t)
    yc = camber(x, m, p)
    y = yc - 0.5*yt
    
    theta = camber_angle(x, m, p)
    xl = x + yt*np.sin(theta)
    yl = y - yt*np.cos(theta)
    
    return yl, xl


def main():
    root = tk.Tk()
    root.withdraw()
    
    filename = tk.filedialog.askopenfilename(
        title="Select the airfoil surface points file",
        filetypes = [("Airfoil Surface Points", ".dat")])
    
    dat_raw = np.loadtxt(filename, delimiter=' ')

    # Divide in to upper and lower part
    idum = dat_raw[:,1] >= 0
    dat_upper = dat_raw[idum,:]
    dat_lower = dat_raw[~idum,:]
    
    # Initial guess
    m = 3 / 100
    p = 3 / 10
    t = 10 / 100
    
    # Solve airfoil
    xu = dat_raw[idum, 0]
    yu, xu = upper(xu, m, p, t)
    xl = dat_raw[~idum, 0]
    yl, xl = lower(xl, m, p, t)
    
    # Print out airfoil plot
    fig, ax = plt.subplots(1,1)
    ax.plot(dat_raw[:,0], dat_raw[:,1])
    ax.plot(np.concatenate((xu,xl)), np.concatenate((yu, yl), 0))
    ax.axis('equal')
    ax.grid(which='major')
    ax.minorticks_on()
    ax.grid(which='minor', linestyle='--', linewidth=0.3)
    
    plt.show()

    
if __name__ == '__main__':
    main()
