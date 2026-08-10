from app import create_app
from app.services.recommender import embed_and_store_missing, cosine_similarity
from app.models import Article
import json

app = create_app()

with app.app_context():
    embed_and_store_missing()

    articles = Article.query.filter(Article.embedding != None).limit(5).all()
    for a in articles:
        print(a.id, "-", a.headline)

    if len(articles) >= 2:
        vec1 = json.loads(articles[0].embedding)
        vec2 = json.loads(articles[1].embedding)
        sim = cosine_similarity(vec1, vec2)
        print(f"\nSimilarity between article {articles[0].id} and {articles[1].id}: {sim:.4f}")