

def posts_list(db):
    return db.execute(
        "SELECT p.id, p.title, p.body, p.created, p.author_id, u.username"
        " FROM post p JOIN user u ON p.author_id = u.id"
    ).fetchall()


def get_post(db, id):
    return db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        ).fetchone()


def create_post(db, title, body, author_id):
    db.execute(
        "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
        (title, body, author_id),
    )
    db.commit()


def update_post(db, title, body, id):
    db.execute(
        "UPDATE post SET title = ?, body = ? WHERE id = ?",
        (title, body, id)
    )
    db.commit()


def delete_post(db, id):
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()

def comments_list(db):
    return db.execute(
        "SELECT c.id, c.body, c.created, c.author_id, c.post_id, u.username"
        " FROM comment c JOIN user u ON c.author_id = u.id"
        " ORDER BY c.created"
    ).fetchall()


def get_comment(db, id):
    return db.execute(
            "SELECT c.id, c.body, c.created, c.author_id, c.post_id, u.username"
            " FROM comment c JOIN user u ON c.author_id = u.id"
            " WHERE c.id = ?",
            (id,),
        ).fetchone()


def create_comment(db, body, author_id, post_id):
    db.execute(
        "INSERT INTO comment (body, author_id, post_id) VALUES (?, ?, ?)",
        (body, author_id, post_id),
    )
    db.commit()


def update_comment(db, body, id):
    db.execute(
        "UPDATE comment SET body = ? WHERE id = ?",
        (body, id)
    )
    db.commit()


def delete_comment(db, id):
    db.execute("DELETE FROM comment WHERE id = ?", (id,))
    db.commit()
