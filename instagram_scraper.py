import os
import time
import json
import requests
import pandas as pd
import numpy as np
import streamlit as st
import instaloader
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from PIL import Image
from io import BytesIO

class InstagramAnalyzer:
    """Class to scrape and analyze Instagram profiles"""
    
    def __init__(self, username="apudsi"):
        """Initialize with a target Instagram username"""
        self.username = username
        
        # Create instance of instaloader with improved settings
        self.instance = instaloader.Instaloader(
            download_pictures=False, 
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=3,  # Increase connection attempts
            request_timeout=30,         # Longer timeout
            quiet=False                 # Show more logging information
        )
        
        # Add optional login capability
        self.is_logged_in = False
        
        # File paths for caching
        self.data_dir = "instagram_data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.profile_cache = os.path.join(self.data_dir, f"{username}_profile.json")
        self.posts_cache = os.path.join(self.data_dir, f"{username}_posts.json")
        self.cache_expiry = 24 * 60 * 60  # 24 hours in seconds
        
        # Set default attributes
        self.profile = None
        self.posts = []
    
    # Add a login method to improve access to data
    def login(self, username=None, password=None):
        """
        Login to Instagram to improve crawling capabilities
        
        Args:
            username (str): Instagram username
            password (str): Instagram password
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            if username and password:
                self.instance.login(username, password)
                self.is_logged_in = True
                st.success(f"✅ Logged in as {username}")
                return True
            return False
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False
    
    def get_profile_data(self, use_cache=True, force_refresh=False):
        """
        Retrieve profile data for the Instagram account
        
        Args:
            use_cache (bool): Whether to use cached data if available
            force_refresh (bool): Whether to force refresh data from Instagram
            
        Returns:
            dict: Profile data including follower count, posts count, etc.
        """
        # Check if we should use cached data
        if use_cache and os.path.exists(self.profile_cache) and not force_refresh:
            # Check if cache is still valid
            if time.time() - os.path.getmtime(self.profile_cache) < self.cache_expiry:
                try:
                    with open(self.profile_cache, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    st.warning(f"Error reading cache: {str(e)}. Refreshing data...")
        
        # Need to fetch new data
        with st.spinner(f"Fetching Instagram profile data for @{self.username}..."):
            try:
                # Get profile
                profile = instaloader.Profile.from_username(self.instance.context, self.username)
                
                # Extract relevant data
                profile_data = {
                    "username": profile.username,
                    "full_name": profile.full_name,
                    "biography": profile.biography,
                    "followers": profile.followers,
                    "following": profile.followees,
                    "posts_count": profile.mediacount,
                    "profile_pic_url": profile.profile_pic_url,
                    "is_private": profile.is_private,
                    "is_verified": profile.is_verified,
                    "external_url": profile.external_url,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save to cache
                with open(self.profile_cache, 'w', encoding='utf-8') as f:
                    json.dump(profile_data, f, ensure_ascii=False, indent=2)
                
                # Store profile reference for later use
                self.profile = profile
                
                return profile_data
            
            except Exception as e:
                st.error(f"Error retrieving Instagram profile data: {str(e)}")
                return None
    
    def get_posts_data(self, limit=30, use_cache=True, force_refresh=False):
        """
        Retrieve posts data for the Instagram account
        
        Args:
            limit (int): Maximum number of posts to retrieve
            use_cache (bool): Whether to use cached data if available
            force_refresh (bool): Whether to force refresh data from Instagram
            
        Returns:
            pd.DataFrame: DataFrame with posts data
        """
        # Check if we should use cached data
        if use_cache and os.path.exists(self.posts_cache) and not force_refresh:
            # Check if cache is still valid
            if time.time() - os.path.getmtime(self.posts_cache) < self.cache_expiry:
                try:
                    with open(self.posts_cache, 'r', encoding='utf-8') as f:
                        posts_data = json.load(f)
                    if posts_data:  # Only return if we have data
                        return pd.DataFrame(posts_data)
                    # If cache is empty, we'll fetch fresh data
                except Exception as e:
                    st.warning(f"Error reading cache: {str(e)}. Refreshing data...")
        
        # Need to fetch new data
        with st.spinner(f"Fetching Instagram posts for @{self.username}... This may take a minute."):
            try:
                # Get profile if not already loaded
                if self.profile is None:
                    # Check if the profile is private
                    self.profile = instaloader.Profile.from_username(self.instance.context, self.username)
                    if self.profile.is_private and not self.is_logged_in:
                        st.warning(f"⚠️ @{self.username} is a private account. Login required to access posts.")
                        return pd.DataFrame()
                
                # Get posts
                posts_data = []
                count = 0
                error_count = 0
                max_errors = 5  # Maximum allowed errors before giving up
                
                # Progress bar for scraping
                progress_bar = st.progress(0.0)
                progress_text = st.empty()
                progress_text.text("Loading posts...")
                
                try:
                    # Enable more detailed feedback
                    post_iterator = self.profile.get_posts()
                    
                    for post in post_iterator:
                        try:
                            # Extract post data with better error handling
                            caption = post.caption if hasattr(post, 'caption') else ""
                            likes = post.likes if hasattr(post, 'likes') else 0
                            
                            post_data = {
                                "post_id": post.shortcode,
                                "timestamp": post.date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                                "date": post.date_utc.strftime("%Y-%m-%d"),
                                "likes": likes,
                                "comments": post.comments if hasattr(post, 'comments') else 0,
                                "caption": caption,
                                "hashtags": list(post.caption_hashtags) if caption else [],
                                "mentions": list(post.caption_mentions) if caption else [],
                                "location": post.location.name if hasattr(post, 'location') and post.location else None,
                                "is_video": post.is_video if hasattr(post, 'is_video') else False,
                                "video_duration": post.video_duration if hasattr(post, 'is_video') and post.is_video and hasattr(post, 'video_duration') else None,
                                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                                "image_url": post.url if hasattr(post, 'url') else ""
                            }
                            
                            posts_data.append(post_data)
                            count += 1
                            
                            # Update progress
                            progress = min(count / limit, 1.0)
                            progress_bar.progress(progress)
                            progress_text.text(f"Loading posts... {count}/{limit}")
                            
                            if count >= limit:
                                break
                                
                        except Exception as post_error:
                            error_count += 1
                            st.warning(f"Error processing post {count+1}: {str(post_error)}")
                            if error_count >= max_errors:
                                st.error(f"Too many errors ({error_count}). Stopping post collection.")
                                break
                            continue
                                
                except Exception as iter_error:
                    st.error(f"Error iterating through posts: {str(iter_error)}")
                
                # Clear progress indicators
                progress_bar.empty()
                progress_text.empty()
                
                # If we got any posts, save to cache
                if posts_data:
                    with open(self.posts_cache, 'w', encoding='utf-8') as f:
                        json.dump(posts_data, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"✅ Retrieved {count} posts from @{self.username}")
                    return pd.DataFrame(posts_data)
                else:
                    st.warning(f"No posts could be retrieved from @{self.username}")
                    return pd.DataFrame()
            
            except instaloader.exceptions.ProfileNotExistsException:
                st.error(f"Profile @{self.username} does not exist.")
                return pd.DataFrame()
            except instaloader.exceptions.LoginRequiredException:
                st.error(f"Login required to access @{self.username}'s content.")
                return pd.DataFrame()
            except instaloader.exceptions.ConnectionException as e:
                st.error(f"Connection error: {str(e)}")
                st.info("Instagram might be rate-limiting your requests. Try again later.")
                return pd.DataFrame()
            except Exception as e:
                st.error(f"Error retrieving Instagram posts: {str(e)}")
                return pd.DataFrame()
    
    def analyze_engagement(self, posts_df):
        """
        Analyze engagement metrics from posts
        
        Args:
            posts_df (pd.DataFrame): DataFrame with posts data
            
        Returns:
            dict: Dictionary with engagement metrics
        """
        if posts_df.empty:
            return {}
        
        try:
            # Basic engagement metrics
            total_likes = posts_df['likes'].sum()
            total_comments = posts_df['comments'].sum()
            total_posts = len(posts_df)
            
            avg_likes = total_likes / total_posts if total_posts > 0 else 0
            avg_comments = total_comments / total_posts if total_posts > 0 else 0
            
            # Calculate engagement rate (assuming profile data is available)
            profile_data = self.get_profile_data()
            followers = profile_data.get('followers', 0) if profile_data else 0
            
            engagement_rate = ((total_likes + total_comments) / (followers * total_posts)) * 100 if followers * total_posts > 0 else 0
            
            # Time series analysis - convert timestamp to datetime
            posts_df['datetime'] = pd.to_datetime(posts_df['timestamp'])
            
            # Group by date
            daily_stats = posts_df.groupby(posts_df['datetime'].dt.date).agg({
                'likes': 'sum',
                'comments': 'sum',
                'post_id': 'count'
            }).rename(columns={'post_id': 'posts'}).reset_index()
            
            # Best day of week for engagement
            posts_df['day_of_week'] = posts_df['datetime'].dt.day_name()
            day_stats = posts_df.groupby('day_of_week').agg({
                'likes': ['sum', 'mean'],
                'comments': ['sum', 'mean'],
            })
            
            # Find best day for engagement
            day_stats['total_engagement'] = day_stats[('likes', 'sum')] + day_stats[('comments', 'sum')]
            best_day = day_stats['total_engagement'].idxmax()
            
            return {
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_posts': total_posts,
                'avg_likes_per_post': round(avg_likes, 2),
                'avg_comments_per_post': round(avg_comments, 2),
                'engagement_rate': round(engagement_rate, 2),
                'best_day': best_day,
                'daily_stats': daily_stats,
                'day_stats': day_stats
            }
            
        except Exception as e:
            st.error(f"Error analyzing engagement: {str(e)}")
            return {}
    
    def analyze_hashtags(self, posts_df):
        """
        Analyze hashtags used in posts
        
        Args:
            posts_df (pd.DataFrame): DataFrame with posts data
            
        Returns:
            dict: Dictionary with hashtag analysis
        """
        if posts_df.empty:
            return {}
            
        try:
            # Collect all hashtags from all posts
            all_hashtags = []
            for hashtags in posts_df['hashtags']:
                all_hashtags.extend(hashtags)
            
            # Count hashtag occurrences
            hashtag_counts = Counter(all_hashtags)
            
            # Most common hashtags
            top_hashtags = hashtag_counts.most_common(20)
            
            # Convert to DataFrame for easier visualization
            hashtags_df = pd.DataFrame(top_hashtags, columns=['hashtag', 'count'])
            
            return {
                'hashtag_counts': dict(hashtag_counts),
                'top_hashtags': top_hashtags,
                'hashtags_df': hashtags_df,
                'total_unique_hashtags': len(hashtag_counts),
                'avg_hashtags_per_post': round(len(all_hashtags) / len(posts_df), 2) if len(posts_df) > 0 else 0
            }
            
        except Exception as e:
            st.error(f"Error analyzing hashtags: {str(e)}")
            return {}
    
    def generate_visualizations(self, posts_df, engagement_data, hashtag_data):
        """
        Generate visualizations for Instagram data
        
        Args:
            posts_df (pd.DataFrame): DataFrame with posts data
            engagement_data (dict): Dictionary with engagement metrics
            hashtag_data (dict): Dictionary with hashtag analysis
            
        Returns:
            dict: Dictionary with visualization figures
        """
        visualizations = {}
        
        try:
            # Only proceed if we have data
            if posts_df.empty:
                return visualizations
            
            # 1. Engagement over time
            if 'daily_stats' in engagement_data:
                daily_stats = engagement_data['daily_stats']
                daily_stats['total_engagement'] = daily_stats['likes'] + daily_stats['comments']
                
                fig = plt.figure(figsize=(10, 6))
                plt.plot(daily_stats['datetime'], daily_stats['likes'], 'b-', label='Likes')
                plt.plot(daily_stats['datetime'], daily_stats['comments'], 'r-', label='Comments')
                plt.title('Engagement Over Time')
                plt.xlabel('Date')
                plt.ylabel('Count')
                plt.legend()
                plt.tight_layout()
                visualizations['engagement_over_time'] = fig
            
            # 2. Hashtag Word Cloud
            if 'hashtag_counts' in hashtag_data and hashtag_data['hashtag_counts']:
                hashtag_counts = hashtag_data['hashtag_counts']
                
                fig = plt.figure(figsize=(10, 6))
                wordcloud = WordCloud(width=800, height=400, background_color='white',
                                    colormap='viridis', max_words=100).generate_from_frequencies(hashtag_counts)
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('Hashtag Analysis')
                plt.tight_layout()
                visualizations['hashtag_wordcloud'] = fig
            
            # 3. Top Hashtags Bar Chart
            if 'hashtags_df' in hashtag_data and not hashtag_data['hashtags_df'].empty:
                hashtags_df = hashtag_data['hashtags_df'].head(10)  # Top 10
                
                fig = plt.figure(figsize=(10, 6))
                plt.barh(hashtags_df['hashtag'], hashtags_df['count'])
                plt.title('Top 10 Hashtags')
                plt.xlabel('Count')
                plt.ylabel('Hashtag')
                plt.tight_layout()
                visualizations['top_hashtags'] = fig
            
            # 4. Post Type Distribution (Video vs Photo)
            video_count = posts_df['is_video'].sum()
            photo_count = len(posts_df) - video_count
            
            fig = plt.figure(figsize=(8, 8))
            plt.pie([photo_count, video_count], labels=['Photos', 'Videos'], autopct='%1.1f%%')
            plt.title('Content Type Distribution')
            plt.tight_layout()
            visualizations['content_type'] = fig
            
            # 5. Day of Week Analysis
            if 'day_stats' in engagement_data:
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_engagement = engagement_data['day_stats'][('likes', 'mean')].reindex(day_order)
                
                fig = plt.figure(figsize=(10, 6))
                plt.bar(day_engagement.index, day_engagement.values)
                plt.title('Average Likes by Day of Week')
                plt.xlabel('Day of Week')
                plt.ylabel('Average Likes')
                plt.xticks(rotation=45)
                plt.tight_layout()
                visualizations['day_analysis'] = fig
                
        except Exception as e:
            st.error(f"Error generating visualizations: {str(e)}")
        
        return visualizations

# Function to help integrate with the main app
def load_instagram_data(username="apudsi"):
    """
    Load Instagram data for analysis
    
    Args:
        username (str): Instagram username to analyze
        
    Returns:
        tuple: (profile_data, posts_df, engagement_data, hashtag_data, visualizations)
    """
    try:
        # Initialize analyzer
        analyzer = InstagramAnalyzer(username)
        
        # Optional login section (uncomment to enable)
        # login_col1, login_col2 = st.columns(2)
        # with login_col1:
        #     insta_username = st.text_input("Instagram Username (optional)", key="insta_username")
        # with login_col2:
        #     insta_password = st.text_input("Instagram Password", type="password", key="insta_password")
        # if insta_username and insta_password:
        #     analyzer.login(insta_username, insta_password)
        
        # Get profile data
        profile_data = analyzer.get_profile_data()
        if not profile_data:
            st.error(f"Could not retrieve profile data for @{username}")
            st.info("This may be due to:  \n1. The profile doesn't exist  \n2. Instagram is blocking automated access  \n3. Network connectivity issues")
            return None, None, None, None, None
        
        # Get posts data with retries
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            posts_df = analyzer.get_posts_data(limit=50)
            if not posts_df.empty:
                break
            if attempt < max_attempts:
                st.warning(f"Attempt {attempt} failed. Retrying...")
                time.sleep(2)  # Wait between attempts
        
        if posts_df.empty:
            st.warning(f"Could not retrieve any posts for @{username} after {max_attempts} attempts")
            st.info("Possible reasons:  \n1. The account is private  \n2. The account has no posts  \n3. Instagram is blocking access (try logging in)  \n4. Rate limits have been reached")
            return profile_data, pd.DataFrame(), None, None, None
        
        # Analyze data
        engagement_data = analyzer.analyze_engagement(posts_df)
        hashtag_data = analyzer.analyze_hashtags(posts_df)
        
        # Generate visualizations
        visualizations = analyzer.generate_visualizations(posts_df, engagement_data, hashtag_data)
        
        return profile_data, posts_df, engagement_data, hashtag_data, visualizations
        
    except Exception as e:
        st.error(f"Error loading Instagram data: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None, None, None, None, None
