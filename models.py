from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    subscriptions = db.relationship(
        "Subscription", backref="user", lazy=True, cascade="all, delete-orphan"
    )


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    icon = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "freq": self.frequency,
            "day": self.day,
            "startMonth": self.start_month,
            "category": self.category,
            "color": self.color,
            "icon": self.icon,
        }
