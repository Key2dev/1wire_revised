import tkinter as tk
from tkinter import filedialog  # Import filedialog for saving functionality
from tkcalendar import DateEntry
import db_functions


class Submenu:
    def __init__(self, parent, title="Submenu"):
        # Create a new Toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x400")  # Reduced size for a more compact layout

        # Create a main frame for all contents
        main_frame = tk.Frame(self.window, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Date and Time Selection
        date_time_frame = tk.LabelFrame(main_frame, text="Date and Time Selection", padx=10, pady=10)
        date_time_frame.pack(fill="x", pady=10)

        # Start date and time
        start_frame = tk.Frame(date_time_frame)
        start_frame.pack(fill="x", pady=5)
        tk.Label(start_frame, text="Start:").pack(side="left", padx=5)
        self.start_date_entry = DateEntry(start_frame, width=10, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_hour_spinbox = tk.Spinbox(start_frame, from_=0, to=23, width=2, format="%02.0f")
        self.start_hour_spinbox.pack(side="left", padx=2)
        tk.Label(start_frame, text=":").pack(side="left")
        self.start_minute_spinbox = tk.Spinbox(start_frame, from_=0, to=59, width=2, format="%02.0f")
        self.start_minute_spinbox.pack(side="left", padx=2)

        # End date and time
        end_frame = tk.Frame(date_time_frame)
        end_frame.pack(fill="x", pady=5)
        tk.Label(end_frame, text="End: ").pack(side="left", padx=5)
        self.end_date_entry = DateEntry(end_frame, width=10, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.pack(side="left", padx=5)
        self.hour_spinbox = tk.Spinbox(end_frame, from_=0, to=23, width=2, format="%02.0f")
        self.hour_spinbox.pack(side="left", padx=2)
        tk.Label(end_frame, text=":").pack(side="left")
        self.minute_spinbox = tk.Spinbox(end_frame, from_=0, to=59, width=2, format="%02.0f")
        self.minute_spinbox.pack(side="left", padx=2)

        # Action Buttons
        button_frame = tk.Frame(main_frame, pady=10)
        button_frame.pack()
        tk.Button(button_frame, text="Get Date and Time", command=self.get_date_and_time).pack(side="left", padx=5)
        tk.Button(button_frame, text="Save filtered", command=self.saving_filtered).pack(side="left", padx=5)
        tk.Button(button_frame, text="Generate graph", command=self.generate_graph).pack(side="left", padx=5)
        tk.Button(button_frame, text="Exit", command=self.close_window).pack(side="left", padx=5)

    def get_date_and_time(self):
        # Get the selected date and time from the UI components
        start_date = self.start_date_entry.get()
        start_time = f"{self.start_hour_spinbox.get()}:{self.start_minute_spinbox.get()}"
        end_date = self.end_date_entry.get()
        end_time = f"{self.hour_spinbox.get()}:{self.minute_spinbox.get()}"
        print(f"Start: {start_date} {start_time}")
        print(f"End: {end_date} {end_time}")
        
        # Conversion to proper date format
        start_date = start_date.split("/")
        start_date = f"20{start_date[2]}-{start_date[0]}-{start_date[1]}"
        end_date = end_date.split("/")
        end_date = f"20{end_date[2]}-{end_date[0]}-{end_date[1]}"
        print(start_date, end_date)
        
        # Combine date and time into a tuple
        date_tuple = (f"{start_date} {start_time}:00", f"{end_date} {end_time}:00")
        print(date_tuple)
        return date_tuple
    def generate_graph(self):
        pass
        #TODO: This

    def open_save_dialog(self):
        file_path = filedialog.asksaveasfilename(title="Save File", defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            print(file_path)
            return file_path 
                
    def saving_filtered(self):
        start_date, end_date = self.get_date_and_time()
        file_path = self.open_save_dialog()
        if file_path:
            db_functions.records_by_time_csv("temperatury.db", "temps", start_date, end_date, file_path)
            print("Filtered data saved to file.")
        else:
            print("No file path selected.")
                
    def close_window(self):
        self.window.destroy()