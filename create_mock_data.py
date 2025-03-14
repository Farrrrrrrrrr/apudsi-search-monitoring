import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

def generate_mock_gsc_data(start_date_str, end_date_str):
    """
    Generate mock Google Search Console data for testing purposes
    
    Parameters:
    - start_date_str: Start date in YYYY-MM-DD format
    - end_date_str: End date in YYYY-MM-DD format
    
    Returns:
    - DataFrame with mock GSC data
    """
    # Convert string dates to datetime
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    # Generate date range
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    # Sample queries
    queries = [
        "how to build a website", 
        "best web development frameworks",
        "python tutorial", 
        "javascript for beginners",
        "css tricks", 
        "react vs angular", 
        "node.js tutorial",
        "api development best practices",
        "streamlit dashboard examples",
        "data visualization tools",
        "google search console api",
        "python pandas tutorial",
        "web analytics dashboard"
    ]
    
    # Sample pages
    pages = [
        "/", 
        "/blog", 
        "/tutorials",
        "/about", 
        "/contact",
        "/blog/python-tips",
        "/blog/web-development",
        "/tutorials/javascript",
        "/tutorials/python",
        "/products"
    ]
    
    # Sample countries
    countries = [
        "United States", 
        "India", 
        "United Kingdom", 
        "Germany",
        "Canada", 
        "Australia", 
        "France",
        "Brazil", 
        "Japan", 
        "Spain"
    ]
    
    # Sample devices
    devices = ["MOBILE", "DESKTOP", "TABLET"]
    
    # Create mock data
    data = []
    
    for date in date_range:
        # Add date dimension data
        base_clicks = np.random.randint(50, 200)
        base_impressions = base_clicks * np.random.randint(10, 30)
        
        # Create daily totals
        data.append({
            'date': date,
            'clicks': base_clicks,
            'impressions': base_impressions,
            'ctr': (base_clicks / base_impressions) * 100,
            'position': np.random.uniform(1.0, 20.0)
        })
        
        # Create query data
        for query in np.random.choice(queries, size=min(5, len(queries)), replace=False):
            q_clicks = max(1, int(np.random.normal(base_clicks / 10, base_clicks / 30)))
            q_impressions = max(q_clicks, int(q_clicks * np.random.randint(5, 15)))
            data.append({
                'date': date,
                'query': query,
                'clicks': q_clicks,
                'impressions': q_impressions,
                'ctr': (q_clicks / q_impressions) * 100,
                'position': np.random.uniform(1.0, 20.0)
            })
        
        # Create page data
        for page in np.random.choice(pages, size=min(3, len(pages)), replace=False):
            p_clicks = max(1, int(np.random.normal(base_clicks / 8, base_clicks / 25)))
            p_impressions = max(p_clicks, int(p_clicks * np.random.randint(4, 12)))
            data.append({
                'date': date,
                'page': page,
                'clicks': p_clicks,
                'impressions': p_impressions,
                'ctr': (p_clicks / p_impressions) * 100,
                'position': np.random.uniform(1.0, 15.0)
            })
        
        # Create country data
        for country in np.random.choice(countries, size=min(5, len(countries)), replace=False):
            c_clicks = max(1, int(np.random.normal(base_clicks / 12, base_clicks / 35)))
            c_impressions = max(c_clicks, int(c_clicks * np.random.randint(5, 18)))
            data.append({
                'date': date,
                'country': country,
                'clicks': c_clicks,
                'impressions': c_impressions,
                'ctr': (c_clicks / c_impressions) * 100,
                'position': np.random.uniform(1.0, 25.0)
            })
        
        # Create device data
        for device in devices:
            d_clicks = max(1, int(np.random.normal(base_clicks / 3, base_clicks / 10)))
            d_impressions = max(d_clicks, int(d_clicks * np.random.randint(5, 15)))
            data.append({
                'date': date,
                'device': device,
                'clicks': d_clicks,
                'impressions': d_impressions,
                'ctr': (d_clicks / d_impressions) * 100,
                'position': np.random.uniform(1.0, 20.0)
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save mock data to CSV for future use
    df.to_csv('mock_gsc_data.csv', index=False)
    print(f"Mock data generated with {len(df)} rows and saved to 'mock_gsc_data.csv'")
    
    return df

def create_mock_gsc_service():
    """Create a mock credentials file for testing"""
    mock_creds = {
        "type": "service_account",
        "project_id": "mock-gsc-project",
        "private_key_id": "mock-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "mock-service@mock-gsc-project.iam.gserviceaccount.com",
        "client_id": "000000000000000000000",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mock-service%40mock-gsc-project.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    # Save mock credentials to file
    with open('mock_credentials.json', 'w') as f:
        json.dump(mock_creds, f, indent=2)
    
    print("Mock credentials file created at 'mock_credentials.json'")

if __name__ == "__main__":
    # Generate 30 days of mock data
    today = datetime.now()
    end_date = today.strftime("%Y-%m-%d")
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    
    generate_mock_gsc_data(start_date, end_date)
    create_mock_gsc_service()
    
    print("\nMock data generation complete. Run the app with:")
    print("streamlit run app.py -- --mock")
