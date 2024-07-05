import asyncio
from .data_models import BaseModule
from .scraper_and_summarizer.summarizer import PegasusSummarizer


class FinancialNewsModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.summarizer = PegasusSummarizer()

    async def process(self, ticker):
        return self.summarizer.scrape_and_summarize_tickers()
    
    
if __name__ == '__main__':
    module = FinancialNewsModule()
    print(asyncio.run(module.process("ETH")))