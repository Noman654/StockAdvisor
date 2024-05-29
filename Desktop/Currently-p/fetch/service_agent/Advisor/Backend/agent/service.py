import requests
from bs4 import BeautifulSoup
import re
import json
import yfinance as yf
import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession
from google.oauth2 import service_account


async def get_stocks_code(symbol: str):
    url = "https://www.google.com/finance/_/GoogleFinanceUi/data/batchexecute?source-path=%2Ffinance%2F&bl=boq_finance-ui_20240519.00_p0&hl=en-GB"

    payload = {'f.req': [f'[[["mKsvE","[\\"{symbol}\\",null,1,1]",null,"generic"]]]']}

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://www.google.com',
        'priority': 'u=1, i',
        'referer': 'https://www.google.com/',
        # Add your actual Google Finance cookie here (from browser inspection)
    }

    response = requests.post(url, headers=headers, data=payload)

    # Extract JSON Data
    # Find the string that starts with a square bracket, which usually is after a comment
    json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group(0)

    # Decode JSON
    data = json.loads(json_str)

    # Get news items from nested response
    stock_list = json.loads(data[0][2])

    stock_details_list = []
    for d in stock_list[0]:
        stock_details_list.append((d[3][2], d[3][-1]))

    return stock_details_list



async def get_news(quote:str) -> list:

    #  fetching  page from financial 
    url = f"https://www.google.com/finance/quote/{quote}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    #  convert page into readable format 
    soup = BeautifulSoup(response.content, "html.parser")

    #  reading news from page 
    news_section = soup.findAll(class_="yY3Lee")
    
    #  extracting needed information 
    data = []
    for news in news_section:
        temp_d = {}
        temp_d['news_source'] = news.find(class_='sfyJob').text
        temp_d['news_time'] = news.find(class_='Adak').text 
        temp_d['news_url'] = news.a.get('href')
        temp_d['news_text'] = news.find(class_="Yfwt5").text
        data.append(temp_d)
    
    return data



async def get_stocks_data(stock_code: str):
    stock = yf.Ticker(stock_code)
    fundamentals = stock.info  # Dictionary containing fundamental data

    # Example: Print the 'marketCap' (market capitalization)
    # print(f"Market Cap: {fundamentals['marketCap']}")
    mandotary_columns = ['longBusinessSummary', 'auditRisk', 'boardRisk', 'compensationRisk', 'shareHolderRightsRisk', 'overallRisk', 'governanceEpochDate', 'compensationAsOfEpochDate', 'maxAge', 'priceHint', 'previousClose', 'open', 'dayLow', 'dayHigh', 'regularMarketPreviousClose', 'regularMarketOpen', 'regularMarketDayLow', 'regularMarketDayHigh', 'dividendRate', 'dividendYield', 'exDividendDate', 'payoutRatio', 'fiveYearAvgDividendYield', 'beta', 'trailingPE', 'forwardPE', 'volume', 'regularMarketVolume', 'averageVolume', 'averageVolume10days', 'averageDailyVolume10Day', 'ask', 'marketCap', 'fiftyTwoWeekLow', 'fiftyTwoWeekHigh', 'priceToSalesTrailing12Months', 'fiftyDayAverage', 'twoHundredDayAverage', 'trailingAnnualDividendRate', 'trailingAnnualDividendYield', 'currency', 'enterpriseValue', 'profitMargins', 'floatShares', 'sharesOutstanding', 'heldPercentInsiders', 'heldPercentInstitutions', 'impliedSharesOutstanding', 'bookValue', 'priceToBook', 'lastFiscalYearEnd', 'nextFiscalYearEnd', 'mostRecentQuarter', 'earningsQuarterlyGrowth', 'netIncomeToCommon', 'trailingEps', 'forwardEps', 'lastSplitFactor', 'lastSplitDate', 'enterpriseToRevenue', 'enterpriseToEbitda', '52WeekChange', 'SandP52WeekChange', 'lastDividendValue', 'lastDividendDate', 'exchange', 'quoteType', 'symbol', 'underlyingSymbol', 'shortName', 'longName', 'firstTradeDateEpochUtc', 'timeZoneFullName', 'timeZoneShortName', 'uuid', 'messageBoardId', 'gmtOffSetMilliseconds', 'currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice', 'recommendationMean', 'recommendationKey', 'numberOfAnalystOpinions', 'totalCash', 'totalCashPerShare', 'ebitda', 'totalDebt', 'quickRatio', 'currentRatio', 'totalRevenue', 'debtToEquity', 'revenuePerShare', 'returnOnAssets', 'returnOnEquity', 'freeCashflow', 'operatingCashflow', 'earningsGrowth', 'revenueGrowth', 'grossMargins', 'ebitdaMargins', 'operatingMargins', 'financialCurrency', 'trailingPegRatio']

    fundamentals_data = {}
    for colum in mandotary_columns:
        fundamentals_data[colum] = fundamentals.get(colum)

    finacial_data = stock.quarterly_financials.iloc[:, :3].to_dict()
    
    return {'finacial_data':finacial_data, 'fundamentals_data':fundamentals_data}


async def get_chat_response(chat: ChatSession, prompt: str):
    response = chat.send_message(prompt)
    return response.text

async def generate_investment_suggestion(fundamental_data, quarterly_results_data, chat, news_titles):
    """
    Generates an investment suggestion based on fundamental and quarterly results data.

    Args:
        fundamental_data (dict): Dictionary containing fundamental data points.
        quarterly_results_data (dict): Dictionary containing quarterly results data.

    Returns:
        str: Investment suggestion.
    """

    prompt = f"""
    Analyze the following fundamental and quarterly results data for a stock:

    Fundamental Data:
    {fundamental_data}

    Quarterly Results:
    {quarterly_results_data}

    News Titles:
    {news_titles}

    For each news headline, describe its potential impact in one line, including the source, link, and timing.
    Provide a concise investment suggestion (Buy, Hold, Sell) and a brief justification based on the analysis of fundamental results and news and show the precentange and nummber if possible.

    This analysis should help in making an informed investment decision by considering both financial performance and recent market sentiment.

     """
     # or other appropriate model
    response = await get_chat_response(chat,
        prompt
    )

    return response


async def get_suggestion(stock_code, news):
    

    
    PROJECT_ID = 'intricate-grove-423611-i9'
    location = "us-central1"


    data_st = await get_stocks_data(stock_code.replace(':','.')[:-1])

    
# insert a credentials 
    data =  {
        "type": "",
        "project_id": "",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "",
        "client_x509_cert_url": "",
        "universe_domain": ""
    }

    credentials = service_account.Credentials.from_service_account_info(data)


    vertexai.init(project=PROJECT_ID, location=location, credentials=credentials)

    
    model = GenerativeModel("gemini-1.0-pro")
    chat = model.start_chat()
    # importlib.reload(sa)
    suggest = await generate_investment_suggestion(data_st['fundamentals_data'], data_st['finacial_data'],chat, news)
    print(suggest)
    # chat.close()
    return suggest

