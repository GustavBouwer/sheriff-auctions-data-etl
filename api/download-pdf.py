"""
Download PDF function - Downloads and stores PDFs in Supabase Storage
"""

import os
import json
from http.server import BaseHTTPRequestHandler
import requests
from supabase import create_client, Client
from datetime import datetime
import base64

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle PDF download request"""
        
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            filename = data.get('filename')
            url = data.get('url')
            
            if not filename or not url:
                raise ValueError("Missing filename or URL")
            
            # Initialize Supabase client
            supabase: Client = create_client(
                os.environ.get('SUPABASE_URL'),
                os.environ.get('SUPABASE_SERVICE_KEY')
            )
            
            # Download the PDF
            result = self.download_and_store_pdf(supabase, filename, url)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())
    
    def download_and_store_pdf(self, supabase: Client, filename, url):
        """Download PDF and store in Supabase Storage"""
        
        # Update status to downloading
        supabase.table('scraped_pdfs').update({
            'status': 'downloading',
            'download_started_at': datetime.now().isoformat()
        }).eq('filename', filename).execute()
        
        try:
            # Headers to bypass blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/pdf,*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.saflii.org/",
                "Cache-Control": "no-cache"
            }
            
            # Download the PDF
            response = requests.get(url, headers=headers, timeout=60, stream=True)
            response.raise_for_status()
            
            # Get PDF content
            pdf_content = response.content
            
            # Store in Supabase Storage
            # Create bucket if it doesn't exist
            try:
                supabase.storage.create_bucket('sheriff-auction-pdfs', {
                    'public': False,
                    'file_size_limit': 52428800  # 50MB limit
                })
            except:
                # Bucket might already exist
                pass
            
            # Upload to storage
            storage_path = f"{datetime.now().year}/{filename}"
            supabase.storage.from_('sheriff-auction-pdfs').upload(
                storage_path,
                pdf_content,
                {
                    'content-type': 'application/pdf',
                    'cache-control': '3600'
                }
            )
            
            # Update database record
            supabase.table('scraped_pdfs').update({
                'status': 'downloaded',
                'storage_path': storage_path,
                'file_size': len(pdf_content),
                'downloaded_at': datetime.now().isoformat()
            }).eq('filename', filename).execute()
            
            # Trigger processing (optional - can be separate cron)
            self.trigger_processing(filename, storage_path)
            
            return {
                'success': True,
                'filename': filename,
                'storage_path': storage_path,
                'size': len(pdf_content)
            }
            
        except Exception as e:
            # Update status to failed
            supabase.table('scraped_pdfs').update({
                'status': 'download_failed',
                'error_message': str(e),
                'failed_at': datetime.now().isoformat()
            }).eq('filename', filename).execute()
            
            raise e
    
    def trigger_processing(self, filename, storage_path):
        """Trigger the PDF processing function"""
        try:
            # Call the process endpoint
            process_url = os.environ.get('VERCEL_URL', 'http://localhost:3000')
            requests.post(
                f"https://{process_url}/api/process-pdf",
                json={'filename': filename, 'storage_path': storage_path},
                timeout=10
            )
        except:
            # Processing will be picked up by another job if this fails
            pass