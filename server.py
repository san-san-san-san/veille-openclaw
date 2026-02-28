#!/usr/bin/env python3
"""
Mini serveur Flask pour dashboard + scraping manuel
"""

from flask import Flask, jsonify, send_file
from flask_cors import CORS
import subprocess
import threading
import os

app = Flask(__name__)
CORS(app)  # Permettre requêtes depuis dashboard

# État du scraping
scraping_status = {
    'running': False,
    'last_run': None,
    'error': None
}

def run_scraper():
    """Lance le scraper en arrière-plan"""
    global scraping_status
    
    try:
        scraping_status['running'] = True
        scraping_status['error'] = None
        
        # Lancer le scraper v3 (avec résumés IA)
        result = subprocess.run(
            ['python3', 'scraper-twitter-v3.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 min max
        )
        
        if result.returncode == 0:
            scraping_status['last_run'] = 'success'
        else:
            scraping_status['last_run'] = 'error'
            scraping_status['error'] = result.stderr[:500]
    
    except Exception as e:
        scraping_status['last_run'] = 'error'
        scraping_status['error'] = str(e)
    
    finally:
        scraping_status['running'] = False

@app.route('/')
def index():
    """Dashboard"""
    return send_file('dashboard.html')

@app.route('/veille-latest.json')
def get_latest():
    """Retourne les dernières données"""
    return send_file('veille-latest.json')

@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Déclenche un scraping manuel"""
    
    if scraping_status['running']:
        return jsonify({
            'status': 'error',
            'message': 'Scraping déjà en cours...'
        }), 400
    
    # Lancer en arrière-plan
    thread = threading.Thread(target=run_scraper)
    thread.start()
    
    return jsonify({
        'status': 'success',
        'message': 'Scraping lancé ! Rafraîchir dans 1-2 min.'
    })

@app.route('/api/status')
def get_status():
    """Retourne le statut du scraping"""
    return jsonify(scraping_status)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Serveur lancé sur http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
