# Py Tk Sort

This is just a clean sort notebook. That is it.

## Overview
This repository contains a simple, lightweight Tkinter-based GUI application with a `ttk.Notebook` interface. It provides a tabbed viewing area where one of the tabs implements a highly optimized, sortable table (ranklist) using `ttk.Treeview` and `pandas`.

## Features
- **Clean Interface:** Uses Tkinter notebook tabs for a minimalistic look.
- **High Performance:** Optimized Pandas operations (`.values.tolist()`) to handle large datasets efficiently with lazy loading and batch insertion.
- **Sorting:** Click on column headers to sort the data dynamically.
- **Multiple Views:** Toggle between standard list view and matrix view.
- **Data Export:** Fast, threaded CSV exports to prevent freezing the UI.
