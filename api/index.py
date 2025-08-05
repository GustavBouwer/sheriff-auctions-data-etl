"""
Welcome page for Sheriff Auctions Data ETL
"""

import json
from http.server import BaseHTTPRequestHandler
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Return welcome message"""
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "Sheriff Auctions Data ETL API",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "manual_check": "/api/check-new-pdfs",
                "cron_job": "/api/cron/hourly-check"
            },
            "status": "active"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())