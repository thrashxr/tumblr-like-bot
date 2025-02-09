#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import time
import schedule
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger
import pytumblr

class TumblrLikeBot:
    def __init__(self, auto_update_cache=False):
        self.load_config()
        self.setup_logging()
        self.setup_client()
        self.like_count = {'hour': 0, 'day': 0}
        self.last_reset = {'hour': datetime.now(), 'day': datetime.now()}
        self.stats = {
            'total_likes': 0,
            'errors': 0,
            'current_tag': None,
            'last_like': None,
            'skipped_posts': 0
        }
        self.stop_requested = False
        self.liked_posts_cache = set()  # Set to store liked post IDs
        self.cache_file = os.path.join(os.path.dirname(__file__), 'data', 'liked_posts_cache.txt')
        self.load_cache()  # Load local cache
        
        if auto_update_cache:
            self.update_liked_posts_cache()  # Load recent likes from API

    def load_config(self):
        """Load configuration file"""
        load_dotenv()
        
        # Config file path
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.credentials = {
            'consumer_key': os.getenv('TUMBLR_CONSUMER_KEY'),
            'consumer_secret': os.getenv('TUMBLR_CONSUMER_SECRET'),
            'oauth_token': os.getenv('TUMBLR_OAUTH_TOKEN'),
            'oauth_secret': os.getenv('TUMBLR_OAUTH_SECRET')
        }

    def setup_logging(self):
        """Configure logging settings"""
        log_config = self.config['logging']
        
        # Create logs directory
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Log file path
        log_path = os.path.join(log_dir, os.path.basename(log_config['file']))
        
        logger.add(
            log_path,
            level=log_config['level'],
            rotation=log_config['max_size'],
            retention=log_config['backup_count']
        )

    def setup_client(self):
        """Initialize Tumblr API client"""
        # Check credentials
        for key, value in self.credentials.items():
            if not value:
                raise ValueError(f"Missing API key: {key}")
            logger.debug(f"{key}: {value[:5]}...")  # Show only first 5 chars for security
        
        try:
            self.client = pytumblr.TumblrRestClient(
                self.credentials['consumer_key'],
                self.credentials['consumer_secret'],
                self.credentials['oauth_token'],
                self.credentials['oauth_secret']
            )
            
            # Test API connection
            user_info = self.client.info()
            if user_info and 'user' in user_info:
                logger.info(f"API connection successful! User: {user_info['user'].get('name', 'Unknown')}")
            else:
                raise Exception("API responded but user info not found")
                
        except Exception as e:
            logger.error(f"API connection error: {str(e)}")
            raise

    def is_within_working_hours(self):
        """Check if current time is within working hours"""
        try:
            # If working hours are disabled, always return True
            if not self.config['timing'].get('enable_work_hours', True):
                return True
                
            now = datetime.now().time()
            start = datetime.strptime(self.config['timing']['start_time'], '%H:%M').time()
            end = datetime.strptime(self.config['timing']['end_time'], '%H:%M').time()
            
            # If end time is less than start time (e.g., 23:00-06:00)
            if end < start:
                return now >= start or now <= end
            
            return start <= now <= end
        except Exception as e:
            logger.error(f"Time check error: {str(e)}")
            return False

    def wait_until_working_hours(self):
        """Wait if outside working hours"""
        # If working hours are disabled, don't wait
        if not self.config['timing'].get('enable_work_hours', True):
            return False
            
        if not self.is_within_working_hours():
            next_start = datetime.strptime(self.config['timing']['start_time'], '%H:%M').time()
            now = datetime.now()
            next_run = datetime.combine(
                (now + timedelta(days=1)).date() if now.time() > next_start else now.date(),
                next_start
            )
            
            wait_seconds = (next_run - now).total_seconds()
            logger.info(f"Outside working hours. Waiting until {self.config['timing']['start_time']} ({wait_seconds/3600:.2f} hours)")
            time.sleep(wait_seconds)
            return True
        return False

    def check_limits(self):
        """Check like limits"""
        current_time = datetime.now()
        
        # Check hourly limit
        hour_diff = (current_time - self.last_reset['hour']).total_seconds() / 3600
        if hour_diff >= 1:
            self.like_count['hour'] = 0
            self.last_reset['hour'] = current_time
        
        # Check daily limit
        day_diff = (current_time - self.last_reset['day']).total_seconds() / 86400
        if day_diff >= 1:
            self.like_count['day'] = 0
            self.last_reset['day'] = current_time
        
        return (
            self.like_count['hour'] < self.config['like_settings']['max_likes_per_hour'] and
            self.like_count['day'] < self.config['like_settings']['max_likes_per_day']
        )

    def load_cache(self):
        """Load liked post IDs from local cache file"""
        try:
            # Create data directory
            cache_dir = os.path.dirname(self.cache_file)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            
            # Load cache if exists
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cached_ids = f.read().splitlines()
                self.liked_posts_cache.update(cached_ids)
                logger.info(f"Local cache loaded: {len(self.liked_posts_cache)} posts")
            else:
                logger.info("Local cache not found, creating new cache")
        
        except Exception as e:
            logger.error(f"Cache loading error: {str(e)}")

    def save_cache(self):
        """Save liked post IDs to local cache file"""
        try:
            with open(self.cache_file, 'w') as f:
                f.write('\n'.join(self.liked_posts_cache))
            logger.debug(f"Cache updated: {len(self.liked_posts_cache)} posts saved")
        except Exception as e:
            logger.error(f"Cache saving error: {str(e)}")

    def update_liked_posts_cache(self):
        """Fetch liked posts from API and update cache"""
        try:
            offset = 0
            total_likes = 0
            processed_count = 0
            initial_cache_size = len(self.liked_posts_cache)
            
            logger.info("Loading recent likes...")
            
            while True:
                # Get liked posts from API
                response = self.client.likes(limit=20, offset=offset)
                
                if not response or 'liked_posts' not in response:
                    break
                
                # Get total likes count from first response
                if offset == 0:
                    total_likes = response.get('liked_count', 0)
                    logger.info(f"Found {total_likes} total likes (Loading last 1000 likes)")
                
                # Add post IDs to cache
                for post in response['liked_posts']:
                    self.liked_posts_cache.add(str(post['id']))
                    processed_count += 1
                
                # Show progress every 200 posts
                if processed_count % 200 == 0:
                    logger.debug(f"Processed posts: {processed_count}/1000")
                
                # Move to next page
                offset += 20
                
                # Check maximum 1000 posts (API limit)
                if offset >= 1000:
                    break
            
            # Calculate new posts count
            new_posts = len(self.liked_posts_cache) - initial_cache_size
            
            if total_likes > 1000:
                logger.warning(f"WARNING: You have {total_likes} likes, but only last 1000 could be loaded due to API limitation")
                logger.info("Previous likes will be checked from local cache")
            
            logger.info(f"Cache updated: {new_posts} new posts added (Total: {len(self.liked_posts_cache)})")
            
            # Save cache
            self.save_cache()
            
        except Exception as e:
            logger.error(f"Cache update error: {str(e)}")

    def is_post_liked(self, post_id):
        """Check if post was liked before"""
        return str(post_id) in self.liked_posts_cache

    def process_tag(self, tag):
        """Process posts for a specific tag"""
        try:
            if not tag:
                logger.warning("Empty tag skipped")
                return True
                
            self.stats['current_tag'] = tag
            encoded_tag = self.encode_tag(tag)
            logger.info(f"Processing tag '{tag}'... (encoded: {encoded_tag})")
            
            try:
                # Get posts from API
                posts = self.client.tagged(encoded_tag)
                if posts is None:
                    logger.error(f"API did not respond: {encoded_tag}")
                    return False
                    
                # Log post count
                post_count = len(posts) if posts else 0
                logger.info(f"Found {post_count} posts for tag '{tag}'")
                    
            except Exception as api_error:
                logger.error(f"API call error: {str(api_error)}")
                return False
            
            # Check API response
            if not posts:
                logger.warning(f"No posts found for tag '{tag}'")
                return True
            
            processed_count = 0
            skipped_count = 0  # Skipped posts count
            for post in posts:
                # Check post
                if not isinstance(post, dict):
                    logger.warning(f"Invalid post format: {type(post)}")
                    continue
                    
                # Check required fields
                if 'type' not in post or 'blog_name' not in post:
                    logger.warning("Missing required fields in post")
                    continue

                # Check if already liked
                if self.is_post_liked(post['id']):
                    logger.debug(f"Post already liked, skipping: {post['id']}")
                    skipped_count += 1
                    self.stats['skipped_posts'] += 1
                    continue
                
                # Check working hours
                if not self.is_within_working_hours():
                    logger.info("Outside working hours")
                    return False

                if not self.check_limits():
                    logger.warning("Like limits reached")
                    return False
                
                # Check content type
                if post['type'] not in self.config['like_settings']['content_types']:
                    logger.debug(f"Content type mismatch: {post['type']}")
                    continue
                
                # Check minimum notes
                note_count = post.get('note_count', 0)
                if note_count < self.config['like_settings']['min_notes']:
                    logger.debug(f"Insufficient notes count: {note_count}")
                    continue
                
                # Check blog blacklist
                if post['blog_name'] in self.config['like_settings']['blog_blacklist']:
                    logger.debug(f"Blog in blacklist: {post['blog_name']}")
                    continue
                
                # Like post
                if self.like_post(post['id'], post.get('reblog_key', '')):
                    processed_count += 1
                    time.sleep(self.config['timing']['delay_between_likes'])
            
            logger.info(f"Tag '{tag}': {processed_count} posts processed, {skipped_count} posts skipped")
            return True
            
        except Exception as e:
            logger.error(f"Tag processing error ({tag}): {str(e)}")
            return False

    def run(self):
        """Run the bot"""
        logger.info("Starting bot...")
        self.stop_requested = False
        
        while not self.stop_requested:
            try:
                # Check working hours
                self.wait_until_working_hours()
                
                for tag in self.config['like_settings']['tags']:
                    if self.stop_requested:
                        break
                        
                    if not self.process_tag(tag):
                        break
                
                if self.stop_requested:
                    break
                    
                logger.info(f"Entering rest mode ({self.config['timing']['rest_time']} seconds)")
                time.sleep(self.config['timing']['rest_time'])
            
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                time.sleep(60)  # Wait 1 minute on error
        
        logger.info("Bot stopped")

    def encode_tag(self, tag):
        """Convert tag to URL-safe format"""
        if not isinstance(tag, str):
            raise ValueError(f"Invalid tag format: {type(tag)}")
            
        # Turkish character conversions
        tr_chars = {
            'ı': 'i', 'İ': 'I',
            'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U',
            'ş': 's', 'Ş': 'S',
            'ö': 'o', 'Ö': 'O',
            'ç': 'c', 'Ç': 'C',
            'â': 'a', 'Â': 'A',
            'î': 'i', 'Î': 'I',
            'û': 'u', 'Û': 'U'
        }
        
        # First convert Turkish characters
        for tr_char, eng_char in tr_chars.items():
            tag = tag.replace(tr_char, eng_char)
            
        # Apply URL encoding
        encoded_tag = urllib.parse.quote(tag)
        logger.debug(f"Tag converted: {tag} -> {encoded_tag}")
        return encoded_tag

    def like_post(self, post_id, reblog_key):
        """Like a post"""
        try:
            self.client.like(post_id, reblog_key)
            self.like_count['hour'] += 1
            self.like_count['day'] += 1
            self.stats['total_likes'] += 1
            self.stats['last_like'] = datetime.now()
            
            # Add new like to cache and save
            self.liked_posts_cache.add(str(post_id))
            self.save_cache()
            
            logger.info(f"Post liked: {post_id}")
            return True
        except Exception as e:
            logger.error(f"Like error: {str(e)}")
            self.stats['errors'] += 1
            return False

if __name__ == "__main__":
    bot = TumblrLikeBot()
    bot.run() 