from app import create_app
from app.models import Article

app = create_app()

with app.app_context():
    articles = Article.query.limit(10).all()
    for a in articles:
        print(a.id, "-", a.headline, "-", a.source)