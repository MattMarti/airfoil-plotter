# Python 3

import tkinter as tk
from tkinter import filedialog
import logging

import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


GUI_BUTTON_WIDTH = 20
GUI_BUTTON_PADDING = 20


def empty_func():
    pass


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


class NacaFourDigitFrame:
    
    def __init__(self):
        self.m = 0
        self.p = 3
        self.t = 10
    
    def set_gui_options(self, frame):
        naca_digit_label = tk.Label(
            master=frame,
            text='NACA 4 Digit')
        naca_digit_label.pack(side=tk.TOP)
        
        m_frame = tk.Frame(master=frame)
        m_frame.pack(side=tk.TOP)
        
        m_label = tk.Label(
            m_frame,
            text='M',
            width=round(GUI_BUTTON_WIDTH/2))
        m_label.pack(side=tk.LEFT)
        
        self.m_entry = tk.Entry(
            m_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.m_entry.pack(side=tk.RIGHT)
        self.m_entry.insert(0, "5")
        
        p_frame = tk.Frame(master=frame)
        p_frame.pack(side=tk.TOP)
        
        p_label = tk.Label(
            p_frame,
            text='P',
            width=round(GUI_BUTTON_WIDTH/2))
        p_label.pack(side=tk.LEFT)
        
        self.p_entry = tk.Entry(
            p_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.p_entry.pack(side=tk.RIGHT)
        self.p_entry.insert(0, "3")
        
        t_frame = tk.Frame(master=frame)
        t_frame.pack(side=tk.TOP)
        
        t_label = tk.Label(
            t_frame,
            text='T',
            width=round(GUI_BUTTON_WIDTH/2))
        t_label.pack(side=tk.LEFT)
        
        self.t_entry = tk.Entry(
            t_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.t_entry.pack(side=tk.RIGHT)
        self.t_entry.insert(0, "8")
    
    def get_m(self):
        return int(self.m_entry.get()) / 100
    
    def get_p(self):
        return int(self.p_entry.get()) / 10
    
    def get_t(self):
        return int(self.t_entry.get()) / 100
    
    def get_upper_surface(self):
        m = self.get_m()
        p = self.get_p()
        t = self.get_t()
        xu = np.arange(1, 0, -0.0001)
        yu, xu = upper(xu, m, p, t)
        return xu, yu
    
    def get_lower_surface(self):
        m = self.get_m()
        p = self.get_p()
        t = self.get_t()
        xl = np.arange(0, 1, 0.0001)
        yl, xl = lower(xl, m, p, t)
        return xl, yl
    

class GuiData:

    def __init__(self, fig):
        self.fig = fig
        self.data_filename = None
        self.imported_data = None
        self.naca_params = None
        self.imported_chord = 1.0
    
    def user_select_file_and_update(self):
        self.data_filename = tk.filedialog.askopenfilename(title="Select the airfoil data file")
        if self.data_filename is not None and self.data_filename != '':
            self.import_file(self.data_filename)
            self.plot_stuff()
    
    def import_file(self, filename:str):
        self.imported_data = np.loadtxt(filename, delimiter=' ')
    
    def set_imported_chord(self, chord):
        self.imported_chord = chord
        self.plot_stuff()
    
    def plot_stuff(self, naca_data_frame):
        
        # Initial guess
        #m = 5 / 100
        #p = 3 / 10
        #t = 8 / 100
        
        # Solve airfoil
        #xu = np.arange(1, 0, -0.0001)
        #yu, xu = upper(xu, m, p, t)
        #xl = np.arange(0, 1, 0.0001)
        #yl, xl = lower(xl, m, p, t)
        
        xu, yu = naca_data_frame.get_upper_surface()
        xl, yl = naca_data_frame.get_lower_surface()
        
        # Update the plot
        ax = self.fig.axes[0]
        ax.clear()
        sf = self.imported_chord
        ax.plot(self.imported_data[:,0]/sf, self.imported_data[:,1]/sf)
        ax.plot(np.concatenate((xu,xl)), np.concatenate((yu, yl), 0))
        ax.axis('equal')
        ax.grid(which='major')
        ax.minorticks_on()
        ax.grid(which='minor', linestyle='--', linewidth=0.3)
        self.fig.canvas.draw()


def quit_gui(self, root):
    root.quit()
    root.destroy()


def main():
    root = tk.Tk()
    root.title('Airfoil Plotter')
    
    # Figure
    fig = Figure(figsize=(5,4), dpi=100)
    ax = fig.add_subplot(111)
    
    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()
    
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    
    toolbar.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    gui_data = GuiData(fig)
    
    
    # Settings
    settings_frame = tk.Frame(master=root)
    settings_frame.pack(side=tk.RIGHT)
    
    
    # Digit Settings
    naca_digit_frame = tk.Frame(master=settings_frame)
    naca_digit_frame.pack(side=tk.RIGHT)
    
    naca_data_frame = NacaFourDigitFrame()
    naca_data_frame.set_gui_options(naca_digit_frame)
    
    
    # Plotting
    ok_button = tk.Button(
        naca_digit_frame,
        text='Plot',
        width=round(GUI_BUTTON_WIDTH/2),
        command=lambda: gui_data.plot_stuff(naca_data_frame))
    ok_button.pack(side=tk.BOTTOM)
    
    
    # File Select
    file_select_frame = tk.Frame(master=settings_frame)
    file_select_frame.pack(side=tk.RIGHT)
    
    file_select_button = tk.Button(
        file_select_frame,
        text='Select File',
        width=round(GUI_BUTTON_WIDTH),
        command=lambda: gui_data.user_select_file_and_update())
    file_select_button.pack(side=tk.TOP)
    
    chord_length_entry = tk.Entry(
        file_select_frame,
        width=round(GUI_BUTTON_WIDTH/2))
    chord_length_entry.pack(side=tk.RIGHT)
    chord_length_entry.insert(0, '1.0')
    
    chord_length_button = tk.Button(
        file_select_frame,
        text='Scale Factor',
        width=round(GUI_BUTTON_WIDTH/2),
        command=lambda: gui_data.set_imported_chord(float(chord_length_entry.get())))
    chord_length_button.pack(side=tk.LEFT)
    
    
    # Fire it up
    filename = "D:\Documents\Personal\Projects\RC\Stratosurfer\Airfoil Analysis\stratosurfer.dat"#tk.filedialog.askfilename(title="Select the airfoil data file")
    gui_data.import_file(filename)
    gui_data.plot_stuff(naca_data_frame)

    root.mainloop()

    
if __name__ == '__main__':
    main()
