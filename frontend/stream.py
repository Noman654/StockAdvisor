

import streamlit as st
import requests
import matplotlib.pyplot as plt
import json

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


def get_stock_trends(symbol):
    # 1. Get Stock Information
    ticker_symbol = symbol.replace(':','.')[:-1]
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)  # Approximately 3 months

    df = yf.download(ticker_symbol, start=start_date, end=end_date)
    # 2. Calculate Important Signals
    # Smooth out the price changes to see overall trends
    df['ShortTermTrend'] = df['Close'].rolling(window=20).mean()
    df['LongTermTrend'] = df['Close'].rolling(window=50).mean()

    # Measure how quickly the price is changing
    df['PriceChangeSpeed'] = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0)).rolling(window=14).mean() / (-df['Close'].diff().where(df['Close'].diff() < 0, 0)).rolling(window=14).mean()))

    # 3. Figure Out When to Buy or Sell
    df['Action'] = 'Hold'  # Initially, we just hold the stock
    df.loc[df['ShortTermTrend'] > df['LongTermTrend'], 'Action'] = 'Buy'  # Buy when short-term trend is above long-term and price isn't changing too fast
    df.loc[df['ShortTermTrend'] < df['LongTermTrend'], 'Action'] = 'Sell' # Sell when short-term trend is below long-term and price isn't changing too fast

    # 4. Create a Picture of the Stock's Performance
    # This will be like a bar chart with extra details
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                        row_heights=[0.7, 0.3], specs=[[{"secondary_y": True}], [{}]])

    # 4.1 Show the Daily Stock Prices
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close'],
                                name='Daily Price'),
                row=1, col=1)

    # 4.2 Show the Trends on the Same Chart
    fig.add_trace(go.Scatter(x=df.index, y=df['ShortTermTrend'], mode='lines', name='Short-Term Trend', line=dict(color='orange')), 
                row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['LongTermTrend'], mode='lines', name='Long-Term Trend', line=dict(color='purple')), 
                row=1, col=1)

    # 4.3 Show When to Buy or Sell
    buy_signals = df.loc[df['Action'] == 'Buy']
    sell_signals = df.loc[df['Action'] == 'Sell']
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', name='Buy', 
                            marker=dict(symbol='triangle-up', size=10, color='green')),
                row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', name='Sell',
                            marker=dict(symbol='triangle-down', size=10, color='red')),
                row=1, col=1, secondary_y=False)

    # 4.4 Show How Quickly the Price is Changing
    fig.add_trace(go.Scatter(x=df.index, y=df['PriceChangeSpeed'], mode='lines', name='Price Change Speed'), 
                row=2, col=1)

    # 4.5 Show if Price Change is Too Fast or Too Slow
    fig.add_hline(y=70, line_width=1, line_dash="dash", line_color="red", row=2, col=1)  
    fig.add_hline(y=30, line_width=1, line_dash="dash", line_color="green", row=2, col=1) 

    stockname = ticker_symbol.split('.')[0]
    # 5. Finalize and Show the Chart
    fig.update_layout(
        title=f"{stockname} - Stock Analysis",
        yaxis_title='Price (INR)',
        yaxis2_title='Price Change Speed',
        showlegend=True,
        xaxis_rangeslider_visible=False  
    )
    return fig
    # fig.show()


# Function to call the API for stock information
def get_stock_info(symbol):
    api_url = f"https://api.example.com/stocks/{symbol}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data from API")
        return None

# Function to fetch list of stocks from an API based on user input
def fetch_stock_list(search_query):
    api_url = f"http://127.0.0.1:5000/api/stocks/{search_query}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return [{"name": entry[0], "symbol": entry[1]} for entry in data["message"]]
    else:
        st.error("Error fetching stock list from API")
        return []

def get_stock_analysis(symbol):
    api_url = f"http://127.0.0.1:5000/api/analysis/{symbol}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching stock analysis from API")
        return None

def get_stock_news(symbol):
    api_url = f"http://127.0.0.1:5000/api/news/{symbol}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching stock news from API")
        return []

# Main Streamlit app





st.set_page_config(page_title="Stock Information", page_icon=":chart_with_upwards_trend:")
st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50; 
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: #3e8e41; 
    }
    </style>
""", unsafe_allow_html=True)  

# --- Main App ---
def main():
    st.title("Stock Search and Information")
    search_query = st.text_input("Search for a stock")

     # Initialize session state variables for persistence
    if "analysis_data" not in st.session_state:
        st.session_state.analysis_data = None
    if "news_data" not in st.session_state:
        st.session_state.news_data = None
    if "trend_data" not in st.session_state:
        st.session_state.trend_data = None

    if search_query:
        search_results = fetch_stock_list(search_query)

        if search_results:
            # User-Friendly Stock Selection
            selected_stock = st.selectbox(
                "Select a stock",
                search_results,
                format_func=lambda stock: f"{stock['name']} ({stock['symbol']})"
            )
            st.markdown("---")
            st.subheader(f"Information for {selected_stock['name']}")
            
            # Tabbed Interface for Analysis, News, and Trend
            tab1, tab2, tab3 = st.tabs(["Analysis", "Recent News", "Trend"])

            with tab1:
                if st.button("Show Analysis", key="analysis_btn"):
                    with st.spinner("Fetching analysis..."):
                        # stock_analysis = get_stock_analysis(selected_stock['symbol'])
                        st.session_state.analysis_data = get_stock_analysis(selected_stock["symbol"])
                    if st.session_state.analysis_data:
                        st.markdown(st.session_state.analysis_data["analysis"])
                        # if stock_analysis:
                        #     st.markdown(stock_analysis['analysis'])

            with tab2:
                if st.button("Show Recent News", key="news_btn"):
                    with st.spinner("Fetching news..."):
                        stock_news = get_stock_news(selected_stock['symbol'])
                        if stock_news:
                            for news_item in stock_news['news']:
                                st.markdown(f"**Source:** {news_item['news_source']}  \n**Time:** {news_item['news_time']}  \n**Link:** [{news_item['news_text']}]({news_item['news_url']})")
                                st.markdown("---")

            with tab3:  # Trend Tab
                if st.button("Show Trend", key="trend_btn"):
                    with st.spinner("Fetching trend data..."):
                        trend_fig = get_stock_trends(selected_stock['symbol'])
                        # trend_fig.show()    
                        if trend_fig:
                            # st.pyplot(trend_fig)
                            st.plotly_chart(trend_fig, use_container_width=True)  

        else:
            st.warning("No stocks found. Please refine your search.")
if __name__ == "__main__":
    main()
