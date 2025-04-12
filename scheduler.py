import schedule
import time
from datetime import datetime
from etl_pipeline import ETLPipeline  # Assuming your class is saved in etl_pipeline.py

def job():
    print(f"\n[INFO] Job started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    etl = ETLPipeline()
    transformed_df = etl.run_transformation()
    etl.load_data(transformed_df)
    
    print(f"[INFO] Job completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Schedule the job every day at 9:00 AM
schedule.every().day.at("09:00").do(job)

print("[INFO] Scheduler is running... Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
