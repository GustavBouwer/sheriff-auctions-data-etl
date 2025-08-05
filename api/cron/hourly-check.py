"""
Vercel Cron Job - Simple hourly check for Legal Notice B PDFs on SAFLII
Runs every hour at minute 0
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle the cron job execution"""
        
        try:
            # Check for PDFs
            results = self.check_for_pdfs()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'cron_job': 'hourly-check',
                'pdfs_found': results['total_pdfs'],
                'pdfs': results['pdfs'][:5]  # Show first 5
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }).encode())
    
    def check_for_pdfs(self):
        """Check SAFLII for Legal Notice B PDFs"""
        
        year = str(datetime.now().year)
        base_url = f"https://www.saflii.org/za/gaz/ZAGovGaz/{year}/"
        
        # Enhanced headers to bypass blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.saflii.org/"
        }
        
        # Fetch the page
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all Legal Notice B links
        all_pdfs = []
        
        for link in soup.find_all('a', href=True):
            if 'Legal Notice B' in link.text or 'Notice B' in link.text:
                pdf_url = link['href']
                if pdf_url.endswith('.pdf'):
                    # Make URL absolute if needed
                    if not pdf_url.startswith('http'):
                        pdf_url = f"https://www.saflii.org{pdf_url}"
                    
                    # Extract filename from URL
                    filename = pdf_url.split('/')[-1]
                    
                    all_pdfs.append({
                        'filename': filename,
                        'url': pdf_url,
                        'link_text': link.text.strip(),
                        'found_at': datetime.now().isoformat()
                    })
        
        return {
            'total_pdfs': len(all_pdfs),
            'pdfs': all_pdfs
        }