from werkzeug.security import generate_password_hash


def get_user_by_id(db, id):
    return db.execute(
        "SELECT * FROM user WHERE id = ?", (id,)
    ).fetchone()


def get_user_by_username(db, username):
    return db.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()


def create_user(db, username, password):
    db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    db.commit()
