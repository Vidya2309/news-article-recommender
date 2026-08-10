from flask import Blueprint, render_template, session, redirect, url_for, request
import uuid

from app.models import db, Article
from app.services.fetch_news import fetch_and_store_news, fetch_tamil_nadu_news
from app.services.recommender import (
    embed_and_store_missing,
    get_personalized_recommendations,
    explain_recommendation,
    log_click,
)

main = Blueprint("main", __name__)


def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


@main.route("/")
def home():
    category = request.args.get("category")
    query = Article.query
    if category:
        query = query.filter_by(category=category)
    articles = query.order_by(Article.published_at.desc()).limit(20).all()
    return render_template("index.html", articles=articles, selected_category=category)


@main.route("/article/<int:article_id>")
def article_detail(article_id):
    session_id = get_session_id()
    article = db.session.get(Article, article_id)

    if not article:
        return render_template("error.html", message="That article doesn't exist or has been removed."), 404

    log_click(session_id, article_id)

    results = get_personalized_recommendations(article_id, session_id, top_n=5)
    recommendations = []
    for rec_article, score in results:
        shared = explain_recommendation(article, rec_article)
        recommendations.append({
            "article": rec_article,
            "score": score,
            "shared_keywords": shared,
        })

    return render_template("result.html", article=article, recommendations=recommendations)

@main.route("/fetch-news")
def manual_fetch():
    fetch_and_store_news()
    fetch_tamil_nadu_news()
    embed_and_store_missing()
    return redirect(url_for("main.home"))