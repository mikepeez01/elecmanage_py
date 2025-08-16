***

# Energy Data Automation & Analysis Project

***

## Overview

This repository contains code, configuration, and notebook pipelines for advanced automation, management, and analysis of Spanish electrical market data and processes.  
All directory structure, templates, and outputs are organized and referenced via a centralized `config.yaml` file.

> **Base Path:**  
> `/Users/mikelperez/0_Python_projects_v3_reduced/0_Python_projects_reduced/`  
> All routes in this project are relative to this root directory.

***

## Access

**This repository is private.**  
To access the code, you must request a personal access token from the maintainer.

> To request access, contact **Mikel Pérez** at [mperezyarno@alumni.unav.es](mailto:mperezyarno@alumni.unav.es).

***

## Features

- **Reusable Path Configuration:** All folders and files defined in `config.yaml`.
- **Automated Jupyter Notebooks:** Orchestrate notebook pipelines using Papermill, with input and output paths centrally managed.
- **Structured Outputs:** Automated and manual report and data exports.
- **Flexible Data Sources:** SFTP, Excel, Parquet, Pickle, CSV, and dynamic template support.
- **Extensible:** Easily add providers, outputs, and notebook workflows.

***

## Project Structure


Directory tree (partial)

```
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
```


See the full structure and dynamic placeholders (`{name}`, `{provider}`, etc.) in `configs/config.yaml`.

***

## Installation & Setup

### 1. Clone Repository

Request your personal access token and use:

```bash
git clone https://@github.com/[your-username]/[your-repo].git
cd [your-repo]
```

### 2. Create Anaconda Environment

```bash
conda create -n elec_env python=3.10
conda activate elec_env
```

### 3. Install Requirements

All main requirements are managed via the `setup.py` file:

```bash
pip install .
```

Or, for development:
```bash
pip install -e .
```

***

## Configuration

All source, output, and template paths are set in `configs/config.yaml`, with dynamic placeholders for flexible data use.  
Edit this file to customize paths for your instance.

**Example:**
```yaml
outputs:
  markets:
    elec:
      graphs:
        html: "outputs/markets/elec/graphs/{name}.html"
        excel: "outputs/markets/elec/graphs/{name}.xlsx"
```

***

## Usage

### Running Notebooks

You can execute analysis, ETL, or reporting notebooks with Papermill (for automation) or interactively:

```bash
papermill notebooks/markets/2a_elec_Markets.ipynb outputs/markets/notebooks/elec/2a_elec_Markets_out.ipynb -p param_name value
```

### Directory Tracking & Git Ignore

To keep necessary subfolders tracked (even if empty), `.gitkeep` files are used. See the `.gitignore` pattern:

```gitignore
/data/load_compilation/elec/**
!/data/load_compilation/elec/**/.gitkeep
```

***

## Documentation & Thesis

- Complete directory and path configuration is annexed in the thesis (Appendix X).
- For canonical and updated path/config, refer to [`configs/config.yaml`](./configs/config.yaml).
- All dynamic placeholders (`{}` brackets) are explained in the thesis and config documentation.

***

## Contributing

This is a closed repository. For collaboration and code review, contact the primary maintainer.  
Contribution guidelines are in `CONTRIBUTING.md`.

***

## License

This project is under MIT License (see `LICENSE` file).

***

## Contact

For repository access, issues, or project collaboration, contact:  
**Mikel Pérez** ([mikelperez@yourdomain.com](mailto:mikelperez@yourdomain.com))

***

**Note:**  
- Update or provide your actual email and GitHub URL before distribution.  
- All dependency management is handled in `setup.py` for simplicity and full control.  
- Consider linking your thesis directly if allowed.

***

*Copy and adapt the above Markdown to your repo as needed.*

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/56415052/ee2f58d5-43fd-4408-9d18-d214a5d85d16/config.yaml