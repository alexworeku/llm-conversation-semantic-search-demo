
from .src.ingestion import run_pipeline

def main():
    # Ingest Data
    # 1. Extract json data from json file, create  RawMessage object  
    run_pipeline()
    
    # 2. Process the RawMessage and get ProcessedMessage object
    # 3. Store ProcessedMessage to DB
    # Simulate Ad
    pass

if __name__ == "__main__":
    main()