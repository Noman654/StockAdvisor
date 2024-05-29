from uagents import Agent, Context
from service import get_suggestion
from model import StockAnalysisRequest, AnalysisResponse





StockAnalysisAgent = Agent(
    name="Stock fundamental data",
    port=8003,
    seed="get the fundamental of stock data",
    endpoint=["http://127.0.0.1:8003/submit"],
)

@StockAnalysisAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'Search Agent Address is {StockAnalysisAgent.address}')

@StockAnalysisAgent.on_query(model=StockAnalysisRequest, replies={AnalysisResponse})
async def get_analysis(ctx: Context, sender: str, msg: StockAnalysisRequest):
    ctx.logger.info(f"Received message from {sender}, session: {ctx.session}")
    try:
        symbol = msg.yahoo_symbol
        news = msg.news
        message = await get_suggestion(symbol, news)
        # message = str(message)
        ctx.logger.info(f"message from endpoint: {message}")
        await ctx.send(sender, AnalysisResponse(analysis=message, status="Success"))
    except Exception as ex:
        ctx.logger.warn(ex)
        await ctx.send(sender, AnalysisResponse(analysis=str(ex), status="Failed"))

if __name__ == "__main__":
    StockAnalysisAgent.run()