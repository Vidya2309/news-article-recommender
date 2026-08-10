import json
import pytest
from app.models import db, Article
from app.services.recommender import cosine_similarity, get_recommendations

def make_article(headline, embedding_vector, **kwargs):
    article = Article(
        headline=headline,
        url=f"https://example.com/{headline.replace(' ', '-')}",
        embedding=json.dumps(embedding_vector),
        **kwargs
    )
    db.session.add(article)
    db.session.commit()
    return article


def test_cosine_similarity_identical_vectors():
    vec = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    vec_a = [1.0, 0.0]
    vec_b = [0.0, 1.0]
    assert cosine_similarity(vec_a, vec_b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector_no_crash():
    vec_a = [0.0, 0.0]
    vec_b = [1.0, 1.0]
    assert cosine_similarity(vec_a, vec_b) == 0.0


def test_get_recommendations_ranks_by_similarity(app):
    source = make_article("Source Article", [1.0, 0.0, 0.0])
    close = make_article("Close Article", [0.9, 0.1, 0.0])
    far = make_article("Far Article", [0.0, 1.0, 0.0])

    results = get_recommendations(source.id, top_n=5)
    ranked_ids = [article.id for article, score in results]

    assert ranked_ids[0] == close.id
    assert ranked_ids[-1] == far.id


def test_get_recommendations_excludes_source_article(app):
    source = make_article("Source Article", [1.0, 0.0])
    make_article("Other Article", [0.5, 0.5])

    results = get_recommendations(source.id, top_n=5)
    ids = [article.id for article, score in results]

    assert source.id not in ids


def test_get_recommendations_missing_article_returns_empty(app):
    results = get_recommendations(article_id=9999, top_n=5)
    assert results == []