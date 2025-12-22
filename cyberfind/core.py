import asyncio
import csv
import json
import logging
import os
import random
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, date
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urlparse

import aiohttp
import cloudscraper
import pandas as pd
import requests
import yaml
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logger = logging.getLogger("cyberfind")

class SearchMode(Enum):
    """Search modes for different stealth levels"""
    STANDARD = "standard"
    DEEP = "deep"
    STEALTH = "stealth"
    AGGRESSIVE = "aggressive"

class OutputFormat(Enum):
    """Output formats for results"""
    TXT = "txt"
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    EXCEL = "excel"
    SQLITE = "sqlite"

class SiteCategory(Enum):
    """Categories for site classification"""
    SOCIAL_MEDIA = "social_media"
    FORUMS = "forums"
    BLOGS = "blogs"
    GAMING = "gaming"
    PROGRAMMING = "programming"
    ECOMMERCE = "ecommerce"
    RUSSIAN = "russian"
    ALL = "all"

class CyberFind:
    """Main class for CyberFind OSINT tool"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize CyberFind with configuration"""
        self.config = self.load_config(config_path)
        self.initialize_components()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        default_config = {
            'general': {
                'timeout': 30,
                'max_threads': 50,
                'retry_attempts': 3,
                'retry_delay': 2,
                'user_agents_rotation': True,
                'rate_limit_delay': 0.5,
            },
            'proxy': {
                'enabled': False,
                'list': [],
                'rotation': True,
            },
            'database': {
                'sqlite_path': 'cyberfind.db',
            },
            'output': {
                'default_format': 'json',
                'save_all_results': True,
            },
            'advanced': {
                'metadata_extraction': True,
                'cache_results': True,
                'verify_ssl': True,
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                
                def update_dict(d: Dict, u: Dict) -> None:
                    """Recursively update dictionary"""
                    for k, v in u.items():
                        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                            update_dict(d[k], v)
                        else:
                            d[k] = v
                
                update_dict(default_config, user_config)
            except Exception as e:
                logger.warning(f"Error loading config file {config_path}: {e}. Using default config.")
        
        return default_config
    
    def get_builtin_site_path(self, list_name: str) -> Optional[Path]:
        """
        Get path to built-in site list file.
        Works both in development and after `pip install`.
        """
        filename = f"{list_name}.txt"

        # 1. Try from package resources (works after pip install)
        try:
            import importlib.resources as pkg_resources
            resource_path = pkg_resources.files('cyberfind.sites').joinpath(filename)
            if resource_path.exists():
                return Path(str(resource_path))
        except Exception as e:
            logger.debug(f"Could not load {filename} from package: {e}")

        # 2. Try local directory (for development)
        local_path = Path(__file__).parent / "sites" / filename
        if local_path.exists():
            return local_path

        logger.error(f"Built-in site list not found: {filename}")
        return None
    
    def initialize_components(self) -> None:
        """Initialize all components"""
        self.ua = UserAgent()
        self.session = requests.Session()
        self.cloud_session = cloudscraper.create_scraper()
        
        self.proxy_list = []
        self.current_proxy_index = 0
        
        self.init_database()
        
        # Initialize statistics
        self.stats = {
            'total_checks': 0,
            'found_accounts': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None,
            'sites_checked': defaultdict(int),
            'response_times': []
        }
        
        self.cache = {}
        self.cache_ttl = 300
        
        # Load built-in site lists
        self.builtin_sites = self.load_builtin_sites()
    
    def load_builtin_sites(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load built-in site lists from files"""
        return {}
    
    def get_builtin_site_list(self, list_name: str = 'quick') -> List[Dict[str, Any]]:
        """Get built-in site list by name"""
        if list_name in self.builtin_sites:
            return self.builtin_sites[list_name]
        else:
            return self.builtin_sites.get('quick', [])
    
    def list_builtin_categories(self) -> Dict[str, int]:
        """Show available built-in categories and site counts"""
        categories = {}
        for name, sites in self.builtin_sites.items():
            categories[name] = len(sites)
        return categories
    
    def init_database(self) -> None:
        """Initialize SQLite database"""
        db_path = self.config['database']['sqlite_path']
        
        if db_path:
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.getcwd(), db_path)
            
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        else:
            db_path = os.path.join(os.getcwd(), 'cyberfind.db')
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                site_name TEXT NOT NULL,
                url TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                found BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                UNIQUE(username, site_name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                searches_count INTEGER DEFAULT 0,
                accounts_found INTEGER DEFAULT 0,
                total_time REAL DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """JSON serializer for objects not serializable by default json module"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, (set, tuple)):
            return list(obj)
        elif isinstance(obj, defaultdict):
            return dict(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
    
    async def search_async(self, usernames: List[str], 
                          sites_file: Optional[str] = None,
                          builtin_list: Optional[str] = None,
                          mode: SearchMode = SearchMode.STANDARD,
                          output_format: OutputFormat = OutputFormat.JSON,
                          output_file: Optional[str] = None,
                          max_concurrent: int = 50) -> Dict[str, Any]:
        """
        Main search method
        
        Args:
            usernames: List of usernames to search for
            sites_file: Path to file with sites list
            builtin_list: Name of built-in site list to use
            mode: Search mode (standard, deep, stealth, aggressive)
            output_format: Format for output results
            output_file: Filename to save results
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary with search results, report and statistics
        """
        
        self.stats['start_time'] = datetime.now()
        
        # Load sites from file or built-in list
        sites = await self.load_sites_async(sites_file, builtin_list)
        
        if not sites:
            logger.error("No sites loaded!")
            return {
                'results': {},
                'report': {},
                'statistics': self.stats
            }
        
        print(f"📋 Loaded {len(sites)} sites")
        
        all_results = {}
        
        # Search for each username
        for username in usernames:
            print(f"\n🔍 Searching: {username}")
            user_results = await self.search_single_user_async(
                username, sites, mode, max_concurrent
            )
            all_results[username] = user_results
            
            # Save intermediate results if configured
            if self.config['output']['save_all_results']:
                self.save_results_intermediate(username, user_results)
        
        self.stats['end_time'] = datetime.now()
        
        # Save results if output file specified
        if output_file:
            await self.save_results_async(all_results, output_format, output_file)
        
        # Generate report and update statistics
        report = await self.generate_report_async(all_results)
        self.update_statistics()
        
        return {
            'results': all_results,
            'report': report,
            'statistics': self.stats
        }
    
    async def load_sites_async(self, sites_file: Optional[str] = None,
                          builtin_list: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load sites from file or built-in list"""
        sites = []

        if builtin_list:
            print(f"✅ Using built-in list: {builtin_list}")
            file_path = self.get_builtin_site_path(builtin_list)
            if file_path:
                sites.extend(await self.load_sites_from_file_async(file_path))
            else:
                logger.error(f"Built-in list '{builtin_list}' not found!")
                return []

        elif sites_file:
            if os.path.exists(sites_file):
                sites.extend(await self.load_sites_from_file_async(sites_file))
            else:
                logger.error(f"File not found: {sites_file}")
                return []

        else:
            print("✅ Using default built-in list: quick (25 sites)")
            file_path = self.get_builtin_site_path('quick')
            if file_path:
                sites.extend(await self.load_sites_from_file_async(file_path))

        # Убираем дубликаты и дополняем полями
        unique_sites = {}
        for site in sites:
            key = (site['name'], site['url_pattern'])
            if key not in unique_sites:
                # Убедимся, что все поля присутствуют
                processed_site = {
                    'name': site.get('name', 'Unknown'),
                    'url_pattern': site.get('url_pattern', ''),
                    'method': site.get('method', 'GET'),
                    'category': site.get('category', 'unknown'),
                    'priority': site.get('priority', 5),
                    'timeout': site.get('timeout', self.config['general']['timeout']),
                    'retry': site.get('retry', self.config['general']['retry_attempts']),
                    'headers': site.get('headers', {}),
                    'cookies': site.get('cookies', {}),
                    'requires_javascript': site.get('requires_javascript', False),
                    'requires_captcha': site.get('requires_captcha', False),
                    'check_strings': site.get('check_strings', []),
                    'error_strings': site.get('error_strings', []),
                    'valid_status_codes': site.get('valid_status_codes', [200]),
                    'invalid_status_codes': site.get('invalid_status_codes', [404, 410]),
                    'check_type': site.get('check_type', 'content'),
                }
                unique_sites[key] = processed_site

        result = list(unique_sites.values())
        print(f"✅ Loaded {len(result)} unique sites")
        return result
    
    async def load_sites_from_file_async(self, file_path: str) -> List[Dict[str, Any]]:
        """Load sites from file (local or remote)"""
        sites = []
        file_path_str = str(file_path)
        
        try:
            if file_path_str.startswith('http'):
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_path_str) as response:
                        content = await response.text()
            else:
                if not os.path.exists(file_path_str):
                    logger.warning(f"File not found: {file_path_str}")
                    return sites
                
                with open(file_path_str, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Parse each line
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle different delimiters
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                elif '\t' in line:
                    parts = [p.strip() for p in line.split('\t')]
                else:
                    parts = [p.strip() for p in line.split(',')]
                
                if len(parts) >= 2:
                    site = self.parse_site_line(parts)
                    if site:
                        sites.append(site)
        
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
        
        return sites
    
    def parse_site_line(self, parts: List[str]) -> Optional[Dict[str, Any]]:
        """Parse a line from sites file into site dictionary"""
        try:
            if len(parts) < 2:
                return None
            name = parts[0].strip()
            url_pattern = parts[1].strip()
            # Ensure URL pattern has {username} placeholder
            if '{username}' not in url_pattern and '${username}' not in url_pattern:
                if url_pattern.endswith('/'):
                    url_pattern += '{username}'
                else:
                    url_pattern += '/{username}'
            site = {
                'name': name,
                'url_pattern': url_pattern,
                'method': 'GET',
                'category': 'unknown',
                'priority': 5,
                'timeout': self.config['general']['timeout'],
                'retry': self.config['general']['retry_attempts'],
                'headers': {},
                'cookies': {},
                'requires_javascript': False,
                'requires_captcha': False,
                'check_strings': [],
                'error_strings': [],
                'valid_status_codes': [200],
                'invalid_status_codes': [404, 410],
                'check_type': 'status_code',
            }
            # Parse optional fields
            if len(parts) >= 3:
                category = parts[2].strip()
                if category in [cat.value for cat in SiteCategory]:
                    site['category'] = category
            if len(parts) >= 4:
                try:
                    site['priority'] = int(parts[3].strip())
                except ValueError:
                    pass
            # Parse success strings (if exists)
            if len(parts) >= 5:
                site['check_strings'] = [s.strip() for s in parts[4].split(',') if s.strip()]
            # Parse error strings (if exists)
            if len(parts) >= 6:
                site['error_strings'] = [s.strip() for s in parts[5].split(',') if s.strip()]
            return site
        except Exception as e:
            logger.error(f"Error parsing site line: {e}")
            return None
    
    async def search_single_user_async(self, username: str, sites: List[Dict[str, Any]],
                                      mode: SearchMode,
                                      max_concurrent: int) -> Dict[str, Any]:
        """Search for a single user across all sites"""
        
        user_results = {
            'username': username,
            'found': [],
            'not_found': [],
            'errors': [],
            'metadata': {}
        }
        
        # Sort sites by priority (higher priority first)
        sites_sorted = sorted(sites, key=lambda x: x['priority'], reverse=True)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        print(f"  Checking {len(sites_sorted)} sites...")
        
        # Create tasks for all sites
        tasks = []
        for i, site in enumerate(sites_sorted):
            task = asyncio.create_task(
                self.check_site_async(username, site, mode, semaphore)
            )
            tasks.append(task)
            
            # Show progress every 10 sites
            if i % 10 == 0 and i > 0:
                print(f"    Progress: {i}/{len(sites_sorted)}")
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        found_count = 0
        error_count = 0
        
        # Process results
        for i, result in enumerate(results):
            site = sites_sorted[i]
            if isinstance(result, Exception):
                user_results['errors'].append({
                    'site': site['name'],
                    'url': site['url_pattern'].replace('{username}', username),
                    'error': str(result),
                })
                self.stats['errors'] += 1
                error_count += 1
                continue
            
            self.stats['total_checks'] += 1
            
            if result['found']:
                user_results['found'].append(result)
                self.stats['found_accounts'] += 1
                found_count += 1
                # Show found accounts immediately
                print(f"    ✓ Found: {result['site']}")
            elif result['error']:
                user_results['errors'].append(result)
                self.stats['errors'] += 1
                error_count += 1
            else:
                user_results['not_found'].append(result)
        
        print(f"  Done: {found_count} found, {error_count} errors")
        
        # Add metadata
        user_results['metadata'] = {
            'search_timestamp': datetime.now().isoformat(),
            'search_mode': mode.value,
            'sites_checked': len(sites),
            'accounts_found': len(user_results['found']),
            'errors_count': len(user_results['errors'])
        }
        
        return user_results
    
    async def check_site_async(self, username: str, site: Dict[str, Any],
                              mode: SearchMode, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Check if user exists on a specific site"""
        
        async with semaphore:
            result = {
                'site': site['name'],
                'url': None,
                'found': False,
                'status_code': None,
                'response_time': 0,
                'error': None,
                'metadata': {}
            }
            
            try:
                url = site['url_pattern'].replace('{username}', username)
                result['url'] = url
                
                start_time = time.time()
                
                # Make request
                response_data = await self.request_standard_async(url, site, mode)
                
                result['response_time'] = time.time() - start_time
                self.stats['response_times'].append(result['response_time'])
                
                if response_data['success']:
                    result['status_code'] = response_data['status']
                    
                    # Extract metadata if enabled
                    if self.config.get('advanced', {}).get('metadata_extraction', True):
                        metadata = await self.extract_metadata_async(
                            url, response_data['content']
                        )
                        result['metadata'].update(metadata)
                        result['metadata']['category'] = site['category']
                    
                    # Check if user exists
                    result['found'] = self.check_user_exists(
                        response_data, site, username
                    )
                else:
                    result['error'] = response_data['error']
                    
            except Exception as e:
                result['error'] = str(e)
                logger.error(f"Error checking {site['name']}: {e}")
            
            return result
    
    async def request_standard_async(self, url: str, site: Dict[str, Any],
                                    mode: SearchMode) -> Dict[str, Any]:
        """Make HTTP request with retries"""
        
        headers = self.generate_headers(mode)
        headers.update(site.get('headers', {}))
        
        timeout = ClientTimeout(total=site['timeout'])
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(site['retry']):
                try:
                    async with session.get(url, headers=headers) as response:
                        content = await response.text()
                        return {
                            'success': True,
                            'status': response.status,
                            'headers': dict(response.headers),
                            'content': content
                        }
                        
                except asyncio.TimeoutError:
                    if attempt == site['retry'] - 1:
                        return {'success': False, 'error': 'Timeout'}
                    await asyncio.sleep(self.config['general']['retry_delay'])
                except Exception as e:
                    if attempt == site['retry'] - 1:
                        return {'success': False, 'error': str(e)}
                    await asyncio.sleep(self.config['general']['retry_delay'])
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
    def generate_headers(self, mode: SearchMode) -> Dict[str, str]:
        """Generate HTTP headers based on search mode"""
        base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if mode == SearchMode.STEALTH:
            base_headers.update({
                'User-Agent': self.ua.random,
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            })
        elif mode == SearchMode.AGGRESSIVE:
            base_headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            })
        else:
            base_headers.update({
                'User-Agent': self.ua.random,
            })
        
        return base_headers
    
    def check_user_exists(self, response_data: Dict[str, Any], site: Dict[str, Any], username: str) -> bool:
        """Determine if user exists based on response using content + status logic"""
        status = response_data['status']
        content = response_data['content']  # keep original case for regex later if needed

        
        if status in site['invalid_status_codes']:
            return False

        
        if status in site['valid_status_codes']:
            if site['error_strings']:
                content_lower = content.lower()
                for err_str in site['error_strings']:
                    if err_str.lower() in content_lower:
                        return False

            if site['check_strings']:
                content_lower = content.lower()
                for check_str in site['check_strings']:
                    if check_str.lower() in content_lower:
                        return True
                return False

            return True

        return False
    
    async def extract_metadata_async(self, url: str, content: str) -> Dict[str, Any]:
        """Extract metadata from HTML content"""
        metadata = {
            'title': '',
            'description': '',
            'keywords': [],
            'links': [],
            'images': [],
        }
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.text.strip()
            
            # Extract meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name', '').lower()
                content_val = meta.get('content', '')
                if name == 'description':
                    metadata['description'] = content_val
                elif name == 'keywords':
                    metadata['keywords'] = [
                        k.strip() for k in content_val.split(',')
                    ]
            
            # Extract links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    metadata['links'].append(href)
            
            # Extract images
            for img in soup.find_all('img', src=True):
                metadata['images'].append(img['src'])
        
        except Exception as e:
            logger.debug(f"Error extracting metadata: {e}")
        
        return metadata
    
    def save_results_intermediate(self, username: str, results: Dict[str, Any]) -> None:
        """Save intermediate results to database"""
        try:
            cursor = self.conn.cursor()
            for result in results['found'] + results['not_found'] + results['errors']:
                cursor.execute('''
                    INSERT OR REPLACE INTO search_results
                    (username, site_name, url, status_code, response_time, found, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    username,
                    result['site'],
                    result.get('url', ''),
                    result.get('status_code'),
                    result.get('response_time', 0),
                    result.get('found', False),
                    json.dumps(result.get('metadata', {}), default=self._json_serializer)
                ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    async def save_results_async(self, all_results: Dict[str, Any], 
                                output_format: OutputFormat,
                                output_file: str) -> None:
        """Save results in specified format"""
        
        output_path = Path(output_file)
        
        if output_format == OutputFormat.JSON:
            await self.save_as_json_async(all_results, output_path)
        elif output_format == OutputFormat.CSV:
            await self.save_as_csv_async(all_results, output_path)
        elif output_format == OutputFormat.HTML:
            await self.save_as_html_async(all_results, output_path)
        elif output_format == OutputFormat.EXCEL:
            await self.save_as_excel_async(all_results, output_path)
        elif output_format == OutputFormat.SQLITE:
            self.save_to_database(all_results)
    
    async def save_as_json_async(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save results as JSON"""
        try:
            def convert_for_json(obj: Any) -> Any:
                """Convert objects for JSON serialization"""
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                elif isinstance(obj, (set, tuple)):
                    return list(obj)
                elif isinstance(obj, defaultdict):
                    return dict(obj)
                elif isinstance(obj, dict):
                    return {k: convert_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [convert_for_json(item) for item in obj]
                elif hasattr(obj, '__dict__'):
                    return convert_for_json(obj.__dict__)
                else:
                    return obj
            
            stats_copy = convert_for_json(self.stats)

            full_results = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'tool': 'CyberFind',
                    'version': '0.1.0',
                    'statistics': stats_copy
                },
                'results': convert_for_json(results)
            }
            
            with open(f'{output_path}.json', 'w', encoding='utf-8') as f:
                json.dump(full_results, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            logger.info(f"Results saved to {output_path}.json")
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
    
    async def save_as_csv_async(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save results as CSV"""
        try:
            with open(f'{output_path}.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Username', 'Site', 'URL', 'Status Code', 'Response Time', 'Found', 'Error', 'Title'])

                for username, user_results in results.items():
                    for result in user_results['found'] + user_results['not_found'] + user_results['errors']:
                        metadata = result.get('metadata', {})
                        writer.writerow([
                            username,
                            result['site'],
                            result.get('url', ''),
                            result.get('status_code', ''),
                            result.get('response_time', 0),
                            result.get('found', False),
                            result.get('error', ''),
                            metadata.get('title', ''),
                        ])
            logger.info(f"Results saved to {output_path}.csv")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
    
    async def save_as_html_async(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save results as HTML report"""
        try:
            found_count = sum(len(r['found']) for r in results.values())
            not_found_count = sum(len(r['not_found']) for r in results.values())
            errors_count = sum(len(r['errors']) for r in results.values())
            
            start_time = self.stats.get('start_time', datetime.now())
            end_time = self.stats.get('end_time', datetime.now())
            time_taken = (end_time - start_time).total_seconds()

            users_html_parts = []
            for username, user_results in results.items():
                rows = []
                for result in user_results['found']:
                    rows.append(f"""
                    <tr>
                        <td>{result['site']}</td>
                        <td><a href="{result.get('url', '#')}" target="_blank">{result.get('url', '')}</a></td>
                        <td>{result.get('status_code', '')}</td>
                        <td>{result.get('response_time', 0):.2f}s</td>
                    </tr>
                    """)
                user_table = "".join(rows)
                users_html_parts.append(f"""
                <div class="user-section">
                    <h3>User: {username}</h3>
                    <table class="results-table">
                        <thead>
                            <tr><th>Site</th><th>URL</th><th>Status</th><th>Time</th></tr>
                        </thead>
                        <tbody>
                            {user_table}
                        </tbody>
                    </table>
                </div>
                """)

            all_users_html = "".join(users_html_parts)

            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>CyberFind Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .summary {{ background-color: #f0f0f0; padding: 10px; margin-bottom: 20px; }}
                    table.results-table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; }}
                </style>
            </head>
            <body>
                <h1>CyberFind Report</h1>
                <div class="summary">
                    <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <p><strong>Accounts found:</strong> {found_count}</p>
                    <p><strong>Not found:</strong> {not_found_count}</p>
                    <p><strong>Errors:</strong> {errors_count}</p>
                    <p><strong>Time taken:</strong> {time_taken:.2f} seconds</p>
                </div>
                {all_users_html}
            </body>
            </html>
            """
            with open(f'{output_path}.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Results saved to {output_path}.html")
        except Exception as e:
            logger.error(f"Error saving HTML: {e}")
    
    async def save_as_excel_async(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save results as Excel file"""
        try:
            with pd.ExcelWriter(f'{output_path}.xlsx', engine='openpyxl') as writer:
                data = []
                for username, user_results in results.items():
                    for result in user_results['found']:
                        data.append({
                            'Username': username,
                            'Site': result['site'],
                            'URL': result.get('url', ''),
                            'Status': 'Found',
                            'Status Code': result.get('status_code', ''),
                            'Response Time': result.get('response_time', 0),
                            'Title': result.get('metadata', {}).get('title', '')
                        })
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='Results', index=False)
                
                stats_df = pd.DataFrame([self.stats])
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            logger.info(f"Results saved to {output_path}.xlsx")
        except Exception as e:
            logger.error(f"Error saving Excel: {e}")
    
    def save_to_database(self, results: Dict[str, Any]) -> None:
        """Save results to SQLite database"""
        try:
            cursor = self.conn.cursor()
            for username, user_results in results.items():
                for result in user_results['found'] + user_results['not_found'] + user_results['errors']:
                    cursor.execute('''
                        INSERT OR REPLACE INTO search_results
                        (username, site_name, url, status_code, response_time, found, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        username,
                        result['site'],
                        result.get('url', ''),
                        result.get('status_code'),
                        result.get('response_time', 0),
                        result.get('found', False),
                        json.dumps(result.get('metadata', {}), default=self._json_serializer)
                    ))
            self.conn.commit()
            logger.info("Results saved to database")
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    async def generate_report_async(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive search report"""
        report = {
            'summary': {
                'total_users': len(results),
                'total_accounts_found': 0,
                'total_errors': 0,
                'unique_sites_found': set(),
                'categories_found': defaultdict(int)
            },
            'users': {},
            'risk_assessment': {},
            'recommendations': []
        }
        
        for username, user_results in results.items():
            user_summary = {
                'accounts_found': len(user_results['found']),
                'sites_found': [],
                'categories': defaultdict(int),
            }
            
            for result in user_results['found']:
                site_name = result['site']
                user_summary['sites_found'].append(site_name)
                report['summary']['unique_sites_found'].add(site_name)
                
                category = result.get('metadata', {}).get('category', 'unknown')
                user_summary['categories'][category] += 1
                report['summary']['categories_found'][category] += 1
            
            report['summary']['total_accounts_found'] += user_summary['accounts_found']
            report['summary']['total_errors'] += len(user_results['errors'])
            report['users'][username] = user_summary
        
        report['risk_assessment'] = self.assess_risks(results)
        report['recommendations'] = self.generate_recommendations(results)
        
        return report
    
    def assess_risks(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Assess privacy and security risks based on found accounts"""
        risks = {
            'privacy_risk': 'low',
            'reputation_risk': 'low',
            'security_risk': 'low',
            'social_engineering_risk': 'low',
            'overall_risk': 'low'
        }
        
        high_risk_sites = {'linkedin', 'facebook', 'instagram', 'twitter', 'vk', 'ok'}
        medium_risk_sites = {'github', 'gitlab', 'reddit', 'pinterest', 'telegram'}
        
        found_sites = set()
        for user_results in results.values():
            for result in user_results['found']:
                found_sites.add(result['site'].lower())
        
        high_risk_count = len(found_sites.intersection(high_risk_sites))
        medium_risk_count = len(found_sites.intersection(medium_risk_sites))
        
        if high_risk_count >= 3:
            risks['privacy_risk'] = 'high'
            risks['overall_risk'] = 'high'
        elif high_risk_count >= 1 or medium_risk_count >= 3:
            risks['privacy_risk'] = 'medium'
            risks['overall_risk'] = 'medium'
        
        total_accounts = sum(len(r['found']) for r in results.values())
        if total_accounts > 10:
            risks['reputation_risk'] = 'medium'
        
        return risks
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on search results"""
        recommendations = []
        total_accounts = sum(len(r['found']) for r in results.values())
        
        if total_accounts == 0:
            recommendations.append("User not found on popular platforms")
        elif total_accounts < 3:
            recommendations.append("Few accounts found, possible use of pseudonym")
        else:
            recommendations.append("Many accounts found, check privacy settings")
        
        has_linkedin = False
        has_vk = False
        for user_results in results.values():
            for result in user_results['found']:
                if 'linkedin' in result['site'].lower():
                    has_linkedin = True
                if 'vk' in result['site'].lower():
                    has_vk = True
        
        if has_linkedin:
            recommendations.append("LinkedIn profile found - check contacts and connections")
        else:
            recommendations.append("LinkedIn profile not found - user may use different name")
        
        if has_vk:
            recommendations.append("VK profile found - Russian-speaking user identified")
        
        return recommendations
    
    def update_statistics(self) -> None:
        """Update statistics in database"""
        try:
            cursor = self.conn.cursor()
            start_time = self.stats.get('start_time', datetime.now())
            end_time = self.stats.get('end_time', datetime.now())
            today = datetime.now().date().isoformat()
            
            if isinstance(start_time, datetime) and isinstance(end_time, datetime):
                total_time = (end_time - start_time).total_seconds()
            else:
                total_time = 0
            
            cursor.execute('''
                SELECT id FROM statistics WHERE date = ?
            ''', (today,))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE statistics 
                    SET searches_count = searches_count + ?,
                        accounts_found = accounts_found + ?,
                        total_time = total_time + ?
                    WHERE date = ?
                ''', (
                    1,
                    self.stats.get('found_accounts', 0),
                    total_time,
                    today
                ))
            else:
                cursor.execute('''
                    INSERT INTO statistics (date, searches_count, accounts_found, total_time)
                    VALUES (?, ?, ?, ?)
                ''', (
                    today,
                    1,
                    self.stats.get('found_accounts', 0),
                    total_time
                ))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    def close(self) -> None:
        """Close connections and clean up resources"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
            if hasattr(self, 'session'):
                self.session.close()
        except Exception as e:
            logger.error(f"Error closing resources: {e}")
    
    def __del__(self) -> None:
        """Destructor to ensure resources are closed"""
        self.close()