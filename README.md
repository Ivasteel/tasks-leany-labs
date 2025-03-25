# LeanyLabs Tasks

## Overview

This repository contains solutions to LeanyLabs tasks. It includes code implementations and a Dockerized environment for easy deployment.

## Getting Started

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

## Usage

Modify and extend the scripts inside the `src/` directory as needed.

## Docker Hub

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
