from app import create_app
from app.models import db, ClickLog

app = create_app()
with app.app_context():
    ClickLog.query.delete()
    db.session.commit()
    print("Click history cleared.")
