"""
Simple Flask-based CRUD interface for User API
Run with: python front-end-app.py
"""

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
API_URL = "http://localhost:5000/users"

# API proxy routes
@app.route('/')
def index():
    return render_template('crud_interface.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        resp = requests.get(f"{API_URL}")
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        resp = requests.post(f"{API_URL}", json=request.json)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/users/by-username/<username>', methods=['PUT'])
def update_user(username):
    try:
        resp = requests.put(f"{API_URL}/by-username/{username}", json=request.json)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/users/by-username/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        resp = requests.delete(f"{API_URL}/by-username/{username}")
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    print("🚀 Starting KJC Testing API Event...")
    print("📖 Frontend: http://localhost:8002")
    app.run(debug=True, port=8002)
