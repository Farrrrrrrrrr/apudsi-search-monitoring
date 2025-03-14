import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def fetch_search_analytics_data(service, site_url, start_date, end_date, dimensions, 
                               row_limit=5000, start_row=0, search_type="web",
                               data_state="all", aggregation_type="auto",
                               dimension_filter_groups=None):
    """
    Fetch search analytics data from Google Search Console
    
    Parameters:
    - service: Authenticated GSC service
    - site_url: Website URL to fetch data for
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - dimensions: List of dimensions (e.g., ['query', 'page', 'device', 'country', 'searchAppearance'])
    - row_limit: Maximum number of rows to return (max 25000)
    - start_row: Start row (pagination)
    - search_type: Type of search ('web', 'image', 'video', 'news', 'googleNews', 'discover')
    - data_state: State of data ('all', 'fresh')
    - aggregation_type: How data is aggregated ('auto', 'byPage', 'byProperty')
    - dimension_filter_groups: Filter data by dimension values
    
    Returns:
    - Pandas DataFrame with the results
    """
    if service is None:
        return pd.DataFrame()
    
    try:
        # Build the request body
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': dimensions,
            'rowLimit': row_limit,
            'startRow': start_row,
        }
        
        # Add optional parameters if provided
        if search_type and search_type != "web":
            request['type'] = search_type
            
        if data_state and data_state != "all":
            request['dataState'] = data_state
            
        if aggregation_type and aggregation_type != "auto":
            request['aggregationType'] = aggregation_type
            
        if dimension_filter_groups:
            request['dimensionFilterGroups'] = dimension_filter_groups
        
        # Log the request for debugging - replace st.debug with a comment or st.write with expanded=False
        # st.write("GSC API Request:", request, expanded=False)  # Uncomment this if you need to see the request details
        
        # Make the API call
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        
        if 'rows' not in response:
            st.warning(f"No data returned from Google Search Console for {site_url}")
            return pd.DataFrame()
            
        rows = response['rows']
        data = []
        
        for row in rows:
            row_data = {}
            # Add dimensions
            for i, key in enumerate(dimensions):
                row_data[key] = row['keys'][i]
            
            # Add metrics
            row_data['clicks'] = row.get('clicks', 0)
            row_data['impressions'] = row.get('impressions', 0)
            row_data['ctr'] = row.get('ctr', 0) * 100  # Convert to percentage
            row_data['position'] = row.get('position', 0)
            
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error fetching search analytics data: {str(e)}")
        return pd.DataFrame()

def get_date_ranges():
    """
    Return common date ranges for analytics
    """
    today = datetime.now()
    
    return {
        # English date ranges
        "Last 7 days": {
            "start_date": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        "Last 28 days": {
            "start_date": (today - timedelta(days=28)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        "Last 3 months": {
            "start_date": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        "Last 6 months": {
            "start_date": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        # Add All Time option (16 months max - GSC limitation)
        "All Time": {
            "start_date": (today - timedelta(days=16*30)).strftime("%Y-%m-%d"),  # ~16 months back (GSC limit)
            "end_date": today.strftime("%Y-%m-%d")
        },
        # Indonesian date ranges
        "7 Hari Terakhir": {
            "start_date": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        "28 Hari Terakhir": {
            "start_date": (today - timedelta(days=28)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        "3 Bulan Terakhir": {
            "start_date": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        "6 Bulan Terakhir": {
            "start_date": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        },
        # Add Indonesian version of All Time
        "Semua Waktu": {
            "start_date": (today - timedelta(days=16*30)).strftime("%Y-%m-%d"),  # ~16 months back (GSC limit)
            "end_date": today.strftime("%Y-%m-%d")
        }
    }
