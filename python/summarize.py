from crawl4ai.chunking_strategy import *
from crawl4ai.extraction_strategy import *
from crawl4ai.crawler_strategy import *
from crawl4ai.web_crawler import WebCrawler
from crawl4ai import config
import yaml
import os
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
import json
from dotenv import load_dotenv
from hook import check_and_skip_ad

class NewsSentiment(BaseModel):
    tickers: List[str] = Field(..., description="List of ticker symbols for the main companies discussed in the news article, directly related to the sentiment.")
    title: str = Field(..., description="Title of the news article.")
    summary: str = Field(..., description="Summary of the news article, focusing on the main companies and their sentiment.")
    sentiment: float = Field(..., description="Overall sentiment score of the news for the main companies, ranging from -1 (very negative) to 1 (very positive).", ge=-1, le=1)

class Summarize:

    def __init__(self):
        load_dotenv()
        crawler_strategy = LocalSeleniumCrawlerStrategy(verbose=True)
        crawler_strategy.set_hook('after_get_url', check_and_skip_ad)
        self.crawler = WebCrawler(verbose=True, crawler_strategy=crawler_strategy)
        self.crawler.warmup()
        self.prompt = self.load_prompt()

    @staticmethod
    def load_prompt():
        base_dir = os.getenv('WORKSPACE_DIR', '/workspace')
        prompt_path = os.path.join(base_dir, 'python', 'instruction', 'summarize_prompt.yaml')
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r') as file:
                prompt_data = yaml.safe_load(file)
            return prompt_data.get('promptText', '')
        else:
            print(f"Warning: Prompt file not found at {prompt_path}")
            return ''

    def summarize(self, url: str):
        result = self.crawler.run(
            url=url,
            word_count_threshold=5,
            bypass_cache=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            extraction_strategy=LLMExtractionStrategy(
                provider="openai/gpt-4o-mini", api_token=os.getenv('OPENAI_API_KEY'),
                schema=NewsSentiment.schema(),
                extraction_type="schema",
                instruction=self.prompt, 
                apply_chunking=False))
        if result.extracted_content is None:
            print(f"Failed to extract content from {url}")
            return pd.DataFrame({
            'url': [url],
            'tickers': [None],
            'title': [None],
            'summary': [None],
            'sentiment': [None],
            'error': [True],
            'error_message': [result.error_message]
        })
        # Parse the JSON string into a Python dictionary
        data = json.loads(result.extracted_content)
        
        # Create a DataFrame with the parsed data
        df = pd.DataFrame(data)
        
        # Add the URL to the DataFrame
        df['url'] = url
        df['error_message'] = None
        
        return df

if __name__ == "__main__":
    summarizer = Summarize()
    # print("Loaded prompt:")
    # print(summarizer.prompt)

    # Test summarize() method
    test_url = "https://www.reuters.com/markets/us/amazon-workers-join-teamsters-unfair-labor-practices-strikes-us-2024-08-29/"
    print(f"\nTesting summarize() with URL: {test_url}")
    try:
        result_df = summarizer.summarize(test_url)
        print("\nSummarization result:")
        
        # Set display options
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        # Print the DataFrame
        print(result_df.to_string(index=False))
        
        # Reset display options to default (optional)
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')
        pd.reset_option('display.max_colwidth')
    except Exception as e:
        print(f"An error occurred during summarization: {str(e)}")