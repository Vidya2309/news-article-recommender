from flask import Flask
from config import Config
from app.models import db
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.fetch_news import fetch_and_store_news


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    if not app.config.get("TESTING"):
        def scheduled_fetch():
            with app.app_context():
                fetch_and_store_news()

        scheduler = BackgroundScheduler()
        scheduler.add_job(scheduled_fetch, "interval", minutes=20)
        scheduler.start()

    return app