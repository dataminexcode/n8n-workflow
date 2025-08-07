# Dynamic Search Interface with Elasticsearch and Automated Report Generation

## 🎯 What this workflow does

This template creates a comprehensive data search and reporting system that allows users to query large datasets through an intuitive web form interface. The system performs real-time searches against Elasticsearch, processes results, and automatically generates structured reports in multiple formats for data analysis and business intelligence.

**Key Features:**
- 🔍 Interactive web form for dynamic data querying
- ⚡ Real-time Elasticsearch data retrieval with complex filtering
- 📊 Auto-generated reports (Text & CSV formats) with custom formatting
- 💾 Automatic file storage system for data persistence
- 🎯 Configurable search parameters (amounts, time ranges, entity filters)
- 🔧 Scalable architecture for handling large datasets

## 🛠️ Setup requirements

### Prerequisites
- **Elasticsearch cluster** running on `https://localhost:9220`
- **Transaction dataset** indexed in `bank_transactions` index
- **Sample dataset**: Download from [Kaggle Bank Transaction Dataset](https://www.kaggle.com/datasets/valakhorasani/bank-transaction-dataset-for-fraud-detection)
- **File system access** to `/tmp/` directory for report storage
- **HTTP Basic Authentication** credentials for Elasticsearch

### Required Elasticsearch Index Structure
This template uses the **Bank Transaction Dataset** from Kaggle: https://www.kaggle.com/datasets/valakhorasani/bank-transaction-dataset-for-fraud-detection

Your `bank_transactions` index should contain documents with these fields:
```json
{
  "transaction_id": "TXN_123456789",
  "customer_id": "CUST_000001", 
  "amount": 5000,
  "merchant_category": "grocery_net",
  "timestamp": "2025-08-10T15:30:00Z"
}
```

**Dataset Info**: This Kaggle dataset contains realistic financial transaction data perfect for testing search algorithms and report generation, with over 1 million transaction records including various transaction patterns and data types.

### Credentials Setup
1. Create HTTP Basic Auth credentials in n8n
2. Configure with your Elasticsearch username/password
3. Assign to the "Search Elasticsearch" node

## ⚙️ Configuration

### 1. Form Customization
- **Webhook Path**: Update the webhook ID if needed
- **Form Fields**: Modify amounts, time ranges, or add new filters
- **Validation**: Adjust required fields based on your needs

### 2. Elasticsearch Configuration
- **URL**: Change `localhost:9220` to your ES cluster endpoint
- **Index Name**: Update `bank_transactions` to your index name
- **Query Logic**: Modify search criteria in "Build Search Query" node
- **Result Limit**: Adjust the `size: 100` parameter for more/fewer results

### 3. File Storage
- **Directory**: Change `/tmp/` to your preferred storage location
- **Filename Pattern**: Modify `fraud_report_YYYY-MM-DD.{ext}` format
- **Permissions**: Ensure n8n has write access to the target directory

### 4. Report Formatting
- **CSV Headers**: Customize column names in the Format Report node
- **Text Layout**: Modify the report template for your organization
- **Data Fields**: Add/remove transaction fields as needed

## 🚀 How to use

### For Administrators:
1. **Import** this workflow template
2. **Configure** Elasticsearch credentials
3. **Activate** the workflow
4. **Share** the webhook URL with data analysts

### For Data Analysts:
1. **Access** the search interface via the webhook URL
2. **Set parameters**: Minimum amount, time range, entity filter
3. **Choose format**: Text report or CSV export
4. **Submit** form to generate instant data report
5. **Review** results in the generated file

### Sample Use Cases:
- **Data analysis**: Search for transactions > $10,000 in last 24 hours
- **Entity investigation**: Filter all activity for specific customer ID  
- **Pattern analysis**: Quick analysis of transaction activity patterns
- **Business reporting**: Generate CSV exports for business intelligence
- **Dataset testing**: Perfect for testing with the Kaggle transaction dataset

## 📊 Sample Output

### Text Report Format:
```
DATA ANALYSIS REPORT
====================

Search Criteria:
- Minimum Amount: $10000
- Time Range: Last 24 Hours  
- Customer: All

Results: 3 transactions found

TRANSACTIONS:
=============

1. Transaction ID: TXN_123456789
   Customer: CUST_000001
   Amount: $15000
   Merchant: grocery_net
   Time: 2025-08-10T15:30:00Z
```

### CSV Export Format:
```csv
Transaction_ID,Customer_ID,Amount,Merchant_Category,Timestamp
"TXN_123456789","CUST_000001",15000,"grocery_net","2025-08-10T15:30:00Z"
```

## 🔧 Customization ideas

### Enhanced Analytics Features:
- Add data validation and quality checks
- Implement statistical analysis (averages, trends, patterns)
- Include data visualization charts and graphs
- Generate summary metrics and KPIs

### Advanced Search Capabilities:
- Multi-field search with complex boolean logic
- Fuzzy search and text matching algorithms
- Date range filtering with custom periods
- Aggregation queries for data grouping

### Integration Options:
- **Email notifications**: Alert teams of significant data findings
- **Slack integration**: Post analytics results to team channels  
- **Dashboard updates**: Push metrics to business intelligence systems
- **API endpoints**: Expose search functionality as REST API

### Report Enhancements:
- **PDF generation**: Create formatted PDF analytics reports
- **Data visualization**: Add charts, graphs, and trending analysis
- **Executive summaries**: Include key metrics and business insights
- **Export formats**: Support for Excel, JSON, and other data formats

## 🏷️ Tags
`elasticsearch`, `data-search`, `reporting`, `analytics`, `automation`, `business-intelligence`, `data-processing`, `csv-export`

## 📈 Use cases
- **Business Intelligence**: Organizations analyzing transaction patterns and trends
- **E-commerce Analytics**: Detecting payment patterns and customer behavior analysis
- **Data Science**: Real-time data exploration and pattern recognition systems
- **Operations Teams**: Automated reporting and data monitoring workflows
- **Research & Development**: Testing search algorithms and data processing techniques
- **Training & Education**: Learning Elasticsearch integration with realistic datasets
- **Financial Technology**: Transaction data analysis and business reporting systems

## ⚠️ Important notes

### Security Considerations:
- Never expose Elasticsearch credentials in logs or form data
- Implement proper access controls for the webhook URL
- Consider encryption for sensitive data processing
- Regular audit of generated reports and access logs

### Performance Tips:
- Index optimization improves search response times
- Consider pagination for large result sets
- Monitor Elasticsearch cluster performance under load
- Archive old reports to manage disk usage

### Data Management:
- Ensure data retention policies align with business requirements
- Implement audit trails for all search operations
- Consider data privacy requirements when processing datasets
- Document all configuration changes for maintenance

---

*This template provides a production-ready data search and reporting system that can be easily customized for various data analysis needs. The modular design allows for incremental enhancements while maintaining core search and reporting functionality.*