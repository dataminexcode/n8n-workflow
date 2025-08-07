#!/usr/bin/env python3
"""
Bank Transaction Dataset Importer for Elasticsearch
Imports Kaggle bank transaction fraud detection dataset into Elasticsearch
"""

import pandas as pd
import json
import requests
from datetime import datetime
import urllib3
from requests.auth import HTTPBasicAuth
import sys
import os
from tqdm import tqdm

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Elasticsearch configuration
ES_HOST = "https://localhost:9220"
ES_USER = "..."
ES_PASSWORD = "..."
INDEX_NAME = "bank_transactions"

# CSV file path - update this to your downloaded CSV file path
CSV_FILE_PATH = "/home/pc/Desktop/sample_workflows/6 - Bank/archive/bank_transactions_data_2.csv"  # Change this to your actual file path

def check_elasticsearch_connection():
    """Test connection to Elasticsearch"""
    try:
        response = requests.get(
            ES_HOST,
            auth=HTTPBasicAuth(ES_USER, ES_PASSWORD),
            verify=False,  # Disable SSL verification for localhost
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Successfully connected to Elasticsearch")
            cluster_info = response.json()
            print(f"   Cluster: {cluster_info.get('cluster_name', 'Unknown')}")
            print(f"   Version: {cluster_info.get('version', {}).get('number', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to connect to Elasticsearch. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def create_index_mapping():
    """Create the index with proper mapping"""
    mapping = {
        "mappings": {
            "properties": {
                "transaction_id": {"type": "keyword"},
                "customer_id": {"type": "keyword"},
                "amount": {"type": "float"},
                "merchant_category": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "hour": {"type": "integer"},
                "day_of_week": {"type": "integer"},
                "is_fraud": {"type": "boolean"},
                "location": {"type": "keyword"},
                "merchant_name": {"type": "text"},
                "account_balance": {"type": "float"},
                "previous_amount": {"type": "float"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    try:
        # Delete index if it exists
        delete_response = requests.delete(
            f"{ES_HOST}/{INDEX_NAME}",
            auth=HTTPBasicAuth(ES_USER, ES_PASSWORD),
            verify=False
        )
        
        # Create new index
        response = requests.put(
            f"{ES_HOST}/{INDEX_NAME}",
            auth=HTTPBasicAuth(ES_USER, ES_PASSWORD),
            headers={"Content-Type": "application/json"},
            data=json.dumps(mapping),
            verify=False
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Index '{INDEX_NAME}' created successfully")
            return True
        else:
            print(f"❌ Failed to create index. Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        return False

def process_csv_data(df):
    """Process and clean the CSV data"""
    print("🔄 Processing CSV data...")
    
    # Display basic info about the dataset
    print(f"📊 Dataset Info:")
    print(f"   Total records: {len(df):,}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Data types:\n{df.dtypes}")
    
    # Clean and prepare data
    processed_data = []
    
    for index, row in df.iterrows():
        try:
            # Create a base document
            doc = {}
            
            # Map common fields (adjust these based on your actual CSV columns)
            # You'll need to modify these mappings based on your actual CSV structure
            if 'transaction_id' in row:
                doc['transaction_id'] = str(row['transaction_id'])
            elif 'id' in row:
                doc['transaction_id'] = str(row['id'])
            else:
                doc['transaction_id'] = f"TXN_{index:010d}"
            
            if 'customer_id' in row:
                doc['customer_id'] = str(row['customer_id'])
            elif 'user' in row:
                doc['customer_id'] = str(row['user'])
            else:
                doc['customer_id'] = f"CUST_{index % 10000:05d}"
            
            if 'amount' in row:
                doc['amount'] = float(row['amount']) if pd.notna(row['amount']) else 0.0
            elif 'amt' in row:
                doc['amount'] = float(row['amt']) if pd.notna(row['amt']) else 0.0
            else:
                doc['amount'] = 0.0
            
            if 'category' in row:
                doc['merchant_category'] = str(row['category'])
            elif 'merchant' in row:
                doc['merchant_category'] = str(row['merchant'])
            else:
                categories = ['gas_transport', 'grocery_net', 'entertainment', 'shopping_net', 'health_fitness', 'food_dining']
                doc['merchant_category'] = categories[index % len(categories)]
            
            # Handle timestamp
            if 'timestamp' in row:
                doc['timestamp'] = str(row['timestamp'])
            elif 'trans_date_trans_time' in row:
                doc['timestamp'] = str(row['trans_date_trans_time'])
            else:
                # Generate a timestamp within the last 30 days
                from datetime import datetime, timedelta
                import random
                base_time = datetime.now() - timedelta(days=random.randint(1, 30))
                doc['timestamp'] = base_time.isoformat()
            
            # Extract hour from timestamp
            try:
                if 'timestamp' in doc:
                    ts = pd.to_datetime(doc['timestamp'])
                    doc['hour'] = ts.hour
                    doc['day_of_week'] = ts.dayofweek
            except:
                doc['hour'] = index % 24
                doc['day_of_week'] = index % 7
            
            # Handle fraud indicator
            if 'is_fraud' in row:
                doc['is_fraud'] = bool(row['is_fraud']) if pd.notna(row['is_fraud']) else False
            elif 'fraud' in row:
                doc['is_fraud'] = bool(row['fraud']) if pd.notna(row['fraud']) else False
            else:
                # Randomly assign fraud status (10% fraud rate)
                doc['is_fraud'] = (index % 10) == 0
            
            # Add additional fields if they exist in CSV
            optional_fields = ['location', 'merchant_name', 'account_balance', 'previous_amount']
            for field in optional_fields:
                if field in row and pd.notna(row[field]):
                    doc[field] = str(row[field]) if field in ['location', 'merchant_name'] else float(row[field])
            
            processed_data.append(doc)
            
        except Exception as e:
            print(f"⚠️  Error processing row {index}: {str(e)}")
            continue
    
    print(f"✅ Processed {len(processed_data):,} records")
    return processed_data

def bulk_insert_data(data, batch_size=1000):
    """Insert data into Elasticsearch using bulk API"""
    print(f"🔄 Inserting {len(data):,} records into Elasticsearch...")
    
    total_batches = (len(data) + batch_size - 1) // batch_size
    successful_inserts = 0
    failed_inserts = 0
    
    for i in tqdm(range(0, len(data), batch_size), desc="Inserting batches"):
        batch = data[i:i + batch_size]
        
        # Prepare bulk request body
        bulk_body = ""
        for doc in batch:
            # Index action
            index_action = {
                "index": {
                    "_index": INDEX_NAME,
                    "_id": doc.get('transaction_id', f"doc_{i + batch.index(doc)}")
                }
            }
            bulk_body += json.dumps(index_action) + "\n"
            bulk_body += json.dumps(doc) + "\n"
        
        try:
            response = requests.post(
                f"{ES_HOST}/_bulk",
                auth=HTTPBasicAuth(ES_USER, ES_PASSWORD),
                headers={"Content-Type": "application/x-ndjson"},
                data=bulk_body,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errors'):
                    failed_items = sum(1 for item in result['items'] if 'error' in item.get('index', {}))
                    failed_inserts += failed_items
                    successful_inserts += len(batch) - failed_items
                else:
                    successful_inserts += len(batch)
            else:
                print(f"❌ Batch {i//batch_size + 1} failed. Status: {response.status_code}")
                failed_inserts += len(batch)
                
        except Exception as e:
            print(f"❌ Error inserting batch {i//batch_size + 1}: {str(e)}")
            failed_inserts += len(batch)
    
    print(f"✅ Successfully inserted: {successful_inserts:,} records")
    if failed_inserts > 0:
        print(f"❌ Failed to insert: {failed_inserts:,} records")
    
    return successful_inserts, failed_inserts

def verify_import():
    """Verify the import by checking document count"""
    try:
        response = requests.get(
            f"{ES_HOST}/{INDEX_NAME}/_count",
            auth=HTTPBasicAuth(ES_USER, ES_PASSWORD),
            verify=False
        )
        
        if response.status_code == 200:
            count = response.json()['count']
            print(f"✅ Verification: {count:,} documents in index '{INDEX_NAME}'")
            
            # Get a sample document
            sample_response = requests.get(
                f"{ES_HOST}/{INDEX_NAME}/_search?size=1",
                auth=HTTPBasicAuth(ES_USER, ES_PASSWORD),
                verify=False
            )
            
            if sample_response.status_code == 200:
                sample_doc = sample_response.json()['hits']['hits'][0]['_source']
                print("📄 Sample document:")
                print(json.dumps(sample_doc, indent=2))
            
            return count
        else:
            print(f"❌ Failed to verify import. Status: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Error verifying import: {str(e)}")
        return 0

def main():
    """Main function to run the import process"""
    print("🚀 Starting Bank Transaction Dataset Import")
    print("=" * 50)
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ CSV file not found: {CSV_FILE_PATH}")
        print("Please download the dataset from Kaggle and update the CSV_FILE_PATH variable")
        sys.exit(1)
    
    # Step 1: Test Elasticsearch connection
    if not check_elasticsearch_connection():
        sys.exit(1)
    
    # Step 2: Create index with mapping
    if not create_index_mapping():
        sys.exit(1)
    
    # Step 3: Load and process CSV data
    try:
        print(f"📖 Reading CSV file: {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"✅ Loaded {len(df):,} rows from CSV")
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        sys.exit(1)
    
    # Step 4: Process the data
    processed_data = process_csv_data(df)
    
    if not processed_data:
        print("❌ No data to import")
        sys.exit(1)
    
    # Step 5: Import data into Elasticsearch
    successful, failed = bulk_insert_data(processed_data)
    
    # Step 6: Verify the import
    final_count = verify_import()
    
    print("\n" + "=" * 50)
    print("🎉 Import completed!")
    print(f"📊 Final Statistics:")
    print(f"   • Successfully imported: {successful:,} documents")
    print(f"   • Failed imports: {failed:,} documents")
    print(f"   • Total in Elasticsearch: {final_count:,} documents")
    print(f"\n🔗 You can now use this index in your n8n workflow:")
    print(f"   Index name: {INDEX_NAME}")
    print(f"   Elasticsearch URL: {ES_HOST}")

if __name__ == "__main__":
    # Install required packages
    try:
        import pandas as pd
        import requests
        from tqdm import tqdm
    except ImportError as e:
        print("❌ Missing required packages. Please install them:")
        print("pip install pandas requests tqdm")
        sys.exit(1)
    
    main()
