from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model (defined first for foreign key reference)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create DB tables
with app.app_context():
    db.create_all()

@app.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    try:
        current_user_id = get_jwt_identity()
        print(f"Getting notes for user ID: {current_user_id}")  # Debug print
        notes = Note.query.filter_by(user_id=current_user_id).all()
        return jsonify([{'id': n.id, 'title': n.title, 'content': n.content} for n in notes])
    except Exception as e:
        print(f"Error in get_notes: {e}")  # Debug print
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:id>', methods=['GET'])
def get_note(id):
    note = Note.query.get_or_404(id)
    return jsonify({'id': note.id, 'title': note.title, 'content': note.content})

@app.route('/notes', methods=['POST'])
@jwt_required()
def add_note():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Missing title or content'}), 400
        
        if not data['title'].strip() or not data['content'].strip():
            return jsonify({'error': 'Title and content cannot be empty'}), 400
            
        new_note = Note(title=data['title'], content=data['content'], user_id=current_user_id)
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'message': 'Note created!'}), 201
    except Exception as e:
        print(f"Error in add_note: {e}")  # Debug print
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:id>', methods=['PUT'])
def update_note(id):
    note = Note.query.get_or_404(id)
    data = request.get_json()
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    db.session.commit()
    return jsonify({'message': 'Note updated!'})

@app.route('/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted!'})

# User model already defined above

app.config['JWT_SECRET_KEY'] = 'test'
jwt = JWTManager(app)

# Add JWT error handlers for debugging
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid token error: {error}")  # Debug print
    return jsonify({'error': f'Invalid token: {str(error)}'}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is required'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'User already exists!'}), 400

    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token})

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
