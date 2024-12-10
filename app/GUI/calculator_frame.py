import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
from datetime import datetime
from app.data_manager import load_turbines
from app.data import get_wind_data
from app.calculations import calculate_annual_production, calculate_monthly_production
from app.export import export_to_pdf
import os
from PIL import ImageGrab
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class SelectTurbineDialog(tk.Toplevel):
    def __init__(self, parent, turbines, on_select):
        super().__init__(parent)
        self.turbines = turbines
        self.on_select = on_select
        self.selected_turbines = []
        self.create_widgets()
        logger.debug("SelectTurbineDialog initialized with turbines: %s", self.turbines)

    def create_widgets(self):
        self.title("Izberi turbine za to lokacijo")
        self.geometry("300x400")
        self.grab_set()
        logger.debug("SelectTurbineDialog widgets created")

        ttk.Label(self, text="Izberi turbine za to lokacijo:").pack(pady=10)

        self.turbine_listbox = tk.Listbox(self, selectmode="multiple")
        for turbine in self.turbines:
            logger.debug("Inserting turbine into listbox: %s", turbine)
            self.turbine_listbox.insert(tk.END, turbine)
        self.turbine_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Potrdi", command=self.on_confirm).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Prekliči", command=self.on_cancel).pack(side="right", padx=5)

    def on_confirm(self):
        selected_indices = self.turbine_listbox.curselection()
        self.selected_turbines = [self.turbines[i] for i in selected_indices]
        logger.debug("Turbines selected: %s", self.selected_turbines)
        self.on_select(self.selected_turbines)
        self.destroy()

    def on_cancel(self):
        logger.debug("Turbine selection cancelled")
        self.destroy()


class CalculatorFrame(tk.Frame):
    def __init__(self, parent, save_report_callback):
        super().__init__(parent, bg="#c7c7c7")
        self.save_report_callback = save_report_callback
        self.turbines = load_turbines()
        self.coordinates = []
        self.markers = []
        self.wind_data = {}
        self.selected_turbines = {}
        self.create_widgets()
        logger.debug("CalculatorFrame initialized with turbines: %s", self.turbines)

    def create_widgets(self):
        logger.debug("Creating widgets in CalculatorFrame")
        # Left Frame
        left_frame = tk.Frame(self, bg="#c7c7c7")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Entry fields for manual coordinate input
        entry_frame = tk.Frame(left_frame, bg="#c7c7c7")
        entry_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(entry_frame, text="Vnesi koordinate:", background="#c7c7c7", font=("Helvetica", 12)).pack(anchor="w")

        coord_entry_frame = tk.Frame(entry_frame, bg="#c7c7c7")
        coord_entry_frame.pack(fill="x", pady=5)

        ttk.Label(coord_entry_frame, text="Lat:", background="#c7c7c7", font=("Helvetica", 12)).pack(side="left")
        self.lat_entry = ttk.Entry(coord_entry_frame, font=("Helvetica", 12))
        self.lat_entry.pack(side="left", padx=(0, 10))

        ttk.Label(coord_entry_frame, text="Lon:", background="#c7c7c7", font=("Helvetica", 12)).pack(side="left")
        self.lon_entry = ttk.Entry(coord_entry_frame, font=("Helvetica", 12))
        self.lon_entry.pack(side="left", padx=(0, 10))

        self.insert_button = tk.Button(coord_entry_frame, text="VSTAVI", font=("Helvetica", 12, "bold"), bg="black",
                                       fg="white", command=self.insert_manual_coordinates)
        self.insert_button.pack(side="left", padx=(10, 0))

        # Map widget
        self.map_frame = tk.Frame(left_frame, bg="white")
        self.map_frame.pack(fill="both", expand=True, pady=5)
        self.map_widget = TkinterMapView(self.map_frame, width=400, height=300, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)

        self.map_widget.set_position(46.559086, 15.638087)  # FERI
        self.map_widget.set_zoom(15)

        self.map_widget.add_left_click_map_command(self.on_left_click_map)

        ttk.Label(left_frame, text="Koordinate:", background="#c7c7c7", font=("Helvetica", 12)).pack(anchor="w",
                                                                                                     pady=(10, 0))

        coord_scroll_frame = tk.Frame(left_frame, bg="#c7c7c7")
        coord_scroll_frame.pack(fill="both", expand=True)
        self.coord_canvas = tk.Canvas(coord_scroll_frame, bg="#c7c7c7")
        self.coord_scrollbar = ttk.Scrollbar(coord_scroll_frame, orient="vertical", command=self.coord_canvas.yview)
        self.coord_frame = tk.Frame(self.coord_canvas, bg="#c7c7c7")

        self.coord_frame.bind(
            "<Configure>",
            lambda e: self.coord_canvas.configure(
                scrollregion=self.coord_canvas.bbox("all")
            )
        )

        self.coord_canvas.create_window((0, 0), window=self.coord_frame, anchor="nw")
        self.coord_canvas.configure(yscrollcommand=self.coord_scrollbar.set)

        self.coord_canvas.pack(side="left", fill="both", expand=True)
        self.coord_scrollbar.pack(side="right", fill="y")

        self.calculate_button = tk.Button(left_frame, text="IZRAČUNAJ", font=("Helvetica", 12, "bold"), bg="black",
                                          fg="white", command=self.calculate)
        self.calculate_button.pack(pady=10)

        # Right Frame
        right_frame = tk.Frame(self, bg="#c7c7c7")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(right_frame, text="POROČILO IZRAČUNA", background="#c7c7c7", font=("Helvetica", 14, "bold")).pack(
            anchor="w")

        # Scrollable frame for results
        self.results_frame = tk.Frame(right_frame, bg="white", bd=2, relief="solid")
        self.results_frame.pack(expand=True, fill="both", pady=10)

        self.results_canvas = tk.Canvas(self.results_frame, bg="white")
        self.results_scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_canvas.yview)
        self.results_scrollable_frame = tk.Frame(self.results_canvas, bg="white")

        self.results_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")
            )
        )

        self.results_canvas.create_window((0, 0), window=self.results_scrollable_frame, anchor="nw")
        self.results_canvas.configure(yscrollcommand=self.results_scrollbar.set)

        self.results_canvas.pack(side="left", fill="both", expand=True)
        self.results_scrollbar.pack(side="right", fill="y")

        self.results_label = ttk.Label(self.results_scrollable_frame, text="", background="white",
                                       font=("Helvetica", 12))
        self.results_label.pack(expand=True, fill="both", padx=10, pady=10)

        # Export button
        self.export_pdf_button = tk.Button(right_frame, text="IZVOZI PDF", font=("Helvetica", 12, "bold"), bg="black",
                                           fg="white", command=self.export_pdf)
        self.export_pdf_button.pack(pady=10)

        # Bind the mouse wheel event to the canvases
        self.bind_mouse_wheel(self.results_canvas)
        self.bind_mouse_wheel(self.coord_canvas)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        logger.debug("Widgets in CalculatorFrame created")

    def bind_mouse_wheel(self, widget):
        widget.bind_all("<MouseWheel>", self.on_mouse_wheel)
        widget.bind_all("<Button-4>", self.on_mouse_wheel)  # For Linux (X11)
        widget.bind_all("<Button-5>", self.on_mouse_wheel)  # For Linux (X11)
        logger.debug("Mouse wheel bound to widget")

    def on_mouse_wheel(self, event):
        if event.num == 4 or event.delta > 0:
            event.widget.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            event.widget.yview_scroll(1, "units")

    def on_left_click_map(self, coords):
        logger.debug("Map left click at coords: %s", coords)
        # Get the mouse click position
        click_x = self.map_widget.winfo_pointerx() - self.map_widget.winfo_rootx()
        click_y = self.map_widget.winfo_pointery() - self.map_widget.winfo_rooty()

        # Check if the click was within the bounds of the zoom-in or zoom-out buttons
        if not self.is_zoom_button_click(click_x, click_y):
            self.select_turbines(coords)

    def is_zoom_button_click(self, x, y):
        # Define the regions of the zoom buttons based on their positions within the map widget
        zoom_in_button_region = (self.map_widget.winfo_width() - 50, 10, self.map_widget.winfo_width() - 10, 50)
        zoom_out_button_region = (self.map_widget.winfo_width() - 50, 60, self.map_widget.winfo_width() - 10, 100)

        if zoom_in_button_region[0] <= x <= zoom_in_button_region[2] and zoom_in_button_region[1] <= y <= \
                zoom_in_button_region[3]:
            self.map_widget.set_zoom(self.map_widget.get_zoom() + 1)
            return True
        elif zoom_out_button_region[0] <= x <= zoom_out_button_region[2] and zoom_out_button_region[1] <= y <= \
                zoom_out_button_region[3]:
            self.map_widget.set_zoom(self.map_widget.get_zoom() - 1)
            return True
        return False

    def insert_manual_coordinates(self):
        try:
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                coords = (lat, lon)
                logger.debug("Manual coordinates inserted: %s", coords)
                self.select_turbines(coords)
            else:
                raise ValueError
        except ValueError:
            logger.error("Invalid manual coordinates entered: Lat=%s, Lon=%s", self.lat_entry.get(),
                         self.lon_entry.get())
            messagebox.showerror("Napaka", "Vnesite veljavne decimalne koordinate.")

    def add_coordinates(self, coords, turbines):
        frame = tk.Frame(self.coord_frame, bg="#c7c7c7")
        frame.pack(fill="x", pady=2)

        label = ttk.Label(frame, text=f"Lat: {coords[0]}, Lon: {coords[1]}", background="#c7c7c7",
                          font=("Helvetica", 12))
        label.pack(side="left", fill="x", expand=True)

        delete_button = tk.Button(frame, text="Briši", font=("Helvetica", 10, "bold"), bg="red", fg="white",
                                  command=lambda: self.remove_marker(coords, frame))
        delete_button.pack(side="right", anchor="e", padx=(210, 0))

        self.coordinates.append(coords)
        self.selected_turbines[coords] = turbines

        marker = self.map_widget.set_marker(coords[0], coords[1], marker_color_circle="white",
                                            marker_color_outside="red")
        self.markers.append((marker, coords))

        logger.debug("Coordinates added: %s with turbines: %s", coords, turbines)

    def select_turbines(self, coords):
        def on_select(turbines):
            if turbines:
                self.add_coordinates(coords, turbines)
                logger.debug("Turbines selected for coordinates %s: %s", coords, turbines)
            else:
                messagebox.showwarning("Izbira turbine", "Izbrati morate vsaj eno turbino.")
                logger.warning("No turbines selected for coordinates: %s", coords)

        dialog = SelectTurbineDialog(self, [turbine["name"] for turbine in self.turbines], on_select)
        self.wait_window(dialog)

    def remove_marker(self, coords, frame):
        for i, (marker, marker_coords) in enumerate(self.markers):
            if (marker_coords == coords):
                marker.set_position(0, 0)
                self.markers.pop(i)
                break

        self.coordinates.remove(coords)
        del self.selected_turbines[coords]

        frame.destroy()

        logger.debug("Marker removed for coordinates: %s", coords)

    def calculate(self):
        if not self.coordinates:
            self.results_label.config(text="Napaka: Vnesite vsaj eno koordinato.")
            logger.warning("Calculation attempt with no coordinates entered")
            return

        self.results_label.config(text="")
        logger.debug("Calculation started")

        wind_data_dict = {}
        production_results = []

        current_year = datetime.now().year
        last_year = current_year - 1

        for coords in self.coordinates:
            lat, lon = coords
            wind_data = get_wind_data(lat, lon, last_year)
            wind_data_dict[coords] = wind_data

            avg_wind_speed = wind_data["wind_speed_100m"].mean()
            logger.debug("Wind data retrieved for coordinates %s: avg wind speed = %.2f m/s", coords, avg_wind_speed)
            location_result = f"Lokacija (Koordinate): {self.format_coords(coords)}\nPovprečna letna hitrost vetra na lokaciji: {avg_wind_speed:.2f} m/s\nMerjeno na višini: 100m\nTurbine:\n"

            turbines = self.selected_turbines[coords]
            for turbine_name in turbines:
                turbine = next(turbine for turbine in self.turbines if turbine["name"] == turbine_name)
                production = calculate_annual_production(wind_data, [turbine], 1) / 1000  # Convert to GWh
                logger.debug("Annual production calculated for turbine %s at %s: %.2f GWh", turbine_name, coords,
                             production)
                location_result += f" - {turbine_name}, {production:.2f} GWh\n"
                production_results.append((coords, turbine_name, production))

            location_result += "\n"
            self.results_label.config(text=self.results_label.cget("text") + location_result)
        logger.debug("Calculation completed")

    def format_coords(self, coords):
        lat_dms = self.decimal_to_dms(coords[0])
        lon_dms = self.decimal_to_dms(coords[1])
        lat_dir = "N" if coords[0] >= 0 else "S"
        lon_dir = "E" if coords[1] >= 0 else "W"
        return f"{lat_dms} {lat_dir}, {lon_dms} {lon_dir}"

    def decimal_to_dms(self, decimal):
        degrees = int(decimal)
        minutes = int((abs(decimal) - abs(degrees)) * 60)
        seconds = (abs(decimal) - abs(degrees) - minutes / 60) * 3600
        return f"{abs(degrees)}°{minutes}'{seconds:.2f}\""

    def save_report(self, report_text):
        # report_text = self.results_label.cget("text")
        # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # formatted_text = f"POROČILO {current_time}: {report_text}"
        # self.save_report_callback(formatted_text)
        # logger.info("Report saved with timestamp %s", current_time)
        self.save_report_callback(report_text)

    def capture_map_image(self, filepath="map_image.png"):

        x0 = self.map_frame.winfo_rootx() + self.map_widget.winfo_x()
        y0 = self.map_frame.winfo_rooty() + self.map_widget.winfo_y()
        x1 = x0 + self.map_widget.winfo_width()
        y1 = y0 + self.map_widget.winfo_height()

        ImageGrab.grab().crop((x0, y0, x1, y1)).save(filepath)
        logger.debug("Map image captured and saved to %s", filepath)
        return filepath

    def export_pdf(self):
        if not self.coordinates:
            raise ValueError("No coordinates provided")
        if not self.selected_turbines:
            raise ValueError("No selected turbines")

        report_text = self.results_label.cget("text")
        map_image_path = self.capture_map_image()
        wind_data_dict = {(lat, lon): get_wind_data(lat, lon, datetime.now().year - 1) for lat, lon in
                          self.coordinates}

        # Generate a timestamped report name
        current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        report_name = f"Report-{current_time}"
        report_file_path = os.path.join("reports", f"{report_name}.pdf")

        # Export to PDF
        export_to_pdf(report_text, wind_data_dict, self.coordinates, self.selected_turbines, map_image_path,
                      report_file_path)
        if os.path.exists(map_image_path):
            os.remove(map_image_path)
        logger.info("PDF export completed successfully")

        # Save the report in the ReportFrame and display it
        self.save_report_callback(report_text, report_name)

        # Display a notification popup
        messagebox.showinfo("Uspeh", "Poročilo je bilo shranjeno, lahko ga ogledate v <<Poročila>>")

    def refresh_turbine_list(self):
        self.turbines = load_turbines()
        logger.debug("Turbine list refreshed in CalculatorFrame")
