from sqlite3 import Connection as SQLite3Connection
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import linked_list
import hash_table
import binary_search_tree
import custom_queue

import random

# App
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlitedb.file"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = 0

# Configure sqlite3 to enforce foreign key constraints
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


db = SQLAlchemy(app)
now = datetime.now()


# Models
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    posts = db.relationship("BlogPost", cascade="all, delete")


class BlogPost(db.Model):
    __tablename__ = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(200))
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# Routes

# Create the User
@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    new_user = User(
        name=data["name"],
        email=data["email"],
        address=data["address"],
        phone=data["phone"],
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 200


# Linked List

# Get all Users in a descending order
@app.route("/user/descending_id", methods=["GET"])
def get_all_users_descending():
    users = User.query.all()
    all_users_ll = linked_list.LinkedList()

    for user in users:
        all_users_ll.insert_beginning(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "phone": user.phone,
            }
        )

    return jsonify(all_users_ll.to_list()), 200


# Get all Users in a ascending order
@app.route("/user/ascending_id", methods=["GET"])
def get_all_users_ascending():
    users = User.query.all()
    all_users_ll = linked_list.LinkedList()

    for user in users:
        all_users_ll.insert_at_end(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "phone": user.phone,
            }
        )

    return jsonify(all_users_ll.to_list()), 200


# Get one user
@app.route("/user/<user_id>", methods=["GET"])
def get_one_user(user_id):
    users = User.query.all()

    all_users_ll = linked_list.LinkedList()

    for user in users:
        all_users_ll.insert_beginning(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "phone": user.phone,
            }
        )

    user = all_users_ll.get_user_by_id(user_id)

    return jsonify(user), 200


# Delete user
@app.route("/user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({}), 200


# Hash Table
# Create a BlogPost
@app.route("/blog_post/<user_id>", methods=["POST"])
def create_blog_post(user_id):
    data = request.get_json()

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "user does not exist!"}), 400

    ht = hash_table.HashTable(10)

    ht.add_key_value("title", data["title"])
    ht.add_key_value("body", data["body"])
    ht.add_key_value("date", now)
    ht.add_key_value("user_id", user_id)

    new_blog_post = BlogPost(
        title=ht.get_value("title"),
        body=ht.get_value("body"),
        date=ht.get_value("date"),
        user_id=ht.get_value("user_id"),
    )
    db.session.add(new_blog_post)
    db.session.commit()
    return jsonify({"message": "new blog post created"}), 200


# Binary Search
# Get blog post id
@app.route("/blog_post/<blog_post_id>", methods=["GET"])
def get_one_blog_post(blog_post_id):
    """Search for a blog post using the binary search method and
    return blog post data as a JSON object or provide an error
    message if requesting blog post id does not exist.

    Args:
        blog_post_id (int): numeric blog post id

    Returns:
        JSON: binary search result
    """

    # Query all the blog post data
    blog_posts = BlogPost.query.all()

    # Shuffle data to optimize future search tree
    random.shuffle(blog_posts)

    # Create BinarySearchTree instance
    bst = binary_search_tree.BinarySearchTree()


    # Insert all retrieved data to the tree
    for post in blog_posts:
        bst.insert({
            "id" : post.id,
            "title" : post.title,
            "body" : post.body,
            "user_id" : post.user_id,
        })

    # Search post using binary search method
    post = bst.search(blog_post_id)

    if not post:
        return jsonify({"message": "post not found"})

    return jsonify(post)


# Queue
# Get numeric body of the blog post
@app.route("/blog_post/numeric_body", methods=["GET"])
def get_numeric_post_bodies():
    """Covert text of the blog post body to a single integer, 
    and return all blog posts with the this transformation.

    Returns:
        JSON: transformed blog post data
    """

    # Query all the blog posts data
    blog_posts = BlogPost.query.all()

    # Create an empty Queue instance
    q = custom_queue.Queue()

    # Add data to the queue using enqueue method
    # (ascending order)
    for post in blog_posts:
        q.enqueue(post)

    return_list = []

    # Remove data from the queue using dequeue method 
    # (descending order)
    for _ in range(len(blog_posts)):
        post = q.dequeue()

        # Convert each character of removed post body to an integer
        # (increasing the numeric body with this integer)
        numeric_body = 0
        for char in post.data.body:
            numeric_body += ord(char)

        # Assign new value to the blog post body
        post.data.body = numeric_body

        # Add transformed data to a return list
        return_list.append(
            {
                "id": post.data.id,
                "title" : post.data.title,
                "body" : post.data.body,
                "user_id" : post.data.user_id,
            }
        )

    return jsonify(return_list)


if __name__ == "__main__":
    app.run(debug=True)