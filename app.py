import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os

# Try to import optional dependencies with graceful fallback
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Import custom modules
from gsc_auth import authenticate_gsc, get_site_list
from gsc_data import fetch_search_analytics_data, get_date_ranges
from visualizations import (
    plot_metrics_over_time, 
    plot_top_items, 
    plot_geo_map, 
    create_summary_metrics
)

# Try to import Instagram module with graceful fallback
try:
    from instagram_scraper import load_instagram_data
    INSTAGRAM_MODULE_AVAILABLE = True
except ImportError:
    INSTAGRAM_MODULE_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="APUDSI Site Performance Dashboard",
    page_icon="📈",
    layout="wide"
)

# Show dependency warning if needed
if not MATPLOTLIB_AVAILABLE or not INSTAGRAM_MODULE_AVAILABLE:
    st.warning("""
    ### Missing Dependencies Detected
    
    Some features require additional packages. Please install them with:
    ```
    pip install -r requirements.txt
    ```
    or specifically:
    ```
    pip install matplotlib instaloader wordcloud pillow
    ```
    """)

# App title and description
st.title("📈 APUDSI Site Performance Dashboard")
st.subheader("Data Analisis dari Google untuk apudsi.com")
st.subheader("Data yang ditampilkan adalah data yang resmi dari Analisis Pencarian Google 🚀")
# Constants and defaults - change this to use ALL data instead of just 28 days
DEFAULT_DATE_RANGE = "All Time"  # Changed from "Last 28 days" to show all available data

# Add function to filter out specific domains
def filter_sensitive_data(df):
    """Filter out rows containing specific domains"""
    if df is None or df.empty:
        return df
    
    # Store original and filtered counts to report what was filtered
    original_count = len(df)
    
    # Filter out any data with the specified domain
    # This works on both 'page' and 'query' columns if they exist
    filtered_df = df.copy()
    
    # Fix typo: bacckend -> backend
    sensitive_domain = "superapp.backend.apudsi.com"
    
    # Filter page column if it exists
    if 'page' in filtered_df.columns:
        filtered_df = filtered_df[~filtered_df['page'].str.contains(sensitive_domain, case=False, na=False)]
    
    # Filter query column if it exists
    if 'query' in filtered_df.columns:
        filtered_df = filtered_df[~filtered_df['query'].str.contains(sensitive_domain, case=False, na=False)]
    
    # Calculate how many rows were filtered
    filtered_count = original_count - len(filtered_df)
    
    # Store the filtering stats in session state
    if filtered_count > 0:
        st.session_state.filtered_domain = sensitive_domain
        st.session_state.filtered_count = filtered_count
    
    return filtered_df

# Helper function to load mock data if needed
def load_mock_data():
    """Load mock data for demonstration"""
    try:
        # Try to import mock data generator
        from create_mock_data import generate_mock_gsc_data
        
        # Get date range - use a much wider range for ALL data
        date_ranges = get_date_ranges()
        if DEFAULT_DATE_RANGE in date_ranges:
            start_date_str = date_ranges[DEFAULT_DATE_RANGE]["start_date"]
            end_date_str = date_ranges[DEFAULT_DATE_RANGE]["end_date"]
        else:
            # Fallback to a very wide date range if "All Time" is not defined
            end_date_str = datetime.now().strftime("%Y-%m-%d")
            start_date_str = (datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d")  # 5 years back
        
        # Generate mock data
        data = generate_mock_gsc_data(start_date_str, end_date_str)
        st.info("📊 Viewing mock data for demonstration purposes.")
        return filter_sensitive_data(data)
    except ImportError:
        st.error("Could not load mock data generator. Make sure create_mock_data.py exists.")
        return None

# Helper function to load data from GSC API
def load_site_data():
    """Load GSC data automatically using stored credentials"""
    with st.spinner("Loading site performance data..."):
        try:
            # Use stored service account credentials
            service = None
            if os.path.exists('service-account-key.json'):
                service = authenticate_gsc(use_stored=True)
                if not service:
                    st.error("Unable to authenticate with stored credentials")
                    return None
            else:
                st.error("Service account credentials not found")
                return None
            
            # Get available sites from GSC
            sites = get_site_list(service)
            
            if not sites:
                st.error("No sites available. Make sure your service account has access to GSC properties.")
                return None
                
            # Use the first available site
            selected_site = sites[0]
            st.success(f"Using site: {selected_site}")
                
            # Get date range - use a much wider range for ALL data
            date_ranges = get_date_ranges()
            if DEFAULT_DATE_RANGE in date_ranges:
                start_date_str = date_ranges[DEFAULT_DATE_RANGE]["start_date"]
                end_date_str = date_ranges[DEFAULT_DATE_RANGE]["end_date"]
            else:
                # Fallback to a very wide date range if "All Time" is not defined
                end_date_str = datetime.now().strftime("%Y-%m-%d")
                start_date_str = (datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d")  # 5 years back
            
            # Set dimensions for analysis
            dimensions = ["date", "query", "page", "country"]
            
            # Fetch data
            data = fetch_search_analytics_data(
                service, 
                selected_site, 
                start_date_str, 
                end_date_str, 
                dimensions,
                row_limit=5000
            )
            
            if data.empty:
                st.warning(f"No data available for {selected_site} in the selected date range")
                
                # Try loading CSV data if it exists
                if os.path.exists('mock_gsc_data.csv'):
                    st.info("Loading data from mock_gsc_data.csv instead")
                    return pd.read_csv('mock_gsc_data.csv')
                return None
                
            return filter_sensitive_data(data)
            
        except Exception as e:
            st.error(f"Error loading site data: {str(e)}")
            
            # Try loading CSV data if it exists
            if os.path.exists('mock_gsc_data.csv'):
                st.info("Loading data from mock_gsc_data.csv instead")
                return pd.read_csv('mock_gsc_data.csv')
            return None

# Load data on app startup
data = load_site_data()

# If no data from API, fall back to mock data
if data is None:
    st.warning("Unable to load real data. Attempting to load mock data instead.")
    data = load_mock_data()

# Create tabs for different analytics views - REMOVED Instagram and Geographic tabs
tab1, tab2 = st.tabs([
    "Performance Overview", 
    "Content Analysis"
])

# If data is available, show visualization
if data is not None:
    # Tab 1: Performance Overview
    with tab1:
        st.header("Performance Overview")
        
        # Update date range info to show actual range if available
        if 'date' in data.columns:
            min_date = data['date'].min()
            max_date = data['date'].max()
            st.caption(f"Data from {min_date} to {max_date}")
        else:
            date_ranges = get_date_ranges()
            if DEFAULT_DATE_RANGE in date_ranges:
                st.caption(f"Data from {date_ranges[DEFAULT_DATE_RANGE]['start_date']} to {date_ranges[DEFAULT_DATE_RANGE]['end_date']}")
        
        # Summary metrics
        create_summary_metrics(data)
        
        # Time series charts
        st.subheader("Performance Trends")
        plot_metrics_over_time(data)
    
    # Tab 2: Content Analysis
    with tab2:
        st.header("Content Analysis")
        
        # Remove the security warning banner
        # (The filtering still happens, we just don't notify users about it)
        
        metric_options = ["clicks", "impressions", "ctr", "position"]
        default_metric = "clicks"
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            metric_option = st.selectbox(
                "Select metric", 
                metric_options,
                index=metric_options.index(default_metric)
            )
            
            top_n = st.slider("Number of items", min_value=5, max_value=30, value=10)
        
        with col2:
            st.write("")  # Empty space for alignment
        
        # Top queries
        if "query" in data.columns:
            st.subheader("Kata Pencarian di Google")
            
            # Create tabs for different visualizations
            query_tab1, query_tab2 = st.tabs(["Bar Chart", "Pie Chart"])
            
            # Prepare query data
            query_df = data.groupby("query").agg({
                'clicks': 'sum',
                'impressions': 'sum',
                'ctr': 'mean', 
                'position': 'mean'
            }).reset_index()
            
            # Sort based on selected metric
            if metric_option == 'position':
                query_df = query_df.sort_values(by=metric_option, ascending=True).head(top_n)
            else:
                query_df = query_df.sort_values(by=metric_option, ascending=False).head(top_n)
            
            # Bar Chart tab
            with query_tab1:
                plot_top_items(data, "query", metric_option, top_n=top_n)
            
            # Pie Chart tab
            with query_tab2:
                fig = px.pie(
                    query_df,
                    values=metric_option,
                    names="query",
                    title=f"Distribution of {metric_option.title()} by Query",
                    hole=0.4,  # Donut chart effect
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        # Top pages
        if "page" in data.columns:
            st.subheader("Halaman Paling Banyak Dikunjungi")
            
            # Create tabs for different visualizations
            page_tab1, page_tab2 = st.tabs(["Bar Chart", "Pie Chart"])
            
            # Prepare page data
            page_df = data.groupby("page").agg({
                'clicks': 'sum',
                'impressions': 'sum',
                'ctr': 'mean', 
                'position': 'mean'
            }).reset_index()
            
            # Sort based on selected metric
            if metric_option == 'position':
                page_df = page_df.sort_values(by=metric_option, ascending=True).head(top_n)
            else:
                page_df = page_df.sort_values(by=metric_option, ascending=False).head(top_n)
            
            # Bar Chart tab
            with page_tab1:
                plot_top_items(data, "page", metric_option, top_n=top_n)
            
            # Pie Chart tab
            with page_tab2:
                fig = px.pie(
                    page_df,
                    values=metric_option,
                    names="page",
                    title=f"Distribution of {metric_option.title()} by Page",
                    hole=0.4,  # Donut chart effect
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

# Show error message if no data was loaded (replacing the else clause)
if data is None:
    # Error message if no data could be loaded
    st.error("Unable to load site performance data.")
    
    # Display troubleshooting information
    with st.expander("Troubleshooting Tips"):
        st.markdown("""
        ### Resolving Permission Issues
        
        1. Make sure your service account has access to your Google Search Console properties:
           - Go to Google Search Console > Settings > Users and Permissions
           - Add your service account email as a user (it's in your service-account-key.json file)
           - Grant either "Owner" or "Full User" permissions
        
        2. Verify your credentials:
           - Ensure service-account-key.json is in the app directory
           - The service account should have Search Console API enabled
        
        3. If the problem persists:
           - Try running the app in mock mode: `streamlit run app.py -- --mock`
           - Check if there is data in the selected date range
        """)