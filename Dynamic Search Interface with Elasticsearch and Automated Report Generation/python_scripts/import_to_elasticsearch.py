import pandas as pd
import requests
import json
from datetime import datetime

# Configuration
ELASTICSEARCH_URL = "https://****.ngrok-free.app"
USERNAME = "elastic"
PASSWORD = "...."
INDEX_NAME = "bank_transactions"
CSV_FILE = "bank_transactions_data_2.csv"

def import_csv_to_elasticsearch():
    # Read CSV file
    print("Reading CSV file...")
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} records from CSV")
    
    # Prepare bulk import data
    bulk_data = []
    
    for index, row in df.iterrows():
        # Create document
        doc = {
            "TransactionID": str(row['TransactionID']),
            "AccountID": str(row['AccountID']),
            "TransactionAmount": float(row['TransactionAmount']),
            "TransactionDate": str(row['TransactionDate']),
            "TransactionType": str(row['TransactionType']),
            "Location": str(row['Location']),
            "DeviceID": str(row['DeviceID']),
            "IP Address": str(row['IP Address']),
            "MerchantID": str(row['MerchantID']),
            "Channel": str(row['Channel']),
            "CustomerAge": int(row['CustomerAge']),
            "CustomerOccupation": str(row['CustomerOccupation']),
            "TransactionDuration": int(row['TransactionDuration']),
            "LoginAttempts": int(row['LoginAttempts']),
            "AccountBalance": float(row['AccountBalance']),
            "PreviousTransactionDate": str(row['PreviousTransactionDate'])
        }
        
        # Add index action
        bulk_data.append({"index": {"_index": INDEX_NAME}})
        bulk_data.append(doc)
        
        # Process in batches of 100
        if len(bulk_data) >= 200:  # 100 docs * 2 lines each
            send_bulk_request(bulk_data)
            bulk_data = []
            print(f"Processed {index + 1} records...")
    
    # Send remaining data
    if bulk_data:
        send_bulk_request(bulk_data)
    
    print("Import completed!")

def send_bulk_request(bulk_data):
    """Send bulk request to Elasticsearch"""
    # Convert to newline-delimited JSON
    bulk_body = "\n".join([json.dumps(item) for item in bulk_data]) + "\n"
    
    # Send request
    response = requests.post(
        f"{ELASTICSEARCH_URL}/_bulk",
        headers={"Content-Type": "application/x-ndjson"},
        auth=(USERNAME, PASSWORD),
        data=bulk_body,
        verify=False  # For ngrok tunnels
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
    else:
        result = response.json()
        if result.get("errors"):
            print("Some documents failed to index:")
            for item in result["items"]:
                if "error" in item.get("index", {}):
                    print(f"Error: {item['index']['error']}")

if __name__ == "__main__":
    try:
        import_csv_to_elasticsearch()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have pandas and requests installed:")
        print("pip install pandas requests")
