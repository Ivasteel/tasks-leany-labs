# 🏗️ LeanyLabs Tasks

This repository contains a collection of tasks related to JSON handling and entity processing.  
It includes Python scripts and SQL queries designed for various use cases in data analysis and automation.

## 📑 Table of Contents

- [📌 Overview](#📌-overview)
- [📁 Repository Structure](#📁-repository-structure)
- [🚀 Getting Started](#🚀-getting-started)
   - [🔹 Prerequisites](#🔹-prerequisites)
   - [🛠️ Installation](#🛠️-installation)
- [🐳 Docker Usage](#🐳-docker-usage)
- [👤 Author](#👤-author)
- [📜 License](#📜-license)

---

## 📌 Overview

This repository contains various tasks related to JSON handling and entity processing. 
The solutions use Python and SQL to process JSON data efficiently.

---

## 📁 Repository Structure

The repository is structured as follows:

```bash
tasks-leany-labs/
│
├── Docs/
│   ├── SQL-BigQuery-Task1-Vasyl-Ivchyk.pdf       # Documentation for Task 1 in GCP BigQuery
│   ├── Python-Postgres-Task1-4-Vasyl-Ivchyk.pdf  # Documentation for all tasks in Python/PosgreSQL
├── employees.json                                # Initial JSON
├── env.txt                                       # Credentials for Render's PostgreSQL, should be renamed to .env
├── validate_json.py                              # Run the SCD2 logic of merging new data to JSON file / PostgreSQL 
├── Dockerfile                                    # Used to containerize the project
├── requirements.txt                              # Python dependencies (if needed)
├── README.md                                     # Documentation
└── .gitignore                                    # Ignore unnecessary files
```

### Prerequisites

Ensure you have the following installed:
- Docker
- Python 3.x

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Ivasteel/tasks-leany-labs.git
   cd tasks-leany-labs
   ```

2. Build the Docker image:
   ```sh
   docker build -t ivasteel/leanylabs .
   ```

3. Run the container:
   ```sh
   docker run --rm -it ivasteel/leanylabs
   ```


## Docker Usage

The Docker image for this project is available on Docker Hub:
[ivasteel/leanylabs](https://hub.docker.com/repository/docker/ivasteel/leanylabs/general)

To pull the latest image:
```sh
   docker pull ivasteel/leanylabs:latest
```

## Contributing

Contributions are welcome! Feel free to fork this repository and submit a pull request.

---

## 📌 Author

* Vasyl Ivchyk – Lead Data Engineer & AI Enthusiast
* 💼 LinkedIn: [Vasyl Ivchyk](https://www.linkedin.com/in/vasyl-ivchyk-1a0b1358/)
* 📧 Email: [ivasteel@gmail.com]()

## 📜 License

This project is **MIT Licensed** – feel free to use and modify it! :)
