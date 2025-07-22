from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from .models import db, User, Note

bp = Blueprint("main", __name__)


@bp.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    try:
        current_user_id = get_jwt_identity()
        notes = Note.query.filter_by(user_id=current_user_id).all()
        return jsonify(
            [{"id": n.id, "title": n.title, "content": n.content}
                for n in notes]
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/notes/<int:id>", methods=["GET"])
def get_note(id):
    note = Note.query.get_or_404(id)
    return jsonify({"id": note.id, "title": note.title, "content": note.content})


@bp.route("/notes", methods=["POST"])
@jwt_required()
def add_note():
    print("Add note function triggered")
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        if not data or "title" not in data or "content" not in data:
            return jsonify({"error": "Missing title or content"}), 400
        if not data["title"].strip() or not data["content"].strip():
            return jsonify({"error": "Title and content cannot be empty"}), 400
        new_note = Note(
            title=data["title"], content=data["content"], user_id=current_user_id
        )
        db.session.add(new_note)
        db.session.commit()
        return jsonify({"message": "Note created!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/notes/<int:id>", methods=["PUT"])
def update_note(id):
    note = Note.query.get_or_404(id)
    data = request.get_json()
    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)
    db.session.commit()
    return jsonify({"message": "Note updated!"})


@bp.route("/notes/<int:id>", methods=["DELETE"])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted!"})


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    existing_user = User.query.filter_by(username=data["username"]).first()
    if existing_user:
        return jsonify({"message": "User already exists!"}), 400
    new_user = User(username=data["username"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials!"}), 401
    access_token = create_access_token(
        identity=str(user.id))
    # For some reason converting user.id to str fixes the note adding feature. Else it gives error 422.
    return jsonify({"access_token": access_token})


@bp.route("/")
def home():
    return render_template("index.html")
