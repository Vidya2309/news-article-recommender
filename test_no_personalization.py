from app import create_app
from app.services.recommender import get_recommendations
from app.models import Article

app = create_app()

with app.app_context():
    results = get_recommendations(article_id=2, top_n=5)
    for article, score in results:
        print(f"{score:.4f} - {article.headline}")
