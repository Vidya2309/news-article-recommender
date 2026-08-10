import json
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models import db, Article, ClickLog
from datetime import datetime, timezone

# Load once, reuse everywhere (loading this model is slow, don't do it per-request)
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def compute_embedding(text):
    model = get_model()
    vector = model.encode(text, convert_to_numpy=True)
    return vector


def embed_and_store_missing():
    """Compute embeddings for any article that doesn't have one yet."""
    articles = Article.query.filter(
        (Article.embedding == None) | (Article.embedding == "")
    ).all()

    if not articles:
        print("[embeddings] Nothing to embed.")
        return 0

    count = 0
    for article in articles:
        text = f"{article.headline}. {article.description or ''}"
        vector = compute_embedding(text)
        article.embedding = json.dumps(vector.tolist())
        count += 1

    db.session.commit()
    print(f"[embeddings] Embedded {count} articles.")
    return count


def cosine_similarity(vec_a, vec_b):
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def get_recommendations(article_id, top_n=5, recency_weight=0.1):
    """Return the top_n most similar articles to the given article_id,
    with a small boost for more recent articles."""
    source = db.session.get(Article, article_id)
    if not source or not source.embedding:
        return []

    source_vec = json.loads(source.embedding)

    candidates = Article.query.filter(
        Article.id != article_id,
        Article.embedding != None
    ).all()

    now = datetime.now(timezone.utc)
    scored = []
    for candidate in candidates:
        cand_vec = json.loads(candidate.embedding)
        sim = cosine_similarity(source_vec, cand_vec)

        recency_score = 0.0
        if candidate.published_at:
            pub = candidate.published_at
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            age_hours = max((now - pub).total_seconds() / 3600, 0)
            # Decays from 1.0 (just published) toward 0 over ~7 days
            recency_score = max(1 - (age_hours / (24 * 7)), 0)

        final_score = sim + (recency_weight * recency_score)
        scored.append((candidate, final_score, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [(article, sim) for article, final_score, sim in scored[:top_n]]
from sklearn.feature_extraction.text import TfidfVectorizer
import re

STOPWORD_SAFE_PATTERN = re.compile(r"[^a-zA-Z\s]")

def extract_keywords(text, top_n=5):
    """Extract top_n keywords from a single piece of text using TF-IDF."""
    if not text:
        return []

    cleaned = STOPWORD_SAFE_PATTERN.sub(" ", text.lower())

    vectorizer = TfidfVectorizer(stop_words="english", max_features=20)
    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned])
    except ValueError:
        # happens if text has zero meaningful words after cleaning
        return []

    scores = tfidf_matrix.toarray()[0]
    terms = vectorizer.get_feature_names_out()

    ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    return [term for term, score in ranked[:top_n] if score > 0]


def explain_recommendation(source_article, candidate_article):
    """Return a list of shared keywords between two articles."""
    source_text = f"{source_article.headline} {source_article.description or ''}"
    cand_text = f"{candidate_article.headline} {candidate_article.description or ''}"

    source_keywords = set(extract_keywords(source_text, top_n=8))
    cand_keywords = set(extract_keywords(cand_text, top_n=8))

    shared = source_keywords & cand_keywords
    return list(shared)
import uuid
from datetime import datetime, timezone

def log_click(session_id, article_id):
    """Record that a user (identified by session_id) clicked on an article."""
    click = ClickLog(session_id=session_id, article_id=article_id)
    db.session.add(click)
    db.session.commit()


def get_user_preference_vector(session_id, max_clicks=10):
    """Average the embeddings of a user's last N clicked articles."""
    recent_clicks = (
        ClickLog.query.filter_by(session_id=session_id)
        .order_by(ClickLog.timestamp.desc())
        .limit(max_clicks)
        .all()
    )

    if not recent_clicks:
        return None

    vectors = []
    for click in recent_clicks:
        article = db.session.get(Article, click.article_id)
        if article and article.embedding:
            vectors.append(json.loads(article.embedding))

    if not vectors:
        return None

    arr = np.array(vectors)
    return arr.mean(axis=0).tolist()


def get_personalized_recommendations(article_id, session_id, top_n=5, recency_weight=0.1, personalization_weight=0.05):
    """Like get_recommendations, but blends in the user's preference vector."""
    source = db.session.get(Article, article_id)
    if not source or not source.embedding:
        return []

    source_vec = json.loads(source.embedding)
    user_vec = get_user_preference_vector(session_id)

    candidates = Article.query.filter(
        Article.id != article_id,
        Article.embedding != None
    ).all()

    now = datetime.now(timezone.utc)
    scored = []
    for candidate in candidates:
        cand_vec = json.loads(candidate.embedding)
        sim = cosine_similarity(source_vec, cand_vec)

        recency_score = 0.0
        if candidate.published_at:
            pub = candidate.published_at
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            age_hours = max((now - pub).total_seconds() / 3600, 0)
            recency_score = max(1 - (age_hours / (24 * 7)), 0)

        personalization_score = 0.0
        if user_vec:
            personalization_score = cosine_similarity(user_vec, cand_vec)

        final_score = (
            sim
            + (recency_weight * recency_score)
            + (personalization_weight * personalization_score)
        )
        scored.append((candidate, final_score, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [(article, final_score) for article, final_score, sim in scored[:top_n]]
