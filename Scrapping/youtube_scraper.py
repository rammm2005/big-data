import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
API_KEY = os.getenv("YOUTUBE_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "youtube_data")
COLLECTION_COMMENTS = "comments"
COLLECTION_VIDEOS = "videos"

VIDEO_IDS = [
    "9II3OGZETo4",  # TULUS - Hati-Hati di Jalan (Official Music Video)
    "_N6vSc_mT6I",  # TULUS - Hati-Hati di Jalan (Official Lyric Video)
    "F4z8MKU3vEk",  # TULUS - Hati-Hati di Jalan (Audio)
    "xVparsxskE0",  # Lirik Lagu
    "1t877p-ZjEw",  # Live Performance
    "IxdQNGYdb10",  # Lirik Gabut
    "rGbifizKEak",  # Lirik 
    "AyN1hiXitBk",  # Cover
    "-Ni9jyfrbQ0",  # Karaoke Version
    "pTAV74Xx_mY",  # Cover by Mario G. Klau
    "UjZrPGYtIso",  # Cover by Lyodra
]

MAX_RESULTS_PER_VIDEO = 100000
OUTPUT_PATH = "./data/processed_comments.csv"

# MongoDB Setup
try:
    # Use pymongo 3.x compatible connection
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    print(f"Connected to MongoDB: {MONGODB_DB}")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

def get_video_details(youtube, video_ids):
    """
    Fetches metadata for the provided video IDs and saves to MongoDB.
    """
    print(f"\nFetching metadata for {len(video_ids)} videos...")
    try:
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids)
        )
        response = request.execute()
        
        items = response.get('items', [])
        if items:
            db[COLLECTION_VIDEOS].delete_many({"id": {"$in": video_ids}}) # Refresh data
            db[COLLECTION_VIDEOS].insert_many(items)
            print(f"  Successfully stored {len(items)} video metadata items.")
        return items
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return []

def get_comments_and_save_to_mongo(youtube, video_id, max_results):
    """
    Fetches comments from YouTube API and saves the raw JSON response items to MongoDB.
    """
    count = 0
    collection = db[COLLECTION_COMMENTS]
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )
        response = request.execute()

        while response and count < max_results:
            items = response.get('items', [])
            if not items:
                break
                
            for item in items:
                item['video_id'] = video_id
            
            if items:
                collection.insert_many(items)
                count += len(items)
                print(f"  Stored {len(items)} items for {video_id} (Total: {count})")

            if count >= max_results:
                break

            if 'nextPageToken' in response:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    pageToken=response['nextPageToken'],
                    maxResults=100,
                    textFormat="plainText"
                )
                response = request.execute()
            else:
                break
                
    except Exception as e:
        print(f"Error fetching/saving comments for video {video_id}: {e}")
        
    return count

def export_to_csv_from_mongodb(output_path):
    """
    Retrieves important fields from MongoDB and saves them to a CSV file.
    """
    print("\nExporting processed comments to CSV...")
    collection = db[COLLECTION_COMMENTS]
    cursor = collection.find({})
    
    important_data = []
    for doc in cursor:
        try:
            snippet = doc.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
            important_data.append({
                'video_id': doc.get('video_id'),
                'author': snippet.get('authorDisplayName'),
                'comment': snippet.get('textDisplay'),
                'published_at': snippet.get('publishedAt'),
                'like_count': snippet.get('likeCount')
            })
        except:
            continue

    if not important_data:
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pd.DataFrame(important_data).to_csv(output_path, index=False, encoding='utf-8')
    print(f"SUCCESS: Exported {len(important_data)} records to {output_path}")

def main():
    if not API_KEY:
        print("ERROR: YOUTUBE_API_KEY not found.")
        return

    youtube = build("youtube", "v3", developerKey=API_KEY)
    
    # Step 1: Fetch Video Metadata
    get_video_details(youtube, VIDEO_IDS)
    
    # Step 2: Fetch Comments
    total_stored = 0
    for v_id in VIDEO_IDS:
        print(f"\nProcessing comments for video: {v_id}...")
        count = get_comments_and_save_to_mongo(youtube, v_id, MAX_RESULTS_PER_VIDEO)
        total_stored += count

    # Step 3: Export
    export_to_csv_from_mongodb(OUTPUT_PATH)
    print(f"\nFinal Count: {total_stored} comments stored in MongoDB.")

if __name__ == "__main__":
    main()
