# 🎣 PhishPipe Airflow Project

[![Python](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/)  
[![Docker](https://img.shields.io/badge/docker-required-orange)](https://www.docker.com/)

---

## 🌊 Overview

**PhishPipe** is an Apache Airflow project designed to automate the process of downloading phishing feed data. It features a custom `PhishingGetterOperator` to handle the data retrieval and storage.

---

## ✨ Features

- **Automated Data Fetching**: Regularly downloads the latest phishing data feeds.
- **Custom Airflow Operator**: Includes a reusable `PhishingGetterOperator`.
- **Dockerized Environment**: Easy to set up and run with Docker and Docker Compose.
- **Clear Project Structure**: Organized for scalability and maintainability.

---

## 🏗️ Project Structure

The project follows a standard Airflow structure:

```
phishpipe-airflow/
├── dags/                 # Airflow DAG definitions
├── plugins/              # Custom Airflow operators
│   └── operators/        # PhishingGetterOperator
├── data/                 # Output directory for downloaded feeds
├── dockerfile            # Container configuration
└── requirements.txt      # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker**: Version 20.x or higher.
- **Docker Compose**: For easy container management.
- **Python**: Version 3.7+ (for local development).

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/draganovdimitar2/PhishPipe.git
    cd phishpipe-airflow
    ```

2.  **Set up a Python virtual environment (optional):**
    - **For MacOS**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        ```
    - **For Windows**
        ```bash
        py -m venv .venv
        .venv/Scripts/activate
        pip install -r requirements.txt
        ```

---

## 🏃‍♂️ Running PhishPipe

### Using Docker (Manual)

1.  **Build the Docker image:**

    ```bash
    docker build -t phishpipe-airflow .
    ```

2.  **Run the Airflow webserver:**
    - **For MacOS**
        ```bash
        docker run -d \
          --name phishpipe-airflow \
          -p 8080:8080 \
          -v $(pwd)/dags:/usr/local/airflow/dags \
          -v $(pwd)/plugins:/usr/local/airflow/plugins \
          -v $(pwd)/data:/opt/airflow/data \
          -e LOAD_EX=n \
          -e EXECUTOR=Sequential \
          phishpipe-airflow webserver
        ```
    - **For Windows**
        ```bash
        docker run -d \
          --name phishpipe-airflow \
          -p 8080:8080 \
          -v $(pwd)/dags:/usr/local/airflow/dags \
          -v $(pwd)/plugins:/usr/local/airflow/plugins \
          -v $(pwd)/data:/opt/airflow/data \
          -e LOAD_EX=n \
          -e EXECUTOR=Sequential \
          phishpipe-airflow webserver
        ```

3.  **Stop and remove the container:**

    ```bash
    docker stop phishpipe-airflow
    docker rm phishpipe-airflow
    ```

---

## DAG Details

- **DAG:** `phishing_pipeline`
- **Action:** Downloads a phishing feed CSV.
- **Source:** `http://svn.code.sf.net/p/aper/code/phishing_reply_addresses`
- **Output:** `/data/phishing_feed.csv`

---