# Flask App - Proper MVC Structure
from flask import Flask, render_template, request, jsonify, url_for
import requests
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # API Configuration
    app.config['API_BASE_URL'] = 'http://localhost:5000'
    
    # Register Blueprints
    from blueprints.main import bp as main_bp
    from blueprints.users import bp as users_bp  
    from blueprints.botnet import bp as botnet_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(botnet_bp, url_prefix='/botnet')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)