from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import streamlit as st
import json

# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = 'service-account-key.json'

def authenticate_gsc(use_stored=False):
    """
    Authenticate with Google Search Console API using service account credentials
    
    Parameters:
    - use_stored: If True, only use stored credentials without showing UI components
    
    Returns the authenticated service or None if authentication fails
    """
    try:
        # Try to get credentials from session state if already authenticated
        if 'gsc_service' in st.session_state:
            return st.session_state.gsc_service
        
        if use_stored and os.path.exists(SERVICE_ACCOUNT_FILE):
            # Use stored credentials without UI
            try:
                SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
                credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
                service = build('webmasters', 'v3', credentials=credentials)
                
                # Test the authentication with a simple API call
                service.sites().list().execute()
                
                # Save in session state for future use
                st.session_state.gsc_service = service
                return service
                
            except Exception as auth_error:
                if not use_stored:
                    st.error(f"Failed to authenticate with stored credentials: {str(auth_error)}")
                return None
        elif use_stored:
            # If use_stored=True but no credentials file exists
            return None
        
        # Check if we want to use the file uploader or stored credentials
        use_stored_credentials = st.checkbox("Use stored service account credentials", value=True)
        
        if use_stored_credentials and os.path.exists(SERVICE_ACCOUNT_FILE):
            # Use stored credentials
            try:
                SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
                credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
                service = build('webmasters', 'v3', credentials=credentials)
                
                # Test the authentication with a simple API call
                try:
                    service.sites().list().execute()
                    st.success("✅ Authentication successful using stored credentials!")
                except HttpError as e:
                    error_details = json.loads(e.content.decode())
                    error_reason = error_details.get('error', {}).get('message', 'Unknown error')
                    st.error(f"API Error: {error_reason}")
                    st.info("Make sure your service account has proper access to your GSC properties")
                    return None
                
                # Save in session state for future use
                st.session_state.gsc_service = service
                return service
                
            except Exception as auth_error:
                st.error(f"Failed to authenticate with stored credentials: {str(auth_error)}")
                st.info("Falling back to file upload method")
        
        if not use_stored_credentials or not os.path.exists(SERVICE_ACCOUNT_FILE):
            # Use file uploader method
            uploaded_file = st.file_uploader("Upload Google Search Console API credentials JSON file", type=['json'])
            
            if uploaded_file:
                # Save the uploaded file temporarily
                with open('temp_credentials.json', 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Authenticate using the credentials
                SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
                
                try:
                    credentials = ServiceAccountCredentials.from_json_keyfile_name('temp_credentials.json', SCOPES)
                    service = build('webmasters', 'v3', credentials=credentials)
                    
                    # Test the authentication with a simple API call
                    try:
                        service.sites().list().execute()
                        st.success("✅ Authentication successful!")
                    except HttpError as e:
                        error_details = json.loads(e.content.decode())
                        error_reason = error_details.get('error', {}).get('message', 'Unknown error')
                        st.error(f"API Error: {error_reason}")
                        st.info("Make sure your service account has proper access to your GSC properties")
                        return None
                    
                    # Save in session state for future use
                    st.session_state.gsc_service = service
                    
                    # Option to save the credentials for future use
                    save_credentials = st.checkbox("Save these credentials for future use")
                    if save_credentials:
                        with open(SERVICE_ACCOUNT_FILE, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        st.success(f"Credentials saved to {SERVICE_ACCOUNT_FILE}")
                    
                    # Clean up temporary file
                    os.remove('temp_credentials.json')
                    
                    return service
                except Exception as auth_error:
                    st.error(f"Failed to authenticate: {str(auth_error)}")
                    st.info("Check that your credentials file is valid and has the correct format")
                    return None
            else:
                st.info("Please upload your Google Search Console API credentials to continue")
                
                with st.expander("ℹ️ How to get Google Search Console API credentials"):
                    st.markdown("""
                    1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
                    2. Create a new project or select an existing one
                    3. Enable the "Search Console API" in the API Library
                    4. Go to "Credentials" and create a service account
                    5. Create a new JSON key for this service account
                    6. Download the JSON file
                    7. Add the service account email to your Google Search Console property with "Owner" or "Full User" permissions
                    """)
                
                return None
                
    except Exception as e:
        if not use_stored:
            st.error(f"Authentication Error: {str(e)}")
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
            st.warning("No sites found. Make sure your service account has access to your GSC properties.")
            st.info("To grant access: Go to GSC > Settings > Users and permissions > Add user")
            return []
            
        return [s['siteUrl'] for s in site_entries]
    except HttpError as e:
        error_details = json.loads(e.content.decode())
        error_reason = error_details.get('error', {}).get('message', 'Unknown error')
        st.error(f"API Error when fetching sites: {error_reason}")
        return []
    except Exception as e:
        st.error(f"Error fetching site list: {str(e)}")
        return []
