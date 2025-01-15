from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import tkinter as tk
import debug_functions as debugf
import db_functions
import datetime
from submenu import Submenu
from configuration import Config
import sys

# Old reader implementation
from wire_reader import read_1wire_sensors

# # TODO:
#   make documentation
#   polish the ui (use more descriptive variable names, make UI elements more visually appealing)
#   maybe add functionality to fetch last n records from the database?


class WireReaderApp:
    def __init__(self):
        """
        Initialize the WireReaderApp.

        This method sets up the main window, initializes variables for data storage and display,
        creates UI elements including labels and buttons, and sets up a live graph for temperature visualization.
        """

        # Create a new Toplevel window
        self.root = tk.Tk()
        self.root.title("1Wire Reader")

        # Load configuration
        self.config = Config(self.root)
        
        # Database Variables
        self.db_path = self.config.get("db_path")
        self.table_name = self.config.get("table_name")

        # Data Variables
        self.data_time = ""
        self.data_temp1 = 0.0
        self.data_temp2 = 0.0
        self.data_temp3 = 0.0

        # Bool for stopping the update loop
        self.inserting_data = False
        
        # Store historical data for the graph
        self.max_points = self.config.get("graph_points")
        
        self.temps1 = deque(maxlen=self.max_points)
        self.temps2 = deque(maxlen=self.max_points)
        self.temps3 = deque(maxlen=self.max_points)

        # Label Variables for UI
        self.time_now = tk.StringVar()
        self.temp1 = tk.StringVar()
        self.temp2 = tk.StringVar()
        self.temp3 = tk.StringVar()

        # Create UI elements (labels, buttons, etc.)
        self.create_ui_elements()

        # Live Graph
        self.create_live_graph()

        # Start updating the GUI
        self.update_all()

    def create_ui_elements(self):
        # Labels for displaying in the UI
        self.time_label = tk.Label(self.root, textvariable=self.time_now, font=('Arial', '14'))
        self.time_label.pack(padx=10, pady=5)

        self.t1_label = tk.Label(self.root, textvariable=self.temp1, font=('Arial', '14'))
        self.t1_label.pack(padx=10, pady=5)

        self.t2_label = tk.Label(self.root, textvariable=self.temp2, font=('Arial', '14'))
        self.t2_label.pack(padx=10, pady=5)

        self.t3_label = tk.Label(self.root, textvariable=self.temp3, font=('Arial', '14'))
        self.t3_label.pack(padx=10, pady=5)

        # Buttons
        self.button1 = tk.Button(self.root, text=" Export DB ", font=('Arial', '12'), command=self.export_db)
        self.button1.pack(padx=10, pady=10)

        self.button3 = tk.Button(self.root, text=" Filter ", font=('Arial', '12'), command=self.open_submenu)
        self.button3.pack(padx=10, pady=10)
        
        self.button4 = tk.Button(self.root, text=" Config ", font=('Arial', '12'), command=self.configuration_menu)
        self.button4.pack(padx=10, pady=10)

        self.button2 = tk.Button(self.root, text="  Exit  ", font=('Arial', '12'), command=self.exit_click)
        self.button2.pack(padx=10, pady=10)
        
        self.toggle_insertion_button = tk.Button(self.root, text="Toggle data recording", font=('Arial', '12'), command=self.toggle_insertion)
        self.toggle_insertion_button.pack(padx=10, pady=10)
        
    def create_live_graph(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.line, = self.ax.plot([], [], label="Temp1")
        self.line2, = self.ax.plot([], [], label="Temp2", color='r')
        self.line3, = self.ax.plot([], [], label="Temp3", color='g')
        temp_range = self.config.get("temperature_range")
        self.ax.set_ylim(temp_range[0], temp_range[1])
        self.ax.legend()
        self.ax.set_title("Live Temperature Plot")
        self.ax.set_xlabel(f"Last {self.max_points} records")
        self.ax.set_ylabel("Temperature (°C)")

        # Embed Matplotlib Figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(padx=10, pady=10)

    def update_all(self):
        self.update_variables()
        if self.inserting_data:
            db_functions.insert_data_to_db(self.db_path, self.table_name, self.data_time, self.data_temp1, self.data_temp2, self.data_temp3)
        self.update_labels()
        self.update_graph()
        self.update_job = self.root.after(self.config.get("update_interval"), self.update_all)

    def update_variables(self):
        self.data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.config.get("debug_mode"):
            self.data_temp1 = debugf.random_temp()
            self.data_temp2 = debugf.random_temp()
            self.data_temp3 = debugf.random_temp()
        else:
            temps = read_1wire_sensors()
            self.data_temp1 = temps[0]
            self.data_temp2 = temps[1]
            self.data_temp3 = temps[2]
        
        self.temps1.append(self.data_temp1)
        self.temps2.append(self.data_temp2)
        self.temps3.append(self.data_temp3)
        
    def update_labels(self):
        # Update label variables with data values
        self.time_now.set(f"Date: {self.data_time}")
        self.temp1.set(f"Temp 1: {self.data_temp1}")
        self.temp2.set(f"Temp 2: {self.data_temp2}")
        self.temp3.set(f"Temp 3: {self.data_temp3}")

    def update_graph(self):
        # Plot temperature data vs index (just using len() for index)
        indices = list(range(len(self.temps1)))  # Create a simple index list for x-axis this is 'time'

        # Set data for each plot
        self.line.set_data(indices, self.temps1)  # Temp1 plot
        self.line2.set_data(indices, self.temps2)  # Temp2 plot
        self.line3.set_data(indices, self.temps3)  # Temp3 plot

        # Adjust the x-axis to display a limited number of recent data points
        self.ax.set_xlim(0, len(self.temps1) + 1)  # Show all available data points, +1 is for slight lead in graph

        # Update x-axis ticks and labels (using the index as labels)
        self.ax.xaxis.set_major_locator(plt.MultipleLocator(10))  # Major ticks every 10 data points
        self.ax.xaxis.set_minor_locator(plt.MultipleLocator(5))   # Minor ticks every 5 data points
        self.ax.set_xlabel(f"Last {self.max_points} records")

        self.canvas.draw()

    def export_db(self):
        print("Export DataBase to csv file")
        db_functions.export_to_csv(self.db_path, self.table_name, self.config.get("export_path"))

        
    def open_submenu(self):
        # Implement a submenu for filtering data
        print("Opening Filter Submenu")
        
        Submenu(self.root)
        
    def toggle_insertion(self):
        self.inserting_data = not self.inserting_data
        if self.inserting_data:
            self.toggle_insertion_button.config(text="Stop Recording Data")
            print("Data insertion started")
        else:
            self.toggle_insertion_button.config(text="Start Recording Data")
            print("Data insertion stopped")


    def exit_click(self):
        print("Exit clicked. Closing the application...")
        self.close_application()

    def close_application(self):
        print("Closing application...")
        # Cancel any scheduled after callbacks
        if hasattr(self, 'update_job'):
            self.root.after_cancel(self.update_job)  # Cancel the scheduled update

        # Close all top-level windows
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                window.destroy()

        # Close the matplotlib figure
        plt.close(self.fig)

        # Destroy all widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Stop the main loop and destroy the root window
        self.root.quit()
        self.root.destroy()

        # Force exit the Python interpreter
        sys.exit(0)

        self.root.quit()  # Stop the main loop
        self.root.destroy()  # Free resources


    
    def configuration_menu(self):
        self.config.edit_config_ui()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.close_application()

def main():
    app = WireReaderApp()
    try:
        app.run()
    except Exception as e:
        print(f"An unhandled exception occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
