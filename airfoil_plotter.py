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


def rotate(x, y, angle):
    x_rotated = x * np.cos(angle) - y * np.sin(angle)
    y_rotated = x * np.sin(angle) + y * np.cos(angle)
    return x_rotated, y_rotated


class NacaFourDigitSettingsFrame:

    def __init__(self, frame):
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

        angle_frame = tk.Frame(master=frame)
        angle_frame.pack(side=tk.TOP)

        self.angle_label = tk.Label(
            angle_frame,
            text="deg",
            width=round(GUI_BUTTON_WIDTH/4))
        self.angle_label.pack(side=tk.LEFT)

        self.angle_entry = tk.Entry(
            angle_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.angle_entry.pack(side=tk.RIGHT)
        self.angle_entry.insert(0, "0")

    @property
    def m(self):
        return int(self.m_entry.get())

    @property
    def p(self):
        return int(self.p_entry.get())

    @property
    def t(self):
        return int(self.t_entry.get())

    @property
    def angle(self):
        return eval(self.angle_entry.get())

    def get_upper_surface(self):
        m = self.m
        p = self.p
        t = self.t
        aoa = - np.deg2rad(self.angle)
        airfoil = NacaFourDigitAirfoil(m, p, t)
        xu = np.linspace(1, 0, 10000)
        xu, yu = airfoil.get_upper(xu)
        return rotate(xu, yu, aoa)

    def get_lower_surface(self):
        m = self.m
        p = self.p
        t = self.t
        aoa = - np.deg2rad(self.angle)
        airfoil = NacaFourDigitAirfoil(m, p, t)
        xl = np.linspace(0, 1, 10000)
        xl, yl = airfoil.get_lower(xl)
        return rotate(xl, yl, aoa)


class AirfoilLoaderFrame:

    def __init__(self, frame):
        self.imported_data = None

        file_select_frame = tk.Frame(master=frame)
        file_select_frame.pack(side=tk.RIGHT)

        self.file_select_button = tk.Button(
            file_select_frame,
            text='Select File',
            width=round(GUI_BUTTON_WIDTH))
        self.file_select_button.pack(side=tk.TOP)

        chord_length_frame = tk.Frame(master=file_select_frame)
        chord_length_frame.pack(side=tk.TOP)

        self.chord_length_entry = tk.Entry(
            chord_length_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.chord_length_entry.pack(side=tk.RIGHT)
        self.chord_length_entry.insert(0, '1.0')

        chord_length_button = tk.Label(
            chord_length_frame,
            text='Scale Factor',
            width=round(GUI_BUTTON_WIDTH/2))
        chord_length_button.pack(side=tk.LEFT)

        position_x_frame = tk.Frame(master=file_select_frame)
        position_x_frame.pack(side=tk.TOP)

        self.position_x_entry = tk.Entry(
            position_x_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.position_x_entry.pack(side=tk.RIGHT)
        self.position_x_entry.insert(0, '0')

        position_x_refresh_button = tk.Label(
            position_x_frame,
            text="Position X",
            width=round(GUI_BUTTON_WIDTH/2))
        position_x_refresh_button.pack(side=tk.LEFT)

        position_y_frame = tk.Frame(master=file_select_frame)
        position_y_frame.pack(side=tk.TOP)

        self.position_y_entry = tk.Entry(
            position_y_frame,
            width=round(GUI_BUTTON_WIDTH/2))
        self.position_y_entry.pack(side=tk.RIGHT)
        self.position_y_entry.insert(0, '0')

        position_y_refresh_button = tk.Label(
            position_y_frame,
            text="Position Y",
            width=round(GUI_BUTTON_WIDTH/2))
        position_y_refresh_button.pack(side=tk.LEFT)

        self.invert_xy_var = tk.IntVar()
        self.switch_xy_button = tk.Checkbutton(
            file_select_frame,
            text="Switch XY",
            width=round(GUI_BUTTON_WIDTH/2),
            variable=self.invert_xy_var)
        self.switch_xy_button.pack(side=tk.TOP)

    @property
    def invert_xy(self):
        return bool(self.invert_xy_var.get())

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

    @property
    def sf(self):
        return eval(self.chord_length_entry.get())

    @property
    def x_pos(self):
        return eval(self.position_x_entry.get())

    @property
    def y_pos(self):
        return eval(self.position_y_entry.get())

    def import_file(self, filename:str):
        self.imported_data = np.loadtxt(filename)


class GuiData:

    def __init__(self, root_frame):

        # Figure
        self.fig = Figure(figsize=(5,4), dpi=100)
        ax = self.fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(self.fig, master=root_frame)  # A tk.DrawingArea.
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, root_frame, pack_toolbar=False)
        toolbar.update()

        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Settings
        settings_frame = tk.Frame(master=root_frame)
        settings_frame.pack(side=tk.RIGHT)

        # Digit Settings
        naca_digit_frame = tk.Frame(master=settings_frame)
        naca_digit_frame.pack(side=tk.RIGHT)
        self.airfoil_builder = NacaFourDigitSettingsFrame(naca_digit_frame)

        # Import Settings
        import_settings_frame = tk.Frame(master=settings_frame)
        import_settings_frame.pack(side=tk.RIGHT)
        self.airfoil_loader = AirfoilLoaderFrame(import_settings_frame)
        self.airfoil_loader.file_select_button.configure(
            command=lambda: self.user_select_file_and_update()
        )

        # Update plots
        ok_button = tk.Button(
            naca_digit_frame,
            text='Plot',
            width=round(GUI_BUTTON_WIDTH/2),
            command=lambda: self.update_plot())
        ok_button.pack(side=tk.BOTTOM)

    def user_select_file_and_update(self):
        filename = tk.filedialog.askopenfilename(title="Select the airfoil data file")
        if filename is not None and filename != '':
            self.import_file(filename)
            self.update_plot()

    def import_file(self, filename:str):
        self.airfoil_loader.import_file(filename=filename)

    def toggle_switch_imported_xy(self):
        self.import_settings.invert_xy = not self.import_settings.invert_xy
        self.update_plot()

    def update_plot(self):
        ax = self.fig.axes[0]
        ax.clear()

        # Imported airfoil
        sf = self.airfoil_loader.sf
        x_offset = self.airfoil_loader.x_pos
        y_offset = self.airfoil_loader.y_pos
        if self.airfoil_loader.imported_data is not None:
            if not self.airfoil_loader.invert_xy:
                x = self.airfoil_loader.x
                y = self.airfoil_loader.y
            else:
                x = self.airfoil_loader.y
                y = self.airfoil_loader.x
            ax.plot(x*sf + x_offset, y*sf + y_offset, color="blue")

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

    gui_data = GuiData(root)
    gui_data.update_plot()
    root.mainloop()


if __name__ == "__main__":
    main()
