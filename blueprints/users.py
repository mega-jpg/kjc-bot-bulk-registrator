# Users Blueprint - User management
from flask import Blueprint, render_template, request, jsonify, current_app
import requests

bp = Blueprint('users', __name__)

@bp.route('/')
def index():
    return render_template('users/index.html', title='User Management')

@bp.route('/api/create', methods=['POST'])
def create_user():
    try:
        api_url = current_app.config['API_BASE_URL']
        data = request.get_json()
        
        response = requests.post(f'{api_url}/users', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/delete/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        api_url = current_app.config['API_BASE_URL']
        
        response = requests.delete(f'{api_url}/users/by-username/{username}')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500