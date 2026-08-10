from app import create_app
from app.models import db, Article
from datetime import datetime

app = create_app()

with app.app_context():
    test_article = Article(
        headline="Test Headline",
        description="Just checking the DB works",
        url="https://example.com/test-article",
        source="TestSource",
        category="general",
        published_at=datetime.utcnow()
    )
    db.session.add(test_article)
    db.session.commit()

    all_articles = Article.query.all()
    for a in all_articles:
        print(a.id, a.headline, a.url)