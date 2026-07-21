# 🎣 PhishPipe Airflow Project

_A data pipeline for ingesting, validating, and publishing public phishing data feeds with Apache Spark processing._

**Technologies and Tools:**

[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Scala](https://img.shields.io/badge/Scala-2.12-red?logo=scala&logoColor=white)](https://www.scala-lang.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-017CEE?style=flat&logo=Apache%20Spark&logoColor=white)](https://spark.apache.org/)
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
  - [🧪 Testing](#-testing)
- [🌟 DAG Details](#-dag-details)

---

## 🌊 Overview and Core Idea

**PhishPipe** is an Apache Airflow project that implements an end-to-end pipeline for ingesting, validating, and publishing a public phishing data feed.

The pipeline uses a custom PhishingGetterOperator to download a free phishing feed provided by Google, persist it locally, and save its content hash in Airflow's metadata DB. A scheduled DAG then verifies if the feed has changed; if so, it processes the data using Apache Spark with Scala transformations and uploads the result to Amazon S3.

The project is designed to run entirely in a Dockerized Airflow environment, enabling fast local development and testing. DAGs and custom operators are mounted as volumes, allowing changes to be tested without rebuilding containers.

---

## ✨ Implemented Features

- **Automated Data Fetching**: Downloads a public phishing feed on a schedule using a custom Airflow operator.
- **Change Detection**: Verifies whether newly downloaded data differs from the previous run using hashes stored in Airflow metadata DB variables.
- **Spark-based Data Processing**: Leverages Apache Spark with Scala transformations for scalable data processing.
- **Custom Airflow Operators**: Implements reusable operators for data ingestion, validation, and publishing.
- **Dockerized Airflow Environment**: Runs entirely in Docker using Docker Compose for easy setup and testing.
- **S3 Integration**: Securely uploads processed data to Amazon S3.
- **Clear Project Structure**: Organized to support extensibility and maintainability.

---

## 🏗️ Project Structure

The project follows a modular architecture designed for scalability and maintainability:

```text
PhishPipe/
│
├── .github/workflows/                    # GitHub Actions CI/CD pipelines
│   └── ci/                               # Continuous Integration workflows
│
├── dags/                                 # Apache Airflow DAG definitions
│   └── phishing_pipeline.py              # Main orchestration DAG
│
├── plugins/                              # Custom Airflow operators and utilities
│   ├── operators/                        # Custom operators
│   │   ├── phishing_getter.py            # Data fetcher operator
│   │   ├── change_verifier.py            # Change detection operator
│   │   └── s3_publisher.py               # S3 upload operator
│   └── config.py                         # Configuration utilities
│
├── project/                              # Project configuration and build files
│   └── (Airflow and Spark configs)
│
├── src/main/scala/com/phishpipe/         # Apache Spark Scala codebase
│   └── processors/                       # Data processing logic
│
├── tests/                                # Test suite
│   └── test_operators/                   # Unit tests for custom operators
│
├── docker/                               # Docker configuration
│   ├── Dockerfile                        # Airflow container image
│   └── docker-compose.yaml               # Multi-container orchestration
│
├── .github/workflows                     # GitHub Actions workflows
├── .gitignore                            # Git ignore patterns
├── .python-version                       # Python version specification (pyenv)
├── .scalafmt.conf                        # Scala code formatter configuration
├── build.sbt                             # Scala/Spark project build configuration
├── Dockerfile                            # Main application Docker image
├── docker-compose.yaml                   # Docker Compose configuration
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
└── (other config files)
```

### Directory Descriptions:

- **dags/**: Contains all Apache Airflow DAG definitions
- **plugins/**: Custom Airflow operators and utilities for DAG tasks
- **src/main/scala/com/phishpipe/**: Apache Spark jobs written in Scala for advanced data processing
- **tests/**: Unit and integration tests for operators and processors
- **project/**: Build and project configuration files
- **.github/workflows/**: CI/CD pipelines for automated testing and deployment

---

## 🚀 Development Setup (Local)

This project is designed for Apache Airflow 2.9.3 (Python 3.11.14) with Apache Spark and Scala support.

To keep environments consistent, this repository uses pyenv and a project-local virtual environment.

### 🧰 Prerequisites

- **Python**: Version: 3.11.14 **required**
- **pyenv** (recommended for Python version management)
- **Docker**: Used for running Airflow and Spark
- **Scala**: 2.12+ (for Spark job development)
- **Apache Spark**: 3.x (containerized, no local installation needed)

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

# Spark Configuration (optional)
SPARK_MASTER=spark://spark-master:7077
SPARK_WORKER_MEMORY=2g
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
- Start Spark cluster (if configured)

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
- **Action:** Downloads a phishing feed CSV, compares current vs previous stored hashes using Spark transformations, and uploads the current file to S3 only when a change is detected.
- **Source:** `http://svn.code.sf.net/p/aper/code/phishing_reply_addresses`
- **Output:** `s3://phishpipe-bucket/phishing/phishing_current.csv`
- **Processing Engine:** Apache Spark with Scala transformations

---
