import os
import pickle
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# OAuth2 scopes required for Google Search Console API
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# Path for storing OAuth credentials
TOKEN_PATH = 'token.pickle'

def get_search_console_service():
    """
    Get an authorized Google Search Console API service instance using OAuth2
    Based on Google's quickstart guide
    
    Returns:
        Google Search Console API service or None if authentication fails
    """
    # Check if we have stored credentials in session state
    if 'gsc_service' in st.session_state:
        return st.session_state.gsc_service
        
    creds = None
    
    # Load credentials from file if it exists
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            st.error(f"Error loading credentials: {e}")
    
    # If no credentials available or if they're invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                st.success("✅ Credentials refreshed successfully")
            except Exception as e:
                st.error(f"Error refreshing credentials: {e}")
                creds = None
        else:
            # Need to get new credentials through the OAuth flow
            try:
                # Create OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', SCOPES)
                
                # In Streamlit, we need to handle the auth flow differently
                # since we can't directly open a browser from server
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                st.markdown("### Google Search Console API Authentication")
                st.info("You need to authenticate with Google Search Console")
                
                st.markdown(f"""
                1. Click this link to authenticate: [Authenticate with Google]({auth_url})
                2. After allowing access, you'll receive an authorization code
                3. Copy the code and paste it below
                """)
                
                # Show a text input for the authorization code
                auth_code = st.text_input("Enter the authorization code:")
                
                if auth_code:
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                    
                    # Save the credentials for the next run
                    with open(TOKEN_PATH, 'wb') as token:
                        pickle.dump(creds, token)
                        
                    st.success("✅ Authentication successful")
                    st.rerun()  # Changed from st.rerun()
                else:
                    return None
                    
            except Exception as e:
                st.error(f"Authentication Error: {e}")
                return None
    
    try:
        # Build and return the service
        service = build('webmasters', 'v3', credentials=creds)
        
        # Test the API with a simple call
        sites = service.sites().list().execute()
        
        # Store in session state
        st.session_state.gsc_service = service
        
        return service
        
    except Exception as e:
        st.error(f"Error building service: {e}")
        return None

def get_site_list(service):
    """
    Get list of sites available in Google Search Console
    """
    if service is None:
        return []
    
    try:
        sites = service.sites().list().execute()
        site_entries = sites.get('siteEntry', [])
        
        if not site_entries:
            st.warning("No sites found. Make sure your Google account has access to GSC properties.")
            return []
            
        return [s['siteUrl'] for s in site_entries]
        
    except Exception as e:
        st.error(f"Error fetching site list: {str(e)}")
        return []
