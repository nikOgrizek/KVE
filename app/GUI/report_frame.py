import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from tkcalendar import Calendar
from PIL import Image, ImageTk
import logging
import os
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


class ReportFrame(tk.Frame):
    def __init__(self, parent, resource_path):
        super().__init__(parent, bg="#c7c7c7")
        self.resource_path = resource_path
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)  # Ensure the reports directory exists
        self.create_widgets()
        self.report_paths = {}  # Dictionary to store report file paths
        logger.debug("ReportFrame initialized")

        self.load_reports()

    def create_widgets(self):
        logger.debug("Creating widgets in ReportFrame")
        header_frame = tk.Frame(self, bg="#c7c7c7")
        header_frame.pack(fill="x", pady=10)

        ttk.Label(header_frame, text="Poročila", background="#c7c7c7", font=("Helvetica", 16)).pack(side="left",
                                                                                           padx=10)


        calendar_icon_path = self.resource_path("resources/images/calendar.png")
        calendar_icon = self.create_icon(calendar_icon_path, (30, 30), (199, 199, 199))
        calendar_button = ttk.Button(header_frame, image=calendar_icon, command=self.open_calendar_popup)
        calendar_button.image = calendar_icon
        calendar_button.pack(side="right", padx=10)

        button_frame = tk.Frame(header_frame, bg="#c7c7c7")
        button_frame.pack(side="right", padx=20)

        open_reports_button = ttk.Button(header_frame, text="Vsa poročila", command=self.open_reports_folder)
        open_reports_button.pack(side="right", padx=20)

        # report_buttons_frame = tk.Frame(button_frame, bg="#c7c7c7")
        # report_buttons_frame.pack(side="top")

        self.report_container = tk.Frame(self, bg="#c7c7c7")
        self.report_container.pack(fill="both", expand=False)

        self.canvas = tk.Canvas(self.report_container, bg="#c7c7c7")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.report_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw", tags="inner_frame")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("inner_frame", width=e.width))

        self.inner_frame.columnconfigure(0, weight=1)  # Make the inner frame responsive

        self.reports = []
        logger.debug("Widgets in ReportFrame created")

        transparent_image = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        transparent_image.save(self.resource_path('transparent.ico'))

    def create_icon(self, icon_path, size, bg_color):
        image = Image.open(icon_path)
        image = image.resize(size)
        background = Image.new('RGBA', size, bg_color)
        background.paste(image, (0, 0), image)
        return ImageTk.PhotoImage(background)

    def open_calendar_popup(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Select Date")
        # self.popup.geometry("311x225")
        self.popup.minsize(311, 225)
        self.popup.iconbitmap(self.resource_path('transparent.ico'))
        self.calendar = Calendar(self.popup, selectmode='day', date_pattern='dd-mm-yyyy')
        self.calendar.pack(pady=10)

        select_button = ttk.Button(self.popup, text="Select Date", command=self.select_date)
        select_button.pack(pady=10)

    def open_reports_folder(self):
        reports_path = os.path.abspath(self.reports_dir)
        try:
            os.startfile(reports_path)  # Windows
        except AttributeError:
            import subprocess
            subprocess.call(['open', reports_path])  # macOS
        logger.info("Opened reports folder: %s", reports_path)

    def filter_reports_by_date(self, selected_date):
        # Clear the current reports
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Reload reports that match the selected date
        matching_reports = [report for report in os.listdir(self.reports_dir) if selected_date in report]
        for filename in matching_reports:
            if filename.endswith(".pdf"):
                report_name = os.path.splitext(filename)[0]  # Get the report name without extension
                self.add_report("", report_name)  # Add the report to the display

        logger.info(f"Reports filtered by date: {selected_date}")

    def select_date(self):
        selected_date = self.calendar.get_date()
        print(f"Selected date: {selected_date}")
        self.popup.destroy()
        self.filter_reports_by_date(selected_date)

    def add_report(self, report_text, report_name):
        report_frame = ttk.Frame(self.inner_frame, style="ReportFrame.TFrame")
        report_frame.grid(row=len(self.reports), column=0, sticky="ew", padx=10, pady=5)

        report_label = ttk.Label(report_frame, text=report_name, background="white", font=("Helvetica", 12))
        report_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        button_frame = ttk.Frame(report_frame)
        button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        open_button = ttk.Button(button_frame, text="Odpri", command=lambda: self.open_report(report_name))
        open_button.pack(side="right", padx=(5, 0))

        delete_button = ttk.Button(button_frame, text="Izbriši", command=lambda: self.delete_report(report_name))
        delete_button.pack(side="right", padx=(5, 0))

        report_frame.columnconfigure(0, weight=1)  # Make the first column expandable
        report_frame.columnconfigure(1, weight=0)  # Second column does not expand

        self.reports.append((report_frame, report_name))
        logger.debug("Report added: %s", report_name)

    def save_report(self, report_name, report_text):
        temp_file_path = os.path.join(self.reports_dir, f"{report_name}.pdf")
        c = canvas.Canvas(temp_file_path, pagesize=letter)
        c.drawString(100, 750, report_text)
        c.save()
        self.report_paths[report_name] = temp_file_path
        logger.info("Report saved temporarily as PDF: %s", temp_file_path)

        # Open the save as dialog
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
                                                 initialfile=f"{report_name}.pdf")
        if file_path:
            os.replace(temp_file_path, file_path)
            self.report_paths[report_name] = file_path
            logger.info("Report saved permanently as PDF: %s", file_path)
            messagebox.showinfo("Save Report", f"Report saved successfully at {file_path}")
        else:
            messagebox.showinfo("Save Report", f"Report saved temporarily at {temp_file_path}")

    def load_reports(self):
        # Iterate over all files in the reports directory
        for filename in os.listdir(self.reports_dir):
            if filename.endswith(".pdf"):
                report_name = os.path.splitext(filename)[0]  # Get the report name without extension
                self.add_report("", report_name)  # Add the report to the display
        logger.info("Reports loaded from folder: %s", self.reports_dir)

    def delete_report(self, report_name):
        file_path = self.report_paths.get(report_name)
        if not file_path:
            file_path = os.path.join(self.reports_dir, f"{report_name}.pdf")

        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            self.report_paths.pop(report_name, None)
            messagebox.showinfo("Delete Report", f"Report {report_name} deleted successfully")
            logger.info("Report deleted: %s", file_path)
            self.refresh_reports()  # Refresh the reports after deletion
        else:
            messagebox.showwarning("Delete Report", f"Report {report_name} does not exist")
            logger.warning("Attempted to delete non-existent report: %s", report_name)

    def open_report(self, report_name):
        file_path = self.report_paths.get(report_name)
        if not file_path:
            # Try to find the file in the reports directory if not found in the report_paths dictionary
            file_path = os.path.join(self.reports_dir, f"{report_name}.pdf")

        if file_path and os.path.exists(file_path):
            try:
                os.startfile(file_path)  # Windows
            except AttributeError:
                import subprocess
                subprocess.call(['open', file_path])  # macOS
                # For Linux, you might need to use a specific command depending on the desktop environment
            logger.info("Opened report: %s", file_path)
        else:
            messagebox.showwarning("Open Report", f"Report {file_path} does not exist")
            logger.warning("Attempted to open non-existent report: %s", report_name)

    def refresh_reports(self):
        # Clear the current list of reports
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.reports = []

        # Reload the reports from the reports directory
        for filename in os.listdir(self.reports_dir):
            if filename.endswith(".pdf"):
                report_name = os.path.splitext(filename)[0]
                self.add_report("", report_name)  # Add the report to the display
        logger.debug("Reports refreshed")