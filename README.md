# 🎣 PhishPipe Airflow Project

[![Python](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/)  
[![Docker](https://img.shields.io/badge/docker-required-orange)](https://www.docker.com/)

---
# 🚧 Project Under Development 
>All features described below are currently under development.
---

## 🌊 Overview and core idea

**PhishPipe** is an Apache Airflow project designed to automate the process of downloading phishing feed data, checking for changes, and uploading it to an S3 bucket if changes are detected.

---

## ✨ Implemented Features

- **Automated Data Fetching**: Regularly downloads the latest phishing data feeds.
- **Custom Airflow Operators**: Includes reusable `PhishingGetterOperator` and `ChangeVerifier` operators.
- **Dockerized Environment**: Easy to set up and run with Docker and Docker Compose.
- **Clear Project Structure**: Organized for scalability and maintainability.

---

## 🏗️ Project Structure

The project follows a standard Airflow structure:

```text
.
├── dags/                 
│   └── phishing_pipeline.py   
├── data/  
├── plugins/              
│   ├── operators/        
│   │   ├── phishing_getter.py
│   │   └── change_verifier.py
│   └── config.py
├── .python-version                                  
├── docker-compose.yaml        
├── README.md    
└── requirements.txt   
```

---

## 🚀 Development Setup (Local)

This project is designed for Apache Airflow 1.10.15, which requires Python 3.7. Using newer Python versions (3.8+) may cause compatibility issues.

To keep environments consistent, this repository uses pyenv and a project-local virtual environment.

### 🧰 Prerequisites

- **Python**: Version: 3.7.16 **required**
- **pyenv (recommended for Python version management)**
- **Docker**: Used for running Airflow

### 🐍 Python Version Management (Important)
This repository includes a .python-version file which includes the version of python used for this project:

```bash
3.7.16
```

If you have pyenv installed, entering the project directory will automatically switch Python to 3.7.16 (Set as local).

If the version is not installed yet, run:
```bash
pyenv install 3.7.16
```

>💡 This does not affect your global Python installation.

### 🧪 Virtual Environment
It is good practice to create a virtual environment (venv).
1.  **Clone the repository:**

    ```bash
    git clone https://github.com/draganovdimitar2/PhishPipe.git
    cd PhishPipe
    ```

2.  **Set up a Python virtual environment (optional):**
    - **For MacOS**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        ```
    - **For Windows (make sure you have python 3.7.16 installed)**:
        ```bash
        py -3.7 -m venv .venv
        .venv/Scripts/activate
        pip install -r requirements.txt
        ```

---

## 🏃‍♂️ Running PhishPipe
⚠️ Prerequisite: Docker and Docker Compose are required.

### Using Docker Compose

1.  **Start the Airflow container:**

    ```bash
    docker-compose up -d
    ```

- The Airflow webserver will be available at: http://localhost:8080
- The SQLite database is stored within the container at `/usr/local/airflow/airflow.db`.

2. **Stop and remove containers:**

    ```bash
    docker-compose down 
    ```

---

## DAG Details

- **DAG:** `phishing_pipeline`
- **Action:** Downloads a phishing feed CSV and then checks if the data has changed since the last download.
- **Source:** `http://svn.code.sf.net/p/aper/code/phishing_reply_addresses`

---