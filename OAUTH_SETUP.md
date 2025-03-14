# Setting Up OAuth Credentials for Google Search Console Dashboard

Follow these steps to set up OAuth credentials for the dashboard to connect to your Google Search Console data.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one

## Step 2: Enable the Search Console API

1. In your Google Cloud project, navigate to "APIs & Services" > "Library"
2. Search for "Search Console API"
3. Click on the API and click "Enable"

## Step 3: Set Up OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. You may need to configure the OAuth consent screen first:
   - User Type: External (or Internal if you have Google Workspace)
   - App name: "GSC Analytics Dashboard" (or your preferred name)
   - User support email: your email
   - Developer contact information: your email
   - Authorized domains: (leave empty for testing)
   - App logo: (optional)

4. Return to "Create credentials" > "OAuth client ID"
   - Application type: "Desktop app" or "Web application"
   - Name: "GSC Analytics Dashboard"
   - If Web application, add Authorized redirect URIs including:
     - `http://localhost:8501/`
     - `https://localhost:8501/`

5. Click "Create" and download the JSON file
6. Rename the downloaded file to `client_secrets.json`
7. Place this file in the root directory of the dashboard application

## Step 4: Run the Application

1. Run the dashboard application:
   ```bash
   streamlit run app.py
   ```

2. The app will provide authentication instructions
3. Follow the link to authenticate with your Google account
4. Paste the provided code back into the app
5. Your credentials will be saved for future sessions

## Notes

- The app stores OAuth tokens in a file called `token.pickle`
- If you need to re-authenticate, delete this file
- For production use, implement more secure token storage
