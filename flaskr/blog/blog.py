from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import Response
from werkzeug.exceptions import abort
import json

from flaskr.auth.auth import auth
from flaskr.db import get_db
from flaskr.auth.queries import get_user_by_id, get_user_by_username
from flaskr.blog.queries import ( create_post, delete_post, get_post,
    posts_list, update_post, create_comment, delete_comment, comments_list,
    get_comment, update_comment )

bp = Blueprint("blog", __name__)

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

    username = auth.username()
    user = get_user_by_username(get_db(), username)

    if not user:
        abort(403)

    if check_author and post["author_id"] != user["id"]:
        abort(403)

    return post

def check_comment(id, check_author=True):
    """Get a comment, its author and post by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of comment to get
    :param check_author: require the current user to be the author
    :return: the comment with author and post information
    :raise 404: if a comment with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """

    comment = get_comment(get_db(), id)

    if comment is None:
        abort(404, "Comment id {0} doesn't exist.".format(id))

    username = auth.username()
    user = get_user_by_username(get_db(), username)

    if not user:
        abort(403)

    if check_author and comment["author_id"] != user["id"]:
        abort(403)

    return comment


@bp.route("/posts", methods=["GET", "POST"])
@auth.login_required
def post_list():
    db = get_db()
    error = None

    # get all posts
    if request.method == "GET":
        posts = list(posts_list(db))
        
        if not posts:
            error = json.dumps({"error": "No posts available."})
        if error:
            return Response(
                error,
                status=404,
                mimetype="application/json"
            )
        data = list()
        for post in posts:
            post = dict(post)
            post['created'] = post['created'].strftime("%d-%b-%Y (%H:%M:%S)")
            data.append(post)

        data = json.dumps(data)
        return Response(
            data,
            status=200,
            mimetype="application/json"
        )
    
    # create new post
    elif request.method == "POST":
        data = request.get_json()
        title = data.get('title', '')
        body = data.get('body', '')

        if not title:
            error = json.dumps({"error": "Title is required"})
        if error:
            return Response(
                error,
                status=400,
                mimetype="application/json"
            )

        db = get_db()
        username = auth.username()
        user = get_user_by_username(username)
        create_post(db, title, body, user["id"])
        data = json.dumps({'title': title,'body': body,
                           'user_id': user["id"]})
        return Response(
            data,
            status=201,
            mimetype="application/json"
        )

    error = json.dumps({"error": 'Unknown method'})
    return Response(
        error,
        stauts=405,
        mimetype="application/json"
    )


@bp.route('/posts/<int:id>', methods=["GET", "PUT", "DELETE"])
@auth.login_required
def post(id):
    post = dict(check_post(id))
    error = None

    # post with id does not exist
    if not post:
        error = json.dumps({"error": "Post id {0} not available.".format(id)})
    if error:
        return Response(
            error,
            status=404,
            mimetype="application/json"
        )

    # get post by id
    if request.method == "GET":
        post['created'] = post['created'].strftime("%d-%b-%Y (%H:%M:%S)")
        data = json.dumps(dict(post))
        return Response(
            data,
            status=200,
            mimetype="application/json"
        )

    # update post by id
    elif request.method == "PUT":
        data = request.get_json()
        title = data.get('title', '')
        body = data.get('body', '')

        if not title:
            error = json.dumps({"error": "Title is required"})
        if error:
            return Response(
                error,
                status=400,
                mimetype="application/json"
            )

        db = get_db()
        update_post(db, title, body, id)
        message = json.dumps({'message': 'Post id {0} update successfully'.format(id)})
        return Response(
            message,
            status=200,
            mimetype="application/json"
        )
    
    # delete post by id
    elif request.method == "DELETE":
        db = get_db()
        delete_post(db, id)
        message = json.dumps({'message': 'Post id {0} delete successfully'.format(id)})
        return Response(
            message,
            status=200,
            mimetype="application/json"
        )

@bp.route("/posts/<int:post_id>/comments", methods=["GET", "POST"])
@auth.login_required
def comment_list(post_id):
    db = get_db()
    error = None

    # get all comments
    if request.method == "GET":
        comments = list(comments_list(db))

        if not comments:
            error = json.dumps({"error": "No comments available."})
        if error:
            return Response(
                error,
                status=404,
                mimetype="application/json"
            )

        data = list()
        for comment in comments:
            comment = dict(comment)
            comment['created'] = comment['created'].strftime("%d-%b-%Y (%H:%M:%S)")
            data.append(comment)

        data = json.dumps(data)
        return Response(
            data,
            status=200,
            mimetype="application/json"
        )
    
    # create new comment
    elif request.method == "POST":
        data = request.get_json()
        body = data.get('body', '')

        if not body:
            error = json.dumps({"error": "Body is required"})
        if error:
            return Response(
                error,
                status=400,
                mimetype="application/json"
            )

        db = get_db()
        username = auth.username()
        user = get_user_by_username(username)
        create_comment(db, body, user["id"], post_id)
        data = json.dumps({'body': body, 'post_id': post_id,
                           'author_id': user["id"]})
        return Response(
            data,
            status=201,
            mimetype="application/json"
        )

    error = json.dumps({"error": 'Unknown method'})
    return Response(
        error,
        stauts=405,
        mimetype="application/json"
    )

@bp.route('/posts/<int:post_id>/comments/<int:id>', methods=["PUT", "DELETE"])
@auth.login_required
def comment(post_id, id):
    comment = dict(check_comment(id))
    error = None

    # comment with id does not exist
    if not comment:
        error = json.dumps({"error": "Comment id {0} not available.".format(id)})
    if error:
        return Response(
            error,
            status=404,
            mimetype="application/json"
        )

    # get comment by id
    if request.method == "GET":
        comment['created'] = comment['created'].strftime("%d-%b-%Y (%H:%M:%S)")
        data = json.dumps(dict(comment))
        return Response(
            data,
            status=200,
            mimetype="application/json"
        )

    # update comment by id
    elif request.method == "PUT":
        data = request.get_json()
        body = data.get('body', '')

        if not body:
            error = json.dumps({"error": "Body is required"})
        if error:
            return Response(
                error,
                status=400,
                mimetype="application/json"
            )

        db = get_db()
        update_comment(db, body, id)
        message = json.dumps({'message': 'Comment id {0} update successfully'.format(id)})
        return Response(
            message,
            status=200,
            mimetype="application/json"
        )
    
    # delete comment by id
    elif request.method == "DELETE":
        db = get_db()
        delete_comment(db, id)
        message = json.dumps({'message': 'Comment id {0} delete successfully'.format(id)})
        return Response(
            message,
            status=200,
            mimetype="application/json"
        )