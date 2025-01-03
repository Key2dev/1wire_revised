import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import db_functions
from igraph import InteractiveTemperaturePlot
import datetime


class Submenu:
    def __init__(self, parent, db_path, table_name, title="Submenu"):  # Added db_path and table_name as parameters to the constructor.
        # Create a new Toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x400")  # Reduced size for a more compact layout

        # Create a database connection
        self.db_path = db_path
        self.table_name = table_name
        
        # Fetch min and max dates from the database
        self.min_date, self.max_date = db_functions.get_date_range(db_path, table_name)

        # Parse the date strings to datetime objects
        self.min_date = self.parse_date(self.min_date)
        self.max_date = self.parse_date(self.max_date)

        print(f"Data range: {self.min_date} to {self.max_date}")  # Debug print


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
        tk.Button(button_frame, text="Save filtered", command=self.save_filtered_to_csv).pack(side="left", padx=5)
        tk.Button(button_frame, text="Generate graph", command=self.generate_graph).pack(side="left", padx=5)
        tk.Button(button_frame, text="Exit", command=self.close_window).pack(side="left", padx=5)

        
        # Update the DateEntry widgets with the valid date range
        self.start_date_entry.set_date(self.min_date.date())
        self.end_date_entry.set_date(self.max_date.date())

    
    def parse_date(self, date_string):
        # Try parsing with YYYY-MM-DD format first
        try:
            return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # If that fails, try YY-MM-DD format
            try:
                return datetime.datetime.strptime(date_string, "%y-%m-%d %H:%M:%S")
            except ValueError:
                # If both fail, raise an exception with a helpful message
                raise ValueError(f"Unable to parse date string: {date_string}. "
                                 "Expected format: YYYY-MM-DD HH:MM:SS or YY-MM-DD HH:MM:SS")

    
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
         # Fetch dates from UI
        start_date, end_date = self.get_date_and_time()
        print(f"Generating graph for dates: {start_date} to {end_date}")

        # Parse the date strings to datetime objects
        start_date = self.parse_date(start_date)
        end_date = self.parse_date(end_date)


        # Validate the date range
        # TODO: BUGGY!!
        if start_date < self.min_date:
            messagebox.showwarning("Invalid Date Range", f"Start date cannot be earlier than {self.min_date.strftime('%Y-%m-%d %H:%M:%S')}")
            return
        if end_date > self.max_date:
            messagebox.showwarning("Invalid Date Range", f"End date cannot be later than {self.max_date.strftime('%Y-%m-%d %H:%M:%S')}")
            return
        if start_date >= end_date:
            messagebox.showwarning("Invalid Date Range", "Start date must be earlier than end date")
            return

        print(f"Generating graph for dates: {start_date} to {end_date}")
        
        # Open the graph window and pass the fetched data
        InteractiveTemperaturePlot(self.window, self.db_path, self.table_name, start_date, end_date)


    def save_filtered_to_csv(self):
        start_date, end_date = self.get_date_and_time()
        db_functions.records_by_time_csv(self.db_path, self.table_name , start_date, end_date)

    def close_window(self):
        self.window.destroy()