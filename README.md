# Dispatch - News Article Recommender

A full-stack news recommendation platform built with Flask. It ingests live headlines from NewsAPI, generates semantic embeddings for each article using a pretrained sentence-transformer model, and recommends similar articles using cosine similarity, blended with recency weighting and lightweight session-based personalization from user click history.

## Features

- Multi-source ingestion: pulls general headlines and Tamil Nadu region-specific news via NewsAPI, deduplicated by URL, refreshed on a scheduled background job
- Semantic recommendations: uses sentence-transformers (all-MiniLM-L6-v2) to embed articles and rank recommendations by cosine similarity, rather than simple keyword overlap
- Recency weighting: blends similarity score with article freshness
- Lightweight personalization: tracks per-session click history and nudges recommendations toward a user's demonstrated interests
- Explainability: surfaces shared keywords between the source article and each recommendation
- Custom UI: a distinct "wire dispatch" visual identity with an image-grid homepage and match-strip score visualizations
- Tested: unit tests cover recommendation ranking logic and graceful API failure handling

## Tech Stack

- Backend: Flask, Flask-SQLAlchemy
- Database: SQLite (dev), designed for easy migration to PostgreSQL
- ML: sentence-transformers, NumPy, scikit-learn
- Data source: NewsAPI
- Scheduling: APScheduler
- Testing: pytest
- Frontend: HTML, custom CSS

## Setup

1. Clone the repo and create a virtual environment:
   git clone https://github.com/Vidya2309/news-article-recommender.git
   cd news-article-recommender
   python -m venv venv
   venv\Scripts\activate

2. Install dependencies:
   pip install -r requirements.txt

3. Create a .env file in the project root:
   NEWS_API_KEY=your_newsapi_key_here
   SECRET_KEY=any_random_string

4. Run the app:
   python run.py

## Running Tests

pytest tests/ -v

## Known Limitations

- NewsAPI's free tier only provides short descriptions, not full article bodies. The app links out to the original source for full content.
- "Real-time" here means scheduled polling every ~20 minutes, not live streaming.
- Similarity search runs as an in-memory loop, fine at this scale but not for thousands of articles.

## Future Improvements

- Migrate to PostgreSQL + a vector database for scalable similarity search
- Add real user accounts instead of session-based personalization
- Refactor duplicated fetch/dedupe logic
- Add Tamil-language coverage

## License

MIT
