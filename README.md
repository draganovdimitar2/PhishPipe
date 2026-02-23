# 🎣 PhishPipe Airflow Project

_A data pipeline for ingesting, validating, and publishing public phishing data feeds._

**Technologies and Tools:**

[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-required-orange?logo=docker&logoColor=white)](https://www.docker.com/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white)](https://airflow.apache.org/)
---

## 📚 Table of Contents

- [🌊 Overview and Core Idea](#-overview-and-core-idea)
- [✨ Implemented Features](#-implemented-features)
- [🏗️ Project Structure](#-project-structure)
- [🚀 Development Setup (Local)](#-development-setup-local)
  - [🧰 Prerequisites](#-prerequisites)
  - [🔑 Generate Fernet Key](#-generate-fernet-key)
  - [📖 Setup .env](#-setup-env)
  - [🐍 Python Version Management (Important)](#-python-version-management-important)
  - [🧪 Virtual Environment](#-virtual-environment)
- [🚀 Quick Start](#-quick-start)
  - [🧐 Testing](#-testing)
- [🌟 DAG Details](#-dag-details)

---

## 🌊 Overview and Core Idea

**PhishPipe** is an Apache Airflow project that implements an end-to-end pipeline for ingesting, validating, and publishing a public phishing data feed.

The pipeline uses a custom PhishingGetterOperator to download a free phishing feed provided by Google, persist it locally, and save its content hash in Airflow's metadata DB. A scheduled DAG then verifies whether the newly downloaded hash differs from the previous processed hash. If changes are detected, the updated dataset is published to Amazon S3 using a configurable S3PublisherOperator.

The project is designed to run entirely in a Dockerized Airflow environment, enabling fast local development and testing. DAGs and custom operators are mounted as volumes, allowing changes to be tested immediately using the airflow test command without restarting the scheduler.

---

## ✨ Implemented Features

- **Automated Data Fetching**: Downloads a public phishing feed on a schedule using a custom Airflow operator.
- **Change Detection**: Verifies whether newly downloaded data differs from the previous run using hashes stored in Airflow metadata DB variables.
- **Custom Airflow Operators**: Implements reusable operators for data ingestion and validation.
- **Dockerized Airflow Environment**: Runs entirely in Docker using Docker Compose for easy setup and testing.
- **Clear Project Structure**: Organized to support extensibility and maintainability.

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
│   │   ├── change_verifier.py
│   │   └── s3_publisher.py
│   └── config.py
├── .python-version                                  
├── docker-compose.yaml     
├── Dockerfile    
├── README.md    
├── .env   
└── requirements.txt   
```

---

## 🚀 Development Setup (Local)

This project is designed for Apache Airflow 2.9.3, which requires Python 3.11.14.

To keep environments consistent, this repository uses pyenv and a project-local virtual environment.

### 🧰 Prerequisites

- **Python**: Version: 3.11.14 **required**
- **pyenv (recommended for Python version management)**
- **Docker**: Used for running Airflow

### 🔑 Generate Fernet Key
- 🔒 Apache Airflow uses a Fernet key to encrypt Variables and Connections stored in the metadata database.

- You must generate a Fernet key before starting the project.

- Run:
    ```bash
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```
- Example output:
    ```bash
    LQVB39qyWZVcAeNlF9vEswg-PF35jhwgqThCvhTOMy4=
    ```
- Copy the key and paste it like this `AIRFLOW__CORE__FERNET_KEY=your_fernet_key` into `.env` file

### 📖 Setup .env
The `.env` file contains AWS credentials and Fernet key, and the expected structure is as follows:
```bash
# AWS
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=your_aws_region
    
# Fernet Key (used by Airflow to encrypt/decrypt data in db)
AIRFLOW__CORE__FERNET_KEY=your_fernet_key
```
⚠️ You must create this file; otherwise, errors will occur immediately when you run the project.

### 🐍 Python Version Management (Important)
This repository includes a `.python-version` file that specifies the Python version used for this project:
```bash
3.11.14
```

If you have pyenv installed, entering the project directory will automatically switch Python to 3.11.14 (set as the local version).

If the version is not installed yet, run:
```bash
pyenv install 3.11.14
```

💡 This does not affect your global Python installation.

### 🧪 Virtual Environment
🐍 It is good practice to create a virtual environment (venv).
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
    - **For Windows (make sure you have python 3.11.14 installed)**:
        ```bash
        py -3.11 -m venv .venv
        .venv/Scripts/activate
        pip install -r requirements.txt
        ```

## 🚀 Quick Start
Make sure the .env is set up as described above. 
1.  **▶️ Start the project:**

    ```bash
    docker compose up --build
    ```
    
Airflow will:
- Wait for PostgreSQL
- Migrate metadata DB
- Create Admin user automatically
- Start Scheduler & Webserver

2. **➡️ Login:**

- 🌐 URL: `http://localhost:8080`
- 👤 Username: `admin`
- 🔑 Password: `admin`


### 🧪 Testing
Replace `<YYYY-MM-DD>` with current date.
- To test the downloader run:
   ```bash
   docker compose exec airflow-webserver airflow tasks test phishing_pipeline downloader <YYYY-MM-DD>
    ```
- To test the change_verifier run:
    ```bash
    docker compose exec airflow-webserver airflow tasks test phishing_pipeline change_verifier <YYYY-MM-DD>
    ```
- To test s3_publisher run:
    ```bash
    docker compose exec airflow-webserver airflow tasks test phishing_pipeline publisher <YYYY-MM-DD>
    ```
*🔄 Clear hash variables in the Airflow UI (Admin → Variables) if you want to fully reset the pipeline.*

## 🌟 DAG Details

- **DAG ID:** `phishing_pipeline`
- **Schedule:** @daily
- **Action:** Downloads a phishing feed CSV, compares current vs previous stored hashes, and uploads the current file to S3 only when a change is detected.
- **Source:** `http://svn.code.sf.net/p/aper/code/phishing_reply_addresses`
- **Output:** `s3://phishpipe-bucket/phishing/phishing_current.csv`

---