import os
import json
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "youtube_data")

def get_db():
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DB]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    db = get_db()
    total_comments = db.comments.count_documents({})
    total_videos = db.videos.count_documents({})
    
    # Aggregate likes from comments
    pipeline = [
        {"$group": {
            "_id": None,
            "total_likes": {"$sum": "$snippet.topLevelComment.snippet.likeCount"}
        }}
    ]
    result = list(db.comments.aggregate(pipeline))
    total_likes = result[0]['total_likes'] if result else 0
    
    return jsonify({
        "total_comments": total_comments,
        "total_videos": total_videos,
        "total_likes": total_likes
    })

@app.route('/api/data')
def get_data():
    db = get_db()
    
    # Params
    data_type = request.args.get('type', 'comments') # 'comments' or 'videos'
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search_query = request.args.get('q', '')

    skip = (page - 1) * per_page
    collection = db[data_type]

    # Build Filter
    filter_query = {}
    if search_query:
        if data_type == 'comments':
            filter_query = {
                "$or": [
                    {"snippet.topLevelComment.snippet.textDisplay": {"$regex": search_query, "$options": "i"}},
                    {"snippet.topLevelComment.snippet.textOriginal": {"$regex": search_query, "$options": "i"}}
                ]
            }
        else:
            filter_query = {"snippet.title": {"$regex": search_query, "$options": "i"}}

    # Fetch Data
    cursor = collection.find(filter_query).sort("_id", -1).skip(skip).limit(per_page)
    total_count = collection.count_documents(filter_query)
    
    # Format results
    items = []
    for doc in cursor:
        # We use json_util to handle MongoDB specific types like ObjectId
        items.append(json.loads(json_util.dumps(doc)))
        
    return jsonify({
        "items": items,
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": (total_count + per_page - 1) // per_page
    })

@app.route('/api/delete_all', methods=['POST'])
def delete_all():
    try:
        db = get_db()
        # Drop collections
        db.comments.drop()
        db.videos.drop()
        
        # Delete CSV if exists
        csv_path = os.path.join("data", "processed_comments.csv")
        if os.path.exists(csv_path):
            os.remove(csv_path)
            
        return jsonify({"success": True, "message": "Semua data berhasil dihapus!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
