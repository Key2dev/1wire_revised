import json
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import db_functions

class Config:
    def __init__(self, master):
        self.master = master
        self.config_file = "config.json"
        self.original_default_config = {
            "db_path": "temperatury.db",
            "export_path": "test_dbdump.csv",
            "temperature_range": [0, 50],
            "table_name": "temps",
            "update_interval": 1000,  # in milliseconds
            "graph_points": 60,
            "debug_mode": True # IMPORTANT: Debug mode should be False in a production environment!
        }
        self.default_config = self.original_default_config.copy()
        self.load_config()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                self.default_config.update(loaded_config)
        else:
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.default_config, f, indent=4)

    def get(self, key):
        return self.default_config.get(key)

    def set(self, key, value):
        self.default_config[key] = value
        self.save_config()

    def edit_config_ui(self):
        root = tk.Toplevel(self.master)
        root.title("Edit Configuration")
    
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
        row = 0
        entries = {}
    
        # Regular settings
        regular_frame = ttk.Frame(frame)
        regular_frame.grid(column=0, row=row, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
        # Advanced settings
        advanced_frame = ttk.Frame(frame)
        advanced_frame.grid(column=0, row=row+1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        advanced_frame.grid_remove()  # Initially hide the advanced frame
    
        def create_config_entry(parent_frame, key, value, row):
            ttk.Label(parent_frame, text=key).grid(column=0, row=row, sticky=tk.W, pady=5)
    
            if key in ["db_path", "export_path"]:
                entry = ttk.Entry(parent_frame)
                entry.insert(0, str(value))
                entry.grid(column=1, row=row, sticky=(tk.W, tk.E), pady=5)
    
                def choose_path(path_type, entry_widget):
                    def inner_choose_path():
                        if path_type == "db_path":
                            filename = filedialog.askopenfilename(
                                title="Select Database File",
                                filetypes=(("SQLite Database", "*.db"), ("All files", "*.*"))
                            )
                        else:  # export_path
                            filename = filedialog.askdirectory(
                                title="Select Export Directory"
                            )
                        if filename:
                            entry_widget.delete(0, tk.END)
                            entry_widget.insert(0, filename)
                            self.set(path_type, filename)
                            messagebox.showinfo("Success", f"{path_type.capitalize()} updated to: {filename}")
                    return inner_choose_path
    
                ttk.Button(parent_frame, text="Choose...", command=choose_path(key, entry)).grid(column=2, row=row, pady=5)
    
                if key == "db_path":
                    def create_new_db():
                        new_db_path = filedialog.asksaveasfilename(
                            title="Create New Database",
                            defaultextension=".db",
                            filetypes=(("SQLite Database", "*.db"), ("All files", "*.*"))
                        )
                        if new_db_path:
                            try:
                                if os.path.exists(new_db_path):
                                    if messagebox.askyesno("Confirm Overwrite", f"The file {new_db_path} already exists. Do you want to overwrite it?"):
                                        os.remove(new_db_path)
                                    else:
                                        return
    
                                db_functions.create_db(new_db_path, self.default_config["table_name"])
    
                                # Update the entry widget
                                entries["db_path"].delete(0, tk.END)
                                entries["db_path"].insert(0, new_db_path)
                                self.set("db_path", new_db_path)
    
                                messagebox.showinfo("Success", f"New database created and set as active at {new_db_path}")
                            except Exception as e:
                                messagebox.showerror("Error", f"Failed to create new database: {str(e)}")
    
                    ttk.Button(parent_frame, text="Create New DB", command=create_new_db).grid(column=3, row=row, pady=5)
    
                entries[key] = entry
    
            elif key == "temperature_range":
                frame_temp = ttk.Frame(parent_frame)
                frame_temp.grid(column=1, row=row, sticky=(tk.W, tk.E), pady=5)
    
                min_temp = tk.IntVar(value=value[0])
                max_temp = tk.IntVar(value=value[1])
    
                ttk.Spinbox(frame_temp, from_=-273, to=1000, textvariable=min_temp, width=5).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(frame_temp, text="-").pack(side=tk.LEFT, padx=5)
                ttk.Spinbox(frame_temp, from_=-273, to=1000, textvariable=max_temp, width=5).pack(side=tk.LEFT, padx=(5, 0))
    
                entries[key] = (min_temp, max_temp)
            elif isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                entry = ttk.Checkbutton(parent_frame, variable=var, onvalue=True, offvalue=False)
                entries[key] = var
            elif isinstance(value, int):
                var = tk.IntVar(value=value)
                entry = ttk.Spinbox(parent_frame, from_=0, to=10000, textvariable=var)
                entries[key] = var
            else:  # string
                entry = ttk.Entry(parent_frame)
                entry.insert(0, str(value))
                entries[key] = entry
    
            if key not in ["db_path", "export_path", "temperature_range"]:
                entry.grid(column=1, row=row, sticky=(tk.W, tk.E), pady=5)
    
            return row + 1
    
        regular_row = 0
        advanced_row = 0
    
        for key, value in self.default_config.items():
            if key in ["table_name", "update_interval", "graph_points", "debug_mode"]:
                advanced_row = create_config_entry(advanced_frame, key, value, advanced_row)
            else:
                regular_row = create_config_entry(regular_frame, key, value, regular_row)
    
        # Advanced settings checkbox
        advanced_var = tk.BooleanVar(value=False)
        advanced_check = ttk.Checkbutton(frame, text="Show Advanced Settings", variable=advanced_var)
        advanced_check.grid(column=0, row=regular_row+1, columnspan=2, sticky=tk.W, pady=5)
    
        def toggle_advanced():
            if advanced_var.get():
                advanced_frame.grid()
            else:
                advanced_frame.grid_remove()
    
        advanced_check.config(command=toggle_advanced)
    
        # Save and Reset buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=0, row=regular_row+2, columnspan=3, sticky=(tk.W, tk.E), pady=10)
    
        def save_changes():
            for key, entry in entries.items():
                if key == "temperature_range":
                    min_temp, max_temp = entry
                    value = [min_temp.get(), max_temp.get()]
                elif isinstance(entry, tk.Variable):
                    value = entry.get()
                else:
                    value = entry.get()
                self.default_config[key] = value  # Update the current config
            self.save_config()  # Save to file
            root.destroy()
    
        def reset_to_default():
            for key, entry in entries.items():
                default_value = self.original_default_config[key]
                if key == "temperature_range":
                    min_temp, max_temp = entry
                    min_temp.set(default_value[0])
                    max_temp.set(default_value[1])
                elif isinstance(entry, tk.Variable):
                    entry.set(default_value)
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(default_value))
    
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Default", command=reset_to_default).pack(side=tk.LEFT, padx=5)
    
        def on_config_window_close():
            # Perform any necessary cleanup here
            self.save_config()  # Save configuration before closing
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_config_window_close)
        
        root.mainloop()
    def on_closing(self):
        try:
            # Perform any cleanup operations here
            self.save_config()  # Save configuration before closing
            self.master.destroy()
        except Exception as e:
            print(f"Error while closing configuration window: {e}")
        finally:
            self.master.quit()
                


# # Example usage / outside edit
# TODO: delete
if __name__ == "__main__":
    root = tk.Tk()
    app = Config(root)
    root.mainloop()