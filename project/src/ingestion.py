import ijson

from .processor import extract_raw_message



def run_pipeline(json_file_path):
    print("Test")
    with open(json_file_path,'+rb') as f:
        for record in ijson.items(f,'item'):
            message = extract_raw_message(record)
            clean_text = sanitize_text(message.message_text)
            print(f"Original Message: {message.message_text}")
            print(f"Anonymized Message: {clean_text}")
            # Process Raw Message
            # Store ProcessedMessage
            break
        
        