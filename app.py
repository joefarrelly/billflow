import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_migrate import Migrate
from models import db, User, Subscription

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:////app/billflow.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Flask's session cookie is not saved on 302 redirects in this setup, so we
# persist Authlib's OAuth state server-side for the duration of the flow.
_oauth_states: dict[str, dict] = {}

db.init_app(app)
Migrate(app, db)

login_manager = LoginManager(app)

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID", ""),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email"},
)

with app.app_context():
    os.makedirs(
        os.path.join(os.path.dirname(__file__), "static", "icons"), exist_ok=True
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/auth/google")
def auth_google():
    from flask import session

    redirect_uri = os.environ.get("OAUTH_REDIRECT_URI") or url_for(
        "auth_callback", _external=True
    )
    resp = google.authorize_redirect(redirect_uri)
    for key, value in session.items():
        if key.startswith("_state_google_"):
            state_token = key[len("_state_google_") :]
            _oauth_states[state_token] = {
                "data": {key: value},
                "exp": time.time() + 300,
            }
    return resp


@app.route("/auth/callback")
def auth_callback():
    from flask import session

    state = request.args.get("state", "")
    entry = _oauth_states.pop(state, None)
    if not entry or time.time() > entry["exp"]:
        return jsonify({"error": "OAuth state invalid or expired"}), 400
    session.update(entry["data"])
    token = google.authorize_access_token()
    email = token["userinfo"]["email"]
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=True)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/api/me")
def api_me():
    if current_user.is_authenticated:
        return jsonify({"email": current_user.email})
    return jsonify({"error": "not authenticated"}), 401


@app.route("/api/subscriptions", methods=["GET"])
def list_subs():
    if not current_user.is_authenticated:
        return jsonify({"error": "not authenticated"}), 401
    subs = (
        Subscription.query.filter_by(user_id=current_user.id)
        .order_by(Subscription.day)
        .all()
    )
    return jsonify([s.to_dict() for s in subs])


@app.route("/api/subscriptions", methods=["POST"])
def create_sub():
    if not current_user.is_authenticated:
        return jsonify({"error": "not authenticated"}), 401
    data = request.get_json(force=True)
    sub = Subscription(
        user_id=current_user.id,
        name=data["name"],
        amount=float(data["amount"]),
        frequency=data["freq"],
        day=int(data["day"]),
        start_month=int(data.get("startMonth", 0)),
        category=data["category"],
        color=data["color"],
        icon=data.get("icon"),
    )
    db.session.add(sub)
    db.session.commit()
    return jsonify(sub.to_dict()), 201


@app.route("/api/subscriptions/<int:sub_id>", methods=["PUT"])
def update_sub(sub_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "not authenticated"}), 401
    sub = Subscription.query.filter_by(
        id=sub_id, user_id=current_user.id
    ).first_or_404()
    data = request.get_json(force=True)
    sub.name = data.get("name", sub.name)
    sub.amount = float(data.get("amount", sub.amount))
    sub.frequency = data.get("freq", sub.frequency)
    sub.day = int(data.get("day", sub.day))
    sub.start_month = int(data.get("startMonth", sub.start_month))
    sub.category = data.get("category", sub.category)
    sub.color = data.get("color", sub.color)
    if "icon" in data:
        sub.icon = data["icon"]
    db.session.commit()
    return jsonify(sub.to_dict())


@app.route("/api/subscriptions/<int:sub_id>", methods=["DELETE"])
def delete_sub(sub_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "not authenticated"}), 401
    sub = Subscription.query.filter_by(
        id=sub_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(sub)
    db.session.commit()
    return "", 204


@app.route("/api/settings", methods=["GET"])
def get_settings():
    if not current_user.is_authenticated:
        return jsonify({"error": "not authenticated"}), 401
    return jsonify(current_user.get_settings())


@app.route("/api/settings", methods=["PUT"])
def save_settings():
    if not current_user.is_authenticated:
        return jsonify({"error": "not authenticated"}), 401
    data = request.get_json(force=True)
    current_user.set_settings(
        {
            "theme": data.get("theme"),
            "currency": data.get("currency"),
            "calDisplay": data.get("calDisplay"),
            "categories": data.get("categories"),
        }
    )
    db.session.commit()
    return jsonify(current_user.get_settings())


@app.route("/api/migrate", methods=["POST"])
def migrate():
    if not current_user.is_authenticated:
        return jsonify({"error": "not authenticated"}), 401
    existing = Subscription.query.filter_by(user_id=current_user.id).count()
    if existing > 0:
        subs = (
            Subscription.query.filter_by(user_id=current_user.id)
            .order_by(Subscription.day)
            .all()
        )
        return jsonify([s.to_dict() for s in subs])
    for data in request.get_json(force=True) or []:
        db.session.add(
            Subscription(
                user_id=current_user.id,
                name=data["name"],
                amount=float(data["amount"]),
                frequency=data["freq"],
                day=int(data.get("day", 1)),
                start_month=int(data.get("startMonth", 0)),
                category=data.get("category", "other"),
                color=data.get("color", "#888"),
                icon=data.get("icon"),
            )
        )
    db.session.commit()
    subs = (
        Subscription.query.filter_by(user_id=current_user.id)
        .order_by(Subscription.day)
        .all()
    )
    return jsonify([s.to_dict() for s in subs])


if __name__ == "__main__":
    app.run(debug=True)
