import os
import sys
import logging
import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from app.GUI.calculator_frame import CalculatorFrame
from app.GUI.report_frame import ReportFrame
from app.GUI.turbine_frame import TurbineFrame
"""from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def open_logs_directory():
    logs_path = os.path.abspath('app.log')
    os.startfile(os.path.dirname(logs_path))
"""
class WindEnergyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KALKULATOR LETNE PROIZODNJE VE")
        self.root.geometry("1200x800")
        self.root.minsize(1200, 800)
        self.root.configure(bg="#c7c7c7")

        # Set the application icon
        icon_path = self.resource_path("resources/icons/wind-energy.ico")
        self.root.iconbitmap(icon_path)

        #logger.debug("WindEnergyApp initialized with window size 1200x800")

        self.create_widgets()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def create_widgets(self):
        # Navigation Bar
        self.nav_frame = tk.Frame(self.root, bg="#4f4f4f", height=50)
        self.nav_frame.pack(fill="x")

        self.nav_button_1 = tk.Button(self.nav_frame, text="KALKULATOR", bg="#4f4f4f", fg="white", bd=0,
                                      command=lambda: self.show_frame(self.calculator_frame))
        self.nav_button_1.pack(side="left", padx=20, pady=10)

        self.nav_button_2 = tk.Button(self.nav_frame, text="TURBINE", bg="#4f4f4f", fg="white", bd=0,
                                      command=lambda: self.show_frame(self.turbine_frame))
        self.nav_button_2.pack(side="left", padx=20, pady=10)

        self.nav_button_3 = tk.Button(self.nav_frame, text="POROČILA", bg="#4f4f4f", fg="white", bd=0,
                                      command=lambda: self.show_frame(self.report_frame))
        self.nav_button_3.pack(side="left", padx=20, pady=10)

        # Add a button to open logs directory
        # self.nav_button_4 = tk.Button(self.nav_frame, text="ODPRI LOGE", bg="#4f4f4f", fg="white", bd=0,
        #                               command=open_logs_directory)
        # self.nav_button_4.pack(side="left", padx=20, pady=10)

        # Main Frames
        self.main_frame = tk.Frame(self.root, bg="#c7c7c7")
        self.main_frame.pack(expand=True, fill="both")

        self.report_frame = ReportFrame(self.main_frame, self.resource_path)
        self.report_frame.pack_forget()

        self.calculator_frame = CalculatorFrame(self.main_frame, self.report_frame.add_report)
        self.calculator_frame.pack_forget()

        self.turbine_frame = TurbineFrame(self.main_frame)
        self.turbine_frame.pack_forget()

        for frame in (self.calculator_frame, self.report_frame, self.turbine_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.show_frame(self.calculator_frame)

    def save_report(self, report_text):
        self.report_frame.add_report(report_text)
        #logger.info("Report saved: %s", report_text[:100])  # Log only the first 100 characters of the report text

    def show_frame(self, frame):
        if isinstance(frame, CalculatorFrame):
            frame.refresh_turbine_list()
        frame.tkraise()
        #logger.debug("Frame shown: %s", type(frame).__name__)

    def run(self):
        #logger.info("WindEnergyApp started")
        self.root.mainloop()
        #logger.info("WindEnergyApp closed")