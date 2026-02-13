# 🎣 PhishPipe Airflow Project

[![Python](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/) [![Docker](https://img.shields.io/badge/docker-required-orange)](https://www.docker.com/) [![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white)](https://airflow.apache.org/)

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

This project is designed for Apache Airflow 1.10.15, which requires Python 3.7. Using newer Python versions (3.8+) will cause compatibility issues.

To keep environments consistent, this repository uses pyenv and a project-local virtual environment.

### 🧰 Prerequisites

- **Python**: Version: 3.7.16 **required**
- **pyenv (recommended for Python version management)**
- **Docker**: Used for running Airflow

### 🔑 Generate Fernet Key
- Apache Airflow uses a Fernet key to encrypt Variables and Connections stored in the metadata database.

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
You must create this file; otherwise, errors will occur immediately when you run the project.

### 🐍 Python Version Management (Important)
This repository includes a `.python-version` file that specifies the Python version used for this project:
```bash
3.7.16
```

If you have pyenv installed, entering the project directory will automatically switch Python to 3.7.16 (set as the local version).

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

### 🧐 Testing
1.  **Start the Airflow container:**

    ```bash
    docker-compose up -d
    ```
    
2. **Run these commands in the terminal in the project root:**
    ```bash
    docker exec -it phishpipe-airflow bash -c "\
    airflow test phishing_pipeline downloader 2026-02-05 && \
    airflow test phishing_pipeline change_verifier 2026-02-05 && \
    airflow test phishing_pipeline publisher 2026-02-05"
   ```
3. **Check the logs in terminal.**

- **Note** that if you use the same data twice, you won’t see any changes in the S3 bucket, even if you delete the object from it.
  This is because the pipeline stores hash baselines in Airflow metadata DB variables (`phishing_current_hash` and `phishing_previous_hash`).
  If you want to test from scratch, clear these variables from Airflow UI (**Admin → Variables**) or via CLI inside the container.
---


## 🏃‍♂️ Running PhishPipe
⚠️ Prerequisite: Docker and Docker Compose are required + .env with AWS credentials and Fernet key.

### Using Docker Compose
The project uses a custom Docker image that extends `puckel/docker-airflow:1.10.9` to include additional dependencies (`boto3` for S3 integration).  
The image is built automatically by Docker Compose and requires .env file with AWS credentials.
1. **Generate Fernet Key**
- Apache Airflow uses a Fernet key to encrypt Variables and Connections stored in the metadata database.
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

2. **Setup .env**
   - The expected structure of `.env` is as follows:
   ```bash
    # AWS
    AWS_ACCESS_KEY_ID=your_aws_access_key_id
    AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
    AWS_DEFAULT_REGION=your_aws_region
    
    # Fernet Key (used by Airflow to encrypt/decrypt data in db)
    AIRFLOW__CORE__FERNET_KEY=your_fernet_key
    ```

3. **Start the Airflow container:**

    ```bash
    docker-compose up -d
    ```

   - The Airflow webserver will be available at: http://localhost:8080
   - The SQLite database is stored within the container at `/usr/local/airflow/airflow.db`.
    
    >    💡 On the first run, Docker Compose will build the custom Airflow image before starting the containers.


4. **Stop and remove containers:**

    ```bash
    docker-compose down 
    ```

---

## DAG Details

- **DAG:** `phishing_pipeline`
- **Action:** Downloads a phishing feed CSV, compares current vs previous stored hashes, and uploads the current file to S3 only when a change is detected.
- **Source:** `http://svn.code.sf.net/p/aper/code/phishing_reply_addresses`
- **Output:** `s3://phishpipe-bucket/phishing/phishing_current.csv`

---