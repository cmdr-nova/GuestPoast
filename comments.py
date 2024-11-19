from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/comments/*": {"origins": "https://address.to.jekyllblog"}})

COMMENTS_FILE = 'comments.json'

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_comments(comments):
    with open(COMMENTS_FILE, 'w') as file:
        json.dump(comments, file)

@app.route('/comments', methods=['GET'])
def get_comments():
    comments = load_comments()
    return jsonify(comments)

@app.route('/comments', methods=['POST'])
def add_comment():
    comment = request.json
    comments = load_comments()
    comments.append(comment)
    save_comments(comments)
    return jsonify(comment), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



