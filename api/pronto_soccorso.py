"""
Vercel Serverless Function - Pronto Soccorso API
File: api/pronto-soccorso.py

Deploy su Vercel:
1. Crea cartella api/ nel tuo progetto
2. Salva questo file come api/pronto-soccorso.py
3. Deploy: vercel --prod

API disponibile automaticamente su:
https://tuosito.vercel.app/api/pronto-soccorso
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random
from urllib.parse import urlparse, parse_qs


def generate_realistic_data():
    """Genera dati PS realistici"""
    hospitals = [
        {
            "name": "Policlinico Umberto I",
            "address": "Viale del Policlinico, 155 - Roma",
            "province": "Roma",
            "lat": 41.9021,
            "lng": 12.5151
        },
        {
            "name": "Ospedale San Camillo",
            "address": "Circonvallazione Gianicolense, 87 - Roma",
            "province": "Roma",
            "lat": 41.8711,
            "lng": 12.4561
        },
        {
            "name": "Policlinico Gemelli",
            "address": "Largo Agostino Gemelli, 8 - Roma",
            "province": "Roma",
            "lat": 41.9304,
            "lng": 12.4363
        },
        {
            "name": "Ospedale San Giovanni",
            "address": "Via dell'Amba Aradam, 9 - Roma",
            "province": "Roma",
            "lat": 41.8808,
            "lng": 12.5183
        },
        {
            "name": "Ospedale Sant'Andrea",
            "address": "Via di Grottarossa, 1035 - Roma",
            "province": "Roma",
            "lat": 41.9650,
            "lng": 12.4740
        },
        {
            "name": "Ospedale Sandro Pertini",
            "address": "Via dei Monti Tiburtini, 385 - Roma",
            "province": "Roma",
            "lat": 41.9247,
            "lng": 12.5494
        },
        {
            "name": "Ospedale Cristo Re",
            "address": "Via delle Calasanziane, 25 - Roma",
            "province": "Roma",
            "lat": 41.8563,
            "lng": 12.4934
        },
        {
            "name": "Ospedale Grassi",
            "address": "Via Gregorio Grassi, 5 - Roma",
            "province": "Roma",
            "lat": 41.7312,
            "lng": 12.5823
        },
        {
            "name": "Ospedale Santa Maria Goretti",
            "address": "Via Antonio Canova - Latina",
            "province": "Latina",
            "lat": 41.4675,
            "lng": 12.9035
        },
        {
            "name": "Ospedale Spaziani",
            "address": "Piazzale Kambo, 1 - Frosinone",
            "province": "Frosinone",
            "lat": 41.6401,
            "lng": 13.3387
        },
        {
            "name": "Ospedale San Camillo De Lellis",
            "address": "Viale Kennedy - Rieti",
            "province": "Rieti",
            "lat": 42.4036,
            "lng": 12.8614
        },
        {
            "name": "Ospedale Belcolle",
            "address": "Strada Sammartinese - Viterbo",
            "province": "Viterbo",
            "lat": 42.4213,
            "lng": 12.1088
        }
    ]
    
    # Pattern realistici
    now = datetime.now()
    hour = now.hour
    is_weekend = now.weekday() >= 5
    is_rush_hour = (9 <= hour <= 12) or (18 <= hour <= 21)
    
    base_load = 1.5 if is_rush_hour else 1.0
    weekend_factor = 1.2 if is_weekend else 1.0
    
    results = []
    
    for hospital in hospitals:
        hospital_factor = 0.7 + random.random() * 0.6
        total_factor = base_load * weekend_factor * hospital_factor
        
        red = max(0, int((1 + random.random() * 3) * hospital_factor))
        orange = max(0, int((4 + random.random() * 8) * total_factor))
        blue = max(0, int((8 + random.random() * 15) * total_factor))
        green = max(0, int((12 + random.random() * 20) * total_factor))
        white = max(0, int((5 + random.random() * 12) * total_factor))
        
        total = red + orange + blue + green + white
        avg_wait = int(30 + (total * 0.8) + (random.random() * 20))
        
        results.append({
            "hospital_name": hospital["name"],
            "address": hospital["address"],
            "province": hospital["province"],
            "latitude": hospital["lat"],
            "longitude": hospital["lng"],
            "red_code": red,
            "orange_code": orange,
            "blue_code": blue,
            "green_code": green,
            "white_code": white,
            "total_patients": total,
            "avg_wait_time": avg_wait,
            "last_update": now.isoformat()
        })
    
    return results


class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Function Handler
    
    Endpoints:
    - GET /api/pronto-soccorso
    - GET /api/pronto-soccorso?province=Roma
    """
    
    def do_GET(self):
        # Parse URL
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Genera dati
        data = generate_realistic_data()
        
        # Filtra per provincia se richiesto
        province = query_params.get('province', [None])[0]
        if province:
            data = [h for h in data if h['province'].lower() == province.lower()]
        
        # Statistiche
        total_hospitals = len(data)
        total_patients = sum(h['total_patients'] for h in data)
        total_red = sum(h['red_code'] for h in data)
        avg_wait = sum(h['avg_wait_time'] for h in data) // total_hospitals if total_hospitals > 0 else 0
        
        # Response
        response_data = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'count': len(data),
            'stats': {
                'total_hospitals': total_hospitals,
                'total_patients': total_patients,
                'total_red_codes': total_red,
                'avg_wait_time': avg_wait
            },
            'data': data
        }
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'public, max-age=300, s-maxage=300')  # 5 min cache
        self.end_headers()
        
        # Body
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
