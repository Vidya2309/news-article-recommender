from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), unique=True, nullable=False)
    source = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    embedding = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)  # NEW

class ClickLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())