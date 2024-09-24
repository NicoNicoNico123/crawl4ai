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
    tickers: List[str] = Field(..., description="List of ticker symbols for the main companies discussed in the news article.")
    success: bool = Field(..., description="Indicates whether the article or content was available and successfully retrieved")
    title: str = Field(..., description="Title of the news article.")
    author: str = Field(..., description="Author of the news article.")
    summary: str = Field(..., description="Summary of the news article, focusing on the main companies.")
    category: str = Field(..., description="Category of the news article, such as 'Corporate and Financial News', 'Industry and Market Trends', 'Product and Innovation', 'Regulatory and Legal Developments', or 'Expert Analysis and Commentary'.")



class Summarize:

    def __init__(self, provider=None, api_token=None, api_base=None):
        load_dotenv()
        crawler_strategy = LocalSeleniumCrawlerStrategy(verbose=True)
        crawler_strategy.set_hook('after_get_url', check_and_skip_ad)
        self.crawler = WebCrawler(verbose=True, crawler_strategy=crawler_strategy)
        self.crawler.warmup()
        self.prompt = self.load_prompt()
        self.provider = provider
        self.api_token = api_token
        self.api_base = api_base

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

    def summarize(self, url: str, provider: str = "groq/llama-3.1-70b-versatile",api_token: str = os.getenv('GROQ_API_KEY')):
        result = self.crawler.run(
            url=url,
            word_count_threshold=5,
            bypass_cache=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
            extraction_strategy=LLMExtractionStrategy(
                provider=provider,
                api_token  =api_token,
                schema=NewsSentiment.schema(),
                extraction_type="schema",
                instruction=self.prompt, 
                apply_chunking=False))
        if result.extracted_content is None:
            print(f"Failed to extract content from {url}")
            return pd.DataFrame({
                'success': [False],
                'url': [url],
                'tickers': [[]],  # Use an empty list instead of None
                'title': [''],    # Use an empty string instead of None
                'summary': [''],  # Use an empty string instead of None
                'category': [''],  # Use an empty string instead of None
                'error': [True],
                'error_message': [result.error_message or '']  # Use an empty string if error_message is None
            })
        # Parse the JSON string into a Python dictionary
        data = json.loads(result.extracted_content)
        print(data)
        # Create a DataFrame with the parsed data
        df = pd.DataFrame(data)
        
        # Add the URL to the DataFrame
        df['url'] = url
        df['error_message'] = None
        
        return df

if __name__ == "__main__":

    summarizer = Summarize(provider="groq/llama-3.1-70b-versatile",
                           api_token=os.getenv('GROQ_API_KEY'),
                        #    api_base=os.getenv('OPENAI_API_BASE')
                                              )
    # print("Loaded prompt:")
    # print(summarizer.prompt)

    # Test summarize() method
    test_url = "https://www.fool.com/investing/2023/01/15/3-tech-stocks-most-likely-to-make-a-comeback/"
    print(f"\nTesting summarize() with URL: {test_url}")
    try:
        summarizer.summarize(test_url)
        
    except Exception as e:
        print(f"An error occurred during summarization: {str(e)}")