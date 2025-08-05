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
        """Check any URL or default to SAFLII for Legal Notice B PDFs"""
        
        try:
            # Parse URL parameter
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Check if custom URL provided
            if 'url' in query_params:
                base_url = query_params['url'][0]
                if not base_url.startswith(('http://', 'https://')):
                    base_url = 'https://' + base_url
                search_for_pdfs = False
            else:
                # Default to SAFLII
                year = str(datetime.now().year)
                base_url = f"https://www.saflii.org/za/gaz/ZAGovGaz/{year}/"
                search_for_pdfs = True
            
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
            
            if search_for_pdfs:
                # Find Legal Notice B links (SAFLII mode)
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
                
                response_data = {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'base_url': base_url,
                    'mode': 'saflii_pdf_search',
                    'user_agent_used': user_agent.split()[0],
                    'total_pdfs_found': len(all_pdfs),
                    'pdfs': all_pdfs
                }
            else:
                # General URL test mode
                title = soup.find('title')
                title_text = title.text.strip() if title else "No title found"
                
                # Count different elements
                links = len(soup.find_all('a'))
                images = len(soup.find_all('img'))
                forms = len(soup.find_all('form'))
                
                # Get first few paragraphs for content sample
                content_elements = soup.find_all(['p', 'div', 'h1', 'h2'], limit=5)
                content_sample = []
                for elem in content_elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 20:  # Only meaningful content
                        content_sample.append(text[:200])  # First 200 chars
                
                response_data = {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'url_tested': base_url,
                    'mode': 'general_url_test',
                    'user_agent_used': user_agent.split()[0],
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type'),
                    'page_info': {
                        'title': title_text,
                        'links_count': links,
                        'images_count': images,
                        'forms_count': forms,
                        'content_length': len(response.text),
                        'content_sample': content_sample[:3]  # First 3 meaningful elements
                    }
                }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }).encode())