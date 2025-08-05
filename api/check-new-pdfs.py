"""
Manual endpoint to check for new PDFs - useful for testing
"""

import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Manual check for new PDFs"""
        
        try:
            # Initialize Supabase client
            supabase: Client = create_client(
                os.environ.get('SUPABASE_URL'),
                os.environ.get('SUPABASE_SERVICE_KEY')
            )
            
            year = str(datetime.now().year)
            base_url = f"https://www.saflii.org/za/gaz/ZAGovGaz/{year}/"
            
            # Headers to bypass blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            
            # Fetch the page
            response = requests.get(base_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all Legal Notice B links
            all_pdfs = []
            new_pdfs = []
            
            for link in soup.find_all('a', href=True):
                if 'Legal Notice B' in link.text or 'Notice B' in link.text:
                    pdf_url = link['href']
                    if pdf_url.endswith('.pdf'):
                        if not pdf_url.startswith('http'):
                            pdf_url = f"https://www.saflii.org{pdf_url}"
                        
                        filename = pdf_url.split('/')[-1]
                        
                        # Check if already in database
                        result = supabase.table('scraped_pdfs').select('*').eq('filename', filename).execute()
                        
                        is_new = len(result.data) == 0
                        
                        pdf_info = {
                            'filename': filename,
                            'url': pdf_url,
                            'is_new': is_new,
                            'link_text': link.text.strip()
                        }
                        
                        all_pdfs.append(pdf_info)
                        if is_new:
                            new_pdfs.append(pdf_info)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'total_pdfs_found': len(all_pdfs),
                'new_pdfs_count': len(new_pdfs),
                'all_pdfs': all_pdfs[:10],  # Show first 10
                'new_pdfs': new_pdfs
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