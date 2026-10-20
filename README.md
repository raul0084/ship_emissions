# Ship Emissions Modeling Using AIS Data

A Python-based ship-emissions modeling and analysis tool developed from the work of two bachelor's theses at the *Departament de Dinàmica de la Terra i de l'Oceà, Universitat de Barcelona*.

The project brings together the modeling work from these theses into a unified software workflow for estimating ship emissions from vessel characteristics and port-call activity derived from Automatic Identification System (AIS) data. It combines data processing, emissions calculations, an interactive Streamlit application, and Quarto-based analytical reporting.

The goal is to make the modeling workflow more accessible, maintainable, and reusable for emissions analysis.

## Objectives

- Consolidate the modeling work developed through two bachelor's theses into a unified Python codebase.
- Organize the emissions calculations and data-processing logic into reusable modules.
- Provide an interactive interface for loading data, running simulations, and exploring results.
- Generate structured analytical reports covering emissions estimates, operating modes, data quality, and sensitivity analysis.
- Support reproducible execution through containerized application and reporting environments.
- Allow developers and analysts to extend or integrate the model into other Python workflows.

## Using the Project

The project provides two user-facing workflows: an interactive application for working with the model and a reporting workflow for producing structured analytical outputs.

### 1. Interactive Streamlit Application

The Streamlit application provides a graphical interface for users who want to work with the emissions model without directly modifying the code.

Users can:

- Explore the application's tools, documentation, and resources.
- Work with vessel and port-call data.
- Configure and run emissions simulations.
- Inspect results through the available interface and visualizations.
- Use the available data-handling and export functionality.

#### Running the application

The application runs in Docker. With Docker installed, execute the following command from the project root:

```bash
./run_streamlit.sh
```

The script builds the application image and starts the container, mounting the local `data/` directory so the application can access the relevant files.

Once the container starts, open:

[http://localhost:8501](http://localhost:8501)

To stop the application, press `Ctrl+C` in the terminal.

No `.env` file is required by the current Streamlit launch script.

### 2. Quarto Analytical Reports

The project includes a Quarto report for presenting emissions estimates in a structured, shareable document. The report covers emissions by pollutant and operating mode, together with data-quality and sensitivity analysis.

#### Building the report environment

Build the Docker image from the project root:

```bash
docker build -f Dockerfile -t emissiones-report .
```

#### Generating a report

Run the report-generation script:

```bash
./render_report.sh
```

The script accepts three optional arguments, in this order:

```bash
./render_report.sh OUTPUT_FILE VESSELS_CSV PORT_CALLS_CSV
```

For example:

```bash
./render_report.sh \
  ship_emissions_report.html \
  data/tests/vessels_2012.csv \
  data/tests/port_calls_2012.csv
```

The script supplies the report author and input-file parameters to Quarto. The generated report is intended to be stored under `reports/archive/`.

The input paths must point to files available within the project directory. Use suitable local datasets when the original data is confidential or cannot be distributed publicly.

## Building on the Project

The `core/` package contains the emissions model and data-processing functionality, separate from the Streamlit interface. This allows developers and analysts to reuse the underlying Python modules in scripts, notebooks, or other applications.

### Installation

Create and activate a Python environment, then install the project and its declared dependencies from the repository root:

```bash
pip install .
```

The dependencies are defined in `pyproject.toml`.

### Using the Python Modules

The core modules can be imported directly into Python code:

```python
from core import emissions
from core import data_handling
```

These imports expose the modules, allowing you to access their implemented functionality. The exact functions, parameters, and return values depend on the module interfaces.

A typical programmatic workflow consists of:

1. Loading vessel and port-call data.
2. Applying the relevant data-processing functions.
3. Running the emissions calculations with the required inputs and configuration.
4. Inspecting, processing, or exporting the resulting estimates.

Refer to the implementation in `core/` for the available functions and their expected inputs and outputs.

You can also run the Streamlit interface directly in your Python environment, without Docker:

```bash
streamlit run app/main.py
```

The Python modules can therefore be used independently of the graphical interface, making it possible to extend the model or incorporate its functionality into other analytical workflows.

## Project Structure

```text
emissiones/
├── app/
│   ├── components/          # Reusable interface components
│   ├── datasets/            # Datasets used by the application
│   ├── pages/               # Streamlit application pages
│   ├── styles/              # Application styling
│   └── main.py              # Streamlit entry point
├── core/                    # Emissions model and data processing
├── data/                    # Input data and configuration files
├── notebooks/               # Exploratory and analytical notebooks
├── reports/
│   ├── archive/             # Generated reports
│   ├── emissions_report.qmd # Quarto report source
│   ├── report_utils.py      # Reporting utilities
│   └── styles.css           # Report styling
├── Dockerfile               # Quarto reporting environment
├── Dockerfile.streamlit     # Streamlit application environment
├── render_report.sh         # Report-generation script
├── run_streamlit.sh         # Application launch script
├── pyproject.toml           # Package metadata and dependencies
└── README.md
```

## Technologies

- **Python** for model implementation and data processing
- **Pandas and NumPy** for tabular data and numerical operations
- **Streamlit** for the interactive application
- **Quarto** for analytical reporting
- **Docker** for containerized application and report environments
- **PostgreSQL** for data preparation in the original AIS workflow
- **MATLAB** as part of the project's research background, where relevant to the original thesis work

## Data and Reproducibility

The results depend on the supplied vessel and port-call records, the model configuration, and the assumptions used in the emissions calculations.

The repository separates application code from input data and provides containerized environments for the main application and reporting workflow. Before sharing or publishing the project, ensure that confidential datasets, credentials, and other restricted materials are excluded from the repository.

The project is intended as a reusable modeling and analysis workflow. The outputs should be interpreted in the context of the input-data quality and the assumptions underlying the model.