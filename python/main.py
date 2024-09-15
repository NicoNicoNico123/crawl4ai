from summarize import Summarize
from upload import SummaryNewsTable
from query import NewsQuery, dataframe_to_db, DataBaseUpload
import pandas as pd
from datetime import datetime, timedelta
import time
from tabulate import tabulate

class SummaryNews:
    
    @staticmethod
    def summarize(start_date=None, end_date=None, symbol=None, table_name='stock_news_fmp', site=None):
        session, _ = DataBaseUpload.connect_sql()
        summarizer = Summarize()
        
        try:
            df = NewsQuery.querynews(start_date, end_date, table_name, site,symbol,session=session)
            
            for _, row in df.iterrows():
                url = row['url']
                
                try:
                    summary_df = summarizer.summarize(url)
                    if summary_df is not None:
                        dataframe_to_db(summary_df, SummaryNewsTable, session)
                        session.commit()
                        print(f"Summarization completed for {len(df)} news items.")
                except Exception as e:
                    print(f"An error occurred while processing {url}: {e}")
                    # Optionally, you might want to log this error or handle it differently
            
            
        except Exception as e:
            session.rollback()
            print(f"An error occurred during the summarization process: {e}")
        finally:
            session.close()
        
        # # Combine all summaries into a single DataFrame
        # combined_summaries = pd.concat(all_summaries, ignore_index=True)
        # return combined_summaries
        

if __name__ == "__main__":
    start_date = '2023-01-06'
    end_date = '2023-01-31'
    SummaryNews.summarize(start_date=start_date, end_date=end_date, symbol='META', table_name='stock_news_fmp')