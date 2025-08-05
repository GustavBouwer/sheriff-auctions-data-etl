"""
Simple endpoint to check SAFLII for Legal Notice B PDFs
Uses proven strategies from sheriff-scraper
"""

import json
import random
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):
    
    # Multiple user agents that work (from your sheriff-scraper)
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
    ]
    
    def do_GET(self):
        """Check SAFLII for Legal Notice B PDFs"""
        
        try:
            year = str(datetime.now().year)
            base_url = f"https://www.saflii.org/za/gaz/ZAGovGaz/{year}/"
            
            # Random user agent selection (proven strategy)
            user_agent = random.choice(self.USER_AGENTS)
            
            # Simplified headers that work (based on your sheriff-scraper)
            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
            
            # Add small random delay (rate limiting)
            time.sleep(random.uniform(0.5, 2.0))
            
            # Create session with simpler approach
            session = requests.Session()
            session.headers.update(headers)
            
            # Fetch the page with longer timeout
            response = session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all Legal Notice B links
            all_pdfs = []
            
            for link in soup.find_all('a', href=True):
                if 'Legal Notice B' in link.text or 'Notice B' in link.text:
                    pdf_url = link['href']
                    if pdf_url.endswith('.pdf'):
                        if not pdf_url.startswith('http'):
                            pdf_url = f"https://www.saflii.org{pdf_url}"
                        
                        filename = pdf_url.split('/')[-1]
                        
                        pdf_info = {
                            'filename': filename,
                            'url': pdf_url,
                            'link_text': link.text.strip()
                        }
                        
                        all_pdfs.append(pdf_info)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'base_url': base_url,
                'total_pdfs_found': len(all_pdfs),
                'pdfs': all_pdfs
            }, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }).encode())