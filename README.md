# BIM Embodied Carbon Analyzer

This project is a desktop app that reads an IFC building model, extracts the building elements inside it, matches their materials to a local Cameroon material database, and calculates embodied carbon.

In simple words:

- You open an IFC file.
- The app reads the walls, slabs, beams, columns, roofs, doors, windows, and other building elements.
- The app checks what material each element uses.
- The app matches that material to a carbon factor from the local database.
- The app calculates the carbon impact.
- The app shows the result in tables and charts.
- You can export the result to Excel or CSV.

If you are new to Python, do not worry. Follow the setup steps exactly and you should be able to run it.

## What this app does

The app helps you estimate embodied carbon from BIM models in IFC format.

It is focused on a Cameroon material database, so the default material matching is based on materials and naming relevant to Cameroon construction.

Main things the app can do:

- Load IFC files
- Extract building elements and their geometry
- Detect or read materials from the IFC
- Map IFC materials to local carbon factors
- Let you review and change the material mapping
- Calculate mass and embodied carbon
- Show charts and tables
- Export results to Excel or CSV

## Project structure

These are the most important files and folders:

```text
PythonProject/
├── app.py
├── requirements.txt
├── data/
│   ├── lca_database.csv
│   ├── cameroon_material_notes.md
│   └── samples/
├── src/
│   ├── core/
│   │   ├── ifc_importer.py
│   │   ├── extractor.py
│   │   ├── carbon_calculator.py
│   │   └── paths.py
│   └── ui/
│       ├── main_window.py
│       ├── chart_widgets.py
│       ├── widgets.py
│       ├── theme.py
│       └── icons.py
└── legacy/
```

## Setup

You need Python installed on your machine first.

Recommended Python version:

- Python 3.10 or 3.11

## Create a virtual environment

A virtual environment keeps this project’s packages separate from other Python projects on your computer.

Open a terminal in the project folder and run:

```powershell
python -m venv .venv
```

## Activate the virtual environment

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If you use Command Prompt instead of PowerShell:

```cmd
.venv\Scripts\activate.bat
```

If activation works, you will usually see `(.venv)` at the start of your terminal line.

## Install dependencies

After activating the environment, run:

```powershell
pip install -r requirements.txt
```

This installs the libraries the app needs:

- `ifcopenshell` for reading IFC models
- `pandas` and `numpy` for working with tables and calculations
- `openpyxl` for Excel export
- `matplotlib` for charts
- `PySide6` for the desktop interface
- `qtawesome` for icons

## Run the app

After the dependencies are installed, start the app with:

```powershell
python app.py
```

That is the main run command for this project.

## How to use the app

### 1. Open an IFC file

When the app starts, load an IFC file by:

- clicking the open button
- browsing to your `.ifc` file
- or loading a sample IFC from the `data/samples` folder

### 2. Let the app extract elements

The app reads the IFC and extracts building elements such as:

- walls
- slabs
- beams
- columns
- footings
- roofs
- stairs
- doors
- windows

It also tries to get:

- element name
- IFC type
- storey
- material
- geometry
- area
- volume

### 3. Review the material mapping

This is one of the most important parts of the app.

The app takes each IFC material and tries to map it to a material in `data/lca_database.csv`.

Example:

- IFC says `Masonry`
- app suggests `Concrete Block`

You can review the suggestion in the mapping table and change it if needed.

This matters because the carbon result depends on the chosen material.

### 4. Calculate embodied carbon

When you click calculate:

- the app looks up the embodied carbon factor
- the app looks up density
- the app estimates mass from volume and density
- the app calculates embodied carbon

Simple formula used:

```text
Embodied Carbon = Volume × Carbon Factor
```

And for mass:

```text
Mass = Volume × Density
```

### 5. Review charts and tables

After calculation, the app shows:

- KPI summary cards
- charts by category
- charts by storey
- charts by material
- a detailed element table

### 6. Export the result

You can export the final data as:

- Excel workbook `.xlsx`
- CSV file `.csv`

## Explanation of each component

This section explains the main parts of the project in very simple language.

## `app.py`

This is the starting point of the program.

Its job is simple:

- start the Qt application
- create the main window
- show the app on screen

If you do not know where the app begins, it begins here.

## `requirements.txt`

This file lists the Python packages the app needs.

When you run:

```powershell
pip install -r requirements.txt
```

Python reads this file and installs everything in it.

## `data/lca_database.csv`

This is the material carbon database.

It contains rows like:

- material name
- embodied carbon factor
- density
- source note

This file is very important because the app uses it to decide the carbon impact of each mapped material.

If you change a value here, you change the carbon result.

## `data/cameroon_material_notes.md`

This file explains where the Cameroon material assumptions came from.

Think of it as the research note behind the database.

It helps a user understand:

- why certain materials were added
- why some values are proxies
- where the material information came from

## `data/samples/`

This folder contains sample IFC files.

Use these if:

- you want to test the app quickly
- you do not have your own IFC file ready

## `src/core/ifc_importer.py`

This part loads the IFC file.

What it does:

- checks whether the file exists
- checks whether the file ends with `.ifc`
- opens the IFC using `ifcopenshell`
- returns the model to the rest of the app

Plain English:

This file is the app’s IFC file loader.

## `src/core/extractor.py`

This part goes through the IFC model and extracts useful building data.

It looks for:

- what type of element it is
- what floor or storey it belongs to
- what material it uses
- its area
- its volume

It then puts all that into a pandas table.

Plain English:

This file is the app’s data miner. It digs information out of the IFC.

## `src/core/carbon_calculator.py`

This part does the carbon calculation.

What it does:

- loads the LCA database CSV
- tries to match IFC material names to database material names
- attaches carbon factors and densities
- calculates mass
- calculates embodied carbon
- creates grouped summaries

Plain English:

This is the brain of the carbon math.

## `src/core/paths.py`

This part handles file paths.

Why it matters:

- when you run the app from source, files are in one place
- when you package the app as an `.exe`, files may be in another place

This helper makes sure the app can still find:

- the material database
- sample IFC files
- output folders

Plain English:

This file helps the app find its files correctly.

## `src/ui/main_window.py`

This is the main screen and the biggest UI file.

It controls:

- the pages
- the buttons
- the mapping table
- the filters
- the charts page
- the export page
- the load and calculate actions

Plain English:

This is the control center of the app.

If the project were a house, this would be the main room connecting everything.

## `src/ui/chart_widgets.py`

This file creates the charts.

It uses `matplotlib` to show:

- bar charts
- horizontal bar charts
- donut charts

These charts help the user understand carbon results visually.

Plain English:

This file turns numbers into pictures.

## `src/ui/widgets.py`

This file contains reusable custom UI widgets.

That means small interface parts that can be reused in many places.

Examples:

- custom dropdowns
- table cell dropdowns

Plain English:

These are helper building blocks for the interface.

## `src/ui/theme.py`

This file controls the visual design of the app.

It defines things like:

- colors
- borders
- table styling
- dropdown styling
- chart colors

Plain English:

This is the app’s look-and-feel file.

If you want to change the app from dark to light, blue to green, or plain to polished, this is one of the first places to check.

## `src/ui/icons.py`

This file handles icons used by the interface.

Plain English:

This gives the app its small visual symbols like arrows and menu icons.

## `legacy/`

This folder contains older code from previous versions of the project.

Usually this means:

- experiments
- older workflows
- code kept for reference

If you are new to the project, focus on:

- `app.py`
- `src/core/`
- `src/ui/`
- `data/`

You usually do not need `legacy/` to run the app.

## How the full workflow fits together

Here is the app flow from start to finish:

1. `app.py` starts the desktop app.
2. `main_window.py` shows the interface.
3. The user opens an IFC file.
4. `ifc_importer.py` loads the IFC.
5. `extractor.py` extracts elements, materials, volumes, and areas.
6. The mapping table lets the user review material matching.
7. `carbon_calculator.py` applies the Cameroon LCA database.
8. The app calculates embodied carbon.
9. `chart_widgets.py` shows charts.
10. The final table and export tools let the user save the results.

## Common questions

## Where do I change material values?

Edit:

[`data/lca_database.csv`](data/lca_database.csv)

## Where do I change the research notes?

Edit:

[`data/cameroon_material_notes.md`](data/cameroon_material_notes.md)

## Where do I change the UI?

Mostly check:

- [`src/ui/main_window.py`](src/ui/main_window.py)
- [`src/ui/theme.py`](src/ui/theme.py)
- [`src/ui/widgets.py`](src/ui/widgets.py)

## Where do I change the calculation logic?

Check:

[`src/core/carbon_calculator.py`](src/core/carbon_calculator.py)

## Where do I change IFC extraction logic?

Check:

[`src/core/extractor.py`](src/core/extractor.py)

## Troubleshooting

## `python app.py` does not work

Check these:

- Python is installed
- you are inside the project folder
- the virtual environment is activated
- dependencies were installed with `pip install -r requirements.txt`

## `PySide6` or another module is missing

Run:

```powershell
pip install -r requirements.txt
```

## IFC file does not load

Possible reasons:

- the file path is wrong
- the file is not really an IFC file
- the IFC is damaged
- `ifcopenshell` cannot parse that file correctly

## Export does not work

Check these:

- you already ran the calculation
- you have permission to write to the selected folder
- `openpyxl` is installed for Excel export

## Quick start

If you want the shortest possible version:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Final note

This project is easier to understand if you think of it in four parts:

- `data` holds the material database
- `core` does the IFC reading and carbon math
- `ui` shows everything to the user
- `app.py` starts the whole program

That is the whole app in one sentence:

It opens an IFC, extracts building data, maps materials to the Cameroon database, calculates embodied carbon, and shows the result in a desktop interface.
