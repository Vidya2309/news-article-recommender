from app import create_app
from app.services.fetch_news import fetch_and_store_news

app = create_app()

with app.app_context():
    count = fetch_and_store_news()
    print(f"Done. {count} new articles added.")
    from app.models import Article
with app.app_context():
    print(Article.query.count(), "total articles in DB")