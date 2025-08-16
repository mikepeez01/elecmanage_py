from setuptools import setup, find_packages

setup(
    name='Celtica Reduced',
    version='0.1.1',
    description='Celtica on Python',
    author='Mikel Perez',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # Core Data Science & Analysis
        "pandas",
        "numpy", 
        "matplotlib",
        "plotly",
        "statsmodels",
        "pmdarima",
        "pyarrow",
        "fastparquet",
        "sqlalchemy",

        # Web Scraping & HTTP
        "requests",
        "beautifulsoup4",
        "selenium",
        "lxml",
        "paramiko"
        
        # Document Processing
        "openpyxl",
        "pdfplumber", 
        "pypandoc",
        "xlrd",
        
        # Jupyter Environment
        "jupyter",
        "jupyterlab",
        "ipython",
        "jupyter-contrib-nbextensions",
        "papermill",
        
        # AI/LLM Integration
        "openai",
        "langchain-core",
        "langchain-openai", 
        "langsmith",
        
        # Utilities
        "click",
        "tqdm",
        "pyyaml",
        "colorlog",
        "xlwings"
    ],
    python_requires='>=3.12.4'
)
