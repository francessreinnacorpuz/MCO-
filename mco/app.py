from flask import Flask, request, jsonify, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# In-memory storage for users and messages
users = {}
messages = []

# Load messages from a file if it exists
if os.path.exists('messages.json'):
    with open('messages.json', 'r') as f:
        messages = json.load(f)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    if username in users:
        return jsonify({'status': 'Username already taken'}), 400
    users[username] = True
    return jsonify({'status': 'User registered'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    if username in users:
        session['username'] = username
        return jsonify({'status': 'Logged in'}), 200
    return jsonify({'status': 'User not found'}), 404

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'status': 'Logged out'}), 200

@app.route('/send', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    data = request.json
    message = {
        'username': session['username'],
        'message': data['message'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    messages.append(message)
    # Save messages to a file
    with open('messages.json', 'w') as f:
        json.dump(messages, f)
    return jsonify({'status': 'Message sent'}), 200

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({'messages': messages}), 200

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({'users': list(users.keys())}), 200

@app.route('/delete/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    if message_id < 0 or message_id >= len(messages):
        return jsonify({'status': 'Message not found'}), 404
    deleted_message = messages.pop(message_id)
    # Save updated messages to a file
    with open('messages.json', 'w') as f:
        json.dump(messages, f)
    return jsonify({'status': 'Message deleted', 'message': deleted_message}), 200

@app.route('/edit/<int:message_id>', methods=['PUT'])
def edit_message(message_id):
    if 'username' not in session:
        return jsonify({'status': 'Unauthorized'}), 401
    if message_id < 0 or message_id >= len(messages):
        return jsonify({'status': 'Message not found'}), 404
    data = request.json
    messages[message_id]['message'] = data['message']
    # Save updated messages to a file
    with open('messages.json', 'w') as f:
        json.dump(messages, f)
    return jsonify({'status': 'Message edited', 'message': messages[message_id]}), 200

if __name__ == '__main__':
    app.run(debug=True)
