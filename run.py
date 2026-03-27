from app import create_app, db

if __name__ == '__main__':
    app = create_app(__name__)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')

