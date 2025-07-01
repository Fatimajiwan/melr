from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Change these as needed
    username = "admin"
    email = "admin@example.com"
    password = "admin123"

    if not User.query.filter_by(username=username).first():
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user created: {username} / {password}")
    else:
        print("Admin user already exists.")