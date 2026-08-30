import json
from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    settings = db.Column(db.Text, nullable=True)
    subscriptions = db.relationship(
        "Subscription", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    pots = db.relationship(
        "Pot", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def get_settings(self):
        return json.loads(self.settings) if self.settings else None

    def set_settings(self, data):
        self.settings = json.dumps(data)


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
    # Set only when frequency == "fortnightly": the reference date from which
    # 14-day billing cycles are counted forward and backward. Null for the
    # fixed monthly/quarterly/annual frequencies, which use day/start_month.
    anchor_date = db.Column(db.Date, nullable=True)
    # Who the expense belongs to: "a" / "b" (the two people named in user
    # settings) or "shared". Drives the list filter and the pot split.
    payer = db.Column(db.String(20), nullable=False, server_default="shared")
    # Which person's bank account the payment actually leaves from: "a" / "b",
    # or NULL when unset. Independent of `payer` (a shared bill still comes out
    # of one real account). Drives the monthly-bills settlement in the pots view.
    paid_from = db.Column(db.String(1), nullable=True)

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
            "anchorDate": self.anchor_date.isoformat() if self.anchor_date else None,
            "payer": self.payer,
            "paidFrom": self.paid_from,
        }


class Pot(db.Model):
    """A named monthly set-aside target (e.g. "House & garden").

    Pots track only how much to put aside each month, not a running
    balance. The built-in "annual expenses" pot is computed on the
    frontend from quarterly/annual subscriptions and is not stored here.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    monthly_amount = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "monthlyAmount": self.monthly_amount,
            "color": self.color,
            "note": self.note,
        }
