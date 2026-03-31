import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from tkinter import messagebox
import threading
import tkinter.filedialog

class Ranklist:
    def __init__(self, master, args=None):
        self.master = master
        self.index_dir = args[0] if args else None
        self.data = None
        self.sort_column = None
        self.sort_ascending = True
        self.pivoted_data = False
        self.min_column_width = 100  # Minimum column width in pixels
        self.batch_size = 1000  # Number of rows to load at once
        
        # Create main frame
        self.frame = ttk.Frame(master)
        self.frame.pack(fill='both', expand=True)
        
        # Create control frame for sort criteria
        self.control_frame = ttk.Frame(self.frame)
        self.control_frame.pack(fill='x', padx=5, pady=5)
        
        # Create sort criteria label and dropdown
        ttk.Label(self.control_frame, text="Sort by:").pack(side='left', padx=5)
        self.sort_criteria = ttk.Combobox(self.control_frame, state='readonly')
        self.sort_criteria.pack(side='left', padx=5)
        self.sort_criteria.bind('<<ComboboxSelected>>', self.on_sort_change)
        
        # Sort direction button
        self.sort_direction_button = ttk.Button(self.control_frame, text="↑", width=3, command=self.toggle_sort_direction)
        self.sort_direction_button.pack(side='left', padx=5)
        
        # Toggle view button (normal/matrix)
        self.view_button = ttk.Button(self.control_frame, text="Matrix View", command=self.toggle_view)
        self.view_button.pack(side='left', padx=5)

        # Export button
        ttk.Button(self.control_frame, text="Export Data", command=self.export_data).pack(side='left', padx=5)
        
        # Refresh button
        ttk.Button(self.control_frame, text="Refresh Data", command=self.load_data).pack(side='right', padx=5)
        
        # Create frame for treeview and scrollbars
        self.tree_frame = ttk.Frame(self.frame)
        self.tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        y_scrollbar.pack(side='right', fill='y')
        
        x_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        x_scrollbar.pack(side='bottom', fill='x')
        
        # Create treeview with fixed column widths
        self.tree = ttk.Treeview(self.tree_frame, 
                                 yscrollcommand=y_scrollbar.set, 
                                 xscrollcommand=x_scrollbar.set, 
                                 selectmode='browse')
        
        # Pack the treeview
        self.tree.pack(fill='both', expand=True)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Set up column click for sorting
        self.tree.bind('<ButtonRelease-1>', self.on_column_click)
        
        # Add virtual event for lazy loading on scroll
        self.tree.bind("<<TreeviewSelect>>", self.check_load_more)
    
    def load_data(self):
        pass  # Placeholder for data loading logic

    def create_demo_data(self):
        # Create demo data suitable for matrix view
        self.data = pd.DataFrame({
            'Asset': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
            'Price': [150.25, 290.45, 2850.12, 3300.75, 320.60],
            'Change': [2.5, -1.2, 0.8, -0.5, 1.7],
            'Volume': [12500000, 8900000, 1500000, 2200000, 9800000],
            'PE Ratio': [25.3, 35.1, 28.7, 70.2, 22.5],
            'Yield': [0.5, 0.8, 0.0, 0.0, 0.3]
        })
        # Current loaded batch counter
        self.loaded_rows = 0
    
    def export_data(self): 
        # Use a separate thread for exporting
        if self.data is not None:
            file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                # Show "exporting" message
                self.export_status = tk.Toplevel(self.master)
                self.export_status.title("Exporting")
                tk.Label(self.export_status, text="Exporting data, please wait...").pack(padx=20, pady=20)
                self.export_status.update()
                
                # Export data in a separate thread
                def export_thread():
                    self.data.to_csv(file_path, index=False)
                    self.export_status.destroy()
                    messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
                
                threading.Thread(target=export_thread).start()
    
    def update_treeview(self):
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Disable redrawing during updates
        self.tree.update_idletasks()
        
        # Configure columns
        if not self.pivoted_data:
            # Standard view
            self._setup_standard_view()
        else:
            # Matrix view
            self._setup_matrix_view()
        
        # Reset loaded rows count
        self.loaded_rows = 0
        
        # Load initial batch of rows
        self.load_more_rows()
    
    def _setup_standard_view(self):
        # Remove all existing columns
        self.tree['columns'] = list(self.data.columns)
        self.tree['show'] = 'headings'
        
        # Set column headings with minimum width
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=self.min_column_width, minwidth=self.min_column_width, anchor='center')
        
        # Sort data if column is selected
        if self.sort_column and self.sort_column in self.data.columns:
            self.data = self.data.sort_values(by=self.sort_column, ascending=self.sort_ascending)
    
    def _setup_matrix_view(self):
        # Matrix view with row and column headers
        pivot_col = self.data.columns[0]
        self.df_pivot = self.data.set_index(pivot_col)
        
        # Sort by row if sort_column is selected
        if self.sort_column and self.sort_column in self.df_pivot.columns:
            # Sort the dataframe by the selected column
            self.df_pivot = self.df_pivot.sort_values(by=self.sort_column, ascending=self.sort_ascending)
        
        # Configure columns
        self.tree['columns'] = [pivot_col] + list(self.df_pivot.columns)
        self.tree['show'] = 'tree headings'
        
        # Set column headings
        self.tree.heading('#0', text='')
        self.tree.column('#0', width=0, stretch=False)
        
        self.tree.heading(pivot_col, text=pivot_col)
        self.tree.column(pivot_col, width=self.min_column_width, minwidth=self.min_column_width, anchor='w')
        
        for col in self.df_pivot.columns:
            self.tree.heading(col, text=str(col))
            self.tree.column(col, width=self.min_column_width, minwidth=self.min_column_width, anchor='center')
    
    def load_more_rows(self):
        # Load next batch of rows
        if not self.pivoted_data:
            # Standard view - load next batch
            end_row = min(self.loaded_rows + self.batch_size, len(self.data))
            batch = self.data.iloc[self.loaded_rows:end_row]
            
            # Convert using values.tolist() for much faster insertion compared to iterrows()
            rows = batch.values.tolist()
            
            # Use insert with a single transaction for better performance
            for values in rows:
                self.tree.insert('', 'end', values=values)
            
            self.loaded_rows = end_row
        else:
            # Matrix view - load next batch
            end_row = min(self.loaded_rows + self.batch_size, len(self.df_pivot))
            batch = self.df_pivot.iloc[self.loaded_rows:end_row]
            
            # Insert rows using vectorized extraction
            indices = batch.index.tolist()
            rows = batch.values.tolist()
            for idx, row_vals in zip(indices, rows):
                values = [idx] + row_vals
                self.tree.insert('', 'end', values=values)
            
            self.loaded_rows = end_row
    
    def check_load_more(self, event):
        # Check if we need to load more rows
        if self.loaded_rows < len(self.data if not self.pivoted_data else self.df_pivot):
            # Get the last visible item
            visible_items = self.tree.identify_row(self.tree.winfo_height())
            if visible_items and self.tree.index(visible_items) >= self.loaded_rows - 10:
                # If close to the bottom, load more rows
                self.load_more_rows()
    
    def on_sort_change(self, event):
        self.sort_column = self.sort_criteria.get()
        self.update_treeview()
    
    def toggle_sort_direction(self):
        self.sort_ascending = not self.sort_ascending
        self.sort_direction_button['text'] = "↑" if self.sort_ascending else "↓"
        self.update_treeview()
    
    def on_column_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            column_index = int(column.replace('#', '')) - 1
            
            if not self.pivoted_data:
                # Standard view sorting
                if column_index >= 0 and column_index < len(self.data.columns):
                    self.sort_column = self.data.columns[column_index]
                    self.sort_criteria.set(self.sort_column)
                    self.update_treeview()
            else:
                # Matrix view sorting
                if column_index == 0:  # Row header column
                    pass  # Do nothing or implement row name sorting
                elif column_index > 0 and column_index <= len(self.tree['columns']):
                    # Get the actual column name from tree
                    self.sort_column = self.tree['columns'][column_index]
                    self.sort_criteria.set(str(self.sort_column))
                    self.update_treeview()
    
    def toggle_view(self):
        self.pivoted_data = not self.pivoted_data
        self.view_button['text'] = "Standard View" if self.pivoted_data else "Matrix View"
        
        # Update sort criteria dropdown for the new view
        if self.pivoted_data:
            pivot_col = self.data.columns[0]
            df_pivot = self.data.set_index(pivot_col)
            self.sort_criteria['values'] = list(df_pivot.columns)
            if len(df_pivot.columns) > 0:
                self.sort_criteria.current(0)
                self.sort_column = df_pivot.columns[0]
        else:
            self.sort_criteria['values'] = list(self.data.columns)
            if len(self.data.columns) > 0:
                self.sort_criteria.current(0)
                self.sort_column = self.data.columns[0]
        
        self.update_treeview()

if __name__ == "__main__":
    root = tk.Tk()
    inpargs = []

    # create a tkinter window with a notebook named "Save Indices", give this to the SaveIndiceses class as master
    root.title("Save Indices")
    root.geometry("900x500")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    # Create the first tab
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Tab 1")
    
    # Create the second tab with test text
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Tab 2")
    
    # Add test text to tab2
    test_label = ttk.Label(tab2, text="This is a test text on Tab 2")
    test_label.pack(pady=20, padx=20)

    Ranklist = Ranklist(tab1, args=inpargs)
    Ranklist.frame.pack(fill='both', expand=True)
    Ranklist.create_demo_data()  # Create demo data for testing
    Ranklist.update_treeview()  # Initial data load

    root.mainloop()
