from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify
from werkzeug.exceptions import abort

from flaskr.auth.auth import login_required
from flaskr.db import get_db
from flaskr.blog.queries import (
    create_post, delete_post, get_post, update_post, post_list
)

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = post_list(db)
    return jsonify({'posts': posts})


def check_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """

    post = get_post(get_db(), id)
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("POST",))
@login_required
def create():
    """Create a new post for the current user."""

    error = None

    title = request.json.get('title', '')
    body = request.json.get('body', '')

    if not title:
        error = "Title is required"

    if error is not None:
        flash(error)
    else:
        db = get_db()
        create_post(db, title, body, g.user["id"])
        # return redirect(url_for("blog.index"))
        return jsonify({'post': {'title': title, 'body': body}}), 201



@bp.route("/<int:id>/update", methods=("POST",))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = check_post(id)

    error = None

    title = request.json.get('title', '')
    body = request.json.get('body', '')

    if not title:
        error = "Title is required"

    if error is not None:
        flash(error)
    else:
        db = get_db()
        update_post(db, title, body, id)
        # return redirect(url_for("blog.index"))
        return jsonify({'message': 'post with id %s updated' % id})



@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    check_post(id)
    db = get_db()
    delete_post(db, id)
    # return redirect(url_for("blog.index"))
    jsonify({'message': 'post with id %s deleted' % id})
