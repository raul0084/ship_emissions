# Ship Emissions Modeling

Maritime transport is a significant source of atmospheric emissions, particularly around ports and densely trafficked coastal areas. Quantifying these emissions requires combining vessel movement information with environmental and operational parameters.

This project focuses on developing a more accessible and maintainable implementation of an existing ship-emissions modeling workflow.

The original model was implemented in MATLAB. The main objective was to reproduce and reorganize its functionality in Python while creating an interface that allows users to interact with the model without directly working with the underlying code.

## Project Structure

```text
project/
│
├── app/        # Streamlit application and UI components
├── core/       # Model calculations and core functionality
├── data/       # Input and processed data
│
├── pyproject.toml
└── README.md
```

### `app/`

Contains the Streamlit application and its UI components. This layer handles user interaction, model configuration, and displaying results.

### `core/`

Contains the main functionality of the project, including data processing and emissions calculations. This is the backend of the application and is independent from the Streamlit interface.

### `data/`

Contains the datasets used by the project, including raw and processed data.

## Data Processing

The original AIS data was provided as CSV files. The CSV files were imported into a **PostgreSQL database**, where the data was cleaned and prepared for use by the model.

The database workflow was used for tasks such as:

* Data cleaning and validation
* Filtering and organizing AIS records
* Handling timestamps and voyage information
* Preparing the data required by the emissions model

The resulting dataset is then used by the Python modeling workflow.

## Model

The project translates an existing MATLAB ship-emissions model into Python. The goal is to reproduce the original calculations while separating the model logic from the user interface.
While this data is for internal use only, the workflow for any user remains the same: upload CSV files with the port calls and vessel info, download generated and filtered reports.

The general workflow is:

```text
AIS CSV files
     ↓
Data cleaning & preparation
     ↓
Python emissions model
     ↓
Results
     ↓
Download reports
```

## Technologies

* **Python** — model implementation and data processing
* **PostgreSQL** — AIS data storage and cleaning
* **Streamlit** — interactive application
* **MATLAB** — original model implementation
* **Git/GitHub** — version control

## Installation & Running

Install the project dependencies using the `pyproject.toml` file:

```bash
pip install .
```

Then run the Streamlit application:

```bash
streamlit run app/main.py
```
