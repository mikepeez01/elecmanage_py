# Energy Data Automation & Analysis Project

***

## Overview

This repository enables advanced automation, management, and analysis of Spanish electricity market data.  
All code, configuration, templates, outputs, and scripts are organized via a centralized `configs/config.yaml` file, supporting reproducible, parameter-driven workflows.

> **Base Path**  
> `/Users/mikelperez/0_Python_projects_v3_reduced/0_Python_projects_reduced/`  
> All directories and references are relative to this root.  
> Customize your installation by editing the `base_path` in `config.yaml`. Example:
>
> ```yaml
> base_path: "/Users/user1/elecmanage/"
> ```

***

## Features

- **Unified Path Configuration:** All source, template, script, output, and log paths are centrally managed via `config.yaml` using flexible placeholders (`{name}`, `{provider}`, `{customer_id}`, etc.).
- **Script-Based Automation:** All main projects and notebook workflows are activated by dedicated Python scripts. Each script orchestrates notebook execution using Papermill and records detailed logs.
- **Manual & Automated Notebook Handling:**  
  - All analysis, ETL, and reporting notebooks (except those in `notebooks/manual/`) are executed via their respective activating scripts.
  - Notebooks in `notebooks/manual/` and `notebooks/invoice_comp/1c_manual_extract_elec.ipynb` require manual execution, as they involve direct user interaction or manual compilation.
- **Multi-format Data Management:** Supports input/output with SFTP, Excel, Parquet, Pickle, CSV, PDF, and dynamic templates.
- **Extensible Architecture:** Add providers, outputs, or new notebook workflows by simply updating `config.yaml` and the relevant scripts.

***

## Project Structure

```text
configs/
│   ├── config.yaml
│   ├── templates/
│   ├── verification_project/
│   ├── load_compilation/
│   └── invoice_comp/
logs/
│   └── {log_name}.log
data/
│   ├── elec/
│   ├── raw/
│   ├── temp/
│   ├── processed/
│   ├── customers/
│   ├── regulation/
│   ├── invoice_comp/
│   ├── load_compilation/
│   ├── position_report/
│   ├── verification_project/
│   └── market_report/
notebooks/
│   ├── automated/
│   ├── manual/
│   ├── invoice_comp/
│   ├── load_compilation/
│   ├── markets/
│   └── verification_project/
outputs/
│   ├── markets/
│   ├── invoice_comp/
│   ├── load_compilation/
│   └── verification_project/
scripts/
│   ├── invoice_comp/
│   │    └── invoice_comp_exe.py
│   ├── markets/
│   │    └── markets_exe.py
│   ├── load_compilation/
│   │    └── load_compilation_exe.py
│   └── verification_project/
│        └── verification_project_exe.py
src/
│   ├── config/
│   ├── invoice_comp/
│   ├── load_compilation/
│   ├── shared/
│   ├── utils/
│   └── verification_project/
```

See `configs/config.yaml` for full directory and placeholder mapping.

***

## Installation & Setup

### 1. Clone Repository

Request your token first, then:

```bash
git clone https://github.com/mikepeez01/elecmanage_py.git
cd [elecmanage_py]
```

### 2. Create Anaconda Environment

```bash
conda create -n elec_env python=3.12
conda activate elec_env
```

### 3. Install Requirements

Install in standard or development mode:

```bash
pip install .
# For development:
pip install -e .
```

### 4. Create Configs for Each Project

Templates for required configs are in `configs/templates/`.  
Copy and adapt these templates to create your own configs.

**Template references:**
```yaml
configs:
  templates:
    verification_template: "configs/templates/verification_params_template.yaml"
    load_compilation_template: "configs/load_compilation/metering_provider_params_template.yaml"
    invoice_sftp_params: "configs/invoice_comp/invoice_sftp_params_template.yaml"
    market_params: "configs/markets/market_params_template.yaml"
```

**Required configs:**
```yaml
configs:
  markets:
    market_params: "configs/markets/market_params.yaml"
  verification_project:
    verification_params: "configs/verification_project/verification_params.yaml"
  load_compilation:
    provider_params: "configs/load_compilation/metering_provider_params.yaml"
  invoice_comp:
    sftp_params: "configs/invoice_comp/invoice_sftp_params.yaml"
```

***

### 5. Create Alias Excel File

Copy the template `data/customers/elec/alias_clientes_elec_template.xlsx`  
Edit and save as `data/customers/elec/alias_clientes_elec.xlsx`.  
Include all customer and supply point data; this is mandatory for running subprojects.

***

## Configuration

All source, output, and template paths are controlled in `configs/config.yaml`.  
Adjust as needed for your environment—see full keys and the directory tree example in the file.

Example:

```yaml
logs:
  exe: "logs/{log_name}.log"

outputs:
  markets:
    elec:
      graphs:
        html: "outputs/markets/elec/graphs/{name}.html"
        excel: "outputs/markets/elec/graphs/{name}.xlsx"
```

***

## Usage

### Automated Workflows

All main notebook pipelines (except manual notebooks) are triggered via activating scripts in the `scripts/` directory:

- `scripts/markets/markets_exe.py`
- `scripts/invoice_comp/invoice_comp_exe.py`
- `scripts/verification_project/verification_project_exe.py`
- `scripts/load_compilation/load_compilation_exe.py`

Each script loads paths and parameters from `config.yaml`, executes the required notebooks using Papermill, and produces output notebooks and logs in relevant folders.

**Example run:**

```bash
python scripts/verification_project/verification_project_exe.py
```

### Manual Notebooks

- Notebooks in `notebooks/manual/` must be opened and executed individually in Jupyter.
- Exception: `notebooks/invoice_comp/1c_manual_extract_elec.ipynb` (manual invoice compilation) is also executed manually due to required user interaction.

### Directory Tracking

Project structure uses `.gitkeep` to retain empty folders in version control. Example:

```gitignore
/data/load_compilation/elec/**
!/data/load_compilation/elec/**/.gitkeep
```

***

## Adding a New Customer or Supply Point

This guide walks you through extending the repository to include new customers or supply points, link contract data, and assign the right liquidation formulas for analytics.

### 1. Register Supply Point in `alias_clientes_elec.xlsx`
- Edit `data/customers/elec/alias_clientes_elec.xlsx`.
- Add a row for each supply point, following the template:

    | cliente       | alias        | cups           | tarifa | electrointensivo | contrato |
    |---------------|--------------|----------------|--------|------------------|----------|
    | ClienteNuevo  | Punto 1      | ES123456ABCD   | 6.1 TD | False            | 1        |

- **Fields:**
    - `cliente:` Customer/group name.
    - `alias:` Supply point name/description.
    - `cups:` Unique CUPS code.
    - `tarifa:` Tariff (e.g., 3.0 TD, 6.1 TD).
    - `electrointensivo:` True/False.
    - `contrato:` Contract group number.

### 2. Create Customer-Contract XLSM File(s)

- Path: `data/customers/elec/{customer_id}/datos_ELEC_{customer_id}_{contract_id}.xlsm`
- Example for “ClienteNuevo”, contract group 1:

    ```
    data/customers/elec/ClienteNuevo/datos_ELEC_ClienteNuevo_1.xlsm
    ```
- For each customer/contract group, create or adapt an XLSM containing contract periods, tariffs, and contract-specific parameters.

### 3. Assign Contract Indices
- In every XLSM, under the "Ficha Cliente" section, define all contracts, their terms/periods, and assign each a unique `contract_id`.
- The universal contract identifier format:
    ```
    {customer_id}_{contractgroup}_{contract_id}
    ```
- This is the key reference for mapping contract logic throughout the repo.

### 4. Map Contract Code to Liquidation Formula
- Open `src/shared/dicts.py` and locate the `contract_dict`.
- Add a mapping from the new contract identifier to an appropriate liquidation function in `liquidation.py`:
    ```python
    contract_dict = {
        "ClienteNuevo_1_1": Liquidation.total_1,
        "ClienteNuevo_1_2": Liquidation.naturgy_1,
        # etc.
    }
    ```
- Ensure that the chosen function matches the utility contract's calculation method.

### 5. Validate Everything Works
- Confirm supply points appear in your outputs after running the activation scripts.
- If errors arise:
    - Alias matches in the Excel and contract XLSM.
    - Universal contract code is present in `contract_dict`.
    - All required files are present and formatted correctly.

***

**Example: Workflow for New Customer "ClienteNuevo":**
1. Add row to `alias_clientes_elec.xlsx`:
    ```
    ClienteNuevo, Suministro1, ES123456ABCD, 6.1 TD, False, 1
    ```
2. Create `data/customers/elec/ClienteNuevo/datos_ELEC_ClienteNuevo_1.xlsm`.
3. Fill in contract details and indices (`contract_id`).
4. Add line to `contract_dict` in `dicts.py`:
    ```python
    "ClienteNuevo_1_1": Liquidation.repsol_1,
    ```
5. Run activating scripts, validate output.

***

### Tips

- Reuse templates from similar setups.
- Always document new liquidation logic clearly in `liquidation.py`.
- Create missing directories before placing new files.

***

### Summary Table

| Step | Action                                    | Location/Example                                  |
|------|-------------------------------------------|---------------------------------------------------|
| 1    | Add supply point to Excel                 | `alias_clientes_elec.xlsx`                        |
| 2    | Create XLSM for customer contract         | `datos_ELEC_{customer_id}_{contractgroup}.xlsm`   |
| 3    | Assign contract indices                   | Field/column `contract_id` in XLSM                |
| 4    | Map contract to formula                   | Update `contract_dict` in `dicts.py`              |
| 5    | Validate by activating script             | Run and check outputs                             |

***

**Note:**  
- Update contact/account information and GitHub URL before distribution.
- Dependencies managed via `setup.py`.
- Consider linking supplementary docs or thesis if permitted.

## Adding a New Metering Provider

This section explains how to integrate a new metering provider for load data into the repository. This process ensures automated, robust handling of new data sources.

***

### 1. Name the Provider and Create Its Directory

Decide a unique name for the provider (e.g., `iberdrola`, `repsol_h`, `seinon`).  
Create a dedicated folder for storing raw metering files:

```bash
mkdir -p data/load_compilation/elec/{provider}
```

*Replace `{provider}` with the actual provider name, e.g., `iberdrola`.*

***

### 2. Implement the Extraction Function

Navigate to `src/load_compilation/load.py`.  
Create a new function to read and preprocess data files from the provider. The function **must return a DataFrame** with the following columns:

- `datetime` (type: datetime, in local time)
- `cups` (supply point identifier)
- `resolution` (optional, values: "hourly" or "quarter-hourly")
- `load` (float, energy in kWh)

**Template Example:**

```python
def extract_{provider}(file_path):
    # Load file into DataFrame (use pd.read_csv, pd.read_excel, etc.)
    df = pd.read_csv(file_path, sep=';')

    # Parse and clean columns as needed
    df['datetime'] = pd.to_datetime(df['Fecha'])  # or adapt field name
    df['cups'] = df['CUPS']
    df['load'] = df['LOAD']  # adapt as necessary

    # Detect resolution
    if df['datetime'].dt.minute.nunique() == 1 and df['datetime'].dt.minute.unique()[0] == 0:
        df['resolution'] = 'hourly'
    elif set(df['datetime'].dt.minute.unique()).issubset({0, 15, 30, 45}):
        df['resolution'] = 'quarter-hourly'
    else:
        df['resolution'] = 'unknown'

    # Return required columns only
    df = df[['datetime', 'cups', 'resolution', 'load']]
    return df
```

- Adapt column names and formats to your provider's archive.
- Support both CSV/Excel and other formats as needed.

For more examples, see existing functions in `src/load_compilation/load.py` such as `extract_cepsa`, `extract_linkener`, and `extract_total`.

***

### 3. Register the Provider in the `provider_dict`

Edit `src/shared/dicts.py`:

- Import your extraction function.
- Add entry to `provider_dict` in the format:

```python
provider_dict = {
    # Other providers...
    "{provider}": (extract_{provider}, {}),
    # Example: "iberdrola": (extract_iberdrola, {}),
}
```

If you need to pass extra arguments (e.g., a dictionary for CUPS mapping), supply them as follows:

```python
"cepsa": (extract_cepsa, {"dict": cepsa_dict})
```

The provider name you define here **must match** the directory name you created earlier.

***

### 4. (Optional) Automate Data Retrieval via API/SFTP

If the provider supports API or SFTP retrieval:

- Add an entry for the provider in `configs/load_compilation/metering_provider_params.yaml`
    - Configure the credentials, endpoints, or folder structure needed for automated downloads.
- Create a notebook to handle the download:
    - Name: `notebooks/load_compilation/2_{provider}_compilation.ipynb`
    - Implement the code to connect to the provider, retrieve files, and save them to `data/load_compilation/elec/{provider}`.

This enables fully automated ingestion of metering files for the new provider.

***

## Workflow Summary Table

| Step | Action                                      | Example / Location                                      |
|------|---------------------------------------------|---------------------------------------------------------|
| 1    | Create provider folder                      | `data/load_compilation/elec/iberdrola`                  |
| 2    | Implement extraction function               | `src/load_compilation/load.py` (`extract_iberdrola`)    |
| 3    | Register provider in `provider_dict`        | `src/shared/dicts.py`                                   |
| 4\*  | Configure automated retrieval (if needed)   | `configs/load_compilation/metering_provider_params.yaml` |
| 4\*  | Create retrieval notebook                   | `notebooks/load_compilation/2_iberdrola_compilation.ipynb` |

*\* Steps 4 are optional if the provider supports direct API/SFTP/FTP data download.*

***

**Best Practices:**

- Reuse code from existing extractors for similar formats.
- Document any provider-specific quirks in your extractor function.
- Ensure file naming and CUPS mapping is robust—use helper arguments as needed.
- After implementing, run the load compilation workflow to verify integration.

***

## Documentation & Thesis

- Complete configuration and folder documentation are annexed in the thesis (Appendix X).
- Always use `configs/config.yaml` for canonical, updated reference.

***

## Contributing

This is a closed repository.  
For reviews or collaboration, contact the maintainer.  
See `CONTRIBUTING.md` for guidelines.

***

## Contact

For access, issues, or collaboration:  
**Mikel Pérez** ([mperezyarno@alumni.unav.es](mailto:mperezyarno@alumni.unav.es))

***