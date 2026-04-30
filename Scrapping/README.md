# 🚀 YouTube Intelligence Scraper & Dashboard

A professional-grade YouTube comment scraping pipeline that stores raw JSON data in **MongoDB** and visualizes it through a premium **Flask Dashboard**. This project is designed for large-scale data collection (47K+ records) and real-time analysis.

## ✨ Features
- **Raw Data Storage**: Saves full YouTube API JSON responses in MongoDB (No data loss).
- **Massive Scraping**: Optimized to handle tens of thousands of comments across multiple videos.
- **Intelligent Extraction**: Automatically filters "important" fields for CSV export.
- **Premium Dashboard**: A modern, glassmorphism-style web UI to monitor scraping progress and stats.
- **Real-time Stats**: Track total comments, engagement (likes), and latest activity.

## 🛠️ Tech Stack
- **Backend**: Python, Flask
- **Database**: MongoDB
- **API**: Google YouTube Data API v3
- **Frontend**: Tailwind CSS, HTML5, JavaScript (Real-time polling)

## 📋 Prerequisites
- Python 3.8+
- MongoDB (Running locally or via Atlas)
- YouTube API Key (from Google Cloud Console)

## 🚀 Getting Started

### 1. Setup Environment
Clone the project and install dependencies:
```bash
pip install pandas google-api-python-client python-dotenv pymongo flask
```

### 2. Configuration
Create a `.env` file in the root directory (refer to `.env.example`):
```env
YOUTUBE_API_KEY=your_key_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=youtube_data
MONGODB_COLLECTION=comments
```

### 3. Usage

#### Step A: Run Scraper
Fetch comments from defined video IDs and store them in MongoDB:
```bash
python youtube_scraper.py
```

#### Step B: Run Dashboard
Visualize the data stored in MongoDB:
```bash
python dashboard.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

## 📁 Project Structure
- `youtube_scraper.py`: Core logic for API scraping and MongoDB storage.
- `dashboard.py`: Flask server for the web interface.
- `templates/index.html`: Dashboard UI with premium styling.
- `data/`: Directory where processed CSV exports are saved.
- `.env`: Local environment configuration (API keys, DB URIs).

## 📊 Data Flow
1. **Scraper** -> **YouTube API** (Fetch)
2. **Scraper** -> **MongoDB** (Store Raw JSON)
3. **Scraper** -> **CSV** (Export Important Fields)
4. **Dashboard** -> **MongoDB** (Query & Visualize)

---
*Developed for Big Data Final Project (UAS) - 2026*
