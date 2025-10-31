import praw
import json
import time
import os
from datetime import datetime

# Keywords to search for
KEYWORDS = ["depression", "community", "anxiety", "therapy", "hikikomori", "healing"]

# Initialize Reddit API client
def initialize_reddit():
    return praw.Reddit(
        client_id="your_client_id",
        client_secret="your_client_secret",
        user_agent="script:omori_data_extractor:v1.0 (by u/YOUR_USERNAME)",
        username="YOUR_USERNAME",  # Optional, only if using authenticated features
        password="YOUR_PASSWORD"   # Optional, only if using authenticated features
    )

def contains_keywords(text):
    """Check if any keyword is in the text."""
    if not text:
        return False
    text = text.lower()
    return any(keyword.lower() in text for keyword in KEYWORDS)

def extract_post_data(post):
    """Extract relevant metadata from a post."""
    return {
        "id": post.id,
        "title": post.title,
        "author": str(post.author) if post.author else "[deleted]",
        "created_utc": post.created_utc,
        "created_date": datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
        "score": post.score,
        "upvote_ratio": post.upvote_ratio,
        "num_comments": post.num_comments,
        "url": post.url,
        "permalink": post.permalink,
        "selftext": post.selftext,
        "is_self": post.is_self,
        "is_video": post.is_video if hasattr(post, 'is_video') else False,
        "link_flair_text": post.link_flair_text,
        "over_18": post.over_18,
        "spoiler": post.spoiler,
        "comments": []
    }

def extract_comment_data(comment):
    """Extract relevant metadata from a comment."""
    return {
        "id": comment.id,
        "author": str(comment.author) if comment.author else "[deleted]",
        "body": comment.body,
        "created_utc": comment.created_utc,
        "created_date": datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
        "score": comment.score,
        "is_submitter": comment.is_submitter
    }

def load_existing_data(output_filename):
    """Load existing data from JSON file if it exists."""
    if os.path.exists(output_filename):
        try:
            with open(output_filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error loading existing file {output_filename}. Starting fresh.")
            return []
    return []

def scrape_omori_subreddit(output_filename=None):
    """Main function to scrape r/OMORI posts and comments with specified keywords."""
    # Define output filename if not provided
    if output_filename is None:
        output_filename = f"omori_posts.json"
    
    # Load existing data and extract processed post IDs
    existing_data = load_existing_data(output_filename)
    processed_posts = set(post["id"] for post in existing_data)
    print(f"Loaded {len(processed_posts)} previously processed posts")
    
    reddit = initialize_reddit()
    subreddit = reddit.subreddit("OMORI")
    
    new_posts_count = 0
    
    # Process different listing types to ensure comprehensive coverage
    listing_generators = [
        ("hot", subreddit.hot(limit=None)),
        ("new", subreddit.new(limit=None)),
        ("top", subreddit.top(limit=None, time_filter="all")),
        ("rising", subreddit.rising(limit=None)),
        ("controversial", subreddit.controversial(limit=None, time_filter="all"))
    ]
    
    for listing_name, generator in listing_generators:
        print(f"Processing {listing_name} posts...")
        post_count = 0
        matched_count = 0
        
        for post in generator:
            post_count += 1
            
            # Skip already processed posts
            if post.id in processed_posts:
                continue
            
            processed_posts.add(post.id)
            
            # Check if post contains any keywords
            if contains_keywords(post.title) or contains_keywords(post.selftext):
                matched_count += 1
                new_posts_count += 1
                
                # Extract post data
                post_data = extract_post_data(post)
                
                # Get first-level comments
                post.comments.replace_more(limit=None)  # Expand all comment trees
                
                for comment in post.comments:
                    if isinstance(comment, praw.models.Comment):
                        post_data["comments"].append(extract_comment_data(comment))
                
                existing_data.append(post_data)
                
                # Periodically save results to avoid data loss
                if new_posts_count % 10 == 0:
                    with open(output_filename, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                    print(f"Interim save: {len(existing_data)} total posts")
                
                # Sleep to avoid rate limiting
                time.sleep(0.5)
            
            # Print progress every 100 posts
            if post_count % 100 == 0:
                print(f"Processed {post_count} posts, found {matched_count} new matching posts")
    
    # Final save of results to JSON
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"Scraping completed. Found {new_posts_count} new relevant posts.")
    print(f"Total posts in database: {len(existing_data)}")
    print(f"Results saved to {output_filename}")

def update_database():
    """Run the script in update mode to add new posts to existing database."""
    scrape_omori_subreddit("omori_posts.json")

if __name__ == "__main__":
    update_database()
