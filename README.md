# ☢️ G.H.O.S.T.-OSINT-Framework ☢️

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

An advanced, asynchronous Open Source Intelligence (OSINT) and Digital Forensics framework designed for security researchers and SOC analysts. Built with Python and Streamlit, G.H.O.S.T. centralizes disparate intelligence feeds into a single, high-performance tactical dashboard.

## _WE ARE CURRENTLY CELEBRATING THE  FALLOUT THEME_  

## 🚀 Core Capabilities

G.H.O.S.T. currently operates **11 integrated forensic modules**:

* **👤 Global Identity Search:** Asynchronous Sherlock-style username probing across 20+ platforms.
* **🌐 Network Topology:** IP geolocation, PTR resolution, and comprehensive DNS record extraction.
* **📞 Comms Intercept:** Offline phone number metadata extraction and carrier routing via `libphonenumber`.
* **📧 Electronic Mail Trace:** MX/SPF record validation and disposable domain detection.
* **🔐 Breach Archives:** Dark-web identity leak correlation using the BreachDirectory API.
* **🔍 Query Generation:** Automated Google Dorking engine for exposing sensitive infrastructure.
* **☢️ Threat Intelligence:** Real-time integration with AlienVault OTX for indicator reputation analysis.
* **👾 Malware Isolation:** Multi-engine sandbox scanning via the VirusTotal v3 API.
* **🐙 Repository Extraction:** Hunts for sensitive strings (AWS Keys, .env files) leaked in public GitHub repositories.
* **🖼️ Image Forensics:** EXIF metadata decoding and automatic GPS-to-address reverse geocoding via Nominatim.
* **💸 Financial Recon (India):** IFSC routing validation and UPI Virtual Payment Address (VPA) fingerprinting.

## 🛠️ Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/sarthakraut003/GHOST-OSINT-Framework.git](https://github.com/sarthakraut003/GHOST-OSINT-Framework.git)
cd GHOST-OSINT-Framework
```
**2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Configure API Keys:
Create a .env file in the root directory based on the .env.example template and add your API keys:
```bash
OTX_KEY=your_key_here
VT_KEY=your_key_here
BREACH_KEY=your_key_here
GITHUB_TOKEN=your_token_here
```
4. Deploy the Framework:
```bash
streamlit run app.py
```
⚖️ Disclaimer
AUTHORIZED USE ONLY. This tool is provided for educational and research purposes only. Users are strictly responsible for complying with local, state, and federal laws. Unauthorized access, probing, or reconnaissance against systems you do not own or have explicit permission to test is illegal. The developer assumes no liability and is not responsible for any misuse or damage caused by this program.
