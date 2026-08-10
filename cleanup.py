from app import create_app
from app.models import db, Article

app = create_app()
with app.app_context():
    dummy = Article.query.filter_by(headline="Test Headline").first()
    if dummy:
        db.session.delete(dummy)
        db.session.commit()
        print("Deleted dummy article.")
