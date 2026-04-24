import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_IDS = [
    "kYfAC0Ed_Uc",  # Tulus - Hati-Hati di Jalan (Official Music Video)
    "0kH3n3V_39c",  # Tulus - Hati-Hati di Jalan (Official Lyric Video)
]
MAX_RESULTS_PER_VIDEO = 1000  # Adjust as needed for Big Data project
OUTPUT_PATH = "../data/raw_comments.csv"

def get_comments(youtube, video_id, max_results):
    comments = []
    
    try:
        # Initial request
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,  # Max allowed per request
            textFormat="plainText"
        )
        response = request.execute()

        while response and len(comments) < max_results:
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'video_id': video_id,
                    'author': comment['authorDisplayName'],
                    'comment': comment['textDisplay'],
                    'published_at': comment['publishedAt'],
                    'like_count': comment['likeCount']
                })
                
                if len(comments) >= max_results:
                    break

            # Check for next page
            if 'nextPageToken' in response and len(comments) < max_results:
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
        print(f"Error fetching comments for video {video_id}: {e}")
        
    return comments

def main():
    if not API_KEY:
        print("ERROR: YOUTUBE_API_KEY not found in environment variables.")
        print("Please create a .env file with YOUTUBE_API_KEY=your_key")
        return

    youtube = build("youtube", "v3", developerKey=API_KEY)
    
    all_comments = []
    
    for v_id in VIDEO_IDS:
        print(f"Fetching comments for video: {v_id}...")
        comments = get_comments(youtube, v_id, MAX_RESULTS_PER_VIDEO)
        all_comments.extend(comments)
        print(f"Retrieved {len(comments)} comments.")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Save to CSV
    df = pd.DataFrame(all_comments)
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    
    print(f"\nSUCCESS: Total {len(all_comments)} comments saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
