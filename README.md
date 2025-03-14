# Google Search Console Analytics Dashboard

A Streamlit dashboard for visualizing Google Search Console analytics data.

## Features

- Connect directly to Google Search Console API using service account
- Visualize key metrics: clicks, impressions, CTR, and average position
- Analyze top performing content (queries, pages)
- Geographic analysis with interactive maps
- Device breakdown analysis
- Advanced filters and query parameters
- Search appearance and search type analysis
- Raw data export

## Setup Instructions

### Prerequisites

- Python 3.7+
- Google Search Console API service account credentials
- Access to Google Search Console data

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd apudsi-analisis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Prepare your service account credentials:
   - Ensure your Google Cloud Project has the Search Console API enabled
   - Make sure your service account has the proper permissions in GSC
   - Download your service account JSON credentials file
   - Have it ready to upload when you run the dashboard

4. Run the application:
   ```bash
   streamlit run app.py
   ```

5. Upload your Google Search Console API credentials when prompted

## Using Your Service Account

This dashboard uses service account authentication to connect to the Google Search Console API. Here's how to use your existing service account:

### Step 1: Prepare Your Service Account

1. Ensure your service account is properly set up in Google Cloud Console:
   - The project has the Search Console API enabled
   - The service account has a JSON key file that you've downloaded
   - The service account email has been added to your Google Search Console properties with appropriate permissions

### Step 2: Upload Your Credentials

1. Run the dashboard application:
   ```bash
   streamlit run app.py
   ```

2. In the sidebar, under "1. Authentication", you'll see a file uploader that says:
   "Upload Google Search Console API credentials JSON file"

3. Click on this uploader and select your service account JSON key file

4. The application will authenticate with Google Search Console API and show a success message if the credentials are valid

5. After successful authentication, you'll see your GSC properties in the website dropdown

### Step 3: Verify Access

If you encounter authentication errors or don't see your websites in the dropdown:

1. Verify that your service account email (found in your JSON file under `client_email`) has been added as a user to your GSC properties
2. In Google Search Console, go to Settings > Users and permissions
3. Make sure the service account email is listed and has "Owner" or "Full User" permissions
4. If you need to add the service account, click "Add User", enter the service account email address, and grant appropriate permissions

## Authentication Method

This dashboard uses service account authentication to connect to the Google Search Console API:

1. **Service Account Authentication**
   - Requires a service account JSON credentials file
   - The service account must have access to your GSC properties
   - Upload the JSON file when prompted by the application
   - More secure for production use cases

2. **Mock Mode (For Testing)**
   - Run with `--mock` flag to use mock data
   - No authentication needed
   - Useful for testing the dashboard functionality

## Testing the Connection and Visualizations

### Step 1: Test the API Connection

1. **Set up proper API credentials:**
   - Ensure your Google Search Console API is enabled in Google Cloud Console
   - Verify your service account has the correct permissions
   - Make sure you've downloaded the JSON credentials file

2. **Run the application:**
   ```bash
   cd c:\laragon\www\git\apudsi-analisis
   streamlit run app.py
   ```

3. **Test authentication:**
   - Upload your credentials JSON file through the file uploader in the sidebar
   - The app should display a success message upon successful authentication
   - You should see your websites appear in the dropdown menu

4. **Check API connectivity:**
   - If your websites appear in the dropdown, the API connection is working
   - If you see an error, check the error message for specific API issues

### Step 2: Test Data Retrieval

1. **Configure query parameters:**
   - Select a website from the dropdown
   - Choose a date range with known data (start with a small range like 7 days)
   - Select dimensions (include at least "Date", "Query", "Page")
   - Click "Load Data"

2. **Verify data is loaded:**
   - Check the "Raw Data" tab to see if your search console data appears
   - Confirm that the data includes the columns you selected as dimensions
   - Verify that metrics (clicks, impressions, CTR, position) are present

### Step 3: Test Advanced API Features

1. **Test different search types:**
   - Expand the "Advanced Options" section
   - Try different search types like Image Search or Video Search
   - Verify that the data changes appropriately

2. **Apply dimension filters:**
   - Expand the "Add Filters" section
   - Create filters for specific queries or pages
   - Verify that the results are filtered correctly

3. **Change aggregation types:**
   - Experiment with different aggregation types
   - Compare results between "byPage" and "byProperty" aggregations

### Step 4: Test Visualizations

1. **Overview tab:**
   - Check that summary metrics (total clicks, impressions, etc.) appear
   - Verify that all four trend charts (clicks, impressions, CTR, position) display properly
   - Confirm that the date range in the charts matches your selected period

2. **Top Content tab:**
   - Test different metrics (clicks, impressions, CTR, position) using the dropdown
   - Adjust the number of items slider and verify the charts update
   - Check that both queries and pages visualizations show data correctly

3. **Geographic tab:**
   - Verify that the world map shows data by country
   - Test switching between different metrics and ensure the map updates
   - Confirm that the top countries list displays correctly

4. **Device Analysis tab:**
   - Check that the pie chart shows device distribution
   - Verify that the device metrics table shows correct data
   - Test switching between clicks and impressions metrics

### Step 5: Test Data Export

1. Click the "Download Data as CSV" button on the Raw Data tab
2. Open the CSV file to verify all data was exported correctly

## Troubleshooting Connection Issues

- **Authentication Error**: 
  - Verify that your JSON credentials file is valid and not expired
  - Check that the service account has the necessary permissions

- **"No sites available" Error**: 
  - Make sure your service account email is added to your GSC properties with correct permissions
  - Go to GSC > Settings > Users and Permissions to verify access

- **Empty Data Results**:
  - Ensure your selected website has data for the chosen date range
  - Try expanding the date range if you see no data
  - Verify that you've selected appropriate dimensions

- **API Quota Exceeded**:
  - GSC API has usage limits - reduce your date range or the number of dimensions
  - Wait a few minutes and try again if you hit rate limits

- **Visualization Errors**:
  - If charts don't display correctly, check the browser console for JavaScript errors
  - Try selecting a smaller dataset (shorter date range) to see if that resolves rendering issues

## Usage

1. Upload your Google Search Console API credentials JSON file
2. Select your website from the dropdown
3. Choose a date range
4. Select dimensions to analyze
5. Click "Load Data" to fetch and visualize your Search Console data

## Notes

- The Google Search Console API has rate limits. If you hit these limits, wait before making additional requests.
- For large sites, consider using more specific date ranges to reduce data volume.

## License

[MIT License](LICENSE)
