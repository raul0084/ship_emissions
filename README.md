# Ship Emissions Modeling Using AIS Data

A Python-based ship-emissions modeling and analysis tool developed from the work of two bachelor's theses at the *Departament de Dinàmica de la Terra i de l'Oceà, Universitat de Barcelona*.

The project brings together research and modeling work into a maintainable software workflow for estimating ship emissions from vessel characteristics and port-call activity derived from Automatic Identification System (AIS) data. It combines data processing, emissions calculations, an interactive Streamlit application, and analytical reporting to make the model more accessible and facilitate the exploration of results.

## Objectives

- Consolidate the modeling work developed through two bachelor's theses into a unified Python codebase.
- Structure the model and data-processing logic into reusable components.
- Provide an interactive interface for configuring inputs, running simulations, and exploring results.
- Generate analytical reports presenting emissions estimates, data quality, and sensitivity analysis.
- Support a more reproducible and accessible workflow through containerized application and reporting environments.

## Using the Project

The project offers two ways to work with the emissions model: an interactive Streamlit application and a Quarto-based reporting workflow.

### 1. Interactive Application

The Streamlit application provides a graphical interface for users who want to work with the model without directly modifying the code.

Users can:

- Navigate the application to explore the available tools and resources.
- Load and inspect vessel and port-call data.
- Configure and run emissions simulations.
- Review results and use the available reporting and export functionality.

To launch the application with Docker, configure a local `.env` file using `.env.example` as a reference, then run the following command from the project root:

```bash
./run_streamlit.sh
```

The application will be available at [http://localhost:8501](http://localhost:8501).

### 2. Analytical Reports

The project includes a Quarto report for presenting emissions estimates and supporting analysis in a structured document. The report covers emissions by pollutant and operating mode, together with data-quality and sensitivity analysis.

First, build the report's Docker image:

```bash
docker build -f Dockerfile -t emissiones-report .
```

Then generate the report:

```bash
./render_report.sh
```

The script accepts an output filename and paths to the vessel and port-call CSV files:

```bash
./render_report.sh OUTPUT_FILE VESSELS_CSV PORT_CALLS_CSV
```

This workflow is useful when the results need to be reviewed or shared as a standalone analytical report.

## Building on the Project

The `core/` package contains the model and data-processing functionality, separated from the Streamlit interface. This separation allows developers and analysts to reuse the underlying Python modules in scripts, notebooks, or other applications.

### Installation

Install the project and its declared dependencies in a Python environment:

```bash
pip install .
```

### Using the Python Modules

The core modules can be imported directly into Python code:

```python
from core import emissions
from core import data_handling
```

These imports expose the modules, not necessarily every function within them. The specific functions, arguments, and return values depend on their implementation.

A typical programmatic workflow consists of:

1. Loading and preparing vessel and port-call data.
2. Applying the relevant data-processing functions.
3. Running the emissions calculations with the required inputs and configuration.
4. Inspecting, processing, or exporting the resulting estimates.

For the available functions and their expected inputs and outputs, refer to the implementation in `core/`.

Developers can also launch the Streamlit application directly, without Docker:

```bash
streamlit run app/main.py
```

The project can therefore serve both as an application for interactive emissions analysis and as a Python codebase that can be extended or integrated into other analytical workflows.