import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def plot_metrics_over_time(df, date_col='date', title="Performance Over Time"):
    """
    Create a line chart of key metrics over time
    """
    if df.empty or date_col not in df.columns:
        st.warning("No data available for time series visualization")
        return
    
    # Ensure date is in datetime format
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Group by date and sum metrics
    df_grouped = df.groupby(date_col).agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'position': 'mean'
    }).reset_index()
    
    # Create tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["Clicks", "Impressions", "CTR (%)", "Position"])
    
    with tab1:
        fig = px.line(df_grouped, x=date_col, y='clicks', title=f"{title} - Clicks")
        fig.update_traces(line_color='#1E88E5')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.line(df_grouped, x=date_col, y='impressions', title=f"{title} - Impressions")
        fig.update_traces(line_color='#43A047')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.line(df_grouped, x=date_col, y='ctr', title=f"{title} - CTR (%)")
        fig.update_traces(line_color='#FBC02D')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = px.line(df_grouped, x=date_col, y='position', title=f"{title} - Average Position")
        fig.update_traces(line_color='#E53935')
        # Invert y-axis for position (lower is better)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

def plot_top_items(df, dimension, metric='clicks', title=None, top_n=10):
    """
    Create a bar chart of top items by a given metric
    """
    if df.empty or dimension not in df.columns or metric not in df.columns:
        st.warning(f"No data available for {dimension} visualization")
        return
    
    if title is None:
        title = f"Top {top_n} {dimension.title()}s by {metric.title()}"
    
    # Group by dimension and sum metrics
    grouped_df = df.groupby(dimension).agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean', 
        'position': 'mean'
    }).reset_index()
    
    # Sort and get top N
    if metric == 'position':
        # For position, lower is better
        sorted_df = grouped_df.sort_values(by=metric, ascending=True).head(top_n)
    else:
        sorted_df = grouped_df.sort_values(by=metric, ascending=False).head(top_n)
    
    # Create bar chart
    fig = px.bar(
        sorted_df,
        x=metric,
        y=dimension,
        orientation='h',
        title=title,
        text=metric,
        color=metric,
        color_continuous_scale=px.colors.sequential.Blues,
        height=max(400, 30 * top_n)  # Dynamic height based on number of items
    )
    
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    if metric == 'ctr':
        fig.update_layout(xaxis_title="CTR (%)")
        fig.update_traces(texttemplate='%{text:.2f}%')
    elif metric == 'position':
        fig.update_layout(xaxis_title="Average Position")
        fig.update_traces(texttemplate='%{text:.1f}')
    else:
        fig.update_traces(texttemplate='%{text:,}')
    
    st.plotly_chart(fig, use_container_width=True)

def plot_device_distribution(df, metric='clicks'):
    """
    Create a pie chart showing distribution by device
    """
    if df.empty or 'device' not in df.columns:
        st.warning("No device data available")
        return
    
    # Group by device
    device_df = df.groupby('device').agg({
        'clicks': 'sum',
        'impressions': 'sum'
    }).reset_index()
    
    # Create pie chart
    fig = px.pie(
        device_df, 
        values=metric, 
        names='device',
        title=f"Distribution by Device ({metric.title()})",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_traces(textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def plot_geo_map(df, country_col='country', metric='clicks'):
    """
    Create a choropleth map showing metrics by country with modern styling
    """
    if df.empty or country_col not in df.columns:
        st.warning("No country data available")
        return
    
    # Group by country
    country_df = df.groupby(country_col).agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'position': 'mean'
    }).reset_index()
    
    # Country name standardization to ensure all countries appear
    # This handles common issues with country names
    country_name_map = {
        'United States': 'United States of America',
        'USA': 'United States of America',
        'US': 'United States of America',
        'UK': 'United Kingdom',
        'UAE': 'United Arab Emirates',
        'Republic of Indonesia': 'Indonesia',
        'Indonesian': 'Indonesia',
        'Indonesia': 'Indonesia',  # Force exact match
        'Republic of India': 'India',
        'India': 'IND',  # Try direct ISO mapping
        'People Republic of China': 'China',
        'China': 'CHN'  # Try direct ISO mapping
    }
    
    # Apply the mapping
    country_df[country_col] = country_df[country_col].replace(country_name_map)
    
    # Create ISO code mapping for more reliable country identification
    iso_country_map = {
        'Indonesia': 'IDN',
        'United States': 'USA',
        'United States of America': 'USA',
        'United Kingdom': 'GBR',
        'India': 'IND',
        'China': 'CHN',
        'Japan': 'JPN',
        'Malaysia': 'MYS',
        'Singapore': 'SGP',
        'Australia': 'AUS'
    }
    
    # MANUAL FIX 1: Print the countries to help with debugging
    st.write("DEBUG - Countries in data:", country_df[country_col].unique())
    
    # Add ISO column for mapping
    country_df['iso_alpha'] = country_df[country_col].map(iso_country_map)
    
    # MANUAL FIX 2: Create a special trace just for Indonesia
    indonesia_df = country_df[country_df[country_col] == 'Indonesia'].copy()
    
    # MANUAL FIX 3: Explicitly add Indonesia if it exists but with wrong naming
    indonesia_in_original = df[df[country_col].str.contains('Indonesia', case=False, na=False)]
    if not indonesia_in_original.empty and 'Indonesia' not in country_df[country_col].values:
        indonesia_metrics = indonesia_in_original.agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        })
        new_row = pd.DataFrame({
            country_col: ['Indonesia'],
            'clicks': [indonesia_metrics['clicks']],
            'impressions': [indonesia_metrics['impressions']],
            'ctr': [indonesia_metrics['ctr']],
            'position': [indonesia_metrics['position']],
            'iso_alpha': ['IDN']
        })
        country_df = pd.concat([country_df, new_row], ignore_index=True)
        st.success("Indonesia manually added to the data")
        
    # Create a copy of the dataframe with ISO codes where available
    iso_df = country_df.copy()
    iso_df = iso_df.dropna(subset=['iso_alpha'])
    
    # For debugging - helps identify countries not showing on map
    if st.checkbox("Show Country Data Table", value=False, key="show_country_debug"):
        st.write("Countries in dataset:")
        st.dataframe(country_df[[country_col, metric, 'iso_alpha']])
    
    # Create choropleth map with modern styling using both country names and ISO codes
    fig = px.choropleth(
        country_df,
        locations=country_col,
        locationmode='country names',
        color=metric,
        hover_name=country_col,
        color_continuous_scale='viridis',
        title=f"{metric.title()} by Country",
        labels={metric: f"{metric.title()}"},
        custom_data=[metric]
    )
    
    # Add ISO-based countries as a second trace to ensure problematic countries appear
    if not iso_df.empty:
        fig2 = px.choropleth(
            iso_df,
            locations='iso_alpha',
            locationmode='ISO-3',
            color=metric,
            hover_name=country_col,
            color_continuous_scale='viridis',
        )
        # Add the ISO trace to the main figure
        for trace in fig2.data:
            fig.add_trace(trace)
    
    # MANUAL FIX 4: Add a specific trace just for Indonesia with ISO code
    if not indonesia_df.empty:
        indonesia_df['iso_alpha'] = 'IDN'  # Force the ISO code
        fig3 = px.choropleth(
            indonesia_df,
            locations='iso_alpha',
            locationmode='ISO-3',
            color=metric,
            hover_name=country_col,
            color_continuous_scale='viridis',
        )
        # Highlight Indonesia with a bright border
        fig3.update_traces(marker_line_color='red', marker_line_width=2)
        for trace in fig3.data:
            fig.add_trace(trace)
    
    # Modern styling updates
    fig.update_layout(
        # Modern dark theme
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='rgba(255, 255, 255, 0.5)',
            projection_type='miller',  # Changed to miller projection
            showcountries=True,
            countrycolor='rgba(255, 255, 255, 0.3)',
            showland=True,
            landcolor='rgba(80, 80, 80, 0.15)',
            showocean=True,
            oceancolor='rgba(0, 0, 0, 0)',
            showlakes=True,
            lakecolor='rgba(0, 0, 0, 0)',
            bgcolor='rgba(0, 0, 0, 0)',
            # Add center and scope for Asia-Pacific region to better show Indonesia
            center=dict(lon=118, lat=0),  # Indonesia's approximate center
            projection_scale=1.2  # Slight zoom
        ),
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar={
            'title': {'text': metric.capitalize(), 'font': {'color': '#fff'}},
            'tickfont': {'color': '#fff'}
        }
    )
    
    # Update hover template for cleaner appearance
    fig.update_traces(
        hovertemplate=
        "<b>%{hovertext}</b><br>" +
        f"{metric.capitalize()}: %{{z:,.0f}}"
    )
    
    # Use a single colorscale for all traces
    fig.update_layout(coloraxis=dict(colorscale='viridis'))
    for i in range(len(fig.data)):
        fig.data[i].update(coloraxis='coloraxis')
    
    # Display the map
    st.plotly_chart(fig, use_container_width=True)
    
    # Add a bar chart of top countries for comparison
    top_countries = 10
    metric_top_label = "Position" if metric == "position" else f"Top {top_countries} Countries by {metric.capitalize()}"
    
    st.subheader(metric_top_label)
    
    # Sort countries for the bar chart
    if metric == 'position':
        sorted_df = country_df.sort_values(by=metric, ascending=True).head(top_countries)
    else:
        sorted_df = country_df.sort_values(by=metric, ascending=False).head(top_countries)
    
    # Create horizontal bar chart
    bar_fig = px.bar(
        sorted_df,
        y=country_col,
        x=metric,
        orientation='h',
        color=metric,
        color_continuous_scale='viridis',
        labels={country_col: '', metric: metric.capitalize()},
        title=f"Top {top_countries} Countries by {metric.capitalize()}"
    )
    
    # Style the bar chart to match the map
    bar_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title=metric.capitalize(),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis=dict(
            title='',
            showgrid=False
        ),
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    st.plotly_chart(bar_fig, use_container_width=True)

def create_indonesia_map(df, country_col='country', metric='clicks'):
    """Create a special map focused on Indonesia"""
    
    # Check if Indonesia is in the data
    indonesia_data = df[df[country_col].str.contains('Indonesia', case=False, na=False)]
    
    if indonesia_data.empty:
        st.warning("No data for Indonesia found")
        return
    
    # Calculate metric for Indonesia
    indonesia_metric = indonesia_data[metric].sum() if metric != 'ctr' and metric != 'position' else indonesia_data[metric].mean()
    
    # Create a figure with a base map centered on Indonesia
    fig = go.Figure()
    
    # Add a specific marker for Indonesia
    fig.add_trace(go.Scattergeo(
        lon=[117.0],  # Indonesia's approximate longitude
        lat=[-2.5],   # Indonesia's approximate latitude
        text=[f"Indonesia: {indonesia_metric:.2f} {metric}"],
        mode='markers+text',
        marker=dict(
            size=20,
            color='red',
            symbol='star',
        ),
        name='Indonesia'
    ))
    
    # Style the map
    fig.update_layout(
        title=f"{metric.title()} for Indonesia",
        geo=dict(
            scope='asia',
            showland=True,
            landcolor='rgb(217, 217, 217)',
            countrycolor='rgb(255, 255, 255)',
            coastlinewidth=0.5,
            countrywidth=0.5,
            projection_type='mercator',
            center=dict(lon=117, lat=-2.5),  # Center on Indonesia
            projection_scale=5  # Zoom level
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show the actual data
    st.subheader(f"Indonesia {metric.title()} Data")
    st.metric("Total", f"{indonesia_metric:.2f}" if metric in ['ctr', 'position'] else f"{indonesia_metric:,.0f}")

def create_summary_metrics(df):
    """
    Create summary KPI metrics cards
    """
    if df.empty:
        st.warning("No data available for summary metrics")
        return
    
    total_clicks = int(df['clicks'].sum())
    total_impressions = int(df['impressions'].sum())
    avg_ctr = df['ctr'].mean()
    avg_position = df['position'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clicks", f"{total_clicks:,}")
    with col2:
        st.metric("Total Impressions", f"{total_impressions:,}")
    with col3:
        st.metric("Average CTR", f"{avg_ctr:.2f}%")
    with col4:
        st.metric("Average Position", f"{avg_position:.1f}")