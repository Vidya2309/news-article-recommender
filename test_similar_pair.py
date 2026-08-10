from app import create_app
from app.services.recommender import cosine_similarity
from app.models import Article
import json

app = create_app()

with app.app_context():
    a4 = Article.query.get(4)
    a5 = Article.query.get(5)
    vec4 = json.loads(a4.embedding)
    vec5 = json.loads(a5.embedding)
    sim = cosine_similarity(vec4, vec5)
    print(a4.headline)
    print(a5.headline)
    print(f"Similarity: {sim:.4f}")
