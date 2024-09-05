from summarize import Summarize
from upload import SummaryNewsTable
from query import NewsQuery, dataframe_to_db
import pandas as pd
from datetime import datetime, timedelta
import time
from tabulate import tabulate

class SummaryNews:
    
    @staticmethod
    def summarize(start_date=None, end_date=None, table_name='rss_news_fmp', site=None):
        df = NewsQuery.querynews(start_date, end_date, table_name, site)
        summarizer = Summarize()
        
        for _, row in df.iterrows():
            url = row['url']
            summary_df = summarizer.summarize(url)
            if summary_df is not None:
                dataframe_to_db(summary_df, SummaryNewsTable)
        
        # # Combine all summaries into a single DataFrame
        # combined_summaries = pd.concat(all_summaries, ignore_index=True)
        # return combined_summaries
        

if __name__ == "__main__":
    start_date = datetime.now() - timedelta(days=3)  # 7 days ago
    # end_date = datetime.now()
    SummaryNews.summarize(start_date)