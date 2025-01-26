# Business Status: SASU vs EURL

## 📄 Description

💼 Discover an application dedicated to comparing salaries and financial outcomes between two common French legal structures: SASU and EURL.

🤔 “Which legal structure will provide a better net salary?” This application helps answer this question by providing detailed simulations and graphical visualizations of net salaries, dividends, and overall financial impacts for both SASU and EURL.

Here's a tool that allows you to analyze and optimize your financial decisions based on various parameters like annual turnover, deductible expenses, and dividend distribution. It's ideal for entrepreneurs and business owners who need to make informed decisions about their company's legal structure.

🌐 Access the app and start your analysis now at [https://business-status.app](https://business-status-583ac98f38cb.herokuapp.com/).

![Image1](images/image1.2.png)

## Prerequisites
- Anaconda or Miniconda
- Docker (for Docker deployment)

## ⚒️ Installation

### Prerequisites
- Python 3.11
- Python libraries
    ```sh
    pip install -r requirements.txt
    ```

## 📝 Usage

### Running without Docker

1. **Clone the repository and navigate to the directory**
    ```bash
    git pull https://github.com/LudovicGardy/business_status
    cd business_status/app_folder
    ```

2. **Environment setup**
    - Create and/or activate the virtual environment:
        ```bash
        conda create -n myenv python=3.11
        conda activate myenv
        ```
        or
        ```bash
        source .venv/bin/activate
        ```

3. **Launch the Streamlit App**
    - Run the Streamlit application:
        ```bash
        streamlit run main.py
        ```

### Running with Docker

1. **Prepare Docker environment**
    - Ensure Docker is installed and running on your system.

2. **Navigate to project directory**
    - For multiple containers:
        ```bash
        cd [path-to-app-folder-containing-docker-compose.yml]
        ```
    - For a single container:
        ```bash
        cd [path-to-app-folder-containing-Dockerfile]
        ```

3. **Build the containers**
    - For multiple containers:
        ```bash
        docker-compose up --build
        ```
    - For a single container:
        ```bash
        docker build -t my-app-title .
        ```

4. **Run the containers**
    - For multiple containers:
        ```bash
        docker run -p 8501:8501 my-app-title
        ```

    - The application will be accessible at `http://localhost:8501`.

    - ⚠️ If you encounter issues with `pymssql`, adjust its version in `requirements.txt` or remove it before building the Docker image.

## 👤 Author
- LinkedIn: [Ludovic Gardy](https://www.linkedin.com/in/ludovic-gardy/)
- Website: [https://www.sotisanalytics.com](https://www.sotisanalytics.com)
