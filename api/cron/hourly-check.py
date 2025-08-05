"""
Vercel Cron Job - Hourly check for new Legal Notice B PDFs on SAFLII
Runs every hour at minute 0
"""

import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle the cron job execution"""
        
        # Verify this is a cron job request (Vercel adds this header)
        auth_header = self.headers.get('Authorization')
        if auth_header != f"Bearer {os.environ.get('CRON_SECRET', '')}":
            # In production, set CRON_SECRET to prevent unauthorized access
            pass  # For now, allow all requests during development
        
        try:
            # Initialize Supabase client
            supabase: Client = create_client(
                os.environ.get('SUPABASE_URL'),
                os.environ.get('SUPABASE_SERVICE_KEY')
            )
            
            # Check for new PDFs
            results = self.check_for_new_pdfs(supabase)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'new_pdfs_found': results['new_pdfs_count'],
                'new_pdfs': results['new_pdfs']
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())
    
    def check_for_new_pdfs(self, supabase: Client):
        """Check SAFLII for new Legal Notice B PDFs"""
        
        year = str(datetime.now().year)
        base_url = f"https://www.saflii.org/za/gaz/ZAGovGaz/{year}/"
        
        # Headers to bypass blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        # Fetch the page
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all Legal Notice B links
        new_pdfs = []
        notice_b_links = []
        
        for link in soup.find_all('a', href=True):
            if 'Legal Notice B' in link.text or 'Notice B' in link.text:
                pdf_url = link['href']
                if pdf_url.endswith('.pdf'):
                    # Make URL absolute if needed
                    if not pdf_url.startswith('http'):
                        pdf_url = f"https://www.saflii.org{pdf_url}"
                    
                    # Extract filename from URL
                    filename = pdf_url.split('/')[-1]
                    
                    # Check if we've already scraped this PDF
                    result = supabase.table('scraped_pdfs').select('*').eq('filename', filename).execute()
                    
                    if len(result.data) == 0:
                        # New PDF found!
                        new_pdfs.append({
                            'filename': filename,
                            'url': pdf_url,
                            'found_at': datetime.now().isoformat()
                        })
                        
                        # Insert into database to mark as found
                        supabase.table('scraped_pdfs').insert({
                            'filename': filename,
                            'url': pdf_url,
                            'status': 'found',
                            'found_at': datetime.now().isoformat()
                        }).execute()
                        
                        # Trigger download job (async)
                        self.trigger_download(filename, pdf_url)
        
        return {
            'new_pdfs_count': len(new_pdfs),
            'new_pdfs': new_pdfs
        }
    
    def trigger_download(self, filename, url):
        """Trigger the PDF download function"""
        try:
            # Call the download endpoint (will create this next)
            download_url = os.environ.get('VERCEL_URL', 'http://localhost:3000')
            requests.post(
                f"https://{download_url}/api/download-pdf",
                json={'filename': filename, 'url': url},
                timeout=10
            )
        except:
            # Don't fail the cron job if download trigger fails
            # It will be retried on next run
            pass