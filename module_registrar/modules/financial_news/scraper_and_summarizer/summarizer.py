from transformers import PegasusTokenizer, PegasusForConditionalGeneration
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json


class PegasusSummarizer:
    def __init__(
        self, model_name="human-centered-summarization/financial-summarization-pegasus"
    ):
        self.model_name = model_name or "human-centered-summarization/financial-summarization-pegasus"
        self.tokenizer = PegasusTokenizer.from_pretrained(self.model_name)
        self.model = PegasusForConditionalGeneration.from_pretrained(self.model_name)
        self.exclude_list = ["maps", "policies", "preferences", "accounts", "support", "setprefs"]
        self.save_dir = "news_data/"
        self.search_url = ""
        self.ticker_dict = {}
        self.article_dict = {}

    @property
    def monitored_tickers(self):
        return ["GME", "TSLA", "BTC", "ETH", "SOL", "COMAI", "wCOMAI", "TAO", "wTAO"]

    def set_search_url(self, ticker):
        self.search_url = f"https://www.google.com/search?q=yahoo+finance+{ticker}&tbm=nws"
        return self.search_url

    def get_url_data(self, url):
        request_data = requests.get(url)
        soup = BeautifulSoup(request_data.text, 'html.parser')
        paragraphs = soup.find_all('p')
        return self.process_data(paragraphs)

    def process_data(self, paragraphs):
        text = [paragraph.text for paragraph in paragraphs]
        words = " ".join(text).split(" ")[:300]
        return " ".join(words)

    def summarize(self, text, model, tokenizer):
        input_ids = tokenizer.encode(text, return_tensors="pt")
        output = model.generate(input_ids, max_length=55, num_beams=5, early_stopping=True)
        return tokenizer.decode(output[0], skip_special_tokens=True)

    def scrape_and_summarize(self, url, model, tokenizer):
        paragraphs = self.get_url_data(url)
        article = self.process_data(paragraphs)
        return self.summarize(article, model, tokenizer)

    def search_for_ticker(self, ticker):
        self.search_url = self.set_search_url(ticker)
        soup = BeautifulSoup(requests.get(self.search_url).text, 'html.parser')
        atags = soup.find_all('a')
        return [link["href"] for link in atags]

    def process_url_data(self, url_links):
        url_list = []
        for link in url_links:
            if all(exclude not in link for exclude in self.exclude_list) and "?q=" in link:
                url = link.split("?q=")[1]
                if url.startswith("http"):
                    url_list.append(url.split("&")[0])
        return url_list

    def get_ticker_urls(self, tickers=None):
        tickers = tickers or self.monitored_tickers
        self.ticker_dict = {}
        for ticker in tickers:
            search_result = self.search_for_ticker(ticker)
            urls = self.process_url_data(search_result)
            if ticker not in self.ticker_dict:
                self.ticker_dict[ticker] = {}
            self.ticker_dict[ticker]["urls"] = urls
        return self.ticker_dict

    def scrape_and_summarize_tickers(self, tickers=None):
        tickers = tickers or self.monitored_tickers
        self.ticker_dict = self.get_ticker_urls()
        not_searched = []
        for ticker, url_dict in self.ticker_dict.items():
            if ticker not in self.article_dict.keys():
                self.article_dict[ticker] = {}
            for urls in url_dict.values():
                for url in urls:
                    self.article_dict[ticker][url] = {"url": url}
                    if url.startswith("http"):
                        paragraph = self.get_url_data(url)
                        if paragraph.startswith("Thank you for your patience"):
                            continue
                        self.article_dict[ticker][url]["article"] = paragraph
                        summary = self.summarize(paragraph, self.model, self.tokenizer)
                        self.article_dict[ticker][url]["summary"] = summary
                    else:
                        not_searched.append(url)
        self.article_dict["not_searched"] = not_searched
        return self.article_dict   

    def save_articles(self, article_dict):
        article_dictionary = article_dict or self.article_dict
        timestamp = datetime.now().strftime("%Y%m%d")
        file_path = Path(f'{self.save_dir}{timestamp}.json')
        file_path.write_text(json.dumps(article_dictionary, indent=4), encoding='utf-8')

    def get_articles(self, date_ymd):
        save_path = Path(f"{self.save_dir}{date_ymd}.json")
        return save_path.read_text(encoding='utf-8')


if __name__ == "__main__":
    summarizer = PegasusSummarizer()
    article_dict = summarizer.scrape_and_summarize_ticker()
    print(article_dict)
    summarizer.save_articles(article_dict)