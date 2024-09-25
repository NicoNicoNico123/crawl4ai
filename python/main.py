from summarize import Summarize
from upload import SummaryNewsTable
from query import NewsQuery, dataframe_to_db, DataBaseUpload
import pandas as pd
from datetime import datetime, timedelta
import time
import colorama
import os
colorama.init()

class SummaryNews:
    
    @staticmethod
    def summarize(start_date=None,
                   end_date=None, 
                   symbol=None, 
                   table_name='stock_news_fmp', 
                   site=None,
                   provider='groq/llama-3.1-70b-versatile',
                   api_token=os.getenv('GROQ_API_KEY')):
        session, _ = DataBaseUpload.connect_sql()
        summarizer = Summarize(provider=provider,
                               api_token=api_token)
        
        try:
            df = NewsQuery.querynews(start_date, end_date, table_name, site,symbol,session=session)
            
            for _, row in df.iterrows():
                url = row['url']
                
                try:
                    summary_df = summarizer.summarize(url)
                    if summary_df is not None:
                        dataframe_to_db(summary_df, SummaryNewsTable, session)
                        session.commit()
                        print(f"{colorama.Fore.GREEN}Summarization completed for {url}{colorama.Fore.RESET}")
                        time.sleep(60)
                except Exception as e:
                    print(f"{colorama.Fore.RED}An error occurred while processing {url}: {e}{colorama.Fore.RESET}")
                    # Optionally, you might want to log this error or handle it differently
            
            print(f"{colorama.Fore.GREEN}Summarization completed for {len(df)} news items.{colorama.Fore.RESET}")
            
        except Exception as e:
            session.rollback()
            print(f"{colorama.Fore.RED}An error occurred during the summarization process: {e}{colorama.Fore.RESET}")
        finally:
            session.close()
        
        # # Combine all summaries into a single DataFrame
        # combined_summaries = pd.concat(all_summaries, ignore_index=True)
        # return combined_summaries
        

if __name__ == "__main__":
    start_date = '2023-02-01'
    end_date = '2023-02-15'
    provider = "sambanova/Meta-Llama-3.1-405B-Instruct"
    api_token = os.getenv('SAMBANOVA_API_KEY')
    SummaryNews.summarize(start_date=start_date, 
                           end_date=end_date,
                           symbol='META', 
                           table_name='stock_news_fmp')