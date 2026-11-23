import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

mail = Mail(app)

@app.context_processor
def sidebar_context():
    from flask_login import current_user
    if current_user.is_authenticated:
        from flaskblog.models import Post, Notification
        recent_posts = (Post.query
                        .filter_by(user_id=current_user.id)
                        .order_by(Post.date_posted.desc())
                        .limit(5).all())
        notifications = (Notification.query
                         .filter_by(user_id=current_user.id, is_read=False)
                         .order_by(Notification.date_created.desc())
                         .limit(10).all())
        total_posts = Post.query.filter_by(user_id=current_user.id).count()
        total_likes = sum(p.liked_by.count() for p in current_user.posts)
        return dict(
            sidebar_recent_posts=recent_posts,
            sidebar_notifications=notifications,
            sidebar_notif_count=len(notifications),
            sidebar_total_posts=total_posts,
            sidebar_total_likes=total_likes
        )
    return dict(
        sidebar_recent_posts=[],
        sidebar_notifications=[],
        sidebar_notif_count=0,
        sidebar_total_posts=0,
        sidebar_total_likes=0
    )

from flaskblog import routes