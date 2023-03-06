# Python 3

import tkinter as tk
from tkinter import filedialog
import logging

import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from airfoil_defs.naca_four_digit_airfoil import NacaFourDigitAirfoil


GUI_BUTTON_WIDTH = 20
GUI_BUTTON_PADDING = 20


def empty_func():
    pass


class NacaFourDigitSettingsFrame:

    def __init__(self):
        pass

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
            width=round(GUI_BUTTON_WIDTH/4))
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
            width=round(GUI_BUTTON_WIDTH/4))
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
            width=round(GUI_BUTTON_WIDTH/4))
        t_label.pack(side=tk.LEFT)

        self.t_entry = tk.Entry(
            t_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.t_entry.pack(side=tk.RIGHT)
        self.t_entry.insert(0, "8")

    def get_m(self):
        return int(self.m_entry.get())

    def get_p(self):
        return int(self.p_entry.get())

    def get_t(self):
        return int(self.t_entry.get())

    def get_upper_surface(self):
        m = self.get_m()
        p = self.get_p()
        t = self.get_t()
        airfoil = NacaFourDigitAirfoil(m, p, t)
        xu = np.linspace(1, 0, 10000)
        xu, yu = airfoil.get_upper(xu)
        return xu, yu

    def get_lower_surface(self):
        m = self.get_m()
        p = self.get_p()
        t = self.get_t()
        airfoil = NacaFourDigitAirfoil(m, p, t)
        xl = np.linspace(0, 1, 10000)
        xl, yl = airfoil.get_lower(xl)
        return xl, yl


class AirfoilLoader:

    def __init__(self):
        self.imported_data = None

    @property
    def x(self):
        if self.imported_data is None:
            return None
        return self.imported_data[:,0]

    @property
    def y(self):
        if self.imported_data is None:
            return None
        return self.imported_data[:,1]

    def import_file(self, filename:str):
        self.imported_data = np.loadtxt(filename)


class AirfoilImportSettings:
    def __init__(self):
        self.filename = None
        self.sf = 1.0
        self.invert_xy = False


class GuiData:

    def __init__(self, fig, airfoil_builder):
        self.fig = fig
        self.airfoil_builder = airfoil_builder
        self.airfoil_loader = AirfoilLoader()
        self.import_settings = AirfoilImportSettings()
        self.naca_params = None

    def user_select_file_and_update(self):
        filename = tk.filedialog.askopenfilename(title="Select the airfoil data file")
        if filename is not None and filename != '':
            self.import_file(filename)
            self.update_plot()

    def import_file(self, filename:str):
        self.airfoil_loader.import_file(filename=filename)

    def set_imported_scale_factor(self, sf):
        self.import_settings.sf = sf
        self.update_plot()

    def toggle_switch_imported_xy(self):
        self.import_settings.invert_xy = not self.import_settings.invert_xy
        self.update_plot()

    def update_plot(self):
        ax = self.fig.axes[0]
        ax.clear()

        # Imported airfoil
        sf = self.import_settings.sf
        if self.airfoil_loader.imported_data is not None:
            if not self.import_settings.invert_xy:
                x = self.airfoil_loader.x
                y = self.airfoil_loader.y
            else:
                x = self.airfoil_loader.y
                y = self.airfoil_loader.x
            ax.plot(x/sf, y/sf, color="blue")

        # Calculated airfoil
        xu, yu = self.airfoil_builder.get_upper_surface()
        xl, yl = self.airfoil_builder.get_lower_surface()
        ax.plot(np.concatenate((xu,xl)), np.concatenate((yu, yl), 0), color="orange")

        # Plot decorations
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

    # Airfoil builder
    naca_surface_builder_frame = NacaFourDigitSettingsFrame()

    # Figure
    fig = Figure(figsize=(5,4), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()

    toolbar.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    gui_data = GuiData(fig, naca_surface_builder_frame)

    # Settings
    settings_frame = tk.Frame(master=root)
    settings_frame.pack(side=tk.RIGHT)

    # Digit Settings
    naca_digit_frame = tk.Frame(master=settings_frame)
    naca_digit_frame.pack(side=tk.RIGHT)
    naca_surface_builder_frame.set_gui_options(naca_digit_frame)

    # Plotting
    ok_button = tk.Button(
        naca_digit_frame,
        text='Plot',
        width=round(GUI_BUTTON_WIDTH/2),
        command=lambda: gui_data.update_plot())
    ok_button.pack(side=tk.BOTTOM)


    # Import
    file_select_frame = tk.Frame(master=settings_frame)
    file_select_frame.pack(side=tk.RIGHT)

    file_select_button = tk.Button(
        file_select_frame,
        text='Select File',
        width=round(GUI_BUTTON_WIDTH),
        command=lambda: gui_data.user_select_file_and_update())
    file_select_button.pack(side=tk.TOP)

    chord_length_frame = tk.Frame(master=file_select_frame)
    chord_length_frame.pack(side=tk.TOP)

    chord_length_entry = tk.Entry(
        chord_length_frame,
        width=round(GUI_BUTTON_WIDTH/2))
    chord_length_entry.pack(side=tk.RIGHT)
    chord_length_entry.insert(0, '1.0')

    chord_length_button = tk.Button(
        chord_length_frame,
        text='Scale Factor',
        width=round(GUI_BUTTON_WIDTH/2),
        command=lambda: gui_data.set_imported_scale_factor(float(chord_length_entry.get())))
    chord_length_button.pack(side=tk.LEFT)

    switch_xy_button = tk.Button(
        file_select_frame,
        text="Switch XY",
        width=round(GUI_BUTTON_WIDTH/2),
        command=lambda: gui_data.toggle_switch_imported_xy())
    switch_xy_button.pack(side=tk.TOP)


    # Start GUI
    gui_data.update_plot()

    root.mainloop()


if __name__ == "__main__":
    main()
