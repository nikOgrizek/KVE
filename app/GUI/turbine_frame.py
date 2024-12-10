import tkinter as tk
from tkinter import ttk
from app.data_manager import load_turbines, save_turbines
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class TurbineFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#c7c7c7")
        self.turbines = load_turbines()
        self.selected_turbine_index = None
        self.create_widgets()
        self.reset_frame()
        logger.debug("TurbineFrame initialized")

    def create_widgets(self):
        logger.debug("Creating widgets in TurbineFrame")
        ttk.Label(self, text="Dodajanje Turbine", font=("Helvetica", 16)).pack(pady=20)

        form_frame = tk.Frame(self, bg="#c7c7c7")
        form_frame.pack(pady=10, padx=10)

        ttk.Label(form_frame, text="Naziv", background="#c7c7c7", font=("Helvetica", 12)).grid(row=0, column=0, pady=5, sticky=tk.W)

        self.turbine_name_entry = ttk.Entry(form_frame, font=("Helvetica", 12))
        self.turbine_name_entry.grid(row=0, column=1, pady=5, sticky=tk.W + tk.E)  # Center the entry

        add_button = tk.Button(form_frame, text="DODAJ TURBINO", font=("Helvetica", 12, "bold"), bg="black", fg="white", command=self.add_turbine)
        add_button.grid(row=1, column=1, pady=10, sticky=tk.W)

        self.update_button = tk.Button(form_frame, text="Posodobi podatke", font=("Helvetica", 12, "bold"), bg="black", fg="white", command=self.update_turbine, state=tk.DISABLED)
        self.update_button.grid(row=2, column=1, pady=10, sticky=tk.W)  # Move the update button below the entry

        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.speed_entries = []
        self.power_entries = []

        self.add_row_button = tk.Button(self.scrollable_frame.inner_frame, text="+", font=("Helvetica", 12, "bold"), bg="black", fg="white", command=self.add_data_row)
        self.add_data_row()

        self.turbine_list_frame = tk.Frame(self, bg="#c7c7c7")
        self.turbine_list_frame.pack(fill="both", expand=True, pady=10, padx=10)

        list_frame = tk.Frame(self.turbine_list_frame, bg="#c7c7c7")
        list_frame.pack(side="left", fill="both", expand=True)

        self.turbine_listbox = tk.Listbox(list_frame, font=("Helvetica", 12), width=50)
        self.turbine_listbox.pack(fill="both", expand=True, pady=10, padx=10)

        button_frame = tk.Frame(self.turbine_list_frame, bg="#c7c7c7")
        button_frame.pack(side="right", fill="y", padx=10, pady=10)

        select_button = tk.Button(button_frame, text="Izberi turbino", font=("Helvetica", 12, "bold"), bg="black", fg="white", command=self.select_turbine)
        select_button.pack(pady=5)

        delete_button = tk.Button(button_frame, text="Izbriši turbino", font=("Helvetica", 12, "bold"), bg="black", fg="white", command=self.delete_turbine)
        delete_button.pack(pady=5)

        self.update_turbine_list()
        logger.debug("Widgets in TurbineFrame created")

    def reset_frame(self):
        self.turbine_name_entry.delete(0, tk.END)
        for entry in self.speed_entries:
            entry.delete(0, tk.END)
        for entry in self.power_entries:
            entry.delete(0, tk.END)
        self.update_button.config(state=tk.DISABLED)
        self.selected_turbine_index = None
        logger.debug("TurbineFrame reset")

    def add_data_row(self):
        row_index = len(self.speed_entries)
        ttk.Label(self.scrollable_frame.inner_frame, text=f"WindSpeed(m/s): ", background="#c7c7c7", font=("Helvetica", 12)).grid(row=row_index, column=0, pady=5, sticky=tk.W)
        speed_entry = ttk.Entry(self.scrollable_frame.inner_frame, font=("Helvetica", 12), justify="center")
        speed_entry.grid(row=row_index, column=1, pady=5, sticky=tk.W + tk.E, padx=(0, 10))  # Center the entry
        self.speed_entries.append(speed_entry)

        ttk.Label(self.scrollable_frame.inner_frame, text=f"Power(kW): ", background="#c7c7c7", font=("Helvetica", 12)).grid(row=row_index, column=2, pady=5, sticky=tk.W)
        power_entry = ttk.Entry(self.scrollable_frame.inner_frame, font=("Helvetica", 12), justify="center")
        power_entry.grid(row=row_index, column=3, pady=5, sticky=tk.W + tk.E)  # Center the entry
        self.power_entries.append(power_entry)

        self.add_row_button.grid(row=row_index + 1, columnspan=4, pady=10)
        logger.debug("Data row added in TurbineFrame")

    def add_turbine(self):
        # Pridobi ime turbine
        turbine_name = self.turbine_name_entry.get()
        if not turbine_name:
            # Če ni imena, prekini
            print("Ime turbine je obvezno.")
            return

        # Pridobi in preveri vrednosti hitrosti
        speeds = []
        for entry in self.speed_entries:
            speed = entry.get()
            if not speed.isdigit():
                print("Hitrost mora biti številska.")
                return
            speeds.append(speed)

        # Pridobi in preveri vrednosti moči
        powers = []
        for entry in self.power_entries:
            power = entry.get()
            if not power.isdigit():
                print("Moč mora biti številska.")
                return
            powers.append(power)

        # Če so podatki veljavni, dodaj turbino
        self.turbines.append({
            "name": turbine_name,
            "speeds": speeds,
            "powers": powers
        })

        # Klic funkcije za shranjevanje in beleženje dogodka
        save_turbines(self.turbines)
        logger.info("Turbine added: %s", turbine_name)

    def clear_form(self):
        self.turbine_name_entry.delete(0, tk.END)
        for entry in self.speed_entries:
            entry.delete(0, tk.END)
        for entry in self.power_entries:
            entry.delete(0, tk.END)
        self.update_button.config(state=tk.DISABLED)
        self.selected_turbine_index = None
        logger.debug("Form cleared in TurbineFrame")

    def update_turbine_list(self):
        self.turbine_listbox.delete(0, tk.END)
        for turbine in self.turbines:
            self.turbine_listbox.insert(tk.END, turbine['name'])
        logger.debug("Turbine list updated in TurbineFrame")

    def select_turbine(self):
        try:
            self.selected_turbine_index = self.turbine_listbox.curselection()[0]
            turbine = self.turbines[self.selected_turbine_index]

            self.turbine_name_entry.delete(0, tk.END)
            self.turbine_name_entry.insert(0, turbine["name"])

            for entry in self.speed_entries:
                entry.grid_forget()
            for entry in self.power_entries:
                entry.grid_forget()

            self.speed_entries.clear()
            self.power_entries.clear()

            for i, (speed, power) in enumerate(zip(turbine["speeds"], turbine["powers"])):
                self.add_data_row()
                self.speed_entries[i].insert(0, speed)
                self.power_entries[i].insert(0, power)

            self.update_button.config(state=tk.NORMAL)
            logger.info("Turbine selected: %s", turbine["name"])
        except IndexError:
            logger.error("No turbine selected")

    def update_turbine(self):
        if self.selected_turbine_index is not None:
            name = self.turbine_name_entry.get()
            speeds = [entry.get() for entry in self.speed_entries]
            powers = [entry.get() for entry in self.power_entries]

            if name and all(speeds) and all(powers):
                turbine = {"name": name, "speeds": speeds, "powers": powers}
                self.turbines[self.selected_turbine_index] = turbine
                save_turbines(self.turbines)
                self.update_turbine_list()
                self.clear_form()
                logger.info("Turbine updated: %s", name)

    def delete_turbine(self):
        if self.selected_turbine_index is not None:
            turbine_name = self.turbines[self.selected_turbine_index]['name']
            del self.turbines[self.selected_turbine_index]
            save_turbines(self.turbines)
            self.update_turbine_list()
            self.clear_form()
            self.selected_turbine_index = None
            logger.info("Turbine deleted: %s", turbine_name)

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg="#c7c7c7")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#c7c7c7")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((self.canvas.winfo_width() / 2, 0), window=self.scrollable_frame, anchor="n")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind the mouse wheel event to the canvas
        self.bind_mouse_wheel(self.canvas)
        logger.debug("ScrollableFrame initialized")

    @property
    def inner_frame(self):
        return self.scrollable_frame

    def bind_mouse_wheel(self, canvas):
        logger.debug("Binding mouse wheel")
        canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        canvas.bind_all("<Button-4>", self.on_mouse_wheel)  # For Linux (X11)
        canvas.bind_all("<Button-5>", self.on_mouse_wheel)  # For Linux (X11)

    def on_mouse_wheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows and MacOS
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        logger.debug("Mouse wheel event: %s", event)
