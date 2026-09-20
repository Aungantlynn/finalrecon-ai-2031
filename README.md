# FinalRecon-AI - Complete Ultimate Edition

**Version:** 2029.0  
**Build:** 2029.000.1  
**Type:** Web Reconnaissance & Security Testing Tool

---

## 📖 About

**FinalRecon-AI** is a comprehensive Python-based web reconnaissance and security testing tool. It provides a wide range of scanning capabilities including cookie analysis, phishing detection, firewall checks, API key detection, and much more — all with automatic TXT report export.

### ✨ Features

- 🍪 **Cookie Keys Analysis** — Analyze and clear cookie keys
- 🔑 **RockYou Wordlist** — Directory bruteforce with rockyou.txt
- 🎣 **Phishing Detection** — Detect phishing attacks on web pages
- 🔥 **Firewall Options** — Firewall rules and web server checks
- 🔒 **SSH Check** — Verify SSH installation
- 📊 **429 Rate Limit Detection** — Detect HTTP 429 responses
- 💥 **Server Destroy Options** — Check and handle broken servers
- 📝 **Export TXT** — Automatically export all results to TXT
- 🌐 **Full Recon** — Run all reconnaissance modules at once
- 🔑 **API Key Detection** — Detect leaked API keys (AWS, Google, GitHub, etc.)
- 🧪 **Vulnerability Scanning** — SQLi, XSS, LFI, RFI, SSRF, etc.
- 🌍 **DNS / WHOIS / ISP / SSL** — Complete infrastructure recon

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Aungantlynn/finalrecon-ai-2031.git
cd finalrecon-ai-2031
pip3 install -r requirements.txt

sudo apt update
sudo apt install openssh-client

sudo apt install wordlists
sudo gunzip /usr/share/wordlists/rockyou.txt.gz


Basic URL Scan
bash
python3 finalrecon-ai.py --url https://example.com
Full Reconnaissance
bash
python3 finalrecon-ai.py --url https://example.com --full
Full Recon + RockYou Wordlist
bash
python3 finalrecon-ai.py --url https://example.com --full --rockyou
Interactive Mode
bash
python3 finalrecon-ai.py
