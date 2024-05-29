from flask import Flask, jsonify , render_template # Import Flask and its necessary modules
from flask_cors import CORS 
import yfinance as yf
from uagents.query import query  # Import the query function from uagents
import json  # Import json for handling JSON data
from agent import model


# Initialize Flask application
app = Flask(__name__)
CORS(app) 

stock_agent_adress = 'agent1qdfw2xc4r87fhfflmc9rgex7h6qypq5zl9sfp9l3gxyv0v4rcw0ngqv4p7h'
news_agent_address = 'agent1qdzwujrdlncnf9u7sm2jqkn9nzc2puyhqe9kc6nmlqcnsfcxh08qgg47ddl'
stock_analysis_address = 'agent1qvfwzgnsefmyf3grhjmerlyvgd8gszuc8hnxn09htcwcw0vc6cz6j0k9y3k'



def get_stocks_data(stock_code: str):
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

async def get_stock_news(stock_symbol):
    try:
        response = await query(destination=news_agent_address, message=model.StockNameOrSymbolRequest(name_or_symbol=stock_symbol), timeout=20.0)
        data = json.loads(response.decode_payload())
        return data['message']
    except Exception as e:
        raise Exception(f"Error fetching news for {stock_symbol}: {str(e)}")
    

@app.route('/')
def home():
    return "Welcome to the Analysis API!"
    # return render_template('abc.html')

@app.route('/api/stocks/<string:stock_name>', methods=['GET'])
async def get_stock(stock_name):
    try:
        response = await query(destination=stock_agent_adress, message=model.StockNameOrSymbolRequest(name_or_symbol=stock_name), timeout=20.0)
        data = json.loads(response.decode_payload())
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'Error': e}), 401

@app.route('/api/analysis/<string:stock_symbol>', methods=['GET'])
async def get_news(stock_symbol: str):
    try:
        
        news = await get_stock_news(stock_symbol)
        # news = news['news']
        print(news)
        stock_symbol_yf = stock_symbol.replace(':', '.')[:-1]
        analysis = await query(destination=stock_analysis_address, message=model.StockAnalysisRequest(yahoo_symbol=stock_symbol_yf, news=news), timeout=50.0)
        analysis = json.loads(analysis.decode_payload())

        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'Error': e}), 401
    
@app.route('/api/news/<string:stock_symbol>', methods=['GET'])
async def get_stock_news_api(stock_symbol):
    try:
        news = await get_stock_news(stock_symbol)
        return jsonify({'news': news}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401


if __name__ == '__main__':
    app.run(debug=True)