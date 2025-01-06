import sys
from app import create_app
from app.extensions import initialize_extensions, SessionLocal
from app.services.user_service import UserService
from app.models.user_model import User

def main():
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)

    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]

    app = create_app('development')  # Or another configuration
    initialize_extensions(app)

    with app.app_context():
        with SessionLocal() as session:
            service = UserService(db=session)
            if service.email_or_username_exists(email, username):
                print("Admin user already exists.")
                return

            admin_user = User(
                username=username,
                email=email,
                is_admin=True
            )
            admin_user.set_password(password)
            service.db.add(admin_user)
            service.db.commit()
            service.db.refresh(admin_user)
            print(f'Admin user successfully created: {admin_user}')

if __name__ == '__main__':
    main()