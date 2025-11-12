# Botnet Blueprint - Botnet operations  
from flask import Blueprint, render_template, request, jsonify, current_app
import requests

bp = Blueprint('botnet', __name__)

@bp.route('/')
def index():
    return render_template('botnet/index.html', title='Botnet Control')

@bp.route('/api/run', methods=['POST'])
def run_botnet():
    try:
        api_url = current_app.config['API_BASE_URL']
        data = request.get_json()
        
        response = requests.post(f'{api_url}/botnet', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500