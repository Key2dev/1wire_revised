from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import tkinter as tk
import debug_functions as debugf
import db_functions
import datetime
from submenu import Submenu

# Old reader implementation
from wire_reader import read_1wire_sensors

# TODO:
"""
    średnia dla 3 czujników
    datetime unification %Y-%M-%D %H:%M:%S
    backup bazy danych w innych miejscach
    refresh na 5s
    """

class WireReaderApp:
    def __init__(self):
        """
        Initialize the WireReaderApp.

        This method sets up the main window, initializes variables for data storage and display,
        creates UI elements including labels and buttons, and sets up a live graph for temperature visualization.

        Attributes:
            usedebug (bool): Flag to enable debug mode.
            root (tk.Tk): The main Tkinter window.
            db_path (str): Path to the SQLite database file.
            table_name (str): Name of the table in the database.
            data_time (str): Current timestamp.
            data_temp1 (float): Temperature reading from sensor 1.
            data_temp2 (float): Temperature reading from sensor 2.
            data_temp3 (float): Temperature reading from sensor 3.
            temps1 (deque): Circular buffer for storing historical temperature data from sensor 1.
            temps2 (deque): Circular buffer for storing historical temperature data from sensor 2.
            temps3 (deque): Circular buffer for storing historical temperature data from sensor 3.
            time_now (tk.StringVar): StringVar for displaying current time in UI.
            temp1 (tk.StringVar): StringVar for displaying temperature 1 in UI.
            temp2 (tk.StringVar): StringVar for displaying temperature 2 in UI.
            temp3 (tk.StringVar): StringVar for displaying temperature 3 in UI.
            fig (matplotlib.figure.Figure): Matplotlib figure for the live graph.
            ax (matplotlib.axes.Axes): Axes for the live graph.
            canvas (FigureCanvasTkAgg): Tkinter canvas for embedding the Matplotlib figure.

        Returns:
            None
        """
        #TODO: debug variables
        self.usedebug = True

        # Create a new Toplevel window
        self.root = tk.Tk()
        self.root.title("1Wire Reader")

        # Database Variables
        self.db_path = "temperatury.db"
        self.table_name = "temps"

        # Data Variables
        self.data_time = ""
        self.data_temp1 = 0.0
        self.data_temp2 = 0.0
        self.data_temp3 = 0.0

        # Store historical data for the graph
        self.temps1 = deque(maxlen=60)
        self.temps2 = deque(maxlen=60)
        self.temps3 = deque(maxlen=60)

        # Label Variables for UI
        self.time_now = tk.StringVar()
        self.temp1 = tk.StringVar()
        self.temp2 = tk.StringVar()
        self.temp3 = tk.StringVar()

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
        self.button1 = tk.Button(self.root, text="Export DB", font=('Arial', '12'), command=self.export_db)
        self.button1.pack(padx=10, pady=10)

        self.button2 = tk.Button(self.root, text="  Exit  ", font=('Arial', '12'), command=self.exit_click)
        self.button2.pack(padx=10, pady=10)

        self.button3 = tk.Button(self.root, text="Filter", font=('Arial', '12'), command=self.open_submenu)
        self.button3.pack(padx=10, pady=10)

        # Live Graph
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.line, = self.ax.plot([], [], label="Temp1")
        self.line2, = self.ax.plot([], [], label="Temp2", color='r')
        self.line3, = self.ax.plot([], [], label="Temp3", color='g')
        self.ax.set_ylim(0, 50)  # Temperature range
        self.ax.legend()
        self.ax.set_title("Live Temperature Plot")
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel("Temperature (°C)")

        # Embed Matplotlib Figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(padx=10, pady=10)

        # Start updating the GUI
        self.update_all()


    def update_all(self):
        self.update_variables()  # Updates the actual data
        db_functions.insert_data_to_db(self.db_path, self.table_name, self.data_time, self.data_temp1, self.data_temp2, self.data_temp3)  # Insert data into DB
        self.update_labels()      # Updates the displayable labels in the UI
        self.update_graph()       # Updates the graph with new data
        self.root.after(1000, self.update_all)  # Update every second

    def update_variables(self):
        # Update data variables
        self.data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Sensor Data Variables
        # TODO: delete this line and fix the next lines when actual sensor data reading is implemented
        if self.usedebug:
            # Using debug_functions to generate random temperatures for testing purposes
            self.data_temp1 = debugf.random_temp()
            self.data_temp2 = debugf.random_temp()
            self.data_temp3 = debugf.random_temp()
        else:
            # Using actual sensor data reading here
            temps = read_1wire_sensors()
            self.data_temp1 = temps[0]
            self.data_temp2 = temps[1]
            self.data_temp3 = temps[2]
        
        # Store historical data (just append new temperatures)
        self.temps1.append(self.data_temp1)
        self.temps2.append(self.data_temp2)
        self.temps3.append(self.data_temp3)

    def update_labels(self):
        # Update label variables with data values
        self.time_now.set(f"Date: {self.data_time}")
        self.temp1.set(f"Temp1: {self.data_temp1}")
        self.temp2.set(f"Temp2: {self.data_temp2}")
        self.temp3.set(f"Temp3: {self.data_temp3}")

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
        self.ax.set_xlabel("Index")

        self.canvas.draw()

    def export_db(self):
        # TODO: this is dumping the while data to a csv file ?remove?
        print("Export DataBase to csv file")
        # DB dump to csv file
        db_functions.export_to_csv(self.db_path, self.table_name, "test_dbdump.csv")
        
    def open_submenu(self):
        # Implement a submenu for filtering data
        print("Opening Filter Submenu")
        
        Submenu(self.root, self.db_path, self.table_name)

    def exit_click(self):
        print("Exit clicked. Closing the application...")
        # Cancel any scheduled after callbacks
        self.root.quit()  # Stop the main loop
        self.root.destroy()  # Free resources

    def run(self):
        self.root.mainloop()

def main():
    app = WireReaderApp()
    app.run()

if __name__ == "__main__":
    main()
