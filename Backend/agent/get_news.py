from uagents import Agent, Context
from model import AgentResponse, StockNameOrSymbolRequest
from service import get_news


NewsAgent = Agent(
    name="Get News By Using Stock Symbol",
    port=8002,
    seed="News Secret Pharase",
    endpoint=["http://127.0.0.1:8002/submit"],
)

@NewsAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'Search Agent Address is {NewsAgent.address}')


# Message handler for data requests sent to this agent
@NewsAgent.on_query(model=StockNameOrSymbolRequest, replies={AgentResponse})
async def fetch_news(ctx: Context, sender: str, msg: StockNameOrSymbolRequest):
    ctx.logger.info(f"Received message from {sender}, session: {ctx.session}")
    try:
        symbol = msg.name_or_symbol
        news = await get_news(symbol)
        ctx.logger.info(f"message from endpoint: {news}")
        await ctx.send(sender, AgentResponse(message=news, status="Success"))
    except Exception as ex:
        ctx.logger.warn(ex)
        await ctx.send(sender, AgentResponse(message=[str(ex)], status="Failed"))


if __name__ == "__main__":
    NewsAgent.run()
