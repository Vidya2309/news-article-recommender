from app import create_app
from app.services.recommender import get_recommendations, explain_recommendation
from app.models import Article
from app.models import db
app = create_app()

with app.app_context():
    source = db.session.get(Article, 4)
    results = get_recommendations(article_id=4, top_n=5)
    for article, score in results:
        shared = explain_recommendation(source, article)
        print(f"{score:.4f} - {article.headline}")
        print(f"   Shared keywords: {shared}")
