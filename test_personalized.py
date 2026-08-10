from app import create_app
from app.services.recommender import log_click, get_personalized_recommendations
from app.models import Article

app = create_app()

with app.app_context():
    fake_session = "test-user-123"

    # Simulate this user clicking article 4 (jobs report) earlier
    log_click(fake_session, article_id=4)

    results = get_personalized_recommendations(article_id=2, session_id=fake_session, top_n=5)
    for article, score in results:
        print(f"{score:.4f} - {article.headline}")
