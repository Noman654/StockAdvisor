# Stock Analysis API with uAgents

Welcome to the Stock Analysis API project using uAgents! This project leverages uAgents to provide detailed stock information, news, and analysis based on fundamental and quarterly results.

![Stock Analysis](https://lucid.app/publicSegments/view/87d1b02c-5f8a-4729-921d-74da78a533af/image.png)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [uAgents Endpoints](#uagents-endpoints)
- [Running the Flask App](#running-the-flask-app)
- [Running the Streamlit App](#running-the-streamlit-app)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Search Stock Using [Google Finance](https://www.google.com/finance/?hl=en)**: Get detailed information about a specific stock.
- **Get Stock News By Scraping [Google Finance](https://www.google.com/finance/?hl=en)**: Retrieve 5 recent news related to a specific stock.
- **Get Stock Data From [Yahoo Finance](https://pypi.org/project/yfinance/)**: Get Fundamental data like **PE, EPS** and last 3 quarter result.
- **Analysis using [Gemini](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/overview)**: Perform analysis on a stock based on its fundamentals and quarterly results on Gemini 1.0 Pro.

## Installation 

### Backend and Agent

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your/repository.git
    cd StockAdvisor/Backend/agent
    ```

2. **Set up a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run all agents**:
    ```bash
    cd agents
    python get_stock.py 
    python get_news.py
    python get_analysis.py
    ```

5. **Run the Flask app**:
    ```bash
    cd ..
    python app.py
    ```

## Usage

1. **Ensure the backend is running**:
    ```bash
    python app.py
    ```

2. **Access the endpoints**:
    - **Get Stock Data**: `GET /api/stocks/<stock_name>`
    - **Perform Analysis**: `GET /api/analysis/<stock_symbol>`
    - **Perform Analysis**: `GET /api/news/<stock_symbol>`

## uAgents Endpoints

The uAgents handle specific types of requests related to stocks. Here are the main agents and their functionalities:

- **Stock Agent**: Retrieves stock data based on the stock name.
- **News Agent**: Provides news related to a stock symbol.
- **Analysis Agent**: Performs analysis based on stock fundamentals and quarterly results.


## Running the Streamlit App

To run the Streamlit frontend, follow these steps:

1. **Navigate to the repository root**:
    ```bash
    cd StockAdvisor/frontend
    ```

2. **Ensure the backend is running**:


5. **Run the Streamlit app**:
    ```bash
    streamlit run streamlit_app.py
    ```

6. **Access the Streamlit app**:
   Open your browser and go to `http://localhost:8501`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

