from uagents import Agent, Context
from service import get_stocks_code
from model import AgentResponse, StockNameOrSymbolRequest


# Method that sends the request to the endpoint which retrieves stock price for the specific share symbol
StockAgent = Agent(
    name="Stock code",
    port=8001,
    seed="Ingredeint Agent secret phrase",
    endpoint=["http://127.0.0.1:8001/submit"],
)

@StockAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'Search Agent Address is {StockAgent.address}')


# Message handler for data requests sent to this agent
@StockAgent.on_query(model=StockNameOrSymbolRequest, replies={AgentResponse})
async def get_stocks_quote(ctx: Context, sender: str, msg: StockNameOrSymbolRequest):
    ctx.logger.info(f"Received message from {sender}, session: {ctx.session}")
    try:
        symbol = msg.name_or_symbol
        message = await get_stocks_code(symbol)
        # message = str(message)
        ctx.logger.info(f"message from endpoint: {message}")
        await ctx.send(sender, AgentResponse(message=message, status="Success"))
    except Exception as ex:
        ctx.logger.warn(ex)
        await ctx.send(sender, AgentResponse(message=str(ex), status="Failed"))


if __name__ == "__main__":
    StockAgent.run()
