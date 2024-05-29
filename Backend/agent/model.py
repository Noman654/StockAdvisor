from uagents import  Model

class AgentResponse(Model):
    message:list
    status:str

class AnalysisResponse(Model):
    analysis:str
    status:str


class StockNameOrSymbolRequest(Model):
    name_or_symbol: str

class StockAnalysisRequest(Model):
    yahoo_symbol: str
    news: list
    
