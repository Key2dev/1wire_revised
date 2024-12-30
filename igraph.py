import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import db_functions
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter.simpledialog
import numpy as np
from matplotlib.lines import Line2D

class InteractiveTemperaturePlot:
    def __init__(self, parent, db_path, table_name, start_time, end_time):
        self.igraph = tk.Toplevel(parent)
        self.igraph.title("Interactive Temperature Plot")
        self.igraph.geometry("1200x800")

        self.db_path = db_path
        self.table_name = table_name
        self.start_time = start_time
        self.end_time = end_time

        # Create main frame
        self.main_frame = tk.Frame(self.igraph)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Create plot frame
        self.plot_frame = tk.Frame(self.main_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=1)

        # Fetch and prepare data
        self.dataset = db_functions.fetch_filtered_data(self.db_path, self.table_name, self.start_time, self.end_time)
        self.timestamps = [datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') for row in self.dataset]
        self.temperatures = [row[2] for row in self.dataset]
        self.temperatures2 = [row[3] for row in self.dataset]
        self.temperatures3 = [row[4] for row in self.dataset]
        self.comments = [row[5] if len(row) > 5 else '' for row in self.dataset]

        # Initialize checkbox variables
        self.temp1_var = tk.BooleanVar(value=True)
        self.temp2_var = tk.BooleanVar(value=True)
        self.temp3_var = tk.BooleanVar(value=True)
        self.avg_temp_var = tk.BooleanVar(value=True)
        self.show_comments_var = tk.BooleanVar()

        # Initialize the plot
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.init_plot()

        # Embed the plot in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()

        # Now we can call update_plot_limits
        self.update_plot_limits()

        self.init_pick_event()
        self.init_annotation()
        self.init_hover_event()

        # Add the matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create control frame and add controls
        self.create_control_frame()

        # Create Treeview for data table
        self.create_data_table()

    def create_control_frame(self):
        # Frame for buttons and controls
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.BOTH, expand=0.6)

        # Add Action Buttons
        self.button1 = tk.Button(self.control_frame, text="Export DB", font=('Arial', '12'), command=self.export_data)
        self.button1.pack(side=tk.LEFT, padx=10, pady=10)

        # Add checkbox for showing comments
        self.show_comments_checkbox = tk.Checkbutton(self.control_frame, text="Show Comments", 
                                                     variable=self.show_comments_var, 
                                                     command=self.toggle_comments)
        self.show_comments_checkbox.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Add checkboxes for showing/hiding temperature lines
        self.temp1_checkbox = tk.Checkbutton(self.control_frame, text="Show Temp 1", 
                                             variable=self.temp1_var, 
                                             command=self.toggle_temp_lines)
        self.temp1_checkbox.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.temp2_checkbox = tk.Checkbutton(self.control_frame, text="Show Temp 2", 
                                             variable=self.temp2_var, 
                                             command=self.toggle_temp_lines)
        self.temp2_checkbox.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.temp3_checkbox = tk.Checkbutton(self.control_frame, text="Show Temp 3", 
                                             variable=self.temp3_var, 
                                             command=self.toggle_temp_lines)
        self.temp3_checkbox.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.avg_temp_checkbox = tk.Checkbutton(self.control_frame, text="Show Avg Temp", 
                                            variable=self.avg_temp_var, 
                                            command=self.toggle_temp_lines)
        self.avg_temp_checkbox.pack(side=tk.LEFT, padx=10, pady=10)
    

        # Add button to update comments
        self.update_comment_button = tk.Button(self.control_frame, text="Update Comment", font=('Arial', '12'), command=self.update_comment)
        self.update_comment_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.exitbutton = tk.Button(self.control_frame, text="Exit", font=('Arial', '12'), command=self.close_window)
        self.exitbutton.pack(side=tk.RIGHT, padx=10, pady=10)

        
    def init_annotation(self):
        self.annotation = self.ax.annotate(
            text='',
            xy=(0, 0),
            xytext=(20, 20),
            textcoords='offset points',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
        )
        self.annotation.set_visible(False)  # Hide it initially

    def create_data_table(self):
        # Frame for the table
        self.table_frame = tk.Frame(self.main_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=1)

        # Scrollbar for the table
        self.table_scrollbar = tk.Scrollbar(self.table_frame)
        self.table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create Treeview
        self.data_table = ttk.Treeview(
            self.table_frame, 
            columns=('Timestamp', 'Temp1', 'Temp2', 'Temp3', 'Comment'), 
            show='headings', 
            yscrollcommand=self.table_scrollbar.set
        )

        # Define headings
        self.data_table.heading('Timestamp', text='Timestamp')
        self.data_table.heading('Temp1', text='Temp 1')
        self.data_table.heading('Temp2', text='Temp 2')
        self.data_table.heading('Temp3', text='Temp 3')
        self.data_table.heading('Comment', text='Comment')

        # Define column widths
        self.data_table.column('Timestamp', width=200, anchor='center')
        self.data_table.column('Temp1', width=100, anchor='center')
        self.data_table.column('Temp2', width=100, anchor='center')
        self.data_table.column('Temp3', width=100, anchor='center')
        self.data_table.column('Comment', width=300, anchor='w')

        # Populate the table
        for i in range(len(self.timestamps)):
            self.data_table.insert('', 'end', values=(
                self.timestamps[i].strftime('%Y-%m-%d %H:%M:%S'),
                f'{self.temperatures[i]:.2f}',
                f'{self.temperatures2[i]:.2f}', 
                f'{self.temperatures3[i]:.2f}',
                self.comments[i]
            ))

        # Configure scrollbar
        self.table_scrollbar.config(command=self.data_table.yview)

        # Pack the table
        self.data_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # Bind selection event:
        self.data_table.bind("<ButtonRelease-1>", self.on_table_select)

    def calculate_average_temperature(self):
        return [(t1 + t2 + t3) / 3 for t1, t2, t3 in zip(self.temperatures, self.temperatures2, self.temperatures3)]
    
    def init_plot(self):
        self.line1, = self.ax.plot(self.timestamps, self.temperatures, c='blue', label="Temp 1", marker='o', linestyle='-', picker=5, markersize=4)
        self.line2, = self.ax.plot(self.timestamps, self.temperatures2, c='red', label="Temp 2", marker='o', linestyle='-', picker=5, markersize=4)
        self.line3, = self.ax.plot(self.timestamps, self.temperatures3, c='green', label="Temp 3", marker='o', linestyle='-', picker=5, markersize=4)
        
        # Avg temp line
        self.avg_temp = self.calculate_average_temperature()
        self.line_avg, = self.ax.plot(self.timestamps, self.avg_temp, c='purple', label="Avg Temp", linestyle='--', linewidth=2)


        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Temperature")
        self.ax.set_title("Interactive Temperature Plot")
        self.ax.legend()

        # Set y-range from 0 to 50
        self.ax.set_ylim(0, 50)
        # Format x-axis as date
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M:%S'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.fig.autofmt_xdate()  # Auto-rotate date labels for readability
        plt.tight_layout()

        # Initialize comment annotations (hidden by default)
        self.comment_annotations = []

        # Create scatter plots for selected points (initially empty)
        self.selected_scatter1 = self.ax.scatter([], [], c='yellow', s=100, zorder=5, label="Selected Temp1")
        self.selected_scatter2 = self.ax.scatter([], [], c='yellow', s=100, zorder=5, label="Selected Temp2")
        self.selected_scatter3 = self.ax.scatter([], [], c='yellow', s=100, zorder=5, label="Selected Temp3")


    def init_pick_event(self):
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        
    def init_hover_event(self):
        self.hover_connection = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        

    # On click function for picking data from graph
    def highlight_graph_point(self, index):
        """Highlight only the selected points for a specific timestamp."""
        # Update scatter plots for selected points
        self.selected_scatter1.set_offsets(np.array([[self.timestamps[index], self.temperatures[index]]]))
        self.selected_scatter2.set_offsets(np.array([[self.timestamps[index], self.temperatures2[index]]]))
        self.selected_scatter3.set_offsets(np.array([[self.timestamps[index], self.temperatures3[index]]]))

        # Update the canvas to show the changes
        self.canvas.draw_idle()

    def onpick(self, event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            if len(ind) > 0:
                i = ind[0]
                x = xdata[i]
                y = ydata[i]
                self.highlight_graph_point(i)

                # Get the timestamp of the selected point
                selected_timestamp = self.timestamps[i].strftime('%Y-%m-%d %H:%M:%S')

                # Find the corresponding row in the table
                for item in self.data_table.get_children():
                    item_values = self.data_table.item(item)['values']
                    if item_values[0] == selected_timestamp:
                        # Select the corresponding row
                        self.data_table.selection_set(item)
                        self.data_table.focus(item)
                        # Scroll to the selected row
                        self.data_table.yview_moveto(self.data_table.index(item) / len(self.data_table.get_children()))
                        break

                # Update the annotation
                self.annotation.xy = (x, y)
                text = f"Time: {selected_timestamp}\n"
                text += f"Temp 1: {self.temperatures[i]:.2f}\n"
                text += f"Temp 2: {self.temperatures2[i]:.2f}\n"
                text += f"Temp 3: {self.temperatures3[i]:.2f}\n"
                if self.comments[i]:
                    text += f"Comment: {self.comments[i]}"
                self.annotation.set_text(text)
                self.annotation.set_visible(True)
                self.fig.canvas.draw_idle()


    def on_table_select(self, event):
        selected_item = self.data_table.selection()
        if selected_item:
            item = self.data_table.item(selected_item)
            timestamp_str = item['values'][0]
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            index = self.timestamps.index(timestamp)
            self.highlight_graph_point(index)

    # Setting up on hover
    def on_hover(self, event):
        if event.inaxes == self.ax:
            for line, temps in [(self.line1, self.temperatures),
                                (self.line2, self.temperatures2),
                                (self.line3, self.temperatures3),
                                (self.line_avg, self.avg_temp)]:
                cont, ind = line.contains(event)
                if cont:
                    i = ind["ind"][0]  # Get the index of the nearest point
                    x, y = self.timestamps[i], temps[i]
                    self.annotation.xy = (x, y)
                    text = f"Time: {self.timestamps[i].strftime('%Y-%m-%d %H:%M:%S')}\n"
                    text += f"Temp 1: {self.temperatures[i]:.2f}\n"
                    text += f"Temp 2: {self.temperatures2[i]:.2f}\n"
                    text += f"Temp 3: {self.temperatures3[i]:.2f}\n"
                    text += f"Avg Temp: {self.avg_temp[i]:.2f}\n"
                    if self.comments[i]:
                        text += f"Comment: {self.comments[i]}"
                    self.annotation.set_text(text)
                    self.annotation.set_visible(True)
                    self.fig.canvas.draw_idle()
                    return

            # If no point is found, hide the annotation
            self.annotation.set_visible(False)
            self.fig.canvas.draw_idle()
        else:
            self.annotation.set_visible(False)
            self.fig.canvas.draw_idle()



    def find_nearest_point(self, x, y, line):
        xdata = mdates.date2num(self.timestamps)
        ydata = line.get_ydata()
        distances = np.sqrt((xdata - x)**2 + (ydata - y)**2)
        return np.argmin(distances)
    
    # Comment checkbox logic
    def toggle_comments(self):
        show_comments = self.show_comments_var.get()
        if show_comments:
            self.display_comments()
        else:
            self.remove_comments()
        self.fig.canvas.draw_idle()
        
    def toggle_temp_lines(self):
        self.line1.set_visible(self.temp1_var.get())
        self.line2.set_visible(self.temp2_var.get())
        self.line3.set_visible(self.temp3_var.get())
        self.line_avg.set_visible(self.avg_temp_var.get())
        self.update_plot_limits()
        self.canvas.draw()

    def update_plot_limits(self):
        visible_lines = [line for line in [self.line1, self.line2, self.line3, self.line_avg] if line.get_visible()]
        if visible_lines:
            ymin = min(min(line.get_ydata()) for line in visible_lines)
            ymax = max(max(line.get_ydata()) for line in visible_lines)
            self.ax.set_ylim(max(0, ymin - 5), min(50, ymax + 5))
        else:
            self.ax.set_ylim(0, 50)  # Default range if no data is visible
        self.canvas.draw()
        
        
    def display_comments(self):
        print("Displaying comments...")  # Debug print
        self.remove_comments()  # Clear existing annotations
        for i, (timestamp, temp1, temp2, temp3, comment) in enumerate(zip(self.timestamps, self.temperatures, self.temperatures2, self.temperatures3, self.comments)):
            if comment:
                print(f"Adding comment: {comment} at time {timestamp}")  # Debug print
                # Find the highest temperature for this timestamp
                max_temp = max(temp1, temp2, temp3)
                ann = self.ax.annotate(
                    comment,
                    (timestamp, max_temp),
                    xytext=(10, 10),
                    textcoords='offset points',
                    fontsize=8,
                    color='black',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='purple', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='purple', alpha=0.7)
                )
                self.comment_annotations.append(ann)
        print(f"Total comments added: {len(self.comment_annotations)}")  # Debug print

    def remove_comments(self):
        if hasattr(self, 'comment_annotations'):
            for ann in self.comment_annotations:
                ann.remove()
            self.comment_annotations = []


    def update_comment(self):
        selected_item = self.data_table.selection()
        if selected_item:
            item = self.data_table.item(selected_item)
            timestamp = item['values'][0]
            comment = item['values'][4]
            new_comment = tk.simpledialog.askstring("Update Comment", "Enter new comment:", initialvalue=comment)
            if new_comment is not None:
                db_functions.add_comment(self.db_path, self.table_name, timestamp, new_comment)

                # Refresh data and reinitialize plot
                self.refresh_data()

    def refresh_data(self):
        # Re-fetch data and update plot and table
        self.dataset = db_functions.fetch_filtered_data(self.db_path, self.table_name, self.start_time, self.end_time)
        self.timestamps = [datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') for row in self.dataset]
        self.temperatures = [row[2] + 1 for row in self.dataset]
        self.temperatures2 = [row[3] + 3 for row in self.dataset]
        self.temperatures3 = [row[4] + 5 for row in self.dataset]
        self.comments = [row[5] if len(row) > 5 else '' for row in self.dataset]
    
        # Clear and repopulate the table
        for item in self.data_table.get_children():
            self.data_table.delete(item)
        for i in range(len(self.timestamps)):
            self.data_table.insert('', 'end', values=(
                self.timestamps[i].strftime('%Y-%m-%d %H:%M:%S'),
                f'{self.temperatures[i]:.2f}',
                f'{self.temperatures2[i]:.2f}', 
                f'{self.temperatures3[i]:.2f}',
                self.comments[i]
            ))
        # Recalculate average temperature
        self.avg_temp = self.calculate_average_temperature()
        
        # Redraw the plot
        self.ax.clear()
        self.init_plot()
        
    
        # Recreate the annotation object
        self.init_annotation()
    
        # Disconnect previous events
        if hasattr(self, 'hover_connection'):
            self.fig.canvas.mpl_disconnect(self.hover_connection)
    
        # Reconnect the hover and pick events
        self.init_pick_event()
        self.hover_connection = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
    
        # Redraw the canvas
        self.canvas.draw()
    
        print("Data refreshed and hover event reconnected")  # Debug print
        
        # Restore visibility state
        self.toggle_temp_lines()
        
        
    def close_window(self):
        self.igraph.destroy()

    # Button functions
    def export_data(self):
        # TODO: add some functionality to determine filepath - done in db_functions.py
        print("Exporting data...")
        db_functions.records_by_time_csv(self.db_path, self.table_name, self.start_time, self.end_time)
        
        
# TODO: this is for debugging, remove later
def main():
    root = tk.Tk()
    root.title("Main Application Window")

    # Example button to launch the subwindow
    def open_plot_window():
        InteractiveTemperaturePlot(root, "temperatury.db", "temps", "2024-11-26 11:40:00", "2024-12-04 11:55:00")

    open_button = tk.Button(root, text="Open Interactive Plot", command=open_plot_window)
    open_button.pack(padx=20, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
    
    
    
