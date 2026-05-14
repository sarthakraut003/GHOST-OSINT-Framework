"""
╔══════════════════════════════════════════════════════════════╗
║         G.H.O.S.T  //  OSINT Reconnaissance Dashboard       ║
║         RobCo Industries Pip-Boy Terminal Edition            ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import asyncio
import httpx
import dns.resolver
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import re
import socket
import time
from datetime import datetime
import urllib.parse
import platform
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# ─────────────────────────────────────────────
#  SYSTEM MEMORY  
# ─────────────────────────────────────────────

if 'pivot_email' not in st.session_state:
    st.session_state.pivot_email = ""

# ─────────────────────────────────────────────
#  SYSTEM CONFIGURATION (API KEYS)
# ─────────────────────────────────────────────
CONFIG = {
    "OTX_KEY": "your_alienvault_otx_key_here",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    "OPENCTI_URL": "http://localhost:8080", 
    "VT_KEY": "your_virustotal_v3_key_here", 
    "BREACH_KEY": "your_rapidapi_breachdirectory_key_here", 
    "GITHUB_TOKEN": "your_github_personal_access_token_here", 
    "OPENCTI_TOKEN": "your_opencti_token_here" 
}

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ROBCO TERMINAL // GHOST",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — FALLOUT PIP-BOY THEME
# ─────────────────────────────────────────────
PIPBOY_CSS = """
<style>
/* ── Import Retro Terminal Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

/* ── Root Palette ── */
:root {
    --pip-bg:       #0a120a;
    --pip-green:    #39ff14;
    --pip-dim:      #1a4220;
    --pip-dark:     #0d1f12;
    --font-term:    'VT323', 'Courier New', Courier, monospace;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-term) !important;
    color: var(--pip-green) !important;
    background-color: var(--pip-bg) !important;
    letter-spacing: 1px;
}

/* ── CRT Scanlines Overlay ── */
.stApp::after {
    content: " ";
    display: block;
    position: absolute;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    z-index: 99999;
    background-size: 100% 2px, 3px 100%;
    pointer-events: none;
}

/* ── Terminal Text Glow ── */
p, span, h1, h2, h3, h4, label, div {
    text-shadow: 0 0 4px rgba(57, 255, 20, 0.4) !important;
}

/* ── Custom RobCo Window Header ── */
.mac-window-header {
    background: var(--pip-green);
    border: 2px solid var(--pip-green);
    height: 30px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    margin-bottom: 5px;
    position: relative;
    z-index: 10;
}

.mac-title-text {
    background: var(--pip-green);
    color: var(--pip-bg) !important;
    padding: 0 15px;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    font-family: var(--font-term);
    font-size: 1.4rem;
    font-weight: bold;
    text-transform: uppercase;
    white-space: nowrap;
    text-shadow: none !important;
}

/* ── Pip-Boy Terminal Blocks ── */
.block-container {
    background-color: var(--pip-bg) !important;
    border: 2px solid var(--pip-green) !important;
    box-shadow: 0 0 10px rgba(57, 255, 20, 0.2), inset 0 0 20px rgba(57, 255, 20, 0.05) !important;
    padding: 2rem 3rem !important;
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
    border-radius: 8px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--pip-dark) !important;
    border-right: 2px solid var(--pip-green) !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}
/* Selected radio item */
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
    background-color: var(--pip-green) !important;
}

/* ── Headers ── */
h1 { font-size: 2.8rem !important; border-bottom: 2px solid var(--pip-green); padding-bottom: 5px; text-transform: uppercase; }
h2 { font-size: 2rem !important; text-transform: uppercase; }

/* ── Text inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-family: var(--font-term) !important;
    font-size: 1.2rem !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}

/* ── Buttons ── */
.stButton button {
    background-color: var(--pip-dim) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-family: var(--font-term) !important;
    font-size: 1.4rem !important;
    text-transform: uppercase;
    border-radius: 0px !important;
    padding: 0.4rem 1.2rem !important;
    transition: all 0.2s !important;
}
.stButton button:hover, .stButton button:active {
    background-color: var(--pip-green) !important;
    color: var(--pip-bg) !important;
    box-shadow: 0 0 10px var(--pip-green) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div { background: var(--pip-green) !important; }
.stProgress > div > div { background-color: var(--pip-dark) !important; border: 1px solid var(--pip-green) !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: var(--pip-dim) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}
.streamlit-expanderContent {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    border-top: none !important;
}

/* ── Dividers ── */
hr { border-color: var(--pip-green) !important; border-width: 1px !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stMetricLabel"] {
    color: var(--pip-green) !important;
    font-size: 1rem !important;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: var(--pip-green) !important;
    font-size: 2.2rem !important;
}

/* ── Code blocks ── */
.stCodeBlock, code, pre {
    background-color: var(--pip-dark) !important;
    border: 1px dashed var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-size: 1.1rem !important;
}

/* ── Success / warning / error ── */
.stSuccess, .stWarning, .stError, .stInfo { 
    background-color: var(--pip-dim) !important; 
    border: 1px solid var(--pip-green) !important; 
    color: var(--pip-green) !important;
    border-radius: 0px !important;
}
.stSuccess p, .stWarning p, .stError p, .stInfo p {
    color: var(--pip-green) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 12px; }
::-webkit-scrollbar-track { background: var(--pip-bg); border-left: 1px solid var(--pip-green); }
::-webkit-scrollbar-thumb { background: var(--pip-green); }

/* ── Custom RobCo Dialog Box ── */
#mac-modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(10, 18, 10, 0.8);
    z-index: 1000;
}
.mac-dialog {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: var(--pip-bg);
    border: 2px solid var(--pip-green);
    box-shadow: 0 0 20px rgba(57, 255, 20, 0.5);
    width: 400px;
    padding: 20px;
    text-align: center;
}
.mac-dialog-title {
    font-size: 1.5rem;
    margin-bottom: 15px;
    text-transform: uppercase;
    display: block;
    color: var(--pip-bg);
    background: var(--pip-green);
    padding: 5px;
}
.mac-dialog-text {
    font-size: 1.2rem;
    margin-bottom: 20px;
    display: block;
}
.mac-dialog-ok {
    background: var(--pip-dim);
    border: 1px solid var(--pip-green);
    color: var(--pip-green);
    padding: 5px 25px;
    font-family: var(--font-term);
    font-size: 1.2rem;
    cursor: pointer;
    text-transform: uppercase;
}
.mac-dialog-ok:hover {
    background: var(--pip-green);
    color: var(--pip-bg);
}

/* ── Vault Boy Image Filter ── */
.vault-boy {
    width: 150px;
    filter: sepia(100%) hue-rotate(80deg) saturate(500%) brightness(0.8) contrast(1.2);
    margin-bottom: 10px;
}
</style>
"""

st.markdown(PIPBOY_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  GLOBAL UI COMPONENTS (Modal & Title Bar)
# ─────────────────────────────────────────────

st.markdown(
    """
    <div id="mac-modal-overlay">
        <div class="mac-dialog">
            <span class="mac-dialog-title" id="modal-title">RobCo Alert</span>
            <span class="mac-dialog-text" id="modal-msg">Error.</span>
            <button class="mac-dialog-ok" onclick="closeMacModal()">ACCEPT</button>
        </div>
    </div>
    <script>
        function showMacModal(title, msg) {
            const overlay = document.getElementById('mac-modal-overlay');
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-msg').innerText = msg;
            overlay.style.display = 'block';
        }
        function closeMacModal() {
            document.getElementById('mac-modal-overlay').style.display = 'none';
        }
    </script>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="mac-window-header">
        <div class="mac-title-text">ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
#  HELPER: render a styled "card" block
# ─────────────────────────────────────────────
def card(title: str, content: str):
    st.markdown(
        f"""
        <div style="
            background:var(--pip-dark);
            border:1px solid var(--pip-green);
            padding:0.75rem 1rem;
            margin-bottom:0.8rem;
            color:var(--pip-green);
        ">
            <span style="font-weight:bold;text-transform:uppercase;border-bottom:1px solid var(--pip-green);">{title}</span><br>
            <span style="font-size:1.1rem;display:block;margin-top:4px;">{content}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def badge(label: str, value: str, ok: bool = True):
    bg = "var(--pip-green)" if ok else "var(--pip-dark)"
    fg = "var(--pip-bg)" if ok else "var(--pip-green)"
    icon = "[OK]" if ok else "[ERR]"
    st.markdown(
        f"""
        <div style="display:inline-block;margin:3px 4px;">
            <span style="
                background:{bg};
                border:1px solid var(--pip-green);
                color:{fg};
                padding:4px 8px;
                font-size:1rem;
                text-transform:uppercase;
            ">{icon} {label}: {value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(text: str):
    st.markdown(
        f"""
        <div style="
            background:var(--pip-green);
            color:var(--pip-bg);
            padding:4px 10px;
            margin:1.5rem 0 1rem 0;
            display:inline-block;
            font-size:1.4rem;
            text-transform:uppercase;
            font-weight:bold;
            text-shadow:none !important;
        ">
            > {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  SIDEBAR — NAVIGATION (PIP-BOY EDITION)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <img src="https://icon2.cleanpng.com/20180802/yqg/3dc04be0578b48f51c4a8d7e9b18136d.webp" class="vault-boy">
            <div style="
                font-size:2.5rem;
                text-transform:uppercase;
                line-height:1;
                font-weight:bold;
                margin-top: 10px;
            ">PIP-OS v7.3</div>
            <div style="
                font-size:1.2rem;
                margin-top:5px;
            ">G.H.O.S.T. Reconnaissance</div>
            <div style="
                font-size:0.9rem;
                margin-top:5px;
                color:var(--pip-dim) !important;
            ">VAULT-TEC KEEPS YOU SAFE ONLINE</div>
        </div>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    MODULE = st.radio(
        "Select Application:",
        [
            "🏠  Control Panel",
            "👤  Username Search",
            "🌐  Network Utility & Recon",
            "📞  Phone Intelligence",
            "📧  Email Discovery",
            "🔍  Google Dorking",
            "☢️  Threat Intelligence",
            "👾  Malware Sandbox",
            "🐙  GitHub Secret Scanner",
            "🖼️  Image Forensics",
            "💸  Financial Intelligence",
            "🔐  Data Breach Search"
        ],
        label_visibility="visible",
    )

    st.markdown(
        """
        <hr>
        <div style="
            font-size:0.9rem;
            text-align:center;
            padding-top:0.5rem;
            border: 1px solid var(--pip-green);
            padding: 5px;
            background: var(--pip-dark);
        ">
            ☢️ VAULT-TEC AUTHORIZED USE ONLY.<br>
            Respect local wasteland laws.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════
#  MODULE 0 — OSINT CONTROL PANEL
# ════════════════════════════════════════════
if MODULE == "🏠  Control Panel":
    st.markdown("<h1>VAULT-TEC OSINT Control Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem;'>Open-Source Intelligence Framework | Vault-Tec Edition v1.3</p>", unsafe_allow_html=True)
    
    row1_cols = st.columns(4)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sys_info = platform.system() + " " + platform.release()
    with row1_cols[0]: st.metric("System Status", "ONLINE")
    with row1_cols[1]: st.metric("Active Modules", "11") 
    with row1_cols[2]: st.metric("System Time", now)
    with row1_cols[3]: st.metric("Host OS", sys_info)

    row2_cols = st.columns(3)
    vt_status = "OK" if CONFIG.get("VT_KEY") != "YOUR_VIRUSTOTAL_API_KEY" else "MISSING"
    rapid_status = "OK" if "591a" in CONFIG.get("BREACH_KEY", "") else "OFFLINE"
    
    with row2_cols[0]: st.metric("API Handshake", f"VT:{vt_status} | BD:{rapid_status}")
    with row2_cols[1]: st.metric("Memory Banks", " OK")
    with row2_cols[2]: st.metric("CPU Architecture", "SUFFICIENT")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:1.2rem 1.5rem;">
            <div style="font-size:1.8rem; border-bottom:1px solid var(--pip-green); margin-bottom:10px; text-transform:uppercase;">
                RobCo Application Registry
            </div>
            <table style="width:100%; font-size:1.1rem; border-collapse:collapse; text-align:left;">
                <tr style="border-bottom:1px solid var(--pip-green); background:var(--pip-dim);">
                    <th style="padding:8px;">Application</th>
                    <th style="padding:8px;">Forensic Technique</th>
                    <th style="padding:8px;">Primary Provider</th>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">👤 Username Search</td><td>HTTP Probing (Async)</td><td>Sherlock DB</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🌐 Network Utility</td><td>GeoIP + DNS Resolver</td><td>ip-api.com</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">📞 Phone Intel</td><td>Local Metadata Extraction</td><td>Libphonenumber</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">📧 Email Discovery</td><td>MX/SPF DNS Lookup</td><td>Public DNS</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🔐 Data Breach</td><td>Identity Leak Correlation</td><td>BreachDirectory</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🔍 Google Dorking</td><td>Query Generation</td><td>Google Dork Engine</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">☢️ Threat Intel</td><td>Reputation Analysis</td><td>AlienVault OTX</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">👾 Malware Sandbox</td><td>Multi-Engine Scan (v3)</td><td>VirusTotal</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🐙 Secret Scanner</td><td>Recursive String Hunt</td><td>GitHub API</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🖼️ Image Forensics</td><td>EXIF + Rev. Geocoding</td><td>Pillow / Nominatim</td>
                </tr>
                <tr>
                    <td style="padding:8px;">💸 Financial Intel</td><td>Routing & UPI Validation</td><td>Razorpay / VPA</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════
#  MODULE 1  — USERNAME SEARCH
# ════════════════════════════════════════════
elif MODULE == "👤  Username Search":
    PLATFORMS = {
        "GitHub":        ("https://github.com/{u}",             "Not Found"),
        "GitLab":        ("https://gitlab.com/{u}",             "404"),
        "Twitter/X":     ("https://x.com/{u}",                  "This account"),
        "Reddit":        ("https://www.reddit.com/user/{u}",    "page not found"),
        "Instagram":     ("https://www.instagram.com/{u}/",     "Sorry"),
        "TikTok":        ("https://www.tiktok.com/@{u}",        "couldn't find"),
        "Pinterest":     ("https://www.pinterest.com/{u}/",     "404"),
        "Twitch":        ("https://www.twitch.tv/{u}",          "404"),
        "YouTube":       ("https://www.youtube.com/@{u}",       "404"),
        "SoundCloud":    ("https://soundcloud.com/{u}",         "404"),
        "Dev.to":        ("https://dev.to/{u}",                 "404"),
        "Keybase":       ("https://keybase.io/{u}",             "Not Found"),
        "Pastebin":      ("https://pastebin.com/u/{u}",         "Not Found"),
        "HackerNews":    ("https://news.ycombinator.com/user?id={u}", "No such user"),
        "ProductHunt":   ("https://www.producthunt.com/@{u}",  "404"),
        "Kaggle":        ("https://www.kaggle.com/{u}",         "404"),
        "Replit":        ("https://replit.com/@{u}",            "404"),
        "Medium":        ("https://medium.com/@{u}",            "404"),
        "Substack":      ("https://{u}.substack.com",           "404"),
        "Steam":         ("https://steamcommunity.com/id/{u}",  "The specified profile"),
        "AngelList":     ("https://angel.co/{u}", "404"),
        "Fiverr":          ("https://www.fiverr.com/{u}",            "404"),
        "Upwork":          ("https://www.upwork.com/freelancers/~{u}", "404"),
        "Bandcamp":        ("https://bandcamp.com/{u}", "404"),
        "HuggingFace":     ("https://huggingface.co/{u}", "404"),
        "DockerHub":       ("https://hub.docker.com/u/{u}", "404"),
        "npm":             ("https://www.npmjs.com/~{u}", "404"),
        "PyPI":            ("https://pypi.org/user/{u}/", "404"),
    }

    HEADERS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 PIP-OS/7.1" }

    async def check_platform(client: httpx.AsyncClient, name: str, url: str, not_found_text: str):
        try:
            r = await client.get(url, timeout=8.0, follow_redirects=True, headers=HEADERS)
            if r.status_code == 200 and not_found_text.lower() not in r.text.lower():
                return name, url, True
            return name, url, False
        except Exception:
            return name, url, False

    async def run_username_scan(username: str):
        results = []
        async with httpx.AsyncClient(http2=True) as client:
            tasks = []
            for name, (url_tpl, nf) in PLATFORMS.items():
                url = url_tpl.replace("{u}", username)
                tasks.append(check_platform(client, name, url, nf))
            results = await asyncio.gather(*tasks)
        return results

    st.markdown("<h1>Global Identity Search</h1>", unsafe_allow_html=True)
    username = st.text_input("Enter Target Alias:", placeholder="e.g. johndoe")

    if st.button("Execute Async Probe"):
        if not username.strip():
            st.error("Error: Subject alias required.")
        else:
            progress_bar = st.progress(0, text="Establishing uplink...")
            status_text  = st.empty()
            t0 = time.perf_counter()

            status_text.markdown(f"> **Scanning databanks for: {username}**", unsafe_allow_html=True)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(run_username_scan(username))
            loop.close()

            elapsed = time.perf_counter() - t0
            progress_bar.progress(1.0, text="Probe sequence complete.")

            found = [r for r in results if r[2]]
            not_found = [r for r in results if not r[2]]

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Vectors Scanned", len(PLATFORMS))
            with c2: st.metric("Positive Hits", len(found))
            with c3: st.metric("Uplink Time", f"{elapsed:.2f}s")

            section_header("Confirmed Identities")
            if found:
                for name, url, _ in found:
                    st.markdown(
                        f"""
                        <div style="
                            background:var(--pip-dark);border:1px solid var(--pip-green);
                            padding:8px 12px;margin-bottom:8px;font-size:1.2rem;
                        ">
                            <span>[HIT] {name}</span>
                            <a href="{url}" target="_blank"
                               style="float:right;color:var(--pip-green);text-decoration:none;">
                                [ LINK ]
                            </a>
                        </div>
                        """, unsafe_allow_html=True
                    )
            else:
                st.warning("Subject is a ghost. No data found.")

            with st.expander("View Null Returns"):
                for name, url, _ in not_found:
                    st.markdown(f"[NULL] {name}", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 2 — NETWORK UTILITY
# ════════════════════════════════════════════
elif MODULE == "🌐  Network Utility & Recon":
    async def fetch_ip_geo(target: str) -> dict:
        url = f"http://ip-api.com/json/{target}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=8.0)
            return r.json()

    def resolve_dns(domain: str) -> dict:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype, lifetime=5.0)
                results[rtype] = [str(r) for r in answers]
            except Exception:
                results[rtype] = []
        return results

    def resolve_ptr(ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "N/A"

    st.markdown("<h1>Network Topography</h1>", unsafe_allow_html=True)
    target = st.text_input("Enter Node Address (IP/Domain):", placeholder="e.g. 8.8.8.8")

    col_a, col_b = st.columns(2)
    run_ip  = col_a.button("[ TRACE IP ]")
    run_dns = col_b.button("[ DUMP DNS ]")

    if run_ip and target.strip():
        with st.spinner("Pinging Satellites..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            geo = loop.run_until_complete(fetch_ip_geo(target.strip()))
            loop.close()

        if geo.get("status") == "success":
            section_header("Node Telemetry")
            c1, c2, c3 = st.columns(3)
            c1.metric("Node IP", geo.get("query", "—"))
            c2.metric("Territory", geo.get("country", "—"))
            c3.metric("Sector", geo.get("city", "—"))

            card("ISP Routing", geo.get("isp", "—"))
            card("Coordinates", f"Lat {geo.get('lat','—')} / Lon {geo.get('lon','—')}")
            card("Reverse DNS", resolve_ptr(geo.get("query", target.strip())))

            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Security Posture (OTX)")
            try:
                otx_r = httpx.get(f"https://otx.alienvault.com/api/v1/indicators/IPv4/{target.strip()}/general", headers={"X-OTX-API-KEY": CONFIG["OTX_KEY"]}, timeout=5.0)
                pulses = otx_r.json().get('pulse_info', {}).get('count', 0)
                badge("Threat Level", f"{pulses} Pulses", ok=(pulses == 0))
                if pulses > 0:
                    st.error(f"⚠ Caution: This IP is associated with {pulses} known threat pulses.")
            except:
                st.warning("OTX Uplink severed.")
        else:
            st.error(f"Routing Error: {geo.get('message','Unknown')}")

    if run_dns and target.strip():
        domain = re.sub(r"^https?://", "", target.strip()).split("/")[0]
        with st.spinner(f"Accessing Domain Registries for {domain}..."):
            records = resolve_dns(domain)

        section_header("DNS Topology")
        for rtype, values in records.items():
            if values:
                with st.expander(f"[{rtype}] Records Found ({len(values)})"):
                    for v in values:
                        st.code(v, language=None)

# ════════════════════════════════════════════
#  MODULE 3  — PHONE INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "📞  Phone Intelligence":
    def analyse_phone(raw: str) -> dict:
        try:
            parsed = phonenumbers.parse(raw, None)
            return {
                "valid": phonenumbers.is_valid_number(parsed),
                "region": geocoder.description_for_number(parsed, "en") or "Unknown",
                "carrier": carrier.name_for_number(parsed, "en") or "Unknown",
                "country_code": parsed.country_code,
                "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                "error": None,
            }
        except Exception as e:
            return {"error": str(e)}

    st.markdown("<h1>Comms Intercept</h1>", unsafe_allow_html=True)
    phone_raw = st.text_input("Enter Comm Frequency (+Country Code):", placeholder="+1 415 555 0100")

    if st.button("Decrypt Frequency"):
        if not phone_raw.strip():
            st.error("Frequency missing.")
        else:
            result = analyse_phone(phone_raw.strip())
            if result.get("error"):
                st.error(f"Decryption failed: {result['error']}")
            else:
                section_header("Signal Origin")
                c1, c2 = st.columns(2)
                with c1: st.metric("Status", "VALID" if result["valid"] else "INVALID")
                with c2: st.metric("Region", result["region"])
                
                card("Tower Operator", result["carrier"])
                card("Routing Format", result["e164"])

# ════════════════════════════════════════════
#  MODULE 4  — EMAIL DISCOVERY
# ════════════════════════════════════════════
elif MODULE == "📧  Email Discovery":
    st.markdown("<h1>Electronic Mail Trace</h1>", unsafe_allow_html=True)
    email_input = st.text_input("Enter Target Address:", placeholder="target@example.com")

    if st.button("Trace Route"):
        if not email_input.strip():
            st.error("Address missing.")
        else:
            domain = email_input.split("@")[1] if "@" in email_input else ""
            with st.spinner("Pinging Mail Exchangers..."):
                try:
                    answers = dns.resolver.resolve(domain, "MX", lifetime=6.0)
                    mx_records = [str(r.exchange) for r in answers]
                    
                    section_header("Server Topology")
                    st.metric("Mail Servers", "ACTIVE")
                    for mx in mx_records:
                        card("MX Node", mx)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("[ Pivot to Breach Analysis ]"):
                        st.session_state.pivot_email = email_input.strip()
                        st.query_params["module"] = "🔐  Data Breach Search"
                        st.rerun()

                except Exception:
                    st.error("No active mail servers found for domain.")

# ════════════════════════════════════════════
#  MODULE 5  — GOOGLE DORKING
# ════════════════════════════════════════════
elif MODULE == "🔍  Google Dorking":

    DORK_TEMPLATES = {
        "Sensitive Files": [
            ('Exposed .env files',        'filetype:env "{target}"'),
            ('Exposed credentials',       'filetype:txt intext:"password" intext:"username" site:{target}'),
            ('Database dumps',            'filetype:sql "{target}"'),
            ('Config files',              'filetype:xml OR filetype:yml "{target}" intext:"password"'),
            ('Log files',                 'filetype:log "{target}"'),
            ('Backup files',              'filetype:bak OR filetype:backup "{target}"'),
        ],
        "Directory Listings": [
            ('Open index pages',          'intitle:"index of" "{target}"'),
            ('Apache directory listing',  'intitle:"index of /" "{target}"'),
            ('FTP open directories',      'intitle:"index of" inurl:ftp "{target}"'),
        ],
        "Login & Admin Panels": [
            ('Admin panels',              'site:{target} inurl:admin'),
            ('Login pages',               'site:{target} inurl:login'),
            ('phpMyAdmin',                'site:{target} inurl:phpmyadmin'),
            ('WordPress admin',           'site:{target} inurl:wp-admin'),
        ],
        "Cloud & Infrastructure": [
            ('AWS S3 buckets',            '"{target}" site:s3.amazonaws.com'),
            ('Azure blobs',               '"{target}" site:blob.core.windows.net'),
            ('GCP buckets',               '"{target}" site:storage.googleapis.com'),
            ('Exposed Grafana dashboards','site:{target} intitle:"Grafana"'),
            ('Jenkins CI',                'site:{target} intitle:"Dashboard [Jenkins]"'),
        ],
        "Personal & Social": [
            ('Email addresses on site',   'site:{target} intext:"@{target}"'),
            ('LinkedIn employees',        'site:linkedin.com intitle:"{target}"'),
            ('Social profiles',           '"{target}" site:twitter.com OR site:facebook.com OR site:instagram.com'),
            ('Resume/CVs',                '"{target}" filetype:pdf intitle:"CV" OR intitle:"Resume"'),
        ],
        "Code & Repositories": [
            ('GitHub repositories',       'site:github.com "{target}"'),
            ('Pastebin leaks',            'site:pastebin.com "{target}"'),
            ('Source code leaks',         'site:github.com OR site:gitlab.com "{target}" password'),
        ],
    }

    def build_dork_url(dork: str) -> str:
        return "https://www.google.com/search?q=" + urllib.parse.quote_plus(dork)

    st.markdown("<h1>Query Generation</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Construct advanced search operators for data extraction from global indexes.</span>
        </div>
        """, unsafe_allow_html=True
    )

    col_t, col_cat = st.columns([2, 1])
    with col_t:
        dork_target = st.text_input("Target Domain/Name:", placeholder="example.com  or  John Smith")
    with col_cat:
        selected_cat = st.selectbox("Category:", list(DORK_TEMPLATES.keys()))

    show_all = st.checkbox("Show all categories")

    if st.button("Generate Operators"):
        if not dork_target.strip():
            st.error("Error: Please enter a target.")
        else:
            target_val = dork_target.strip()
            cats = DORK_TEMPLATES if show_all else {selected_cat: DORK_TEMPLATES[selected_cat]}

            for cat_name, dorks in cats.items():
                section_header(cat_name)
                for label, dork_tpl in dorks:
                    dork = dork_tpl.replace("{target}", target_val)
                    url  = build_dork_url(dork)
                    st.markdown(
                        f"""
                        <div style="
                            background:var(--pip-dark);border:1px solid var(--pip-green);
                            padding:10px;margin-bottom:10px;
                        ">
                            <span style="font-weight:bold;text-transform:uppercase;">{label}</span><br>
                            <code>{dork}</code><br><br>
                            <a href="{url}" target="_blank"
                               style="color:var(--pip-bg);font-weight:bold;text-decoration:none;background:var(--pip-green);padding:4px 8px;">
                                [ EXECUTE SEARCH ]
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# ════════════════════════════════════════════
#  MODULE 6  — THREAT INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "☢️  Threat Intelligence":
    st.markdown("<h1>OTX Threat Feed</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Querying global threat nodes (AlienVault OTX) for malicious signatures.</span>
        </div>
        """, unsafe_allow_html=True
    )

    num_pulses = st.slider("Pulse Display Limit:", 5, 50, 10)
    target = st.text_input("Enter Indicator (IP, Domain, or Hash):", placeholder="e.g. apple.com")
    
    if st.button("☣️ Query Nodes"):
        if not target.strip():
            st.error("Missing indicator value.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                ind_type, otx_path = "IPv4", "IPv4"
            elif "@" in target:
                ind_type, otx_path = "Email", "email"
            else:
                ind_type, otx_path = "Domain", "domain"

            headers = {"X-OTX-API-KEY": CONFIG["OTX_KEY"]}
            url = f"https://otx.alienvault.com/api/v1/indicators/{otx_path}/{target.strip()}/general"
            
            with st.spinner("Accessing Global Intelligence Feed..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=12.0)
                    data = r.json()
                    
                    section_header(f"Reputation Analysis: {target}")
                    
                    pulse_info = data.get('pulse_info', {})
                    total_pulses = pulse_info.get('count', 0)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("Indicator Type", ind_type)
                    with c2: st.metric("Active Pulses", total_pulses)
                    with c3: st.metric("Reputation", "MALICIOUS" if total_pulses > 0 else "CLEAN")

                    if total_pulses > 0:
                        st.warning(f"System Alert: Indicator identified in {total_pulses} community threat pulses.")
                        
                        for pulse in pulse_info.get('pulses', [])[:num_pulses]:
                            pulse_name = pulse.get('name', 'Unnamed Pulse')
                            
                            with st.expander(f"📁 Pulse: {pulse_name}"):
                                author = pulse.get('author_name', 'Anonymous')
                                created = (pulse.get('created') or "N/A")[:10]
                                tags = pulse.get('tags', [])
                                indicators = pulse.get('indicators', [])
                                
                                st.markdown(f"**Author:** {author}")
                                st.markdown(f"**Date:** {created}")
                                st.markdown(f"**Tags:** {', '.join(tags) if tags else 'None'}")
                                
                                st.markdown("---")
                                st.info(pulse.get('description', 'No description available.'))
                                
                                if indicators:
                                    st.markdown(f"**Related Indicators ({len(indicators)} total):**")
                                    for ioc in indicators[:5]:
                                        st.code(f"[{ioc.get('type')}] {ioc.get('indicator')}", language=None)
                    else:
                        st.success("No known malicious associations found in OTX database.")
                except Exception as e:
                    st.error(f"OTX Connectivity Error: {str(e)}")

# ════════════════════════════════════════════
#  MODULE 7  — MALWARE SANDBOX
# ════════════════════════════════════════════
elif MODULE == "👾  Malware Sandbox":
    st.markdown("<h1>VirusTotal Isolation</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Cross-references indicators against 70+ antivirus scanners using VirusTotal v3 API.</span>
        </div>
        """, unsafe_allow_html=True
    )

    target = st.text_input("Enter Hash, Domain, or IP:", placeholder="e.g. 44d88612fea8a8f36de82e1278abb02f")

    if st.button("🔎 Execute Scan"):
        if not target.strip():
            st.error("Please provide a target for the sandbox.")
        elif CONFIG["VT_KEY"] == "YOUR_VIRUSTOTAL_API_KEY":
            st.warning("SYSTEM ERROR: VirusTotal API Key missing in CONFIG.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                vt_type = "ip_addresses"
            elif "." in target and "@" not in target:
                vt_type = "domains"
            else:
                vt_type = "files"

            url = f"https://www.virustotal.com/api/v3/{vt_type}/{target.strip()}"
            headers = {"x-apikey": CONFIG["VT_KEY"]}

            with st.spinner("Uploading to multi-engine sandbox..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=15.0)
                    if r.status_code == 200:
                        data = r.json()['data']['attributes']
                        stats = data.get('last_analysis_stats', {})
                        
                        section_header(f"Security Report: {target}")
                        
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Malicious", stats.get('malicious', 0))
                        with c2: st.metric("Suspicious", stats.get('suspicious', 0))
                        with c3: st.metric("Harmless", stats.get('harmless', 0))
                        with c4: st.metric("Undetected", stats.get('undetected', 0))

                        col_left, col_right = st.columns(2)
                        with col_left:
                            card("Reputation Score", str(data.get('reputation', 0)))
                            card("Provider Tags", ", ".join(data.get('tags', [])) if data.get('tags') else "None")
                        
                        with col_right:
                            card("Primary Label", data.get('meaningful_name', data.get('type_description', 'N/A')))
                            card("Last DNS Records", str(len(data.get('last_dns_records', []))))

                        if stats.get('malicious', 0) > 0:
                            st.markdown("---")
                            st.markdown("**Engine Flags:**")
                            results = data.get('last_analysis_results', {})
                            for engine, res in results.items():
                                if res['category'] == 'malicious':
                                    st.error(f"[ {engine} ] : {res['result']}")
                    
                    elif r.status_code == 404:
                        st.info("Indicator not found in VirusTotal database.")
                    else:
                        st.error(f"VT API Error: {r.status_code}")
                except Exception as e:
                    st.error(f"Sandbox Connectivity Failed: {str(e)}")    

# ════════════════════════════════════════════
#  MODULE 8  — GITHUB SECRET SCANNER
# ════════════════════════════════════════════
elif MODULE == "🐙  GitHub Secret Scanner":
    st.markdown("<h1>Repository Extraction</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Hunts for sensitive strings (AWS Keys, Private Keys, .env files) leaked in public GitHub repos.</span>
        </div>
        """, unsafe_allow_html=True
    )

    target_user = st.text_input("Enter GitHub Username/Org:", placeholder="e.g. apple or torvalds")
    
    DANGER_QUERIES = {
        "AWS Keys": "AKIA",
        "Private RSA Keys": "BEGIN RSA PRIVATE KEY",
        "Environment Files": "filename:.env",
        "GitHub Tokens": "ghp_",
        "Config w/ Passwords": "extension:config password"
    }

    if st.button("🚀 Hunt Secrets"):
        if not target_user.strip():
            st.error("Target username is required.")
        else:
            section_header(f"Scanning Repositories for: {target_user}")
            
            headers = {}
            if CONFIG["GITHUB_TOKEN"]:
                headers["Authorization"] = f"token {CONFIG['GITHUB_TOKEN']}"
            
            found_secrets = False
            
            with st.spinner(f"Analyzing {target_user}'s digital trail..."):
                for label, query in DANGER_QUERIES.items():
                    search_url = f"https://api.github.com/search/code?q={query}+user:{target_user}"
                    try:
                        r = httpx.get(search_url, headers=headers, timeout=15.0)
                        if r.status_code == 200:
                            data = r.json()
                            count = data.get('total_count', 0)
                            
                            if count > 0:
                                found_secrets = True
                                st.warning(f"⚠ {label} Detected: {count} potential leaks found.")
                                for item in data.get('items', [])[:3]:
                                    repo_name = item['repository']['full_name']
                                    file_path = item['path']
                                    file_url = item['html_url']
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:8px; margin-bottom:5px;">
                                            <span>
                                                <b>Repo:</b> {repo_name}<br>
                                                <b>File:</b> {file_path}<br>
                                                <a href="{file_url}" target="_blank" style="color:var(--pip-bg); background:var(--pip-green); padding:2px 5px; text-decoration:none; display:inline-block; margin-top:5px;">[ VIEW SOURCE ]</a>
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                        elif r.status_code == 403:
                            st.error("API Rate Limit Exceeded.")
                            break
                        time.sleep(2) 
                    except Exception as e:
                        st.error(f"Search Failed for {label}: {str(e)}")

            if not found_secrets:
                st.success("Clean Scan: No obvious secrets detected.")                    

# ════════════════════════════════════════════
#  MODULE 9 — IMAGE FORENSICS
# ════════════════════════════════════════════
elif MODULE == "🖼️  Image Forensics":
    st.markdown("<h1>EXIF Decoding</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Extracts metadata and pings Nominatim to convert raw GPS data into physical street addresses.</span>
        </div>
        """, unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Drop Evidence Image (JPG/TIFF):", type=["jpg", "jpeg", "tiff"])

    def get_decimal_from_dms(dms, ref):
        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0
        val = float(degrees + minutes + seconds)
        return -val if ref in ['S', 'W'] else val

    async def get_human_address(lat, lon):
        headers = {"User-Agent": "GHOST-OSINT-App/1.1 (Cybersecurity-Research)"}
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                r = await client.get(url, timeout=10.0)
                if r.status_code == 200:
                    return r.json().get('display_name', 'Address not found')
                return f"API Error: HTTP {r.status_code}"
            except Exception as e:
                return f"Connection Error: {str(e)}"

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Evidence", use_container_width=True)
        
        exif_data = image._getexif()
        
        if not exif_data:
            st.error("SYSTEM ERROR: No EXIF metadata found. Image may have been scrubbed.")
        else:
            section_header("Metadata Analysis")
            clean_exif, gps_info = {}, {}
            
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    for t in value:
                        gps_info[GPSTAGS.get(t, t)] = value[t]
                else:
                    clean_exif[decoded] = value

            row1 = st.columns(3)
            with row1[0]: st.metric("Device", clean_exif.get('Model', 'Unknown'))
            with row1[1]: st.metric("Software", str(clean_exif.get('Software', '1.0')))
            with row1[2]: st.metric("Timestamp", str(clean_exif.get('DateTime', 'N/A'))[:10])

            if gps_info and 'GPSLatitude' in gps_info:
                lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
                lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
                
                row2 = st.columns(3)
                with row2[0]: st.metric("Latitude", f"{lat:.6f}")
                with row2[1]: st.metric("Longitude", f"{lon:.6f}")
                with row2[2]: st.metric("GPS Status", "LOCKED", delta_color="normal")

                with st.spinner("Decoding GPS into physical address..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    address = loop.run_until_complete(get_human_address(lat, lon))
                    loop.close()

                st.markdown(f"""
                    <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:15px; margin-top:10px;">
                        <b>[📍] DETECTED ADDRESS:</b><br>
                        <span>{address}</span>
                    </div>
                """, unsafe_allow_html=True)

                maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; margin-top:10px; padding:10px;">[ VIEW SATELLITE IMAGERY ]</button></a>', unsafe_allow_html=True)
            else:
                st.info("No GPS coordinates detected for this asset.")

            with st.expander("📁 View Raw Metadata Dump"):
                for k, v in clean_exif.items():
                    st.write(f"**{k}:** {v}")

# ════════════════════════════════════════════
#  MODULE 10 — FINANCIAL INTELLIGENCE (INDIA)
# ════════════════════════════════════════════
elif MODULE == "💸  Financial Intelligence":
    st.markdown("<h1>Caps & Currency Trace</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Validates IFSC routing codes and analyzes UPI Virtual Payment Addresses (VPA) for the Indian subcontinent.</span>
        </div>
        """, unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["[ 🏦 IFSC Trace ]", "[ 💳 UPI Analysis ]"])

    with tab1:
        ifsc_input = st.text_input("Enter Routing Code (IFSC):", placeholder="e.g. HDFC0000007")
        if st.button("🔎 Trace Branch"):
            if len(ifsc_input) != 11:
                st.error("INVALID FORMAT: IFSC must be exactly 11 characters.")
            else:
                with st.spinner("Accessing RBI Routing Tables..."):
                    try:
                        r = httpx.get(f"https://ifsc.razorpay.com/{ifsc_input.strip()}", timeout=10.0)
                        if r.status_code == 200:
                            data = r.json()
                            section_header(f"Branch Details: {data.get('BANK')}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                card("Bank Name", data.get('BANK'))
                                card("Branch",    data.get('BRANCH'))
                                card("IFSC",      data.get('IFSC'))
                            with c2:
                                card("City",      data.get('CITY'))
                                card("District",  data.get('DISTRICT'))
                                card("State",     data.get('STATE'))
                            
                            st.info(f"📍 Address: {data.get('ADDRESS')}")
                            
                            addr_query = f"{data.get('BANK')} {data.get('BRANCH')} {data.get('CITY')}"
                            maps_url = f"https://www.google.com/maps/search/{addr_query.replace(' ', '+')}"
                            st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; padding:10px;">[ LOCATE ON MAP ]</button></a>', unsafe_allow_html=True)
                        else:
                            st.error(f"IFSC NOT FOUND: Ensure the code is correct (Status {r.status_code}).")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")

    with tab2:
        vpa_input = st.text_input("Enter UPI ID (VPA):", placeholder="username@bank")
        UPI_HANDLES = {
            "okicici": "ICICI Bank", "okaxis": "Axis Bank", "oksbi": "State Bank of India",
            "okhdfcbank": "HDFC Bank", "ybl": "Yes Bank", "ibl": "ICICI Bank (PhonePe)",
            "axl": "Axis Bank (PhonePe)", "paytm": "Paytm Payments Bank",
            "upl": "Union Bank", "postbank": "India Post Payments Bank"
        }

        if st.button("🧪 Analyze VPA"):
            if "@" not in vpa_input:
                st.error("INVALID FORMAT: UPI ID must contain an '@' symbol.")
            else:
                handle = vpa_input.split("@")[-1].lower()
                bank_partner = UPI_HANDLES.get(handle, "Unknown/Custom Provider")
                
                section_header(f"Analysis: {vpa_input}")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("Provider", bank_partner)
                with c2: st.metric("Format Status", "VALID" if len(vpa_input) > 3 else "INVALID")
                
                st.markdown(
                    """
                    <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:10px; margin-top:10px;">
                        <b>[ NOTE ]</b> In India, the handle reveals the processing bank. 
                        To verify the Legal Name, scan the QR below with a banking app.
                    </div>
                    """, unsafe_allow_html=True
                )
                
                upi_link = f"upi://pay?pa={vpa_input}&pn=GHOST_RECON&cu=INR"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={upi_link}"
                st.image(qr_url, caption="Scan to verify Legal Name in app")

# ════════════════════════════════════════════
#  MODULE 11 — DATA BREACH SEARCH (RAPID-API)
# ════════════════════════════════════════════
elif MODULE == "🔐  Data Breach Search":
    st.markdown("<h1>Breach Archives</h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Querying external dark-web indices for compromised assets via BreachDirectory.</span>
        </div>
        """, unsafe_allow_html=True
    )

    pivot_val = st.session_state.get('pivot_email', "")
    query_input = st.text_input("Enter Identifier:", value=pivot_val, placeholder="e.g. target@example.com")
    
    if pivot_val:
        if st.button("[ Flush Memory ]"):
            st.session_state.pivot_email = ""
            st.rerun()

    if st.button("Execute Override"):
        target = query_input.strip()
        if not target:
            st.error("Input required.")
        else:
            api_url = "https://breachdirectory.p.rapidapi.com" 
            headers = {
                "x-rapidapi-key": CONFIG["BREACH_KEY"],
                "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PIP-OS/7.1"
            }
            query_params = {"func": "auto", "term": target}

            with st.spinner("Decrypting mainframe logs..."):
                try:
                    with httpx.Client(follow_redirects=True, timeout=25.0) as client:
                        r = client.get(api_url, headers=headers, params=query_params)
                    
                    if r.status_code == 200:
                        data = r.json()
                        if data.get('success') or 'result' in data:
                            results = data.get('result', [])
                            total_found = len(results)
                            
                            section_header(f"Compromise Report: {target}")
                            c1, c2 = st.columns(2)
                            with c1: st.metric("Leaks Found", total_found)
                            with c2: st.metric("Status", "COMPROMISED" if total_found > 0 else "SECURE")

                            if total_found > 0:
                                for breach in results:
                                    sources = breach.get('sources', [])
                                    source_name = ", ".join(sources) if isinstance(sources, list) else str(sources)
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:10px; margin-bottom:8px;">
                                            <b>> DATABASE: {source_name}</b><br>
                                            <span style="font-size:1.1rem;">
                                                Password Leaked: {"[ YES ]" if breach.get('has_password') else "[ NO ]"}<br>
                                                Hash Type: {breach.get('hash_type', 'N/A')}
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                            else:
                                st.success("Subject is clean. No records found.")
                        else:
                            st.info("No records match this identifier.")
                    else:
                        st.error(f"System Error {r.status_code}. Connection to archive failed.")
                except Exception as e:
                    st.error(f"Uplink Severed: {str(e)}")
"""
╔══════════════════════════════════════════════════════════════╗
║         G.H.O.S.T  //  OSINT Reconnaissance Dashboard       ║
║         RobCo Industries Pip-Boy Terminal Edition            ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import asyncio
import httpx
import dns.resolver
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import re
import socket
import time
from datetime import datetime
import urllib.parse
import platform
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# ─────────────────────────────────────────────
#  SYSTEM MEMORY  
# ─────────────────────────────────────────────

if 'pivot_email' not in st.session_state:
    st.session_state.pivot_email = ""

# ─────────────────────────────────────────────
#  SYSTEM CONFIGURATION (API KEYS)
# ─────────────────────────────────────────────
CONFIG = {
    "OTX_KEY": "cec0f6c86ef2ee22f1ab3a3734cacd8c2e96846622cf808ef4c07a2f712e25d9",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    "OPENCTI_URL": "http://localhost:8080", 
    "VT_KEY": "70f961af90b0a23b61b4d22fa1223b64694304a105925e25e61b3b22ecc23e22", 
    "BREACH_KEY": "591a17a2cemsh80a79611e6132c2p100379jsnf0065f1d3d92", 
    "GITHUB_TOKEN": "", 
    "OPENCTI_TOKEN": "9d29da5c-d768-4f22-b765-b891e53b8313" 
}

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ROBCO TERMINAL // GHOST",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — FALLOUT PIP-BOY THEME
# ─────────────────────────────────────────────
PIPBOY_CSS = """
<style>
/* ── Import Retro Terminal Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

/* ── Root Palette ── */
:root {
    --pip-bg:       #0a120a;
    --pip-green:    #39ff14;
    --pip-dim:      #1a4220;
    --pip-dark:     #0d1f12;
    --font-term:    'VT323', 'Courier New', Courier, monospace;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-term) !important;
    color: var(--pip-green) !important;
    background-color: var(--pip-bg) !important;
    letter-spacing: 1px;
}

/* ── CRT Scanlines Overlay ── */
.stApp::after {
    content: " ";
    display: block;
    position: absolute;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    z-index: 99999;
    background-size: 100% 2px, 3px 100%;
    pointer-events: none;
}

/* ── Terminal Text Glow ── */
p, span, h1, h2, h3, h4, label, div {
    text-shadow: 0 0 4px rgba(57, 255, 20, 0.4) !important;
}

/* ── Custom RobCo Window Header ── */
.mac-window-header {
    background: var(--pip-green);
    border: 2px solid var(--pip-green);
    height: 30px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    margin-bottom: 5px;
    position: relative;
    z-index: 10;
}

.mac-title-text {
    background: var(--pip-green);
    color: var(--pip-bg) !important;
    padding: 0 15px;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    font-family: var(--font-term);
    font-size: 1.4rem;
    font-weight: bold;
    text-transform: uppercase;
    white-space: nowrap;
    text-shadow: none !important;
}

/* ── Pip-Boy Terminal Blocks ── */
.block-container {
    background-color: var(--pip-bg) !important;
    border: 2px solid var(--pip-green) !important;
    box-shadow: 0 0 10px rgba(57, 255, 20, 0.2), inset 0 0 20px rgba(57, 255, 20, 0.05) !important;
    padding: 2rem 3rem !important;
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
    border-radius: 8px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--pip-dark) !important;
    border-right: 2px solid var(--pip-green) !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}
/* Selected radio item */
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
    background-color: var(--pip-green) !important;
}

/* ── Headers ── */
h1 { font-size: 2.8rem !important; border-bottom: 2px solid var(--pip-green); padding-bottom: 5px; text-transform: uppercase; }
h2 { font-size: 2rem !important; text-transform: uppercase; }

/* ── Text inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-family: var(--font-term) !important;
    font-size: 1.2rem !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}

/* ── Buttons ── */
.stButton button {
    background-color: var(--pip-dim) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-family: var(--font-term) !important;
    font-size: 1.4rem !important;
    text-transform: uppercase;
    border-radius: 0px !important;
    padding: 0.4rem 1.2rem !important;
    transition: all 0.2s !important;
}
.stButton button:hover, .stButton button:active {
    background-color: var(--pip-green) !important;
    color: var(--pip-bg) !important;
    box-shadow: 0 0 10px var(--pip-green) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div { background: var(--pip-green) !important; }
.stProgress > div > div { background-color: var(--pip-dark) !important; border: 1px solid var(--pip-green) !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: var(--pip-dim) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}
.streamlit-expanderContent {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    border-top: none !important;
}

/* ── Dividers ── */
hr { border-color: var(--pip-green) !important; border-width: 1px !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stMetricLabel"] {
    color: var(--pip-green) !important;
    font-size: 1rem !important;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: var(--pip-green) !important;
    font-size: 2.2rem !important;
}

/* ── Code blocks ── */
.stCodeBlock, code, pre {
    background-color: var(--pip-dark) !important;
    border: 1px dashed var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-size: 1.1rem !important;
}

/* ── Success / warning / error ── */
.stSuccess, .stWarning, .stError, .stInfo { 
    background-color: var(--pip-dim) !important; 
    border: 1px solid var(--pip-green) !important; 
    color: var(--pip-green) !important;
    border-radius: 0px !important;
}
.stSuccess p, .stWarning p, .stError p, .stInfo p {
    color: var(--pip-green) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 12px; }
::-webkit-scrollbar-track { background: var(--pip-bg); border-left: 1px solid var(--pip-green); }
::-webkit-scrollbar-thumb { background: var(--pip-green); }

/* ── Custom RobCo Dialog Box ── */
#mac-modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(10, 18, 10, 0.8);
    z-index: 1000;
}
.mac-dialog {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: var(--pip-bg);
    border: 2px solid var(--pip-green);
    box-shadow: 0 0 20px rgba(57, 255, 20, 0.5);
    width: 400px;
    padding: 20px;
    text-align: center;
}
.mac-dialog-title {
    font-size: 1.5rem;
    margin-bottom: 15px;
    text-transform: uppercase;
    display: block;
    color: var(--pip-bg);
    background: var(--pip-green);
    padding: 5px;
}
.mac-dialog-text {
    font-size: 1.2rem;
    margin-bottom: 20px;
    display: block;
}
.mac-dialog-ok {
    background: var(--pip-dim);
    border: 1px solid var(--pip-green);
    color: var(--pip-green);
    padding: 5px 25px;
    font-family: var(--font-term);
    font-size: 1.2rem;
    cursor: pointer;
    text-transform: uppercase;
}
.mac-dialog-ok:hover {
    background: var(--pip-green);
    color: var(--pip-bg);
}

/* ── Vault Boy Image Filter ── */
.vault-boy {
    width: 150px;
    filter: sepia(100%) hue-rotate(80deg) saturate(500%) brightness(0.8) contrast(1.2);
    margin-bottom: 10px;
}
</style>
"""

st.markdown(PIPBOY_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  GLOBAL UI COMPONENTS (Modal & Title Bar)
# ─────────────────────────────────────────────

st.markdown(
    """
    <div id="mac-modal-overlay">
        <div class="mac-dialog">
            <span class="mac-dialog-title" id="modal-title">RobCo Alert</span>
            <span class="mac-dialog-text" id="modal-msg">Error.</span>
            <button class="mac-dialog-ok" onclick="closeMacModal()">ACCEPT</button>
        </div>
    </div>
    <script>
        function showMacModal(title, msg) {
            const overlay = document.getElementById('mac-modal-overlay');
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-msg').innerText = msg;
            overlay.style.display = 'block';
        }
        function closeMacModal() {
            document.getElementById('mac-modal-overlay').style.display = 'none';
        }
    </script>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="mac-window-header">
        <div class="mac-title-text">ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
#  HELPER: render a styled "card" block
# ─────────────────────────────────────────────
def card(title: str, content: str):
    st.markdown(
        f"""
        <div style="
            background:var(--pip-dark);
            border:1px solid var(--pip-green);
            padding:0.75rem 1rem;
            margin-bottom:0.8rem;
            color:var(--pip-green);
        ">
            <span style="font-weight:bold;text-transform:uppercase;border-bottom:1px solid var(--pip-green);">{title}</span><br>
            <span style="font-size:1.1rem;display:block;margin-top:4px;">{content}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def badge(label: str, value: str, ok: bool = True):
    bg = "var(--pip-green)" if ok else "var(--pip-dark)"
    fg = "var(--pip-bg)" if ok else "var(--pip-green)"
    icon = "[OK]" if ok else "[ERR]"
    st.markdown(
        f"""
        <div style="display:inline-block;margin:3px 4px;">
            <span style="
                background:{bg};
                border:1px solid var(--pip-green);
                color:{fg};
                padding:4px 8px;
                font-size:1rem;
                text-transform:uppercase;
            ">{icon} {label}: {value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(text: str):
    st.markdown(
        f"""
        <div style="
            background:var(--pip-green);
            color:var(--pip-bg);
            padding:4px 10px;
            margin:1.5rem 0 1rem 0;
            display:inline-block;
            font-size:1.4rem;
            text-transform:uppercase;
            font-weight:bold;
            text-shadow:none !important;
        ">
            > {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  SIDEBAR — NAVIGATION (PIP-BOY EDITION)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <img src="https://icon2.cleanpng.com/20180802/yqg/3dc04be0578b48f51c4a8d7e9b18136d.webp" class="vault-boy">
            <div style="
                font-size:2.5rem;
                text-transform:uppercase;
                line-height:1;
                font-weight:bold;
                margin-top: 10px;
            ">PIP-OS v7.3</div>
            <div style="
                font-size:1.2rem;
                margin-top:5px;
            ">G.H.O.S.T. Reconnaissance</div>
            <div style="
                font-size:0.9rem;
                margin-top:5px;
                color:var(--pip-dim) !important;
            ">VAULT-TEC KEEPS YOU SAFE ONLINE</div>
        </div>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    MODULE = st.radio(
        "Select Application:",
        [
            "🏠  Control Panel",
            "👤  Username Search",
            "🌐  Network Utility & Recon",
            "📞  Phone Intelligence",
            "📧  Email Discovery",
            "🔍  Google Dorking",
            "☢️  Threat Intelligence",
            "👾  Malware Sandbox",
            "🐙  GitHub Secret Scanner",
            "🖼️  Image Forensics",
            "💸  Financial Intelligence",
            "🔐  Data Breach Search"
        ],
        label_visibility="visible",
    )

    st.markdown(
        """
        <hr>
        <div style="
            font-size:0.9rem;
            text-align:center;
            padding-top:0.5rem;
            border: 1px solid var(--pip-green);
            padding: 5px;
            background: var(--pip-dark);
        ">
            ☢️ VAULT-TEC AUTHORIZED USE ONLY.<br>
            Respect local wasteland laws.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════
#  MODULE 0 — OSINT CONTROL PANEL
# ════════════════════════════════════════════
if MODULE == "🏠  Control Panel":
    st.markdown("<h1>VAULT-TEC OSINT Control Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem;'>Open-Source Intelligence Framework | Vault-Tec Edition v1.3</p>", unsafe_allow_html=True)
    
    row1_cols = st.columns(4)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sys_info = platform.system() + " " + platform.release()
    with row1_cols[0]: st.metric("System Status", "ONLINE")
    with row1_cols[1]: st.metric("Active Modules", "11") 
    with row1_cols[2]: st.metric("System Time", now)
    with row1_cols[3]: st.metric("Host OS", sys_info)

    row2_cols = st.columns(3)
    vt_status = "OK" if CONFIG.get("VT_KEY") != "YOUR_VIRUSTOTAL_API_KEY" else "MISSING"
    rapid_status = "OK" if "591a" in CONFIG.get("BREACH_KEY", "") else "OFFLINE"
    
    with row2_cols[0]: st.metric("API Handshake", f"VT:{vt_status} | BD:{rapid_status}")
    with row2_cols[1]: st.metric("Memory Banks", " OK")
    with row2_cols[2]: st.metric("CPU Architecture", "SUFFICIENT")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:1.2rem 1.5rem;">
            <div style="font-size:1.8rem; border-bottom:1px solid var(--pip-green); margin-bottom:10px; text-transform:uppercase;">
                RobCo Application Registry
            </div>
            <table style="width:100%; font-size:1.1rem; border-collapse:collapse; text-align:left;">
                <tr style="border-bottom:1px solid var(--pip-green); background:var(--pip-dim);">
                    <th style="padding:8px;">Application</th>
                    <th style="padding:8px;">Forensic Technique</th>
                    <th style="padding:8px;">Primary Provider</th>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">👤 Username Search</td><td>HTTP Probing (Async)</td><td>Sherlock DB</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🌐 Network Utility</td><td>GeoIP + DNS Resolver</td><td>ip-api.com</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">📞 Phone Intel</td><td>Local Metadata Extraction</td><td>Libphonenumber</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">📧 Email Discovery</td><td>MX/SPF DNS Lookup</td><td>Public DNS</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🔐 Data Breach</td><td>Identity Leak Correlation</td><td>BreachDirectory</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🔍 Google Dorking</td><td>Query Generation</td><td>Google Dork Engine</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">☢️ Threat Intel</td><td>Reputation Analysis</td><td>AlienVault OTX</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">👾 Malware Sandbox</td><td>Multi-Engine Scan (v3)</td><td>VirusTotal</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🐙 Secret Scanner</td><td>Recursive String Hunt</td><td>GitHub API</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🖼️ Image Forensics</td><td>EXIF + Rev. Geocoding</td><td>Pillow / Nominatim</td>
                </tr>
                <tr>
                    <td style="padding:8px;">💸 Financial Intel</td><td>Routing & UPI Validation</td><td>Razorpay / VPA</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════
#  MODULE 1  — USERNAME SEARCH
# ════════════════════════════════════════════
elif MODULE == "👤  Username Search":
    PLATFORMS = {
        "GitHub":        ("https://github.com/{u}",             "Not Found"),
        "GitLab":        ("https://gitlab.com/{u}",             "404"),
        "Twitter/X":     ("https://x.com/{u}",                  "This account"),
        "Reddit":        ("https://www.reddit.com/user/{u}",    "page not found"),
        "Instagram":     ("https://www.instagram.com/{u}/",     "Sorry"),
        "TikTok":        ("https://www.tiktok.com/@{u}",        "couldn't find"),
        "Pinterest":     ("https://www.pinterest.com/{u}/",     "404"),
        "Twitch":        ("https://www.twitch.tv/{u}",          "404"),
        "YouTube":       ("https://www.youtube.com/@{u}",       "404"),
        "SoundCloud":    ("https://soundcloud.com/{u}",         "404"),
        "Dev.to":        ("https://dev.to/{u}",                 "404"),
        "Keybase":       ("https://keybase.io/{u}",             "Not Found"),
        "Pastebin":      ("https://pastebin.com/u/{u}",         "Not Found"),
        "HackerNews":    ("https://news.ycombinator.com/user?id={u}", "No such user"),
        "ProductHunt":   ("https://www.producthunt.com/@{u}",  "404"),
        "Kaggle":        ("https://www.kaggle.com/{u}",         "404"),
        "Replit":        ("https://replit.com/@{u}",            "404"),
        "Medium":        ("https://medium.com/@{u}",            "404"),
        "Substack":      ("https://{u}.substack.com",           "404"),
        "Steam":         ("https://steamcommunity.com/id/{u}",  "The specified profile"),
        "AngelList":     ("https://angel.co/{u}", "404"),
        "Fiverr":          ("https://www.fiverr.com/{u}",            "404"),
        "Upwork":          ("https://www.upwork.com/freelancers/~{u}", "404"),
        "Bandcamp":        ("https://bandcamp.com/{u}", "404"),
        "HuggingFace":     ("https://huggingface.co/{u}", "404"),
        "DockerHub":       ("https://hub.docker.com/u/{u}", "404"),
        "npm":             ("https://www.npmjs.com/~{u}", "404"),
        "PyPI":            ("https://pypi.org/user/{u}/", "404"),
    }

    HEADERS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 PIP-OS/7.1" }

    async def check_platform(client: httpx.AsyncClient, name: str, url: str, not_found_text: str):
        try:
            r = await client.get(url, timeout=8.0, follow_redirects=True, headers=HEADERS)
            if r.status_code == 200 and not_found_text.lower() not in r.text.lower():
                return name, url, True
            return name, url, False
        except Exception:
            return name, url, False

    async def run_username_scan(username: str):
        results = []
        async with httpx.AsyncClient(http2=True) as client:
            tasks = []
            for name, (url_tpl, nf) in PLATFORMS.items():
                url = url_tpl.replace("{u}", username)
                tasks.append(check_platform(client, name, url, nf))
            results = await asyncio.gather(*tasks)
        return results

    st.markdown("<h1>Global Identity Search</h1>", unsafe_allow_html=True)
    username = st.text_input("Enter Target Alias:", placeholder="e.g. johndoe")

    if st.button("Execute Async Probe"):
        if not username.strip():
            st.error("Error: Subject alias required.")
        else:
            progress_bar = st.progress(0, text="Establishing uplink...")
            status_text  = st.empty()
            t0 = time.perf_counter()

            status_text.markdown(f"> **Scanning databanks for: {username}**", unsafe_allow_html=True)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(run_username_scan(username))
            loop.close()

            elapsed = time.perf_counter() - t0
            progress_bar.progress(1.0, text="Probe sequence complete.")

            found = [r for r in results if r[2]]
            not_found = [r for r in results if not r[2]]

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Vectors Scanned", len(PLATFORMS))
            with c2: st.metric("Positive Hits", len(found))
            with c3: st.metric("Uplink Time", f"{elapsed:.2f}s")

            section_header("Confirmed Identities")
            if found:
                for name, url, _ in found:
                    st.markdown(
                        f"""
                        <div style="
                            background:var(--pip-dark);border:1px solid var(--pip-green);
                            padding:8px 12px;margin-bottom:8px;font-size:1.2rem;
                        ">
                            <span>[HIT] {name}</span>
                            <a href="{url}" target="_blank"
                               style="float:right;color:var(--pip-green);text-decoration:none;">
                                [ LINK ]
                            </a>
                        </div>
                        """, unsafe_allow_html=True
                    )
            else:
                st.warning("Subject is a ghost. No data found.")

            with st.expander("View Null Returns"):
                for name, url, _ in not_found:
                    st.markdown(f"[NULL] {name}", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 2 — NETWORK UTILITY
# ════════════════════════════════════════════
elif MODULE == "🌐  Network Utility & Recon":
    async def fetch_ip_geo(target: str) -> dict:
        url = f"http://ip-api.com/json/{target}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=8.0)
            return r.json()

    def resolve_dns(domain: str) -> dict:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype, lifetime=5.0)
                results[rtype] = [str(r) for r in answers]
            except Exception:
                results[rtype] = []
        return results

    def resolve_ptr(ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "N/A"

    st.markdown("<h1>Network Topography</h1>", unsafe_allow_html=True)
    target = st.text_input("Enter Node Address (IP/Domain):", placeholder="e.g. 8.8.8.8")

    col_a, col_b = st.columns(2)
    run_ip  = col_a.button("[ TRACE IP ]")
    run_dns = col_b.button("[ DUMP DNS ]")

    if run_ip and target.strip():
        with st.spinner("Pinging Satellites..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            geo = loop.run_until_complete(fetch_ip_geo(target.strip()))
            loop.close()

        if geo.get("status") == "success":
            section_header("Node Telemetry")
            c1, c2, c3 = st.columns(3)
            c1.metric("Node IP", geo.get("query", "—"))
            c2.metric("Territory", geo.get("country", "—"))
            c3.metric("Sector", geo.get("city", "—"))

            card("ISP Routing", geo.get("isp", "—"))
            card("Coordinates", f"Lat {geo.get('lat','—')} / Lon {geo.get('lon','—')}")
            card("Reverse DNS", resolve_ptr(geo.get("query", target.strip())))

            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Security Posture (OTX)")
            try:
                otx_r = httpx.get(f"https://otx.alienvault.com/api/v1/indicators/IPv4/{target.strip()}/general", headers={"X-OTX-API-KEY": CONFIG["OTX_KEY"]}, timeout=5.0)
                pulses = otx_r.json().get('pulse_info', {}).get('count', 0)
                badge("Threat Level", f"{pulses} Pulses", ok=(pulses == 0))
                if pulses > 0:
                    st.error(f"⚠ Caution: This IP is associated with {pulses} known threat pulses.")
            except:
                st.warning("OTX Uplink severed.")
        else:
            st.error(f"Routing Error: {geo.get('message','Unknown')}")

    if run_dns and target.strip():
        domain = re.sub(r"^https?://", "", target.strip()).split("/")[0]
        with st.spinner(f"Accessing Domain Registries for {domain}..."):
            records = resolve_dns(domain)

        section_header("DNS Topology")
        for rtype, values in records.items():
            if values:
                with st.expander(f"[{rtype}] Records Found ({len(values)})"):
                    for v in values:
                        st.code(v, language=None)

# ════════════════════════════════════════════
#  MODULE 3  — PHONE INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "📞  Phone Intelligence":
    def analyse_phone(raw: str) -> dict:
        try:
            parsed = phonenumbers.parse(raw, None)
            return {
                "valid": phonenumbers.is_valid_number(parsed),
                "region": geocoder.description_for_number(parsed, "en") or "Unknown",
                "carrier": carrier.name_for_number(parsed, "en") or "Unknown",
                "country_code": parsed.country_code,
                "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                "error": None,
            }
        except Exception as e:
            return {"error": str(e)}

    st.markdown("<h1>Comms Intercept</h1>", unsafe_allow_html=True)
    phone_raw = st.text_input("Enter Comm Frequency (+Country Code):", placeholder="+1 415 555 0100")

    if st.button("Decrypt Frequency"):
        if not phone_raw.strip():
            st.error("Frequency missing.")
        else:
            result = analyse_phone(phone_raw.strip())
            if result.get("error"):
                st.error(f"Decryption failed: {result['error']}")
            else:
                section_header("Signal Origin")
                c1, c2 = st.columns(2)
                with c1: st.metric("Status", "VALID" if result["valid"] else "INVALID")
                with c2: st.metric("Region", result["region"])
                
                card("Tower Operator", result["carrier"])
                card("Routing Format", result["e164"])

# ════════════════════════════════════════════
#  MODULE 4  — EMAIL DISCOVERY
# ════════════════════════════════════════════
elif MODULE == "📧  Email Discovery":
    st.markdown("<h1>Electronic Mail Trace</h1>", unsafe_allow_html=True)
    email_input = st.text_input("Enter Target Address:", placeholder="target@example.com")

    if st.button("Trace Route"):
        if not email_input.strip():
            st.error("Address missing.")
        else:
            domain = email_input.split("@")[1] if "@" in email_input else ""
            with st.spinner("Pinging Mail Exchangers..."):
                try:
                    answers = dns.resolver.resolve(domain, "MX", lifetime=6.0)
                    mx_records = [str(r.exchange) for r in answers]
                    
                    section_header("Server Topology")
                    st.metric("Mail Servers", "ACTIVE")
                    for mx in mx_records:
                        card("MX Node", mx)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("[ Pivot to Breach Analysis ]"):
                        st.session_state.pivot_email = email_input.strip()
                        st.query_params["module"] = "🔐  Data Breach Search"
                        st.rerun()

                except Exception:
                    st.error("No active mail servers found for domain.")

# ════════════════════════════════════════════
#  MODULE 5  — GOOGLE DORKING
# ════════════════════════════════════════════
elif MODULE == "🔍  Google Dorking":

    DORK_TEMPLATES = {
        "Sensitive Files": [
            ('Exposed .env files',        'filetype:env "{target}"'),
            ('Exposed credentials',       'filetype:txt intext:"password" intext:"username" site:{target}'),
            ('Database dumps',            'filetype:sql "{target}"'),
            ('Config files',              'filetype:xml OR filetype:yml "{target}" intext:"password"'),
            ('Log files',                 'filetype:log "{target}"'),
            ('Backup files',              'filetype:bak OR filetype:backup "{target}"'),
        ],
        "Directory Listings": [
            ('Open index pages',          'intitle:"index of" "{target}"'),
            ('Apache directory listing',  'intitle:"index of /" "{target}"'),
            ('FTP open directories',      'intitle:"index of" inurl:ftp "{target}"'),
        ],
        "Login & Admin Panels": [
            ('Admin panels',              'site:{target} inurl:admin'),
            ('Login pages',               'site:{target} inurl:login'),
            ('phpMyAdmin',                'site:{target} inurl:phpmyadmin'),
            ('WordPress admin',           'site:{target} inurl:wp-admin'),
        ],
        "Cloud & Infrastructure": [
            ('AWS S3 buckets',            '"{target}" site:s3.amazonaws.com'),
            ('Azure blobs',               '"{target}" site:blob.core.windows.net'),
            ('GCP buckets',               '"{target}" site:storage.googleapis.com'),
            ('Exposed Grafana dashboards','site:{target} intitle:"Grafana"'),
            ('Jenkins CI',                'site:{target} intitle:"Dashboard [Jenkins]"'),
        ],
        "Personal & Social": [
            ('Email addresses on site',   'site:{target} intext:"@{target}"'),
            ('LinkedIn employees',        'site:linkedin.com intitle:"{target}"'),
            ('Social profiles',           '"{target}" site:twitter.com OR site:facebook.com OR site:instagram.com'),
            ('Resume/CVs',                '"{target}" filetype:pdf intitle:"CV" OR intitle:"Resume"'),
        ],
        "Code & Repositories": [
            ('GitHub repositories',       'site:github.com "{target}"'),
            ('Pastebin leaks',            'site:pastebin.com "{target}"'),
            ('Source code leaks',         'site:github.com OR site:gitlab.com "{target}" password'),
        ],
    }

    def build_dork_url(dork: str) -> str:
        return "https://www.google.com/search?q=" + urllib.parse.quote_plus(dork)

    st.markdown("<h1>Query Generation</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Construct advanced search operators for data extraction from global indexes.</span>
        </div>
        """, unsafe_allow_html=True
    )

    col_t, col_cat = st.columns([2, 1])
    with col_t:
        dork_target = st.text_input("Target Domain/Name:", placeholder="example.com  or  John Smith")
    with col_cat:
        selected_cat = st.selectbox("Category:", list(DORK_TEMPLATES.keys()))

    show_all = st.checkbox("Show all categories")

    if st.button("Generate Operators"):
        if not dork_target.strip():
            st.error("Error: Please enter a target.")
        else:
            target_val = dork_target.strip()
            cats = DORK_TEMPLATES if show_all else {selected_cat: DORK_TEMPLATES[selected_cat]}

            for cat_name, dorks in cats.items():
                section_header(cat_name)
                for label, dork_tpl in dorks:
                    dork = dork_tpl.replace("{target}", target_val)
                    url  = build_dork_url(dork)
                    st.markdown(
                        f"""
                        <div style="
                            background:var(--pip-dark);border:1px solid var(--pip-green);
                            padding:10px;margin-bottom:10px;
                        ">
                            <span style="font-weight:bold;text-transform:uppercase;">{label}</span><br>
                            <code>{dork}</code><br><br>
                            <a href="{url}" target="_blank"
                               style="color:var(--pip-bg);font-weight:bold;text-decoration:none;background:var(--pip-green);padding:4px 8px;">
                                [ EXECUTE SEARCH ]
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# ════════════════════════════════════════════
#  MODULE 6  — THREAT INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "☢️  Threat Intelligence":
    st.markdown("<h1>OTX Threat Feed</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Querying global threat nodes (AlienVault OTX) for malicious signatures.</span>
        </div>
        """, unsafe_allow_html=True
    )

    num_pulses = st.slider("Pulse Display Limit:", 5, 50, 10)
    target = st.text_input("Enter Indicator (IP, Domain, or Hash):", placeholder="e.g. apple.com")
    
    if st.button("☣️ Query Nodes"):
        if not target.strip():
            st.error("Missing indicator value.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                ind_type, otx_path = "IPv4", "IPv4"
            elif "@" in target:
                ind_type, otx_path = "Email", "email"
            else:
                ind_type, otx_path = "Domain", "domain"

            headers = {"X-OTX-API-KEY": CONFIG["OTX_KEY"]}
            url = f"https://otx.alienvault.com/api/v1/indicators/{otx_path}/{target.strip()}/general"
            
            with st.spinner("Accessing Global Intelligence Feed..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=12.0)
                    data = r.json()
                    
                    section_header(f"Reputation Analysis: {target}")
                    
                    pulse_info = data.get('pulse_info', {})
                    total_pulses = pulse_info.get('count', 0)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("Indicator Type", ind_type)
                    with c2: st.metric("Active Pulses", total_pulses)
                    with c3: st.metric("Reputation", "MALICIOUS" if total_pulses > 0 else "CLEAN")

                    if total_pulses > 0:
                        st.warning(f"System Alert: Indicator identified in {total_pulses} community threat pulses.")
                        
                        for pulse in pulse_info.get('pulses', [])[:num_pulses]:
                            pulse_name = pulse.get('name', 'Unnamed Pulse')
                            
                            with st.expander(f"📁 Pulse: {pulse_name}"):
                                author = pulse.get('author_name', 'Anonymous')
                                created = (pulse.get('created') or "N/A")[:10]
                                tags = pulse.get('tags', [])
                                indicators = pulse.get('indicators', [])
                                
                                st.markdown(f"**Author:** {author}")
                                st.markdown(f"**Date:** {created}")
                                st.markdown(f"**Tags:** {', '.join(tags) if tags else 'None'}")
                                
                                st.markdown("---")
                                st.info(pulse.get('description', 'No description available.'))
                                
                                if indicators:
                                    st.markdown(f"**Related Indicators ({len(indicators)} total):**")
                                    for ioc in indicators[:5]:
                                        st.code(f"[{ioc.get('type')}] {ioc.get('indicator')}", language=None)
                    else:
                        st.success("No known malicious associations found in OTX database.")
                except Exception as e:
                    st.error(f"OTX Connectivity Error: {str(e)}")

# ════════════════════════════════════════════
#  MODULE 7  — MALWARE SANDBOX
# ════════════════════════════════════════════
elif MODULE == "👾  Malware Sandbox":
    st.markdown("<h1>VirusTotal Isolation</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Cross-references indicators against 70+ antivirus scanners using VirusTotal v3 API.</span>
        </div>
        """, unsafe_allow_html=True
    )

    target = st.text_input("Enter Hash, Domain, or IP:", placeholder="e.g. 44d88612fea8a8f36de82e1278abb02f")

    if st.button("🔎 Execute Scan"):
        if not target.strip():
            st.error("Please provide a target for the sandbox.")
        elif CONFIG["VT_KEY"] == "YOUR_VIRUSTOTAL_API_KEY":
            st.warning("SYSTEM ERROR: VirusTotal API Key missing in CONFIG.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                vt_type = "ip_addresses"
            elif "." in target and "@" not in target:
                vt_type = "domains"
            else:
                vt_type = "files"

            url = f"https://www.virustotal.com/api/v3/{vt_type}/{target.strip()}"
            headers = {"x-apikey": CONFIG["VT_KEY"]}

            with st.spinner("Uploading to multi-engine sandbox..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=15.0)
                    if r.status_code == 200:
                        data = r.json()['data']['attributes']
                        stats = data.get('last_analysis_stats', {})
                        
                        section_header(f"Security Report: {target}")
                        
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Malicious", stats.get('malicious', 0))
                        with c2: st.metric("Suspicious", stats.get('suspicious', 0))
                        with c3: st.metric("Harmless", stats.get('harmless', 0))
                        with c4: st.metric("Undetected", stats.get('undetected', 0))

                        col_left, col_right = st.columns(2)
                        with col_left:
                            card("Reputation Score", str(data.get('reputation', 0)))
                            card("Provider Tags", ", ".join(data.get('tags', [])) if data.get('tags') else "None")
                        
                        with col_right:
                            card("Primary Label", data.get('meaningful_name', data.get('type_description', 'N/A')))
                            card("Last DNS Records", str(len(data.get('last_dns_records', []))))

                        if stats.get('malicious', 0) > 0:
                            st.markdown("---")
                            st.markdown("**Engine Flags:**")
                            results = data.get('last_analysis_results', {})
                            for engine, res in results.items():
                                if res['category'] == 'malicious':
                                    st.error(f"[ {engine} ] : {res['result']}")
                    
                    elif r.status_code == 404:
                        st.info("Indicator not found in VirusTotal database.")
                    else:
                        st.error(f"VT API Error: {r.status_code}")
                except Exception as e:
                    st.error(f"Sandbox Connectivity Failed: {str(e)}")    

# ════════════════════════════════════════════
#  MODULE 8  — GITHUB SECRET SCANNER
# ════════════════════════════════════════════
elif MODULE == "🐙  GitHub Secret Scanner":
    st.markdown("<h1>Repository Extraction</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Hunts for sensitive strings (AWS Keys, Private Keys, .env files) leaked in public GitHub repos.</span>
        </div>
        """, unsafe_allow_html=True
    )

    target_user = st.text_input("Enter GitHub Username/Org:", placeholder="e.g. apple or torvalds")
    
    DANGER_QUERIES = {
        "AWS Keys": "AKIA",
        "Private RSA Keys": "BEGIN RSA PRIVATE KEY",
        "Environment Files": "filename:.env",
        "GitHub Tokens": "ghp_",
        "Config w/ Passwords": "extension:config password"
    }

    if st.button("🚀 Hunt Secrets"):
        if not target_user.strip():
            st.error("Target username is required.")
        else:
            section_header(f"Scanning Repositories for: {target_user}")
            
            headers = {}
            if CONFIG["GITHUB_TOKEN"]:
                headers["Authorization"] = f"token {CONFIG['GITHUB_TOKEN']}"
            
            found_secrets = False
            
            with st.spinner(f"Analyzing {target_user}'s digital trail..."):
                for label, query in DANGER_QUERIES.items():
                    search_url = f"https://api.github.com/search/code?q={query}+user:{target_user}"
                    try:
                        r = httpx.get(search_url, headers=headers, timeout=15.0)
                        if r.status_code == 200:
                            data = r.json()
                            count = data.get('total_count', 0)
                            
                            if count > 0:
                                found_secrets = True
                                st.warning(f"⚠ {label} Detected: {count} potential leaks found.")
                                for item in data.get('items', [])[:3]:
                                    repo_name = item['repository']['full_name']
                                    file_path = item['path']
                                    file_url = item['html_url']
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:8px; margin-bottom:5px;">
                                            <span>
                                                <b>Repo:</b> {repo_name}<br>
                                                <b>File:</b> {file_path}<br>
                                                <a href="{file_url}" target="_blank" style="color:var(--pip-bg); background:var(--pip-green); padding:2px 5px; text-decoration:none; display:inline-block; margin-top:5px;">[ VIEW SOURCE ]</a>
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                        elif r.status_code == 403:
                            st.error("API Rate Limit Exceeded.")
                            break
                        time.sleep(2) 
                    except Exception as e:
                        st.error(f"Search Failed for {label}: {str(e)}")

            if not found_secrets:
                st.success("Clean Scan: No obvious secrets detected.")                    

# ════════════════════════════════════════════
#  MODULE 9 — IMAGE FORENSICS
# ════════════════════════════════════════════
elif MODULE == "🖼️  Image Forensics":
    st.markdown("<h1>EXIF Decoding</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Extracts metadata and pings Nominatim to convert raw GPS data into physical street addresses.</span>
        </div>
        """, unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Drop Evidence Image (JPG/TIFF):", type=["jpg", "jpeg", "tiff"])

    def get_decimal_from_dms(dms, ref):
        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0
        val = float(degrees + minutes + seconds)
        return -val if ref in ['S', 'W'] else val

    async def get_human_address(lat, lon):
        headers = {"User-Agent": "GHOST-OSINT-App/1.1 (Cybersecurity-Research)"}
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                r = await client.get(url, timeout=10.0)
                if r.status_code == 200:
                    return r.json().get('display_name', 'Address not found')
                return f"API Error: HTTP {r.status_code}"
            except Exception as e:
                return f"Connection Error: {str(e)}"

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Evidence", use_container_width=True)
        
        exif_data = image._getexif()
        
        if not exif_data:
            st.error("SYSTEM ERROR: No EXIF metadata found. Image may have been scrubbed.")
        else:
            section_header("Metadata Analysis")
            clean_exif, gps_info = {}, {}
            
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    for t in value:
                        gps_info[GPSTAGS.get(t, t)] = value[t]
                else:
                    clean_exif[decoded] = value

            row1 = st.columns(3)
            with row1[0]: st.metric("Device", clean_exif.get('Model', 'Unknown'))
            with row1[1]: st.metric("Software", str(clean_exif.get('Software', '1.0')))
            with row1[2]: st.metric("Timestamp", str(clean_exif.get('DateTime', 'N/A'))[:10])

            if gps_info and 'GPSLatitude' in gps_info:
                lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
                lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
                
                row2 = st.columns(3)
                with row2[0]: st.metric("Latitude", f"{lat:.6f}")
                with row2[1]: st.metric("Longitude", f"{lon:.6f}")
                with row2[2]: st.metric("GPS Status", "LOCKED", delta_color="normal")

                with st.spinner("Decoding GPS into physical address..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    address = loop.run_until_complete(get_human_address(lat, lon))
                    loop.close()

                st.markdown(f"""
                    <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:15px; margin-top:10px;">
                        <b>[📍] DETECTED ADDRESS:</b><br>
                        <span>{address}</span>
                    </div>
                """, unsafe_allow_html=True)

                maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; margin-top:10px; padding:10px;">[ VIEW SATELLITE IMAGERY ]</button></a>', unsafe_allow_html=True)
            else:
                st.info("No GPS coordinates detected for this asset.")

            with st.expander("📁 View Raw Metadata Dump"):
                for k, v in clean_exif.items():
                    st.write(f"**{k}:** {v}")

# ════════════════════════════════════════════
#  MODULE 10 — FINANCIAL INTELLIGENCE (INDIA)
# ════════════════════════════════════════════
elif MODULE == "💸  Financial Intelligence":
    st.markdown("<h1>Caps & Currency Trace</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Validates IFSC routing codes and analyzes UPI Virtual Payment Addresses (VPA) for the Indian subcontinent.</span>
        </div>
        """, unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["[ 🏦 IFSC Trace ]", "[ 💳 UPI Analysis ]"])

    with tab1:
        ifsc_input = st.text_input("Enter Routing Code (IFSC):", placeholder="e.g. HDFC0000007")
        if st.button("🔎 Trace Branch"):
            if len(ifsc_input) != 11:
                st.error("INVALID FORMAT: IFSC must be exactly 11 characters.")
            else:
                with st.spinner("Accessing RBI Routing Tables..."):
                    try:
                        r = httpx.get(f"https://ifsc.razorpay.com/{ifsc_input.strip()}", timeout=10.0)
                        if r.status_code == 200:
                            data = r.json()
                            section_header(f"Branch Details: {data.get('BANK')}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                card("Bank Name", data.get('BANK'))
                                card("Branch",    data.get('BRANCH'))
                                card("IFSC",      data.get('IFSC'))
                            with c2:
                                card("City",      data.get('CITY'))
                                card("District",  data.get('DISTRICT'))
                                card("State",     data.get('STATE'))
                            
                            st.info(f"📍 Address: {data.get('ADDRESS')}")
                            
                            addr_query = f"{data.get('BANK')} {data.get('BRANCH')} {data.get('CITY')}"
                            maps_url = f"https://www.google.com/maps/search/{addr_query.replace(' ', '+')}"
                            st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; padding:10px;">[ LOCATE ON MAP ]</button></a>', unsafe_allow_html=True)
                        else:
                            st.error(f"IFSC NOT FOUND: Ensure the code is correct (Status {r.status_code}).")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")

    with tab2:
        vpa_input = st.text_input("Enter UPI ID (VPA):", placeholder="username@bank")
        UPI_HANDLES = {
            "okicici": "ICICI Bank", "okaxis": "Axis Bank", "oksbi": "State Bank of India",
            "okhdfcbank": "HDFC Bank", "ybl": "Yes Bank", "ibl": "ICICI Bank (PhonePe)",
            "axl": "Axis Bank (PhonePe)", "paytm": "Paytm Payments Bank",
            "upl": "Union Bank", "postbank": "India Post Payments Bank"
        }

        if st.button("🧪 Analyze VPA"):
            if "@" not in vpa_input:
                st.error("INVALID FORMAT: UPI ID must contain an '@' symbol.")
            else:
                handle = vpa_input.split("@")[-1].lower()
                bank_partner = UPI_HANDLES.get(handle, "Unknown/Custom Provider")
                
                section_header(f"Analysis: {vpa_input}")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("Provider", bank_partner)
                with c2: st.metric("Format Status", "VALID" if len(vpa_input) > 3 else "INVALID")
                
                st.markdown(
                    """
                    <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:10px; margin-top:10px;">
                        <b>[ NOTE ]</b> In India, the handle reveals the processing bank. 
                        To verify the Legal Name, scan the QR below with a banking app.
                    </div>
                    """, unsafe_allow_html=True
                )
                
                upi_link = f"upi://pay?pa={vpa_input}&pn=GHOST_RECON&cu=INR"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={upi_link}"
                st.image(qr_url, caption="Scan to verify Legal Name in app")

# ════════════════════════════════════════════
#  MODULE 11 — DATA BREACH SEARCH (RAPID-API)
# ════════════════════════════════════════════
elif MODULE == "🔐  Data Breach Search":
    st.markdown("<h1>Breach Archives</h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Querying external dark-web indices for compromised assets via BreachDirectory.</span>
        </div>
        """, unsafe_allow_html=True
    )

    pivot_val = st.session_state.get('pivot_email', "")
    query_input = st.text_input("Enter Identifier:", value=pivot_val, placeholder="e.g. target@example.com")
    
    if pivot_val:
        if st.button("[ Flush Memory ]"):
            st.session_state.pivot_email = ""
            st.rerun()

    if st.button("Execute Override"):
        target = query_input.strip()
        if not target:
            st.error("Input required.")
        else:
            api_url = "https://breachdirectory.p.rapidapi.com" 
            headers = {
                "x-rapidapi-key": CONFIG["BREACH_KEY"],
                "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PIP-OS/7.1"
            }
            query_params = {"func": "auto", "term": target}

            with st.spinner("Decrypting mainframe logs..."):
                try:
                    with httpx.Client(follow_redirects=True, timeout=25.0) as client:
                        r = client.get(api_url, headers=headers, params=query_params)
                    
                    if r.status_code == 200:
                        data = r.json()
                        if data.get('success') or 'result' in data:
                            results = data.get('result', [])
                            total_found = len(results)
                            
                            section_header(f"Compromise Report: {target}")
                            c1, c2 = st.columns(2)
                            with c1: st.metric("Leaks Found", total_found)
                            with c2: st.metric("Status", "COMPROMISED" if total_found > 0 else "SECURE")

                            if total_found > 0:
                                for breach in results:
                                    sources = breach.get('sources', [])
                                    source_name = ", ".join(sources) if isinstance(sources, list) else str(sources)
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:10px; margin-bottom:8px;">
                                            <b>> DATABASE: {source_name}</b><br>
                                            <span style="font-size:1.1rem;">
                                                Password Leaked: {"[ YES ]" if breach.get('has_password') else "[ NO ]"}<br>
                                                Hash Type: {breach.get('hash_type', 'N/A')}
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                            else:
                                st.success("Subject is clean. No records found.")
                        else:
                            st.info("No records match this identifier.")
                    else:
                        st.error(f"System Error {r.status_code}. Connection to archive failed.")
                except Exception as e:
                    st.error(f"Uplink Severed: {str(e)}")
"""
╔══════════════════════════════════════════════════════════════╗
║         G.H.O.S.T  //  OSINT Reconnaissance Dashboard       ║
║         Retro Macintosh System 7 Edition                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import asyncio
import httpx
import dns.resolver
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import re
import socket
import time
from datetime import datetime
import urllib.parse
import platform

# ─────────────────────────────────────────────
#  SYSTEM MEMORY  
# ─────────────────────────────────────────────

if 'pivot_email' not in st.session_state:
    st.session_state.pivot_email = ""

# ─────────────────────────────────────────────
#  SYSTEM CONFIGURATION (API KEYS)
# ─────────────────────────────────────────────
CONFIG = {
    "OTX_KEY": "cec0f6c86ef2ee22f1ab3a3734cacd8c2e96846622cf808ef4c07a2f712e25d9", ## REPLACE WITH YOUR OTX KEY                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    "OPENCTI_URL": "http://localhost:8080", 
    "VT_KEY": "70f961af90b0a23b61b4d22fa1223b64694304a105925e25e61b3b22ecc23e22", ## REPLACE WITH YOUR VIRUSTOTAL KEY
    "BREACH_KEY": "591a17a2cemsh80a79611e6132c2p100379jsnf0065f1d3d92", ## REPLACE WITH YOUR BREACH KEY
    "GITHUB_TOKEN": "", ## REPLACE WITH YOUR GITHUB TOKEN (optional, for higher rate limits)
    "OPENCTI_TOKEN": "9d29da5c-d768-4f22-b765-b891e53b8313" ## REPLACE WITH YOUR OPENCTI TOKEN IF NEEDED
}

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GHOST // OSINT",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — RETRO MACINTOSH THEME
# ─────────────────────────────────────────────
MAC_CSS = """
<style>
/* ── Import Retro Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

/* ── Root Palette ── */
:root {
    --black:        #000000;
    --white:        #ffffff;
    --gray:         #aaaaaa;
    --light-gray:   #dfdfdf;
    --font-sys:     'Geneva', 'Tahoma', 'Verdana', sans-serif;
    --font-mono:    'Monaco', 'Courier New', Courier, monospace;
    --font-title:   'VT323', 'Chicago', sans-serif;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-sys) !important;
    color: var(--black) !important;
}

/* ── Classic Mac Dithered Desktop Background ── */
.stApp {
    background-color: var(--white) !important;
    background-image:
      linear-gradient(45deg, var(--gray) 25%, transparent 25%),
      linear-gradient(-45deg, var(--gray) 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, var(--gray) 75%),
      linear-gradient(-45deg, transparent 75%, var(--gray) 75%) !important;
    background-size: 4px 4px !important;
    background-position: 0 0, 0 2px, 2px -2px, -2px 0px !important;
}

/* ── Classic Mac Title Bar ── */
.mac-window-header {
    background: repeating-linear-gradient(
        0deg,
        #000,
        #000 1px,
        #fff 1px,
        #fff 3px
    );
    border: 2px solid #000;
    height: 28px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    margin-bottom: -2px;
    position: relative;
    z-index: 10;
}


.mac-title-text {
    background: #fff;
    padding: 0 15px;
    /* This centers the text even with buttons on the left */
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'VT323', sans-serif;
    font-size: 1.2rem;
    border: 2px solid #000;
    text-transform: uppercase;
    white-space: nowrap;
}

/* ── The Buttons ── */
/* ── The Buttons (Colored Edition) ── */
.mac-btn {
    width: 14px;
    height: 14px;
    border: 1px solid rgba(0, 0, 0, 0.2); /* Subtle border like modern Mac */
    border-radius: 50%; /* Modern circular buttons */
    cursor: pointer;
    margin-right: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: bold;
    color: transparent; /* Hide icons until hover */
    transition: all 0.2s ease;
    box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.3);
}

/* Reveal icons on hover - very Mac-like */
.mac-window-header:hover .mac-btn {
    color: rgba(0, 0, 0, 0.6);
}

.mac-close { background-color: #FF605C; border-color: #E0443E; }
.mac-min   { background-color: #FFBD44; border-color: #DEA123; }
.mac-max   { background-color: #00CA4E; border-color: #14B047; }

.mac-btn:active {
    filter: brightness(0.8);
    transform: translateY(1px);
}

/* Icons inside the colored circles */
.mac-close::after { content: '×'; margin-top: -1px; }
.mac-min::after   { content: '−'; }
.mac-max::after   { content: '+'; }

/* Adding the Icons */
.mac-close::after { content: '×'; }
.mac-min::after   { content: '_'; }
.mac-max::after   { content: '□'; }

/* ── Custom System 7 Dialog Box ── */
#mac-modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(255, 255, 255, 0.4); /* Glass effect */
    z-index: 1000;
}

.mac-dialog {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: #fff;
    border: 1px solid #000;
    outline: 2px solid #fff;
    box-shadow: 4px 4px 0px #000; /* Dithered shadow vibe */
    width: 350px;
    padding: 20px;
    text-align: center;
    border: 3px double #000; /* Classic double border */
}

.mac-dialog-title {
    font-family: 'Chicago', 'Geneva', sans-serif;
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 15px;
    text-transform: uppercase;
    display: block;
}

.mac-dialog-text {
    font-family: 'Monaco', monospace;
    font-size: 0.9rem;
    margin-bottom: 20px;
    display: block;
}

.mac-dialog-ok {
    background: #fff;
    border: 2px solid #000;
    padding: 5px 25px;
    font-family: 'Chicago', sans-serif;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 2px 2px 0px #000;
}

.mac-dialog-ok:active {
    background: #000;
    color: #fff;
    box-shadow: none;
    transform: translate(1px, 1px);
}

/* ── Wrap main content to look like a Mac Window ── */
.block-container {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    box-shadow: 4px 4px 0px var(--black) !important;
    padding: 2rem 3rem !important;
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--white) !important;
    border-right: 2px solid var(--black) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-sys) !important; }

/* ── Sidebar radio buttons ── */
[data-testid="stSidebar"] .stRadio label {
    color: var(--black) !important;
    font-size: 0.9rem !important;
    font-weight: bold;
}

/* ── Headers ── */
h1, h2, h3, h4 {
    font-family: var(--font-title) !important;
    color: var(--black) !important;
    text-transform: uppercase;
}
h1 { font-size: 2.2rem !important; border-bottom: 4px double var(--black); padding-bottom: 5px; }
h2 { font-size: 1.5rem !important; }

/* ── Text inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-radius: 0px !important;
    color: var(--black) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.9rem !important;
    box-shadow: 2px 2px 0px var(--light-gray) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--black) !important;
    font-weight: bold !important;
    font-family: var(--font-sys) !important;
}

/* ── Buttons ── */
.stButton button {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    color: var(--black) !important;
    font-family: var(--font-title) !important;
    font-size: 1.2rem !important;
    text-transform: uppercase;
    border-radius: 0px !important;
    padding: 0.4rem 1.2rem !important;
    box-shadow: 3px 3px 0px var(--black) !important;
    transition: none !important;
}
.stButton button:hover, .stButton button:active {
    background-color: var(--black) !important;
    color: var(--white) !important;
    box-shadow: 1px 1px 0px var(--black) !important;
    transform: translate(2px, 2px);
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: var(--black) !important;
}
.stProgress > div > div {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-radius: 0px !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: var(--light-gray) !important;
    border: 2px solid var(--black) !important;
    color: var(--black) !important;
    font-family: var(--font-sys) !important;
    font-weight: bold !important;
    border-radius: 0px !important;
}
.streamlit-expanderContent {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-top: none !important;
}

/* ── Dividers ── */
hr { border-color: var(--black) !important; border-width: 2px !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-radius: 0px !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 2px 2px 0px var(--black) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--black) !important;
    font-size: 0.8rem !important;
    font-weight: bold !important;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: var(--black) !important;
    font-family: var(--font-title) !important;
    font-size: 1.8rem !important;
}

/* ── Code blocks ── */
.stCodeBlock, code, pre {
    background-color: var(--light-gray) !important;
    border: 2px solid var(--black) !important;
    color: var(--black) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
    border-radius: 0px !important;
}

/* ── Success / warning / error ── */
.stSuccess, .stWarning, .stError, .stInfo { 
    background-color: var(--white) !important; 
    border: 2px solid var(--black) !important; 
    color: var(--black) !important;
    box-shadow: 3px 3px 0px var(--black) !important;
    border-radius: 0px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 12px; }
::-webkit-scrollbar-track { background: var(--white); border-left: 2px solid var(--black); }
::-webkit-scrollbar-thumb { background: var(--light-gray); border: 2px solid var(--black); }
</style>
"""

st.markdown(MAC_CSS, unsafe_allow_html=True)
# ─────────────────────────────────────────────
#  GLOBAL UI COMPONENTS (Modal & Title Bar)
# ─────────────────────────────────────────────

# ── MODAL COMPONENT & LOGIC ──
# We place this here so the JavaScript is available to all modules
st.markdown(
    """
    <div id="mac-modal-overlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(255,255,255,0.4); z-index:9999;">
        <div class="mac-dialog" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); background:#fff; border:3px double #000; box-shadow:4px 4px 0px #000; width:350px; padding:20px; text-align:center;">
            <span class="mac-dialog-title" id="modal-title" style="font-family:'Chicago', sans-serif; font-weight:bold; display:block; margin-bottom:15px; text-transform:uppercase;">System Advisory</span>
            <span class="mac-dialog-text" id="modal-msg" style="font-family:'Monaco', monospace; font-size:0.9rem; display:block; margin-bottom:20px;">Error details go here.</span>
            <button class="mac-dialog-ok" onclick="closeMacModal()" style="background:#fff; border:2px solid #000; padding:5px 25px; font-family:'Chicago', sans-serif; font-weight:bold; cursor:pointer; box-shadow:2px 2px 0px #000;">OK</button>
        </div>
    </div>

    <script>
        function showMacModal(title, msg) {
            const overlay = document.getElementById('mac-modal-overlay');
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-msg').innerText = msg;
            overlay.style.display = 'block';
        }

        function closeMacModal() {
            document.getElementById('mac-modal-overlay').style.display = 'none';
        }
    </script>
    """,
    unsafe_allow_html=True
)

# ── WINDOW HEADER ──
# This puts the colored buttons and title at the top of every module
st.markdown(
    """
    <div class="mac-window-header">
        <div class="mac-btn mac-close" onclick="showMacModal('FATAL ERROR', 'The G.H.O.S.T. exit is encrypted. Your session is now infinite. Coffee-flavored ice cream is recommended for the long haul.')"></div>
        <div class="mac-btn mac-min" onclick="showMacModal('SYSTEM ADVISORY', 'G.H.O.S.T. has been minimized into your subconscious. Proceed to the gym for leg day to recalibrate your physical shell.')"></div>
        <div class="mac-btn mac-max" onclick="showMacModal('RESOURCE ERROR', 'Reality.exe is already at 100% capacity. Your Ryzen 7 is providing too much power for the local Maharashtra power grid.')"></div>
        <div class="mac-title-text">G.H.O.S.T. Explorer v1.2</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ─────────────────────────────────────────────
#  HELPER: render a styled "card" block
# ─────────────────────────────────────────────
def card(title: str, content: str):
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:2px solid #000000;
            box-shadow:2px 2px 0px #000000;
            padding:0.75rem 1rem;
            margin-bottom:0.8rem;
            font-family:'Monaco', 'Courier New', monospace;
            color:#000000;
        ">
            <span style="font-weight:bold;text-transform:uppercase;border-bottom:1px solid #000;">{title}</span><br>
            <span style="font-size:0.9rem;display:block;margin-top:4px;">{content}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def badge(label: str, value: str, ok: bool = True):
    bg = "#ffffff" if ok else "#000000"
    fg = "#000000" if ok else "#ffffff"
    icon = "✓" if ok else "✗"
    st.markdown(
        f"""
        <div style="display:inline-block;margin:3px 4px;">
            <span style="
                background:{bg};
                border:2px solid #000000;
                color:{fg};
                padding:4px 8px;
                font-size:0.85rem;
                font-weight:bold;
                font-family:'Geneva', 'Tahoma', sans-serif;
            ">{icon} {label}: {value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(text: str):
    st.markdown(
        f"""
        <div style="
            background:#000000;
            color:#ffffff;
            padding:4px 8px;
            margin:1.5rem 0 1rem 0;
            display:inline-block;
            font-family:'VT323', 'Chicago', sans-serif;
            font-size:1.2rem;
            text-transform:uppercase;
            border:2px solid #000000;
        ">
            {text}
        </div>
        <div style="height:2px; background:#000; width:100%; margin-top:-1.2rem; margin-bottom:1.5rem; z-index:-1; position:relative;"></div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  SIDEBAR — NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0 0.5rem 0; color:#000;">
            <div style="font-size:3rem; margin-bottom: 10px;">💾</div>
            <div style="
                font-family:'VT323', 'Chicago', sans-serif;
                font-size:2rem;
                text-transform:uppercase;
                line-height:1;
            ">G.H.O.S.T</div>
            <div style="
                font-size:1rem;
                font-weight:bold;
                margin-top:5px;
            ">System 7 Reconnaissance</div>
            <div style="
                font-size:0.6rem;
                font-weight:bold;
                margin-top:5px;
            ">PLEASE SET SYSTEM THEME TO LIGHT MODE </div>
        </div>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    MODULE = st.radio(
        "Select Application:",
        [
            "🏠  Control Panel",
            "👤  Username Search",
            "🌐  Network Utility & Recon",
            "📞  Phone Intelligence",
            "📧  Email Discovery",
            "🔐  Data Breach Search",
            "🔍  Google Dorking",
            "☢️  Threat Intelligence",
            "👾  Malware Sandbox",
            "🐙  GitHub Secret Scanner",
            "🖼️  Image Forensics",
            "💸  Financial Intelligence"
        ],
        label_visibility="visible",
    )

    st.markdown(
        """
        <hr>
        <div style="
            color:#000;
            font-size:0.7rem;
            text-align:center;
            font-weight:bold;
            padding-top:0.5rem;
            border: 2px solid #000;
            padding: 5px;
            background: #dfdfdf;
        ">
            AUTHORIZED USE ONLY.<br>
            Respect local laws.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════
#  MODULE 0 — OSINT CONTROL PANEL (v1.3)
# ════════════════════════════════════════════
if MODULE == "🏠  Control Panel":
    st.markdown("<h1>OSINT Control Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Open-Source Intelligence Framework | Macintosh Edition v1.3</p>", unsafe_allow_html=True)
    
    # Row 1: Primary System Metrics
    row1_cols = st.columns(4)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sys_info = platform.system() + " " + platform.release()
    with row1_cols[0]: st.metric("System Status", "ONLINE")
    with row1_cols[1]: st.metric("Active Modules", "11") 
    with row1_cols[2]: st.metric("System Time", now)
    with row1_cols[3]: st.metric("Host OS", sys_info)

    # Row 2: Hardware & API Integration Status
    row2_cols = st.columns(3)
    # Check status of the major APIs
    vt_status = "OK" if CONFIG.get("VT_KEY") != "YOUR_VIRUSTOTAL_API_KEY" else "MISSING"
    rapid_status = "OK" if "591a" in CONFIG.get("BREACH_KEY", "") else "OFFLINE"
    
    with row2_cols[0]: st.metric("API Handshake", f"VT:{vt_status} | BD:{rapid_status}")
    with row2_cols[1]: st.metric("Host RAM", " OK")
    with row2_cols[2]: st.metric("Processor", " SUFFICIENT")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── COMPLETE SYSTEM APPLICATION REGISTRY ──
    st.markdown(
        """
        <div style="background:#ffffff; border:2px solid #000; box-shadow:4px 4px 0px #000; padding:1.2rem 1.5rem;">
            <div style="font-family:'Chicago', sans-serif; font-size:1.5rem; border-bottom:2px solid #000; margin-bottom:10px;">
                System Application Registry
            </div>
            <table style="width:100%; font-size:0.8rem; border-collapse:collapse; font-family:'Monaco', monospace;">
                <tr style="border-bottom:2px solid #000; background:#dfdfdf;">
                    <th style="text-align:left; padding:8px;">Application</th>
                    <th style="text-align:left; padding:8px;">Forensic Technique</th>
                    <th style="text-align:left; padding:8px;">Primary Provider</th>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Username Search</td><td>HTTP Probing (Async)</td><td>Sherlock DB</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Network Utility</td><td>GeoIP + DNS Resolver</td><td>ip-api.com</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Phone Intel</td><td>Local Metadata Extraction</td><td>Libphonenumber</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Email Discovery</td><td>MX/SPF DNS Lookup</td><td>Public DNS</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Data Breach</td><td>Identity Leak Correlation</td><td>BreachDirectory</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Google Dorking</td><td>Query Generation</td><td>Google Dork Engine</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Threat Intel</td><td>Reputation Analysis</td><td>AlienVault OTX</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Malware Sandbox</td><td>Multi-Engine Scan (v3)</td><td>VirusTotal</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Secret Scanner</td><td>Recursive String Hunt</td><td>GitHub API</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Image Forensics</td><td>EXIF + Rev. Geocoding</td><td>Pillow / Nominatim</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Financial Intel</td><td>Routing & UPI Validation</td><td>Razorpay / VPA</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Select an application from the **sidebar** to begin. Operations run locally or via free APIs.")


# ════════════════════════════════════════════
#  MODULE 1  — USERNAME SEARCH
# ════════════════════════════════════════════
elif MODULE == "👤  Username Search":

    # ── Sherlock-inspired platform list ──
    PLATFORMS = {
        "GitHub":        ("https://github.com/{u}",             "Not Found"),
        "GitLab":        ("https://gitlab.com/{u}",             "404"),
        "Twitter/X":     ("https://x.com/{u}",                  "This account"),
        "Reddit":        ("https://www.reddit.com/user/{u}",    "page not found"),
        "Instagram":     ("https://www.instagram.com/{u}/",     "Sorry"),
        "TikTok":        ("https://www.tiktok.com/@{u}",        "couldn't find"),
        "Pinterest":     ("https://www.pinterest.com/{u}/",     "404"),
        "Twitch":        ("https://www.twitch.tv/{u}",          "404"),
        "YouTube":       ("https://www.youtube.com/@{u}",       "404"),
        "SoundCloud":    ("https://soundcloud.com/{u}",         "404"),
        "Dev.to":        ("https://dev.to/{u}",                 "404"),
        "Keybase":       ("https://keybase.io/{u}",             "Not Found"),
        "Pastebin":      ("https://pastebin.com/u/{u}",         "Not Found"),
        "HackerNews":    ("https://news.ycombinator.com/user?id={u}", "No such user"),
        "ProductHunt":   ("https://www.producthunt.com/@{u}",  "404"),
        "Kaggle":        ("https://www.kaggle.com/{u}",         "404"),
        "Replit":        ("https://replit.com/@{u}",            "404"),
        "Medium":        ("https://medium.com/@{u}",            "404"),
        "Substack":      ("https://{u}.substack.com",           "404"),
        "Steam":         ("https://steamcommunity.com/id/{u}",  "The specified profile"),
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    async def check_platform(client: httpx.AsyncClient, name: str, url: str, not_found_text: str):
        try:
            r = await client.get(url, timeout=8.0, follow_redirects=True, headers=HEADERS)
            if r.status_code == 200 and not_found_text.lower() not in r.text.lower():
                return name, url, True
            return name, url, False
        except Exception:
            return name, url, False

    async def run_username_scan(username: str):
        results = []
        async with httpx.AsyncClient(http2=True) as client:
            tasks = []
            for name, (url_tpl, nf) in PLATFORMS.items():
                url = url_tpl.replace("{u}", username)
                tasks.append(check_platform(client, name, url, nf))
            results = await asyncio.gather(*tasks)
        return results

    # ── UI ──
    st.markdown("<h1>Username Search</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Async probe across 20 platforms. Inspired by the Sherlock Project.</p>", unsafe_allow_html=True)

    username = st.text_input("Target Username:", placeholder="e.g. johndoe")

    if st.button("Execute Scan"):
        if not username.strip():
            st.error("Error: Please enter a valid username.")
        else:
            progress_bar = st.progress(0, text="Initialising scan…")
            status_text  = st.empty()
            t0 = time.perf_counter()

            status_text.markdown(f"<b>Scanning username: {username}</b>", unsafe_allow_html=True)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(run_username_scan(username))
            loop.close()

            elapsed = time.perf_counter() - t0
            progress_bar.progress(1.0, text="Scan complete.")

            found = [r for r in results if r[2]]
            not_found = [r for r in results if not r[2]]

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Targets Scanned", len(PLATFORMS))
            with c2: st.metric("Matches Found", len(found))
            with c3: st.metric("Elapsed Time", f"{elapsed:.2f}s")

            section_header("Results — Found")
            if found:
                for name, url, _ in found:
                    st.markdown(
                        f"""
                        <div style="
                            background:#ffffff;border:2px solid #000;
                            box-shadow:2px 2px 0px #000;
                            padding:8px 12px;margin-bottom:8px;
                            font-family:'Monaco', monospace; font-weight:bold;
                        ">
                            <span>✓ {name}</span>
                            <a href="{url}" target="_blank"
                               style="float:right;color:#000;text-decoration:underline;">
                                {url} ↗
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.warning("No profiles detected.")

            with st.expander("Show Missing / Not Found"):
                for name, url, _ in not_found:
                    st.markdown(f"✗ {name}", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 2 — NETWORK UTILITY (OG EDITION)
# ════════════════════════════════════════════
elif MODULE == "🌐  Network Utility & Recon":

    async def fetch_ip_geo(target: str) -> dict:
        url = f"http://ip-api.com/json/{target}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=8.0)
            return r.json()

    def resolve_dns(domain: str) -> dict:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype, lifetime=5.0)
                results[rtype] = [str(r) for r in answers]
            except Exception:
                results[rtype] = []
        return results

    def resolve_ptr(ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "N/A"

    # ── UI RENDERING ──
    st.markdown("<h1>Network Utility</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Geolocation via ip-api.com  · DNS records via dnspython</p>", unsafe_allow_html=True)

    target = st.text_input("Enter Hostname or IP Address:", placeholder="e.g. 8.8.8.8")

    col_a, col_b = st.columns(2)
    run_ip  = col_a.button("🌍 GEOLOCATE IP")
    run_dns = col_b.button("🔎 RESOLVE DNS")

    if run_ip and target.strip():
        with st.spinner("Querying ip-api.com…"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            geo = loop.run_until_complete(fetch_ip_geo(target.strip()))
            loop.close()

        if geo.get("status") == "success":
            section_header("Geolocation Data")
            c1, c2, c3 = st.columns(3)
            c1.metric("IP / Query", geo.get("query", "—"))
            c2.metric("Country", geo.get("country", "—"))
            c3.metric("City", geo.get("city", "—"))

            card("Continent",   geo.get("continent",   "—"))
            card("Region",      geo.get("regionName",  "—"))
            card("ZIP Code",    geo.get("zip",         "—"))
            card("Timezone",    geo.get("timezone",    "—"))
            card("ISP",         geo.get("isp",         "—"))
            card("Organisation",geo.get("org",         "—"))
            card("AS Number",   geo.get("as",          "—"))
            card("Coordinates", f"Lat {geo.get('lat','—')} / Lon {geo.get('lon','—')}")

            ptr = resolve_ptr(geo.get("query", target.strip()))
            card("Reverse DNS (PTR)", ptr)

            # --- OTX REPUTATION AUTO-CHECK ---
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Security Reputation (OTX)")
            otx_headers = {"X-OTX-API-KEY": CONFIG["OTX_KEY"]}
            otx_url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{target.strip()}/general"
            
            try:
                otx_r = httpx.get(otx_url, headers=otx_headers, timeout=5.0)
                otx_data = otx_r.json()
                pulses = otx_data.get('pulse_info', {}).get('count', 0)
                badge("Threat Pulses", str(pulses), ok=(pulses == 0))
                if pulses > 0:
                    st.error(f"⚠ Caution: This IP is associated with {pulses} known threat pulses.")
            except:
                st.warning("Could not reach OTX for reputation check.")
        else:
            st.error(f"ip-api.com returned: {geo.get('message','Unknown error')}")

    if run_dns and target.strip():
        domain = re.sub(r"^https?://", "", target.strip()).split("/")[0]
        with st.spinner(f"Resolving DNS for {domain}…"):
            records = resolve_dns(domain)

        section_header("DNS Record Set")
        for rtype, values in records.items():
            if values:
                with st.expander(f"Type {rtype} Records ({len(values)})"):
                    for v in values:
                        st.code(v, language=None)
            else:
                st.markdown(f"<span style='font-family:Monaco,monospace;color:#555;'>No {rtype} records found.</span>", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 3  — PHONE INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "📞  Phone Intelligence":

    def analyse_phone(raw: str) -> dict:
        try:
            parsed = phonenumbers.parse(raw, None)
            valid   = phonenumbers.is_valid_number(parsed)
            possible= phonenumbers.is_possible_number(parsed)
            region  = geocoder.description_for_number(parsed, "en")
            carr    = carrier.name_for_number(parsed, "en")
            tzones  = list(timezone.time_zones_for_number(parsed))
            fmt_e164= phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            fmt_intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            fmt_natl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            ntype_raw = phonenumbers.number_type(parsed)
            number_type_map = {
                0: "FIXED_LINE", 1: "MOBILE", 2: "FIXED_OR_MOBILE",
                3: "TOLL_FREE", 4: "PREMIUM_RATE", 6: "VOIP",
                7: "PERSONAL_NUMBER", 99: "UNKNOWN",
            }
            ntype = number_type_map.get(ntype_raw, "UNKNOWN")
            return {
                "valid": valid, "possible": possible,
                "region": region or "Unknown",
                "carrier": carr or "Unknown",
                "timezones": tzones,
                "country_code": parsed.country_code,
                "national_number": parsed.national_number,
                "e164": fmt_e164, "intl": fmt_intl, "national": fmt_natl,
                "number_type": ntype,
                "error": None,
            }
        except Exception as e:
            return {"error": str(e)}

    # ── UI ──
    st.markdown("<h1>Phone Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Offline metadata extraction via phonenumbers lib.</p>", unsafe_allow_html=True)

    st.info("Note: Include country code prefix (e.g. +1 415 555 0100)")
    phone_raw = st.text_input("Target Phone Number:", placeholder="+1 415 555 0100")

    if st.button("Analyse Number"):
        if not phone_raw.strip():
            st.error("Error: Please enter a phone number.")
        else:
            result = analyse_phone(phone_raw.strip())
            if result.get("error"):
                st.error(f"Parse error: {result['error']}")
            else:
                section_header("Number Metadata")

                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Valid", "YES" if result["valid"] else "NO")
                with c2: st.metric("Type", result["number_type"])
                with c3: st.metric("Country Code", f"+{result['country_code']}")

                card("Region / Country",   result["region"])
                card("Carrier / Operator", result["carrier"])
                card("E.164 Format",       result["e164"])
                card("International",      result["intl"])
                card("National",           result["national"])
                card("Timezones", ", ".join(result["timezones"]) if result["timezones"] else "Unknown")

                section_header("System Flags")
                badge("Is Valid",    str(result["valid"]),    result["valid"])
                badge("Is Possible", str(result["possible"]), result["possible"])


# ════════════════════════════════════════════
#  MODULE 4  — EMAIL DISCOVERY
# ════════════════════════════════════════════
elif MODULE == "📧  Email Discovery":

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    )

    DISPOSABLE_DOMAINS = {
        "mailinator.com", "guerrillamail.com", "tempmail.com",
        "throwam.com", "sharklasers.com", "trashmail.com",
        "yopmail.com", "getairmail.com", "fakeinbox.com",
        "dispostable.com", "spam4.me", "maildrop.cc",
    }

    def check_email(email: str) -> dict:
        valid_fmt = bool(EMAIL_REGEX.match(email))
        if not valid_fmt:
            return {"valid_format": False}

        domain = email.split("@")[1].lower()
        disposable = domain in DISPOSABLE_DOMAINS

        mx_records = []
        mx_ok = False
        try:
            answers = dns.resolver.resolve(domain, "MX", lifetime=6.0)
            mx_records = sorted(
                [(r.preference, str(r.exchange)) for r in answers],
                key=lambda x: x[0],
            )
            mx_ok = True
        except Exception:
            pass

        a_records = []
        try:
            answers = dns.resolver.resolve(domain, "A", lifetime=6.0)
            a_records = [str(r) for r in answers]
        except Exception:
            pass

        spf = None
        try:
            answers = dns.resolver.resolve(domain, "TXT", lifetime=6.0)
            for r in answers:
                txt = str(r).strip('"')
                if txt.startswith("v=spf1"):
                    spf = txt
                    break
        except Exception:
            pass

        return {
            "valid_format": valid_fmt,
            "domain": domain,
            "disposable": disposable,
            "mx_ok": mx_ok,
            "mx_records": mx_records,
            "a_records": a_records,
            "spf": spf,
        }

    # ── UI ──
    st.markdown("<h1>Email Discovery</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Format validation · DNS lookups · Disposable check</p>", unsafe_allow_html=True)

    email_input = st.text_input("Target Email Address:", placeholder="target@example.com")

    if st.button("Analyse Email"):
        if not email_input.strip():
            st.error("Error: Please enter an email address.")
        else:
            with st.spinner("Executing DNS lookups…"):
                res = check_email(email_input.strip().lower())

            if not res["valid_format"]:
                st.error("Error: Invalid email format.")
            else:
                section_header("Analysis Results")

                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Format", "VALID")
                with c2: st.metric("MX Records", "FOUND" if res["mx_ok"] else "NONE")
                with c3: st.metric("Deliverable?", "LIKELY" if res["mx_ok"] else "UNLIKELY")

                card("Domain", res["domain"])

                badge("Format Valid", "Yes", True)
                badge("MX Exists",    "Yes" if res["mx_ok"]    else "No", res["mx_ok"])
                badge("Disposable",   "Yes" if res["disposable"] else "No", not res["disposable"])
                badge("SPF Found",    "Yes" if res["spf"]      else "No", bool(res["spf"]))

                if res["mx_records"]:
                    section_header("MX Records (Mail Servers)")
                    for pref, host in res["mx_records"]:
                        card(f"Priority {pref}", host)

                if res["a_records"]:
                    section_header("A Records (Domain IPs)")
                    for ip in res["a_records"]:
                        card("IP Address", ip)

                if res["spf"]:
                    section_header("SPF Record")
                    st.code(res["spf"], language=None)

                if res["disposable"]:
                    st.warning("Warning: This domain is a known disposable/temporary provider.")


# ════════════════════════════════════════════
#  MODULE 5  — GOOGLE DORKING
# ════════════════════════════════════════════
elif MODULE == "🔍  Google Dorking":

    DORK_TEMPLATES = {
        "Sensitive Files": [
            ('Exposed .env files',        'filetype:env "{target}"'),
            ('Exposed credentials',       'filetype:txt intext:"password" intext:"username" site:{target}'),
            ('Database dumps',            'filetype:sql "{target}"'),
            ('Config files',              'filetype:xml OR filetype:yml "{target}" intext:"password"'),
            ('Log files',                 'filetype:log "{target}"'),
            ('Backup files',              'filetype:bak OR filetype:backup "{target}"'),
        ],
        "Directory Listings": [
            ('Open index pages',          'intitle:"index of" "{target}"'),
            ('Apache directory listing',  'intitle:"index of /" "{target}"'),
            ('FTP open directories',      'intitle:"index of" inurl:ftp "{target}"'),
        ],
        "Login & Admin Panels": [
            ('Admin panels',              'site:{target} inurl:admin'),
            ('Login pages',               'site:{target} inurl:login'),
            ('phpMyAdmin',                'site:{target} inurl:phpmyadmin'),
            ('WordPress admin',           'site:{target} inurl:wp-admin'),
        ],
        "Cloud & Infrastructure": [
            ('AWS S3 buckets',            '"{target}" site:s3.amazonaws.com'),
            ('Azure blobs',               '"{target}" site:blob.core.windows.net'),
            ('GCP buckets',               '"{target}" site:storage.googleapis.com'),
            ('Exposed Grafana dashboards','site:{target} intitle:"Grafana"'),
            ('Jenkins CI',                'site:{target} intitle:"Dashboard [Jenkins]"'),
        ],
        "Personal & Social": [
            ('Email addresses on site',   'site:{target} intext:"@{target}"'),
            ('LinkedIn employees',        'site:linkedin.com intitle:"{target}"'),
            ('Social profiles',           '"{target}" site:twitter.com OR site:facebook.com OR site:instagram.com'),
            ('Resume/CVs',                '"{target}" filetype:pdf intitle:"CV" OR intitle:"Resume"'),
        ],
        "Code & Repositories": [
            ('GitHub repositories',       'site:github.com "{target}"'),
            ('Pastebin leaks',            'site:pastebin.com "{target}"'),
            ('Source code leaks',         'site:github.com OR site:gitlab.com "{target}" password'),
        ],
    }

    def build_dork_url(dork: str) -> str:
        return "https://www.google.com/search?q=" + urllib.parse.quote_plus(dork)

    # ── UI ──
    st.markdown("<h1>Google Dorking Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Generate targeted search operators.</p>", unsafe_allow_html=True)

    col_t, col_cat = st.columns([2, 1])
    with col_t:
        dork_target = st.text_input("Target Domain/Name:", placeholder="example.com  or  John Smith")
    with col_cat:
        selected_cat = st.selectbox("Category:", list(DORK_TEMPLATES.keys()))

    show_all = st.checkbox("Show all categories")

    if st.button("Generate Dorks"):
        if not dork_target.strip():
            st.error("Error: Please enter a target.")
        else:
            target_val = dork_target.strip()
            cats = DORK_TEMPLATES if show_all else {selected_cat: DORK_TEMPLATES[selected_cat]}

            for cat_name, dorks in cats.items():
                section_header(cat_name)
                for label, dork_tpl in dorks:
                    dork = dork_tpl.replace("{target}", target_val)
                    url  = build_dork_url(dork)
                    st.markdown(
                        f"""
                        <div style="
                            background:#ffffff;border:2px solid #000;
                            box-shadow:2px 2px 0px #000;padding:10px;margin-bottom:10px;
                            font-family:'Monaco', monospace;
                        ">
                            <span style="font-weight:bold;text-transform:uppercase;">{label}</span><br>
                            <code>{dork}</code><br><br>
                            <a href="{url}" target="_blank"
                               style="color:#000;font-weight:bold;text-decoration:underline;background:#dfdfdf;padding:2px 6px;border:1px solid #000;">
                                ↗ Execute Search
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Dork Syntax Reference"):
        ref = {
            "site:":        "Restrict to a domain",
            "filetype:":    "Search specific file extensions",
            "inurl:":       "Keyword must appear in URL",
            "intitle:":     "Keyword must appear in page title",
            "intext:":      "Keyword must appear in body text",
            '\"exact\"':    "Exact phrase match",
            "OR":           "Boolean OR between terms",
            "-keyword":     "Exclude keyword from results",
        }
        for op, desc in ref.items():
            col1, col2 = st.columns([1, 3])
            col1.code(op)
            col2.markdown(f"<span style='font-weight:bold;'>{desc}</span>", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 6  — THREAT INTELLIGENCE (v1.1)
# ════════════════════════════════════════════
elif MODULE == "☢️  Threat Intelligence":
    st.markdown("<h1><span>Global Threat Intelligence</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Open Threat Exchange (OTX) Integration</p>", unsafe_allow_html=True)

    # Add a slider to control how many pulses to show (up to 50)
    num_pulses = st.slider("Pulse Display Limit:", 5, 50, 10)

    target = st.text_input("Enter Indicator (IP, Domain, or Hash):", placeholder="e.g. apple.com")
    
    if st.button("☣️ Query OTX Pulse Database"):
        if not target.strip():
            st.error("Missing indicator value.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                ind_type, otx_path = "IPv4", "IPv4"
            elif "@" in target:
                ind_type, otx_path = "Email", "email"
            else:
                ind_type, otx_path = "Domain", "domain"

            headers = {"X-OTX-API-KEY": CONFIG["OTX_KEY"]}
            url = f"https://otx.alienvault.com/api/v1/indicators/{otx_path}/{target.strip()}/general"
            
            with st.spinner("Accessing OTX Global Intelligence Feed..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=12.0)
                    data = r.json()
                    
                    section_header(f"Reputation Analysis: {target}")
                    
                    pulse_info = data.get('pulse_info', {})
                    total_pulses = pulse_info.get('count', 0)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("Indicator Type", ind_type)
                    with c2: st.metric("Active Pulses", total_pulses)
                    with c3: st.metric("Reputation", "MALICIOUS" if total_pulses > 0 else "CLEAN")

                    if total_pulses > 0:
                        st.warning(f"System Alert: Indicator identified in {total_pulses} community threat pulses.")
                        
                        # Use the slider value here to show more pulses
                        for pulse in pulse_info.get('pulses', [])[:num_pulses]:
                            pulse_name = pulse.get('name', 'Unnamed Pulse')
                            
                            with st.expander(f"📁 Pulse: {pulse_name}"):
                                # High-detail metadata extraction
                                author = pulse.get('author_name', 'Anonymous')
                                created = (pulse.get('created') or "N/A")[:10]
                                tags = pulse.get('tags', [])
                                
                                # ENRICHMENT: Show Indicators and References
                                indicators = pulse.get('indicators', [])
                                references = pulse.get('references', [])
                                
                                # Use Markdown with explicit colors to fix the "blank info" bug
                                st.markdown(f"**Author:** <span style='color:black;'>{author}</span>", unsafe_allow_html=True)
                                st.markdown(f"**Date:** <span style='color:black;'>{created}</span>", unsafe_allow_html=True)
                                st.markdown(f"**Tags:** <span style='color:black;'>{', '.join(tags) if tags else 'None'}</span>", unsafe_allow_html=True)
                                
                                st.markdown("---")
                                st.markdown("**Pulse Description:**")
                                st.info(pulse.get('description', 'No description available.'))
                                
                                if indicators:
                                    st.markdown(f"**Related Indicators ({len(indicators)} total):**")
                                    # List the first 5 IOCs in the pulse
                                    for ioc in indicators[:5]:
                                        st.code(f"[{ioc.get('type')}] {ioc.get('indicator')}", language=None)
                                
                                if references:
                                    st.markdown("**External References:**")
                                    for ref in references[:3]:
                                        st.markdown(f"- [{ref}]({ref})")
                    else:
                        st.success("No known malicious associations found in OTX database.")
                
                except Exception as e:
                    st.error(f"OTX Connectivity Error: {str(e)}")

# ════════════════════════════════════════════
#  MODULE 7  — MALWARE SANDBOX (VIRUSTOTAL)
# ════════════════════════════════════════════
elif MODULE == "👾  Malware Sandbox":
    st.markdown("<h1><span>VirusTotal Intelligence</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: VirusTotal v3</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Cross-references indicators against 70+ antivirus scanners and URL/domain blacklisting services.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    target = st.text_input("Enter Hash, Domain, or IP:", placeholder="e.g. 44d88612fea8a8f36de82e1278abb02f")

    if st.button("🔎 Scan Indicator"):
        if not target.strip():
            st.error("Please provide a target for the sandbox.")
        elif CONFIG["VT_KEY"] == "YOUR_VIRUSTOTAL_API_KEY":
            st.warning("SYSTEM ERROR: VirusTotal API Key missing in CONFIG.")
        else:
            # Determine type for VT API v3
            # Simple regex to check if it's an IP
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                vt_type = "ip_addresses"
            # Check if it looks like a domain (has a dot, no @)
            elif "." in target and "@" not in target:
                vt_type = "domains"
            # Otherwise treat as a hash
            else:
                vt_type = "files"

            url = f"https://www.virustotal.com/api/v3/{vt_type}/{target.strip()}"
            headers = {"x-apikey": CONFIG["VT_KEY"]}

            with st.spinner("Uploading to multi-engine sandbox..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=15.0)
                    if r.status_code == 200:
                        data = r.json()['data']['attributes']
                        stats = data.get('last_analysis_stats', {})
                        
                        section_header(f"Security Report: {target}")
                        
                        # Mac Metric Grid
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Malicious", stats.get('malicious', 0))
                        with c2: st.metric("Suspicious", stats.get('suspicious', 0))
                        with c3: st.metric("Harmless", stats.get('harmless', 0))
                        with c4: st.metric("Undetected", stats.get('undetected', 0))

                        # Detailed breakdown
                        col_left, col_right = st.columns(2)
                        with col_left:
                            card("Reputation Score", str(data.get('reputation', 0)))
                            card("Provider Tags", ", ".join(data.get('tags', [])) if data.get('tags') else "None")
                        
                        with col_right:
                            # For files/domains, VT often has a 'categories' or 'meaningful_name'
                            card("Primary Label", data.get('meaningful_name', data.get('type_description', 'N/A')))
                            card("Last DNS Records", str(len(data.get('last_dns_records', []))))

                        # Show the specific engines that flagged it
                        if stats.get('malicious', 0) > 0:
                            st.markdown("---")
                            st.markdown("**Engine Flags:**")
                            results = data.get('last_analysis_results', {})
                            for engine, res in results.items():
                                if res['category'] == 'malicious':
                                    st.error(f"🚩 {engine}: {res['result']}")
                    
                    elif r.status_code == 404:
                        st.info("Indicator not found in VirusTotal database. It may be clean or brand new.")
                    else:
                        st.error(f"VT API Error: {r.status_code}")
                
                except Exception as e:
                    st.error(f"Sandbox Connectivity Failed: {str(e)}")    

# ════════════════════════════════════════════
#  MODULE 8  — GITHUB SECRET SCANNER
# ════════════════════════════════════════════
elif MODULE == "🐙  GitHub Secret Scanner":
    st.markdown("<h1><span>GitHub Secret Scanner</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: GitHub API v3</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Hunts for sensitive strings (AWS Keys, Private Keys, .env files) leaked in public repositories.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    target_user = st.text_input("Enter GitHub Username/Org:", placeholder="e.g. apple or torvalds")
    
    # Common high-risk search queries
    DANGER_QUERIES = {
        "AWS Keys": "AKIA",
        "Private RSA Keys": "BEGIN RSA PRIVATE KEY",
        "Environment Files": "filename:.env",
        "GitHub Tokens": "ghp_",
        "Config w/ Passwords": "extension:config password"
    }

    if st.button("🚀 Execute Secret Hunt"):
        if not target_user.strip():
            st.error("Target username is required.")
        else:
            section_header(f"Scanning Repositories for: {target_user}")
            
            headers = {}
            if CONFIG["GITHUB_TOKEN"]:
                headers["Authorization"] = f"token {CONFIG['GITHUB_TOKEN']}"
            
            found_secrets = False
            
            with st.spinner(f"Analyzing {target_user}'s digital trail..."):
                # We check each danger query against the user
                for label, query in DANGER_QUERIES.items():
                    # GitHub Search API: q={query}+user:{target_user}
                    search_url = f"https://api.github.com/search/code?q={query}+user:{target_user}"
                    
                    try:
                        r = httpx.get(search_url, headers=headers, timeout=15.0)
                        
                        if r.status_code == 200:
                            data = r.json()
                            count = data.get('total_count', 0)
                            
                            if count > 0:
                                found_secrets = True
                                st.warning(f"⚠ {label} Detected: {count} potential leaks found.")
                                for item in data.get('items', [])[:3]: # Show top 3 matches
                                    repo_name = item['repository']['full_name']
                                    file_path = item['path']
                                    file_url = item['html_url']
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:#fff; border:2px solid #000; padding:8px; margin-bottom:5px; box-shadow:2px 2px 0px #000;">
                                            <span style="font-family:Monaco, monospace; font-size:0.8rem;">
                                                <b>Repo:</b> {repo_name}<br>
                                                <b>File:</b> {file_path}<br>
                                                <a href="{file_url}" target="_blank" style="color:#000; font-weight:bold;">[VIEW SOURCE ↗]</a>
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                        elif r.status_code == 403:
                            st.error("API Rate Limit Exceeded. Please wait or add a GITHUB_TOKEN to CONFIG.")
                            break
                        
                        # GitHub Search API is rate-limited to 10 requests/min unauthenticated
                        # So we add a small delay
                        time.sleep(2) 
                        
                    except Exception as e:
                        st.error(f"Search Failed for {label}: {str(e)}")

            if not found_secrets:
                st.success("Clean Scan: No obvious secrets detected in public repositories.")                    

# ════════════════════════════════════════════
#  MODULE 9 — IMAGE FORENSICS (EXIF v1.1)
# ════════════════════════════════════════════
elif MODULE == "🖼️  Image Forensics":
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS

    st.markdown("<h1><span>Image Forensics Explorer</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: EXIF + Reverse Geocoding</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Extracts metadata and pings Nominatim to convert raw GPS data into physical street addresses.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Drop Evidence Image (JPG/TIFF):", type=["jpg", "jpeg", "tiff"])

    def get_decimal_from_dms(dms, ref):
        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0
        val = float(degrees + minutes + seconds)
        return -val if ref in ['S', 'W'] else val

    async def get_human_address(lat, lon):
        # Nominatim Reverse Geocoding (Keyless)
        # Policy: Must provide User-Agent and respect 1req/sec
        headers = {"User-Agent": "GHOST-OSINT-App/1.1 (Cybersecurity-Research)"}
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                r = await client.get(url, timeout=10.0)
                if r.status_code == 200:
                    return r.json().get('display_name', 'Address not found')
                return f"API Error: HTTP {r.status_code}"
            except Exception as e:
                return f"Connection Error: {str(e)}"

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Evidence", use_container_width=True)
        
        exif_data = image._getexif()
        
        if not exif_data:
            st.error("SYSTEM ERROR: No EXIF metadata found. Image may have been scrubbed.")
        else:
            section_header("Metadata Analysis")
            clean_exif, gps_info = {}, {}
            
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    for t in value:
                        gps_info[GPSTAGS.get(t, t)] = value[t]
                else:
                    clean_exif[decoded] = value

            # --- MAIN DATA DISPLAY ---
            row1 = st.columns(3)
            with row1[0]: st.metric("Device", clean_exif.get('Model', 'Unknown'))
            with row1[1]: st.metric("Software", str(clean_exif.get('Software', '1.0')))
            with row1[2]: st.metric("Timestamp", str(clean_exif.get('DateTime', 'N/A'))[:10])

            # GPS Data Logic
            if gps_info and 'GPSLatitude' in gps_info:
                lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
                lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
                
                # Update row with coordinates
                row2 = st.columns(3)
                with row2[0]: st.metric("Latitude", f"{lat:.6f}")
                with row2[1]: st.metric("Longitude", f"{lon:.6f}")
                with row2[2]: st.metric("GPS Status", "LOCKED", delta_color="normal")

                # --- REVERSE GEOCODING API CALL ---
                with st.spinner("Decoding GPS into physical address..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    address = loop.run_until_complete(get_human_address(lat, lon))
                    loop.close()

                st.markdown(f"""
                    <div style="background:#39ff1411; border:2px solid #39ff14; padding:15px; border-radius:4px; margin-top:10px;">
                        <b style="color:#000;">📍 DETECTED ADDRESS:</b><br>
                        <span style="font-family:Monaco, monospace; color:#000;">{address}</span>
                    </div>
                """, unsafe_allow_html=True)

                maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; margin-top:10px; padding:10px; background:#fff; border:2px solid #000; font-weight:bold; cursor:pointer; box-shadow:3px 3px 0px #000;">🛰️ VIEW SATELLITE IMAGERY</button></a>', unsafe_allow_html=True)
            else:
                st.info("No GPS coordinates detected for this asset.")

            with st.expander("📁 View Raw Metadata Dump"):
                for k, v in clean_exif.items():
                    st.write(f"**{k}:** {v}")

# ════════════════════════════════════════════
#  MODULE 10 — FINANCIAL INTELLIGENCE (INDIA)
# ════════════════════════════════════════════
elif MODULE == "💸  Financial Intelligence":
    st.markdown("<h1><span>Financial Reconnaissance</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: Indian Fin-Tech OSINT</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Validates IFSC routing codes and analyzes UPI Virtual Payment Addresses (VPA) to identify underlying banking partners.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["🏦 IFSC Branch Trace", "💳 UPI Handle Analysis"])

    # --- TAB 1: IFSC LOOKUP ---
    with tab1:
        ifsc_input = st.text_input("Enter IFSC Code:", placeholder="e.g. HDFC0000007")
        
        if st.button("🔎 Trace Branch"):
            if len(ifsc_input) != 11:
                st.error("INVALID FORMAT: IFSC must be exactly 11 characters.")
            else:
                with st.spinner("Accessing RBI Routing Tables..."):
                    try:
                        r = httpx.get(f"https://ifsc.razorpay.com/{ifsc_input.strip()}", timeout=10.0)
                        if r.status_code == 200:
                            data = r.json()
                            section_header(f"Branch Details: {data.get('BANK')}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                card("Bank Name", data.get('BANK'))
                                card("Branch",    data.get('BRANCH'))
                                card("IFSC",      data.get('IFSC'))
                            with c2:
                                card("City",      data.get('CITY'))
                                card("District",  data.get('DISTRICT'))
                                card("State",     data.get('STATE'))
                            
                            st.info(f"📍 Address: {data.get('ADDRESS')}")
                            
                            # Deep Link to Map
                            addr_query = f"{data.get('BANK')} {data.get('BRANCH')} {data.get('CITY')}"
                            maps_url = f"https://www.google.com/maps/search/{addr_query.replace(' ', '+')}"
                            st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; padding:10px; background:#fff; border:2px solid #000; font-weight:bold; cursor:pointer; box-shadow:3px 3px 0px #000;">🗺️ LOCATE ON MAP</button></a>', unsafe_allow_html=True)
                        else:
                            st.error(f"IFSC NOT FOUND: Ensure the code is correct (Status {r.status_code}).")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")

    # --- TAB 2: UPI ANALYSIS ---
    with tab2:
        vpa_input = st.text_input("Enter UPI ID (VPA):", placeholder="username@bank")
        
        # OSINT Mapping of Suffixes
        UPI_HANDLES = {
            "okicici": "ICICI Bank", "okaxis": "Axis Bank", "oksbi": "State Bank of India",
            "okhdfcbank": "HDFC Bank", "ybl": "Yes Bank", "ibl": "ICICI Bank (PhonePe)",
            "axl": "Axis Bank (PhonePe)", "paytm": "Paytm Payments Bank",
            "upl": "Union Bank", "postbank": "India Post Payments Bank"
        }

        if st.button("🧪 Analyze VPA"):
            if "@" not in vpa_input:
                st.error("INVALID FORMAT: UPI ID must contain an '@' symbol.")
            else:
                handle = vpa_input.split("@")[-1].lower()
                bank_partner = UPI_HANDLES.get(handle, "Unknown/Custom Provider")
                
                section_header(f"Analysis: {vpa_input}")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("Provider", bank_partner)
                with c2: st.metric("Format Status", "VALID" if len(vpa_input) > 3 else "INVALID")
                
                st.markdown(
                    """
                    <div style="background:#f0f0f0; border:1px dashed #000; padding:10px; margin-top:10px;">
                        <b>OSINT Note:</b> In India, the handle (suffix) reveals the processing bank. 
                        To verify the <b>Legal Name</b>, scan the QR below with a banking app.
                    </div>
                    """, unsafe_allow_html=True
                )
                
                # Generate a UPI Deep Link QR for Verification
                upi_link = f"upi://pay?pa={vpa_input}&pn=GHOST_RECON&cu=INR"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={upi_link}"
                
                st.image(qr_url, caption="Scan to verify Legal Name in app")

# ════════════════════════════════════════════
#  MODULE 11 — DATA BREACH SEARCH (RAPID-API)
# ════════════════════════════════════════════
elif MODULE == "🔐  Data Breach Search":
    st.markdown("<h1><span>Breach Compilation Search</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: BreachDirectory v1.0</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Queries the RapidAPI BreachDirectory engine. Uses 'Auto-Detect' mode to find compromised assets. 
                (Fixed: URL Path and Redirect Following).
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    query_input = st.text_input("Enter Email or Username:", placeholder="e.g. target@example.com")
    
    if st.button("🔓 Execute Breach Hunt"):
        target = query_input.strip()
        if not target:
            st.error("Input is required.")
        else:
            # ── DATA FROM YOUR SCREENSHOT ──
            # Fix: Removed the trailing slash to prevent double-slash errors
            api_url = "https://breachdirectory.p.rapidapi.com" 
            api_key = "591a17a2cemsh80a79611e6132c2p100379jsnf0065f1d3d92"
            
            headers = {
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GHOST/1.2"
            }
            
            # Using the exact params from the RapidAPI snippet
            query_params = {"func": "auto", "term": target}

            with st.spinner("Decoding dark-web archives..."):
                try:
                    # Creating a client to handle redirects more robustly
                    with httpx.Client(follow_redirects=True, timeout=25.0) as client:
                        r = client.get(api_url, headers=headers, params=query_params)
                    
                    if r.status_code == 200:
                        data = r.json()
                        
                        # Process results
                        if data.get('success') or 'result' in data:
                            results = data.get('result', [])
                            total_found = len(results)
                            
                            section_header(f"Exposure Report: {target}")
                            
                            c1, c2 = st.columns(2)
                            with c1: st.metric("Total Breaches", total_found)
                            with c2: st.metric("Risk Level", "CRITICAL" if total_found > 3 else "LOW")

                            if total_found > 0:
                                st.error(f"⚠ COMPROMISE DETECTED: {total_found} instances found.")
                                for breach in results:
                                    sources = breach.get('sources', [])
                                    source_name = ", ".join(sources) if isinstance(sources, list) else str(sources)
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:#fff; border:2px solid #000; padding:10px; margin-bottom:8px; box-shadow:2px 2px 0px #000;">
                                            <b style="font-family:'Chicago', sans-serif;">📂 SOURCE: {source_name}</b><br>
                                            <span style="font-family:'Monaco', monospace; font-size:0.8rem;">
                                                <b>Password Leaked:</b> {"✅ YES" if breach.get('has_password') else "❌ NO"}<br>
                                                <b>Hash Type:</b> {breach.get('hash_type', 'N/A')}
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                            else:
                                st.success("Clear Scan: No exposure found in this database.")
                        else:
                            st.info(data.get('message', "No records found for this identifier."))
                    
                    else:
                        st.error(f"System Error: HTTP {r.status_code}")
                        if r.status_code == 307:
                            st.info("The server is still redirecting. Please check if your RapidAPI endpoint URL has changed.")
                
                except Exception as e:
                    st.error(f"Search Failed: {str(e)}")
"""
╔══════════════════════════════════════════════════════════════╗
║         G.H.O.S.T  //  OSINT Reconnaissance Dashboard       ║
║         Retro Macintosh System 7 Edition                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import asyncio
import httpx
import dns.resolver
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import re
import socket
import time
from datetime import datetime
import urllib.parse
import platform

# ─────────────────────────────────────────────
#  SYSTEM MEMORY  
# ─────────────────────────────────────────────

if 'pivot_email' not in st.session_state:
    st.session_state.pivot_email = ""

# ─────────────────────────────────────────────
#  SYSTEM CONFIGURATION (API KEYS)
# ─────────────────────────────────────────────
CONFIG = {
    "OTX_KEY": "cec0f6c86ef2ee22f1ab3a3734cacd8c2e96846622cf808ef4c07a2f712e25d9", ## REPLACE WITH YOUR OTX KEY                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    "OPENCTI_URL": "http://localhost:8080", 
    "VT_KEY": "70f961af90b0a23b61b4d22fa1223b64694304a105925e25e61b3b22ecc23e22", ## REPLACE WITH YOUR VIRUSTOTAL KEY
    "BREACH_KEY": "591a17a2cemsh80a79611e6132c2p100379jsnf0065f1d3d92", ## REPLACE WITH YOUR BREACH KEY
    "GITHUB_TOKEN": "", ## REPLACE WITH YOUR GITHUB TOKEN (optional, for higher rate limits)
    "OPENCTI_TOKEN": "9d29da5c-d768-4f22-b765-b891e53b8313" ## REPLACE WITH YOUR OPENCTI TOKEN IF NEEDED
}

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GHOST // OSINT",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — RETRO MACINTOSH THEME
# ─────────────────────────────────────────────
MAC_CSS = """
<style>
/* ── Import Retro Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

/* ── Root Palette ── */
:root {
    --black:        #000000;
    --white:        #ffffff;
    --gray:         #aaaaaa;
    --light-gray:   #dfdfdf;
    --font-sys:     'Geneva', 'Tahoma', 'Verdana', sans-serif;
    --font-mono:    'Monaco', 'Courier New', Courier, monospace;
    --font-title:   'VT323', 'Chicago', sans-serif;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-sys) !important;
    color: var(--black) !important;
}

/* ── Classic Mac Dithered Desktop Background ── */
.stApp {
    background-color: var(--white) !important;
    background-image:
      linear-gradient(45deg, var(--gray) 25%, transparent 25%),
      linear-gradient(-45deg, var(--gray) 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, var(--gray) 75%),
      linear-gradient(-45deg, transparent 75%, var(--gray) 75%) !important;
    background-size: 4px 4px !important;
    background-position: 0 0, 0 2px, 2px -2px, -2px 0px !important;
}

/* ── Classic Mac Title Bar ── */
.mac-window-header {
    background: repeating-linear-gradient(
        0deg,
        #000,
        #000 1px,
        #fff 1px,
        #fff 3px
    );
    border: 2px solid #000;
    height: 28px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    margin-bottom: -2px;
    position: relative;
    z-index: 10;
}


.mac-title-text {
    background: #fff;
    padding: 0 15px;
    /* This centers the text even with buttons on the left */
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'VT323', sans-serif;
    font-size: 1.2rem;
    border: 2px solid #000;
    text-transform: uppercase;
    white-space: nowrap;
}

/* ── The Buttons ── */
/* ── The Buttons (Colored Edition) ── */
.mac-btn {
    width: 14px;
    height: 14px;
    border: 1px solid rgba(0, 0, 0, 0.2); /* Subtle border like modern Mac */
    border-radius: 50%; /* Modern circular buttons */
    cursor: pointer;
    margin-right: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: bold;
    color: transparent; /* Hide icons until hover */
    transition: all 0.2s ease;
    box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.3);
}

/* Reveal icons on hover - very Mac-like */
.mac-window-header:hover .mac-btn {
    color: rgba(0, 0, 0, 0.6);
}

.mac-close { background-color: #FF605C; border-color: #E0443E; }
.mac-min   { background-color: #FFBD44; border-color: #DEA123; }
.mac-max   { background-color: #00CA4E; border-color: #14B047; }

.mac-btn:active {
    filter: brightness(0.8);
    transform: translateY(1px);
}

/* Icons inside the colored circles */
.mac-close::after { content: '×'; margin-top: -1px; }
.mac-min::after   { content: '−'; }
.mac-max::after   { content: '+'; }

/* Adding the Icons */
.mac-close::after { content: '×'; }
.mac-min::after   { content: '_'; }
.mac-max::after   { content: '□'; }

/* ── Custom System 7 Dialog Box ── */
#mac-modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(255, 255, 255, 0.4); /* Glass effect */
    z-index: 1000;
}

.mac-dialog {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: #fff;
    border: 1px solid #000;
    outline: 2px solid #fff;
    box-shadow: 4px 4px 0px #000; /* Dithered shadow vibe */
    width: 350px;
    padding: 20px;
    text-align: center;
    border: 3px double #000; /* Classic double border */
}

.mac-dialog-title {
    font-family: 'Chicago', 'Geneva', sans-serif;
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 15px;
    text-transform: uppercase;
    display: block;
}

.mac-dialog-text {
    font-family: 'Monaco', monospace;
    font-size: 0.9rem;
    margin-bottom: 20px;
    display: block;
}

.mac-dialog-ok {
    background: #fff;
    border: 2px solid #000;
    padding: 5px 25px;
    font-family: 'Chicago', sans-serif;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 2px 2px 0px #000;
}

.mac-dialog-ok:active {
    background: #000;
    color: #fff;
    box-shadow: none;
    transform: translate(1px, 1px);
}

/* ── Wrap main content to look like a Mac Window ── */
.block-container {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    box-shadow: 4px 4px 0px var(--black) !important;
    padding: 2rem 3rem !important;
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--white) !important;
    border-right: 2px solid var(--black) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-sys) !important; }

/* ── Sidebar radio buttons ── */
[data-testid="stSidebar"] .stRadio label {
    color: var(--black) !important;
    font-size: 0.9rem !important;
    font-weight: bold;
}

/* ── Headers ── */
h1, h2, h3, h4 {
    font-family: var(--font-title) !important;
    color: var(--black) !important;
    text-transform: uppercase;
}
h1 { font-size: 2.2rem !important; border-bottom: 4px double var(--black); padding-bottom: 5px; }
h2 { font-size: 1.5rem !important; }

/* ── Text inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-radius: 0px !important;
    color: var(--black) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.9rem !important;
    box-shadow: 2px 2px 0px var(--light-gray) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--black) !important;
    font-weight: bold !important;
    font-family: var(--font-sys) !important;
}

/* ── Buttons ── */
.stButton button {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    color: var(--black) !important;
    font-family: var(--font-title) !important;
    font-size: 1.2rem !important;
    text-transform: uppercase;
    border-radius: 0px !important;
    padding: 0.4rem 1.2rem !important;
    box-shadow: 3px 3px 0px var(--black) !important;
    transition: none !important;
}
.stButton button:hover, .stButton button:active {
    background-color: var(--black) !important;
    color: var(--white) !important;
    box-shadow: 1px 1px 0px var(--black) !important;
    transform: translate(2px, 2px);
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: var(--black) !important;
}
.stProgress > div > div {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-radius: 0px !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: var(--light-gray) !important;
    border: 2px solid var(--black) !important;
    color: var(--black) !important;
    font-family: var(--font-sys) !important;
    font-weight: bold !important;
    border-radius: 0px !important;
}
.streamlit-expanderContent {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-top: none !important;
}

/* ── Dividers ── */
hr { border-color: var(--black) !important; border-width: 2px !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background-color: var(--white) !important;
    border: 2px solid var(--black) !important;
    border-radius: 0px !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 2px 2px 0px var(--black) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--black) !important;
    font-size: 0.8rem !important;
    font-weight: bold !important;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: var(--black) !important;
    font-family: var(--font-title) !important;
    font-size: 1.8rem !important;
}

/* ── Code blocks ── */
.stCodeBlock, code, pre {
    background-color: var(--light-gray) !important;
    border: 2px solid var(--black) !important;
    color: var(--black) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
    border-radius: 0px !important;
}

/* ── Success / warning / error ── */
.stSuccess, .stWarning, .stError, .stInfo { 
    background-color: var(--white) !important; 
    border: 2px solid var(--black) !important; 
    color: var(--black) !important;
    box-shadow: 3px 3px 0px var(--black) !important;
    border-radius: 0px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 12px; }
::-webkit-scrollbar-track { background: var(--white); border-left: 2px solid var(--black); }
::-webkit-scrollbar-thumb { background: var(--light-gray); border: 2px solid var(--black); }
</style>
"""

st.markdown(MAC_CSS, unsafe_allow_html=True)
# ─────────────────────────────────────────────
#  GLOBAL UI COMPONENTS (Modal & Title Bar)
# ─────────────────────────────────────────────

# ── MODAL COMPONENT & LOGIC ──
# We place this here so the JavaScript is available to all modules
st.markdown(
    """
    <div id="mac-modal-overlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(255,255,255,0.4); z-index:9999;">
        <div class="mac-dialog" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); background:#fff; border:3px double #000; box-shadow:4px 4px 0px #000; width:350px; padding:20px; text-align:center;">
            <span class="mac-dialog-title" id="modal-title" style="font-family:'Chicago', sans-serif; font-weight:bold; display:block; margin-bottom:15px; text-transform:uppercase;">System Advisory</span>
            <span class="mac-dialog-text" id="modal-msg" style="font-family:'Monaco', monospace; font-size:0.9rem; display:block; margin-bottom:20px;">Error details go here.</span>
            <button class="mac-dialog-ok" onclick="closeMacModal()" style="background:#fff; border:2px solid #000; padding:5px 25px; font-family:'Chicago', sans-serif; font-weight:bold; cursor:pointer; box-shadow:2px 2px 0px #000;">OK</button>
        </div>
    </div>

    <script>
        function showMacModal(title, msg) {
            const overlay = document.getElementById('mac-modal-overlay');
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-msg').innerText = msg;
            overlay.style.display = 'block';
        }

        function closeMacModal() {
            document.getElementById('mac-modal-overlay').style.display = 'none';
        }
    </script>
    """,
    unsafe_allow_html=True
)

# ── WINDOW HEADER ──
# This puts the colored buttons and title at the top of every module
st.markdown(
    """
    <div class="mac-window-header">
        <div class="mac-btn mac-close" onclick="showMacModal('FATAL ERROR', 'The G.H.O.S.T. exit is encrypted. Your session is now infinite. Coffee-flavored ice cream is recommended for the long haul.')"></div>
        <div class="mac-btn mac-min" onclick="showMacModal('SYSTEM ADVISORY', 'G.H.O.S.T. has been minimized into your subconscious. Proceed to the gym for leg day to recalibrate your physical shell.')"></div>
        <div class="mac-btn mac-max" onclick="showMacModal('RESOURCE ERROR', 'Reality.exe is already at 100% capacity. Your Ryzen 7 is providing too much power for the local Maharashtra power grid.')"></div>
        <div class="mac-title-text">G.H.O.S.T. Explorer v1.2</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ─────────────────────────────────────────────
#  HELPER: render a styled "card" block
# ─────────────────────────────────────────────
def card(title: str, content: str):
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:2px solid #000000;
            box-shadow:2px 2px 0px #000000;
            padding:0.75rem 1rem;
            margin-bottom:0.8rem;
            font-family:'Monaco', 'Courier New', monospace;
            color:#000000;
        ">
            <span style="font-weight:bold;text-transform:uppercase;border-bottom:1px solid #000;">{title}</span><br>
            <span style="font-size:0.9rem;display:block;margin-top:4px;">{content}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def badge(label: str, value: str, ok: bool = True):
    bg = "#ffffff" if ok else "#000000"
    fg = "#000000" if ok else "#ffffff"
    icon = "✓" if ok else "✗"
    st.markdown(
        f"""
        <div style="display:inline-block;margin:3px 4px;">
            <span style="
                background:{bg};
                border:2px solid #000000;
                color:{fg};
                padding:4px 8px;
                font-size:0.85rem;
                font-weight:bold;
                font-family:'Geneva', 'Tahoma', sans-serif;
            ">{icon} {label}: {value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(text: str):
    st.markdown(
        f"""
        <div style="
            background:#000000;
            color:#ffffff;
            padding:4px 8px;
            margin:1.5rem 0 1rem 0;
            display:inline-block;
            font-family:'VT323', 'Chicago', sans-serif;
            font-size:1.2rem;
            text-transform:uppercase;
            border:2px solid #000000;
        ">
            {text}
        </div>
        <div style="height:2px; background:#000; width:100%; margin-top:-1.2rem; margin-bottom:1.5rem; z-index:-1; position:relative;"></div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  SIDEBAR — NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0 0.5rem 0; color:#000;">
            <div style="font-size:3rem; margin-bottom: 10px;">💾</div>
            <div style="
                font-family:'VT323', 'Chicago', sans-serif;
                font-size:2rem;
                text-transform:uppercase;
                line-height:1;
            ">G.H.O.S.T</div>
            <div style="
                font-size:1rem;
                font-weight:bold;
                margin-top:5px;
            ">System 7 Reconnaissance</div>
            <div style="
                font-size:0.6rem;
                font-weight:bold;
                margin-top:5px;
            ">PLEASE SET SYSTEM THEME TO LIGHT MODE </div>
        </div>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    MODULE = st.radio(
        "Select Application:",
        [
            "🏠  Control Panel",
            "👤  Username Search",
            "🌐  Network Utility & Recon",
            "📞  Phone Intelligence",
            "📧  Email Discovery",
            "🔐  Data Breach Search",
            "🔍  Google Dorking",
            "☢️  Threat Intelligence",
            "👾  Malware Sandbox",
            "🐙  GitHub Secret Scanner",
            "🖼️  Image Forensics",
            "💸  Financial Intelligence"
        ],
        label_visibility="visible",
    )

    st.markdown(
        """
        <hr>
        <div style="
            color:#000;
            font-size:0.7rem;
            text-align:center;
            font-weight:bold;
            padding-top:0.5rem;
            border: 2px solid #000;
            padding: 5px;
            background: #dfdfdf;
        ">
            AUTHORIZED USE ONLY.<br>
            Respect local laws.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════
#  MODULE 0 — OSINT CONTROL PANEL (v1.3)
# ════════════════════════════════════════════
if MODULE == "🏠  Control Panel":
    st.markdown("<h1>OSINT Control Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Open-Source Intelligence Framework | Macintosh Edition v1.3</p>", unsafe_allow_html=True)
    
    # Row 1: Primary System Metrics
    row1_cols = st.columns(4)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sys_info = platform.system() + " " + platform.release()
    with row1_cols[0]: st.metric("System Status", "ONLINE")
    with row1_cols[1]: st.metric("Active Modules", "11") 
    with row1_cols[2]: st.metric("System Time", now)
    with row1_cols[3]: st.metric("Host OS", sys_info)

    # Row 2: Hardware & API Integration Status
    row2_cols = st.columns(3)
    # Check status of the major APIs
    vt_status = "OK" if CONFIG.get("VT_KEY") != "YOUR_VIRUSTOTAL_API_KEY" else "MISSING"
    rapid_status = "OK" if "591a" in CONFIG.get("BREACH_KEY", "") else "OFFLINE"
    
    with row2_cols[0]: st.metric("API Handshake", f"VT:{vt_status} | BD:{rapid_status}")
    with row2_cols[1]: st.metric("Host RAM", " OK")
    with row2_cols[2]: st.metric("Processor", " SUFFICIENT")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── COMPLETE SYSTEM APPLICATION REGISTRY ──
    st.markdown(
        """
        <div style="background:#ffffff; border:2px solid #000; box-shadow:4px 4px 0px #000; padding:1.2rem 1.5rem;">
            <div style="font-family:'Chicago', sans-serif; font-size:1.5rem; border-bottom:2px solid #000; margin-bottom:10px;">
                System Application Registry
            </div>
            <table style="width:100%; font-size:0.8rem; border-collapse:collapse; font-family:'Monaco', monospace;">
                <tr style="border-bottom:2px solid #000; background:#dfdfdf;">
                    <th style="text-align:left; padding:8px;">Application</th>
                    <th style="text-align:left; padding:8px;">Forensic Technique</th>
                    <th style="text-align:left; padding:8px;">Primary Provider</th>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Username Search</td><td>HTTP Probing (Async)</td><td>Sherlock DB</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Network Utility</td><td>GeoIP + DNS Resolver</td><td>ip-api.com</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Phone Intel</td><td>Local Metadata Extraction</td><td>Libphonenumber</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Email Discovery</td><td>MX/SPF DNS Lookup</td><td>Public DNS</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Data Breach</td><td>Identity Leak Correlation</td><td>BreachDirectory</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Google Dorking</td><td>Query Generation</td><td>Google Dork Engine</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Threat Intel</td><td>Reputation Analysis</td><td>AlienVault OTX</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Malware Sandbox</td><td>Multi-Engine Scan (v3)</td><td>VirusTotal</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Secret Scanner</td><td>Recursive String Hunt</td><td>GitHub API</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf; background:#f9f9f9;">
                    <td> Image Forensics</td><td>EXIF + Rev. Geocoding</td><td>Pillow / Nominatim</td>
                </tr>
                <tr style="border-bottom:1px solid #dfdfdf;">
                    <td> Financial Intel</td><td>Routing & UPI Validation</td><td>Razorpay / VPA</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Select an application from the **sidebar** to begin. Operations run locally or via free APIs.")


# ════════════════════════════════════════════
#  MODULE 1  — USERNAME SEARCH
# ════════════════════════════════════════════
elif MODULE == "👤  Username Search":

    # ── Sherlock-inspired platform list ──
    PLATFORMS = {
        "GitHub":        ("https://github.com/{u}",             "Not Found"),
        "GitLab":        ("https://gitlab.com/{u}",             "404"),
        "Twitter/X":     ("https://x.com/{u}",                  "This account"),
        "Reddit":        ("https://www.reddit.com/user/{u}",    "page not found"),
        "Instagram":     ("https://www.instagram.com/{u}/",     "Sorry"),
        "TikTok":        ("https://www.tiktok.com/@{u}",        "couldn't find"),
        "Pinterest":     ("https://www.pinterest.com/{u}/",     "404"),
        "Twitch":        ("https://www.twitch.tv/{u}",          "404"),
        "YouTube":       ("https://www.youtube.com/@{u}",       "404"),
        "SoundCloud":    ("https://soundcloud.com/{u}",         "404"),
        "Dev.to":        ("https://dev.to/{u}",                 "404"),
        "Keybase":       ("https://keybase.io/{u}",             "Not Found"),
        "Pastebin":      ("https://pastebin.com/u/{u}",         "Not Found"),
        "HackerNews":    ("https://news.ycombinator.com/user?id={u}", "No such user"),
        "ProductHunt":   ("https://www.producthunt.com/@{u}",  "404"),
        "Kaggle":        ("https://www.kaggle.com/{u}",         "404"),
        "Replit":        ("https://replit.com/@{u}",            "404"),
        "Medium":        ("https://medium.com/@{u}",            "404"),
        "Substack":      ("https://{u}.substack.com",           "404"),
        "Steam":         ("https://steamcommunity.com/id/{u}",  "The specified profile"),
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    async def check_platform(client: httpx.AsyncClient, name: str, url: str, not_found_text: str):
        try:
            r = await client.get(url, timeout=8.0, follow_redirects=True, headers=HEADERS)
            if r.status_code == 200 and not_found_text.lower() not in r.text.lower():
                return name, url, True
            return name, url, False
        except Exception:
            return name, url, False

    async def run_username_scan(username: str):
        results = []
        async with httpx.AsyncClient(http2=True) as client:
            tasks = []
            for name, (url_tpl, nf) in PLATFORMS.items():
                url = url_tpl.replace("{u}", username)
                tasks.append(check_platform(client, name, url, nf))
            results = await asyncio.gather(*tasks)
        return results

    # ── UI ──
    st.markdown("<h1>Username Search</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Async probe across 20 platforms. Inspired by the Sherlock Project.</p>", unsafe_allow_html=True)

    username = st.text_input("Target Username:", placeholder="e.g. johndoe")

    if st.button("Execute Scan"):
        if not username.strip():
            st.error("Error: Please enter a valid username.")
        else:
            progress_bar = st.progress(0, text="Initialising scan…")
            status_text  = st.empty()
            t0 = time.perf_counter()

            status_text.markdown(f"<b>Scanning username: {username}</b>", unsafe_allow_html=True)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(run_username_scan(username))
            loop.close()

            elapsed = time.perf_counter() - t0
            progress_bar.progress(1.0, text="Scan complete.")

            found = [r for r in results if r[2]]
            not_found = [r for r in results if not r[2]]

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Targets Scanned", len(PLATFORMS))
            with c2: st.metric("Matches Found", len(found))
            with c3: st.metric("Elapsed Time", f"{elapsed:.2f}s")

            section_header("Results — Found")
            if found:
                for name, url, _ in found:
                    st.markdown(
                        f"""
                        <div style="
                            background:#ffffff;border:2px solid #000;
                            box-shadow:2px 2px 0px #000;
                            padding:8px 12px;margin-bottom:8px;
                            font-family:'Monaco', monospace; font-weight:bold;
                        ">
                            <span>✓ {name}</span>
                            <a href="{url}" target="_blank"
                               style="float:right;color:#000;text-decoration:underline;">
                                {url} ↗
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.warning("No profiles detected.")

            with st.expander("Show Missing / Not Found"):
                for name, url, _ in not_found:
                    st.markdown(f"✗ {name}", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 2 — NETWORK UTILITY (OG EDITION)
# ════════════════════════════════════════════
elif MODULE == "🌐  Network Utility & Recon":

    async def fetch_ip_geo(target: str) -> dict:
        url = f"http://ip-api.com/json/{target}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=8.0)
            return r.json()

    def resolve_dns(domain: str) -> dict:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype, lifetime=5.0)
                results[rtype] = [str(r) for r in answers]
            except Exception:
                results[rtype] = []
        return results

    def resolve_ptr(ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "N/A"

    # ── UI RENDERING ──
    st.markdown("<h1>Network Utility</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Geolocation via ip-api.com  · DNS records via dnspython</p>", unsafe_allow_html=True)

    target = st.text_input("Enter Hostname or IP Address:", placeholder="e.g. 8.8.8.8")

    col_a, col_b = st.columns(2)
    run_ip  = col_a.button("🌍 GEOLOCATE IP")
    run_dns = col_b.button("🔎 RESOLVE DNS")

    if run_ip and target.strip():
        with st.spinner("Querying ip-api.com…"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            geo = loop.run_until_complete(fetch_ip_geo(target.strip()))
            loop.close()

        if geo.get("status") == "success":
            section_header("Geolocation Data")
            c1, c2, c3 = st.columns(3)
            c1.metric("IP / Query", geo.get("query", "—"))
            c2.metric("Country", geo.get("country", "—"))
            c3.metric("City", geo.get("city", "—"))

            card("Continent",   geo.get("continent",   "—"))
            card("Region",      geo.get("regionName",  "—"))
            card("ZIP Code",    geo.get("zip",         "—"))
            card("Timezone",    geo.get("timezone",    "—"))
            card("ISP",         geo.get("isp",         "—"))
            card("Organisation",geo.get("org",         "—"))
            card("AS Number",   geo.get("as",          "—"))
            card("Coordinates", f"Lat {geo.get('lat','—')} / Lon {geo.get('lon','—')}")

            ptr = resolve_ptr(geo.get("query", target.strip()))
            card("Reverse DNS (PTR)", ptr)

            # --- OTX REPUTATION AUTO-CHECK ---
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Security Reputation (OTX)")
            otx_headers = {"X-OTX-API-KEY": CONFIG["OTX_KEY"]}
            otx_url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{target.strip()}/general"
            
            try:
                otx_r = httpx.get(otx_url, headers=otx_headers, timeout=5.0)
                otx_data = otx_r.json()
                pulses = otx_data.get('pulse_info', {}).get('count', 0)
                badge("Threat Pulses", str(pulses), ok=(pulses == 0))
                if pulses > 0:
                    st.error(f"⚠ Caution: This IP is associated with {pulses} known threat pulses.")
            except:
                st.warning("Could not reach OTX for reputation check.")
        else:
            st.error(f"ip-api.com returned: {geo.get('message','Unknown error')}")

    if run_dns and target.strip():
        domain = re.sub(r"^https?://", "", target.strip()).split("/")[0]
        with st.spinner(f"Resolving DNS for {domain}…"):
            records = resolve_dns(domain)

        section_header("DNS Record Set")
        for rtype, values in records.items():
            if values:
                with st.expander(f"Type {rtype} Records ({len(values)})"):
                    for v in values:
                        st.code(v, language=None)
            else:
                st.markdown(f"<span style='font-family:Monaco,monospace;color:#555;'>No {rtype} records found.</span>", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 3  — PHONE INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "📞  Phone Intelligence":

    def analyse_phone(raw: str) -> dict:
        try:
            parsed = phonenumbers.parse(raw, None)
            valid   = phonenumbers.is_valid_number(parsed)
            possible= phonenumbers.is_possible_number(parsed)
            region  = geocoder.description_for_number(parsed, "en")
            carr    = carrier.name_for_number(parsed, "en")
            tzones  = list(timezone.time_zones_for_number(parsed))
            fmt_e164= phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            fmt_intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            fmt_natl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            ntype_raw = phonenumbers.number_type(parsed)
            number_type_map = {
                0: "FIXED_LINE", 1: "MOBILE", 2: "FIXED_OR_MOBILE",
                3: "TOLL_FREE", 4: "PREMIUM_RATE", 6: "VOIP",
                7: "PERSONAL_NUMBER", 99: "UNKNOWN",
            }
            ntype = number_type_map.get(ntype_raw, "UNKNOWN")
            return {
                "valid": valid, "possible": possible,
                "region": region or "Unknown",
                "carrier": carr or "Unknown",
                "timezones": tzones,
                "country_code": parsed.country_code,
                "national_number": parsed.national_number,
                "e164": fmt_e164, "intl": fmt_intl, "national": fmt_natl,
                "number_type": ntype,
                "error": None,
            }
        except Exception as e:
            return {"error": str(e)}

    # ── UI ──
    st.markdown("<h1>Phone Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Offline metadata extraction via phonenumbers lib.</p>", unsafe_allow_html=True)

    st.info("Note: Include country code prefix (e.g. +1 415 555 0100)")
    phone_raw = st.text_input("Target Phone Number:", placeholder="+1 415 555 0100")

    if st.button("Analyse Number"):
        if not phone_raw.strip():
            st.error("Error: Please enter a phone number.")
        else:
            result = analyse_phone(phone_raw.strip())
            if result.get("error"):
                st.error(f"Parse error: {result['error']}")
            else:
                section_header("Number Metadata")

                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Valid", "YES" if result["valid"] else "NO")
                with c2: st.metric("Type", result["number_type"])
                with c3: st.metric("Country Code", f"+{result['country_code']}")

                card("Region / Country",   result["region"])
                card("Carrier / Operator", result["carrier"])
                card("E.164 Format",       result["e164"])
                card("International",      result["intl"])
                card("National",           result["national"])
                card("Timezones", ", ".join(result["timezones"]) if result["timezones"] else "Unknown")

                section_header("System Flags")
                badge("Is Valid",    str(result["valid"]),    result["valid"])
                badge("Is Possible", str(result["possible"]), result["possible"])


# ════════════════════════════════════════════
#  MODULE 4  — EMAIL DISCOVERY
# ════════════════════════════════════════════
elif MODULE == "📧  Email Discovery":

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    )

    DISPOSABLE_DOMAINS = {
        "mailinator.com", "guerrillamail.com", "tempmail.com",
        "throwam.com", "sharklasers.com", "trashmail.com",
        "yopmail.com", "getairmail.com", "fakeinbox.com",
        "dispostable.com", "spam4.me", "maildrop.cc",
    }

    def check_email(email: str) -> dict:
        valid_fmt = bool(EMAIL_REGEX.match(email))
        if not valid_fmt:
            return {"valid_format": False}

        domain = email.split("@")[1].lower()
        disposable = domain in DISPOSABLE_DOMAINS

        mx_records = []
        mx_ok = False
        try:
            answers = dns.resolver.resolve(domain, "MX", lifetime=6.0)
            mx_records = sorted(
                [(r.preference, str(r.exchange)) for r in answers],
                key=lambda x: x[0],
            )
            mx_ok = True
        except Exception:
            pass

        a_records = []
        try:
            answers = dns.resolver.resolve(domain, "A", lifetime=6.0)
            a_records = [str(r) for r in answers]
        except Exception:
            pass

        spf = None
        try:
            answers = dns.resolver.resolve(domain, "TXT", lifetime=6.0)
            for r in answers:
                txt = str(r).strip('"')
                if txt.startswith("v=spf1"):
                    spf = txt
                    break
        except Exception:
            pass

        return {
            "valid_format": valid_fmt,
            "domain": domain,
            "disposable": disposable,
            "mx_ok": mx_ok,
            "mx_records": mx_records,
            "a_records": a_records,
            "spf": spf,
        }

    # ── UI ──
    st.markdown("<h1>Email Discovery</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Format validation · DNS lookups · Disposable check</p>", unsafe_allow_html=True)

    email_input = st.text_input("Target Email Address:", placeholder="target@example.com")

    if st.button("Analyse Email"):
        if not email_input.strip():
            st.error("Error: Please enter an email address.")
        else:
            with st.spinner("Executing DNS lookups…"):
                res = check_email(email_input.strip().lower())

            if not res["valid_format"]:
                st.error("Error: Invalid email format.")
            else:
                section_header("Analysis Results")

                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Format", "VALID")
                with c2: st.metric("MX Records", "FOUND" if res["mx_ok"] else "NONE")
                with c3: st.metric("Deliverable?", "LIKELY" if res["mx_ok"] else "UNLIKELY")

                card("Domain", res["domain"])

                badge("Format Valid", "Yes", True)
                badge("MX Exists",    "Yes" if res["mx_ok"]    else "No", res["mx_ok"])
                badge("Disposable",   "Yes" if res["disposable"] else "No", not res["disposable"])
                badge("SPF Found",    "Yes" if res["spf"]      else "No", bool(res["spf"]))

                if res["mx_records"]:
                    section_header("MX Records (Mail Servers)")
                    for pref, host in res["mx_records"]:
                        card(f"Priority {pref}", host)

                if res["a_records"]:
                    section_header("A Records (Domain IPs)")
                    for ip in res["a_records"]:
                        card("IP Address", ip)

                if res["spf"]:
                    section_header("SPF Record")
                    st.code(res["spf"], language=None)

                if res["disposable"]:
                    st.warning("Warning: This domain is a known disposable/temporary provider.")


# ════════════════════════════════════════════
#  MODULE 5  — GOOGLE DORKING
# ════════════════════════════════════════════
elif MODULE == "🔍  Google Dorking":

    DORK_TEMPLATES = {
        "Sensitive Files": [
            ('Exposed .env files',        'filetype:env "{target}"'),
            ('Exposed credentials',       'filetype:txt intext:"password" intext:"username" site:{target}'),
            ('Database dumps',            'filetype:sql "{target}"'),
            ('Config files',              'filetype:xml OR filetype:yml "{target}" intext:"password"'),
            ('Log files',                 'filetype:log "{target}"'),
            ('Backup files',              'filetype:bak OR filetype:backup "{target}"'),
        ],
        "Directory Listings": [
            ('Open index pages',          'intitle:"index of" "{target}"'),
            ('Apache directory listing',  'intitle:"index of /" "{target}"'),
            ('FTP open directories',      'intitle:"index of" inurl:ftp "{target}"'),
        ],
        "Login & Admin Panels": [
            ('Admin panels',              'site:{target} inurl:admin'),
            ('Login pages',               'site:{target} inurl:login'),
            ('phpMyAdmin',                'site:{target} inurl:phpmyadmin'),
            ('WordPress admin',           'site:{target} inurl:wp-admin'),
        ],
        "Cloud & Infrastructure": [
            ('AWS S3 buckets',            '"{target}" site:s3.amazonaws.com'),
            ('Azure blobs',               '"{target}" site:blob.core.windows.net'),
            ('GCP buckets',               '"{target}" site:storage.googleapis.com'),
            ('Exposed Grafana dashboards','site:{target} intitle:"Grafana"'),
            ('Jenkins CI',                'site:{target} intitle:"Dashboard [Jenkins]"'),
        ],
        "Personal & Social": [
            ('Email addresses on site',   'site:{target} intext:"@{target}"'),
            ('LinkedIn employees',        'site:linkedin.com intitle:"{target}"'),
            ('Social profiles',           '"{target}" site:twitter.com OR site:facebook.com OR site:instagram.com'),
            ('Resume/CVs',                '"{target}" filetype:pdf intitle:"CV" OR intitle:"Resume"'),
        ],
        "Code & Repositories": [
            ('GitHub repositories',       'site:github.com "{target}"'),
            ('Pastebin leaks',            'site:pastebin.com "{target}"'),
            ('Source code leaks',         'site:github.com OR site:gitlab.com "{target}" password'),
        ],
    }

    def build_dork_url(dork: str) -> str:
        return "https://www.google.com/search?q=" + urllib.parse.quote_plus(dork)

    # ── UI ──
    st.markdown("<h1>Google Dorking Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Generate targeted search operators.</p>", unsafe_allow_html=True)

    col_t, col_cat = st.columns([2, 1])
    with col_t:
        dork_target = st.text_input("Target Domain/Name:", placeholder="example.com  or  John Smith")
    with col_cat:
        selected_cat = st.selectbox("Category:", list(DORK_TEMPLATES.keys()))

    show_all = st.checkbox("Show all categories")

    if st.button("Generate Dorks"):
        if not dork_target.strip():
            st.error("Error: Please enter a target.")
        else:
            target_val = dork_target.strip()
            cats = DORK_TEMPLATES if show_all else {selected_cat: DORK_TEMPLATES[selected_cat]}

            for cat_name, dorks in cats.items():
                section_header(cat_name)
                for label, dork_tpl in dorks:
                    dork = dork_tpl.replace("{target}", target_val)
                    url  = build_dork_url(dork)
                    st.markdown(
                        f"""
                        <div style="
                            background:#ffffff;border:2px solid #000;
                            box-shadow:2px 2px 0px #000;padding:10px;margin-bottom:10px;
                            font-family:'Monaco', monospace;
                        ">
                            <span style="font-weight:bold;text-transform:uppercase;">{label}</span><br>
                            <code>{dork}</code><br><br>
                            <a href="{url}" target="_blank"
                               style="color:#000;font-weight:bold;text-decoration:underline;background:#dfdfdf;padding:2px 6px;border:1px solid #000;">
                                ↗ Execute Search
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Dork Syntax Reference"):
        ref = {
            "site:":        "Restrict to a domain",
            "filetype:":    "Search specific file extensions",
            "inurl:":       "Keyword must appear in URL",
            "intitle:":     "Keyword must appear in page title",
            "intext:":      "Keyword must appear in body text",
            '\"exact\"':    "Exact phrase match",
            "OR":           "Boolean OR between terms",
            "-keyword":     "Exclude keyword from results",
        }
        for op, desc in ref.items():
            col1, col2 = st.columns([1, 3])
            col1.code(op)
            col2.markdown(f"<span style='font-weight:bold;'>{desc}</span>", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 6  — THREAT INTELLIGENCE (v1.1)
# ════════════════════════════════════════════
elif MODULE == "☢️  Threat Intelligence":
    st.markdown("<h1><span>Global Threat Intelligence</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Open Threat Exchange (OTX) Integration</p>", unsafe_allow_html=True)

    # Add a slider to control how many pulses to show (up to 50)
    num_pulses = st.slider("Pulse Display Limit:", 5, 50, 10)

    target = st.text_input("Enter Indicator (IP, Domain, or Hash):", placeholder="e.g. apple.com")
    
    if st.button("☣️ Query OTX Pulse Database"):
        if not target.strip():
            st.error("Missing indicator value.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                ind_type, otx_path = "IPv4", "IPv4"
            elif "@" in target:
                ind_type, otx_path = "Email", "email"
            else:
                ind_type, otx_path = "Domain", "domain"

            headers = {"X-OTX-API-KEY": CONFIG["OTX_KEY"]}
            url = f"https://otx.alienvault.com/api/v1/indicators/{otx_path}/{target.strip()}/general"
            
            with st.spinner("Accessing OTX Global Intelligence Feed..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=12.0)
                    data = r.json()
                    
                    section_header(f"Reputation Analysis: {target}")
                    
                    pulse_info = data.get('pulse_info', {})
                    total_pulses = pulse_info.get('count', 0)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("Indicator Type", ind_type)
                    with c2: st.metric("Active Pulses", total_pulses)
                    with c3: st.metric("Reputation", "MALICIOUS" if total_pulses > 0 else "CLEAN")

                    if total_pulses > 0:
                        st.warning(f"System Alert: Indicator identified in {total_pulses} community threat pulses.")
                        
                        # Use the slider value here to show more pulses
                        for pulse in pulse_info.get('pulses', [])[:num_pulses]:
                            pulse_name = pulse.get('name', 'Unnamed Pulse')
                            
                            with st.expander(f"📁 Pulse: {pulse_name}"):
                                # High-detail metadata extraction
                                author = pulse.get('author_name', 'Anonymous')
                                created = (pulse.get('created') or "N/A")[:10]
                                tags = pulse.get('tags', [])
                                
                                # ENRICHMENT: Show Indicators and References
                                indicators = pulse.get('indicators', [])
                                references = pulse.get('references', [])
                                
                                # Use Markdown with explicit colors to fix the "blank info" bug
                                st.markdown(f"**Author:** <span style='color:black;'>{author}</span>", unsafe_allow_html=True)
                                st.markdown(f"**Date:** <span style='color:black;'>{created}</span>", unsafe_allow_html=True)
                                st.markdown(f"**Tags:** <span style='color:black;'>{', '.join(tags) if tags else 'None'}</span>", unsafe_allow_html=True)
                                
                                st.markdown("---")
                                st.markdown("**Pulse Description:**")
                                st.info(pulse.get('description', 'No description available.'))
                                
                                if indicators:
                                    st.markdown(f"**Related Indicators ({len(indicators)} total):**")
                                    # List the first 5 IOCs in the pulse
                                    for ioc in indicators[:5]:
                                        st.code(f"[{ioc.get('type')}] {ioc.get('indicator')}", language=None)
                                
                                if references:
                                    st.markdown("**External References:**")
                                    for ref in references[:3]:
                                        st.markdown(f"- [{ref}]({ref})")
                    else:
                        st.success("No known malicious associations found in OTX database.")
                
                except Exception as e:
                    st.error(f"OTX Connectivity Error: {str(e)}")

# ════════════════════════════════════════════
#  MODULE 7  — MALWARE SANDBOX (VIRUSTOTAL)
# ════════════════════════════════════════════
elif MODULE == "👾  Malware Sandbox":
    st.markdown("<h1><span>VirusTotal Intelligence</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: VirusTotal v3</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Cross-references indicators against 70+ antivirus scanners and URL/domain blacklisting services.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    target = st.text_input("Enter Hash, Domain, or IP:", placeholder="e.g. 44d88612fea8a8f36de82e1278abb02f")

    if st.button("🔎 Scan Indicator"):
        if not target.strip():
            st.error("Please provide a target for the sandbox.")
        elif CONFIG["VT_KEY"] == "YOUR_VIRUSTOTAL_API_KEY":
            st.warning("SYSTEM ERROR: VirusTotal API Key missing in CONFIG.")
        else:
            # Determine type for VT API v3
            # Simple regex to check if it's an IP
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                vt_type = "ip_addresses"
            # Check if it looks like a domain (has a dot, no @)
            elif "." in target and "@" not in target:
                vt_type = "domains"
            # Otherwise treat as a hash
            else:
                vt_type = "files"

            url = f"https://www.virustotal.com/api/v3/{vt_type}/{target.strip()}"
            headers = {"x-apikey": CONFIG["VT_KEY"]}

            with st.spinner("Uploading to multi-engine sandbox..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=15.0)
                    if r.status_code == 200:
                        data = r.json()['data']['attributes']
                        stats = data.get('last_analysis_stats', {})
                        
                        section_header(f"Security Report: {target}")
                        
                        # Mac Metric Grid
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Malicious", stats.get('malicious', 0))
                        with c2: st.metric("Suspicious", stats.get('suspicious', 0))
                        with c3: st.metric("Harmless", stats.get('harmless', 0))
                        with c4: st.metric("Undetected", stats.get('undetected', 0))

                        # Detailed breakdown
                        col_left, col_right = st.columns(2)
                        with col_left:
                            card("Reputation Score", str(data.get('reputation', 0)))
                            card("Provider Tags", ", ".join(data.get('tags', [])) if data.get('tags') else "None")
                        
                        with col_right:
                            # For files/domains, VT often has a 'categories' or 'meaningful_name'
                            card("Primary Label", data.get('meaningful_name', data.get('type_description', 'N/A')))
                            card("Last DNS Records", str(len(data.get('last_dns_records', []))))

                        # Show the specific engines that flagged it
                        if stats.get('malicious', 0) > 0:
                            st.markdown("---")
                            st.markdown("**Engine Flags:**")
                            results = data.get('last_analysis_results', {})
                            for engine, res in results.items():
                                if res['category'] == 'malicious':
                                    st.error(f"🚩 {engine}: {res['result']}")
                    
                    elif r.status_code == 404:
                        st.info("Indicator not found in VirusTotal database. It may be clean or brand new.")
                    else:
                        st.error(f"VT API Error: {r.status_code}")
                
                except Exception as e:
                    st.error(f"Sandbox Connectivity Failed: {str(e)}")    

# ════════════════════════════════════════════
#  MODULE 8  — GITHUB SECRET SCANNER
# ════════════════════════════════════════════
elif MODULE == "🐙  GitHub Secret Scanner":
    st.markdown("<h1><span>GitHub Secret Scanner</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: GitHub API v3</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Hunts for sensitive strings (AWS Keys, Private Keys, .env files) leaked in public repositories.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    target_user = st.text_input("Enter GitHub Username/Org:", placeholder="e.g. apple or torvalds")
    
    # Common high-risk search queries
    DANGER_QUERIES = {
        "AWS Keys": "AKIA",
        "Private RSA Keys": "BEGIN RSA PRIVATE KEY",
        "Environment Files": "filename:.env",
        "GitHub Tokens": "ghp_",
        "Config w/ Passwords": "extension:config password"
    }

    if st.button("🚀 Execute Secret Hunt"):
        if not target_user.strip():
            st.error("Target username is required.")
        else:
            section_header(f"Scanning Repositories for: {target_user}")
            
            headers = {}
            if CONFIG["GITHUB_TOKEN"]:
                headers["Authorization"] = f"token {CONFIG['GITHUB_TOKEN']}"
            
            found_secrets = False
            
            with st.spinner(f"Analyzing {target_user}'s digital trail..."):
                # We check each danger query against the user
                for label, query in DANGER_QUERIES.items():
                    # GitHub Search API: q={query}+user:{target_user}
                    search_url = f"https://api.github.com/search/code?q={query}+user:{target_user}"
                    
                    try:
                        r = httpx.get(search_url, headers=headers, timeout=15.0)
                        
                        if r.status_code == 200:
                            data = r.json()
                            count = data.get('total_count', 0)
                            
                            if count > 0:
                                found_secrets = True
                                st.warning(f"⚠ {label} Detected: {count} potential leaks found.")
                                for item in data.get('items', [])[:3]: # Show top 3 matches
                                    repo_name = item['repository']['full_name']
                                    file_path = item['path']
                                    file_url = item['html_url']
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:#fff; border:2px solid #000; padding:8px; margin-bottom:5px; box-shadow:2px 2px 0px #000;">
                                            <span style="font-family:Monaco, monospace; font-size:0.8rem;">
                                                <b>Repo:</b> {repo_name}<br>
                                                <b>File:</b> {file_path}<br>
                                                <a href="{file_url}" target="_blank" style="color:#000; font-weight:bold;">[VIEW SOURCE ↗]</a>
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                        elif r.status_code == 403:
                            st.error("API Rate Limit Exceeded. Please wait or add a GITHUB_TOKEN to CONFIG.")
                            break
                        
                        # GitHub Search API is rate-limited to 10 requests/min unauthenticated
                        # So we add a small delay
                        time.sleep(2) 
                        
                    except Exception as e:
                        st.error(f"Search Failed for {label}: {str(e)}")

            if not found_secrets:
                st.success("Clean Scan: No obvious secrets detected in public repositories.")                    

# ════════════════════════════════════════════
#  MODULE 9 — IMAGE FORENSICS (EXIF v1.1)
# ════════════════════════════════════════════
elif MODULE == "🖼️  Image Forensics":
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS

    st.markdown("<h1><span>Image Forensics Explorer</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: EXIF + Reverse Geocoding</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Extracts metadata and pings Nominatim to convert raw GPS data into physical street addresses.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Drop Evidence Image (JPG/TIFF):", type=["jpg", "jpeg", "tiff"])

    def get_decimal_from_dms(dms, ref):
        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0
        val = float(degrees + minutes + seconds)
        return -val if ref in ['S', 'W'] else val

    async def get_human_address(lat, lon):
        # Nominatim Reverse Geocoding (Keyless)
        # Policy: Must provide User-Agent and respect 1req/sec
        headers = {"User-Agent": "GHOST-OSINT-App/1.1 (Cybersecurity-Research)"}
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                r = await client.get(url, timeout=10.0)
                if r.status_code == 200:
                    return r.json().get('display_name', 'Address not found')
                return f"API Error: HTTP {r.status_code}"
            except Exception as e:
                return f"Connection Error: {str(e)}"

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Evidence", use_container_width=True)
        
        exif_data = image._getexif()
        
        if not exif_data:
            st.error("SYSTEM ERROR: No EXIF metadata found. Image may have been scrubbed.")
        else:
            section_header("Metadata Analysis")
            clean_exif, gps_info = {}, {}
            
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    for t in value:
                        gps_info[GPSTAGS.get(t, t)] = value[t]
                else:
                    clean_exif[decoded] = value

            # --- MAIN DATA DISPLAY ---
            row1 = st.columns(3)
            with row1[0]: st.metric("Device", clean_exif.get('Model', 'Unknown'))
            with row1[1]: st.metric("Software", str(clean_exif.get('Software', '1.0')))
            with row1[2]: st.metric("Timestamp", str(clean_exif.get('DateTime', 'N/A'))[:10])

            # GPS Data Logic
            if gps_info and 'GPSLatitude' in gps_info:
                lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
                lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
                
                # Update row with coordinates
                row2 = st.columns(3)
                with row2[0]: st.metric("Latitude", f"{lat:.6f}")
                with row2[1]: st.metric("Longitude", f"{lon:.6f}")
                with row2[2]: st.metric("GPS Status", "LOCKED", delta_color="normal")

                # --- REVERSE GEOCODING API CALL ---
                with st.spinner("Decoding GPS into physical address..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    address = loop.run_until_complete(get_human_address(lat, lon))
                    loop.close()

                st.markdown(f"""
                    <div style="background:#39ff1411; border:2px solid #39ff14; padding:15px; border-radius:4px; margin-top:10px;">
                        <b style="color:#000;">📍 DETECTED ADDRESS:</b><br>
                        <span style="font-family:Monaco, monospace; color:#000;">{address}</span>
                    </div>
                """, unsafe_allow_html=True)

                maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; margin-top:10px; padding:10px; background:#fff; border:2px solid #000; font-weight:bold; cursor:pointer; box-shadow:3px 3px 0px #000;">🛰️ VIEW SATELLITE IMAGERY</button></a>', unsafe_allow_html=True)
            else:
                st.info("No GPS coordinates detected for this asset.")

            with st.expander("📁 View Raw Metadata Dump"):
                for k, v in clean_exif.items():
                    st.write(f"**{k}:** {v}")

# ════════════════════════════════════════════
#  MODULE 10 — FINANCIAL INTELLIGENCE (INDIA)
# ════════════════════════════════════════════
elif MODULE == "💸  Financial Intelligence":
    st.markdown("<h1><span>Financial Reconnaissance</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: Indian Fin-Tech OSINT</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Validates IFSC routing codes and analyzes UPI Virtual Payment Addresses (VPA) to identify underlying banking partners.
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["🏦 IFSC Branch Trace", "💳 UPI Handle Analysis"])

    # --- TAB 1: IFSC LOOKUP ---
    with tab1:
        ifsc_input = st.text_input("Enter IFSC Code:", placeholder="e.g. HDFC0000007")
        
        if st.button("🔎 Trace Branch"):
            if len(ifsc_input) != 11:
                st.error("INVALID FORMAT: IFSC must be exactly 11 characters.")
            else:
                with st.spinner("Accessing RBI Routing Tables..."):
                    try:
                        r = httpx.get(f"https://ifsc.razorpay.com/{ifsc_input.strip()}", timeout=10.0)
                        if r.status_code == 200:
                            data = r.json()
                            section_header(f"Branch Details: {data.get('BANK')}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                card("Bank Name", data.get('BANK'))
                                card("Branch",    data.get('BRANCH'))
                                card("IFSC",      data.get('IFSC'))
                            with c2:
                                card("City",      data.get('CITY'))
                                card("District",  data.get('DISTRICT'))
                                card("State",     data.get('STATE'))
                            
                            st.info(f"📍 Address: {data.get('ADDRESS')}")
                            
                            # Deep Link to Map
                            addr_query = f"{data.get('BANK')} {data.get('BRANCH')} {data.get('CITY')}"
                            maps_url = f"https://www.google.com/maps/search/{addr_query.replace(' ', '+')}"
                            st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; padding:10px; background:#fff; border:2px solid #000; font-weight:bold; cursor:pointer; box-shadow:3px 3px 0px #000;">🗺️ LOCATE ON MAP</button></a>', unsafe_allow_html=True)
                        else:
                            st.error(f"IFSC NOT FOUND: Ensure the code is correct (Status {r.status_code}).")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")

    # --- TAB 2: UPI ANALYSIS ---
    with tab2:
        vpa_input = st.text_input("Enter UPI ID (VPA):", placeholder="username@bank")
        
        # OSINT Mapping of Suffixes
        UPI_HANDLES = {
            "okicici": "ICICI Bank", "okaxis": "Axis Bank", "oksbi": "State Bank of India",
            "okhdfcbank": "HDFC Bank", "ybl": "Yes Bank", "ibl": "ICICI Bank (PhonePe)",
            "axl": "Axis Bank (PhonePe)", "paytm": "Paytm Payments Bank",
            "upl": "Union Bank", "postbank": "India Post Payments Bank"
        }

        if st.button("🧪 Analyze VPA"):
            if "@" not in vpa_input:
                st.error("INVALID FORMAT: UPI ID must contain an '@' symbol.")
            else:
                handle = vpa_input.split("@")[-1].lower()
                bank_partner = UPI_HANDLES.get(handle, "Unknown/Custom Provider")
                
                section_header(f"Analysis: {vpa_input}")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("Provider", bank_partner)
                with c2: st.metric("Format Status", "VALID" if len(vpa_input) > 3 else "INVALID")
                
                st.markdown(
                    """
                    <div style="background:#f0f0f0; border:1px dashed #000; padding:10px; margin-top:10px;">
                        <b>OSINT Note:</b> In India, the handle (suffix) reveals the processing bank. 
                        To verify the <b>Legal Name</b>, scan the QR below with a banking app.
                    </div>
                    """, unsafe_allow_html=True
                )
                
                # Generate a UPI Deep Link QR for Verification
                upi_link = f"upi://pay?pa={vpa_input}&pn=GHOST_RECON&cu=INR"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={upi_link}"
                
                st.image(qr_url, caption="Scan to verify Legal Name in app")

# ════════════════════════════════════════════
#  MODULE 11 — DATA BREACH SEARCH (RAPID-API)
# ════════════════════════════════════════════
elif MODULE == "🔐  Data Breach Search":
    st.markdown("<h1><span>Breach Compilation Search</span></h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:#FFFFFF; border:2px solid #000; padding:10px; margin-bottom:20px; box-shadow:3px 3px 0px #000;">
            <b style="font-family:'Chicago', sans-serif;">💾 System Briefing: BreachDirectory v1.0</b><br>
            <span style="font-size:0.85rem; font-family:'Monaco', monospace;">
                Queries the RapidAPI BreachDirectory engine. Uses 'Auto-Detect' mode to find compromised assets. 
                (Fixed: URL Path and Redirect Following).
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

    query_input = st.text_input("Enter Email or Username:", placeholder="e.g. target@example.com")
    
    if st.button("🔓 Execute Breach Hunt"):
        target = query_input.strip()
        if not target:
            st.error("Input is required.")
        else:
            # ── DATA FROM YOUR SCREENSHOT ──
            # Fix: Removed the trailing slash to prevent double-slash errors
            api_url = "https://breachdirectory.p.rapidapi.com" 
            api_key = "591a17a2cemsh80a79611e6132c2p100379jsnf0065f1d3d92"
            
            headers = {
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GHOST/1.2"
            }
            
            # Using the exact params from the RapidAPI snippet
            query_params = {"func": "auto", "term": target}

            with st.spinner("Decoding dark-web archives..."):
                try:
                    # Creating a client to handle redirects more robustly
                    with httpx.Client(follow_redirects=True, timeout=25.0) as client:
                        r = client.get(api_url, headers=headers, params=query_params)
                    
                    if r.status_code == 200:
                        data = r.json()
                        
                        # Process results
                        if data.get('success') or 'result' in data:
                            results = data.get('result', [])
                            total_found = len(results)
                            
                            section_header(f"Exposure Report: {target}")
                            
                            c1, c2 = st.columns(2)
                            with c1: st.metric("Total Breaches", total_found)
                            with c2: st.metric("Risk Level", "CRITICAL" if total_found > 3 else "LOW")

                            if total_found > 0:
                                st.error(f"⚠ COMPROMISE DETECTED: {total_found} instances found.")
                                for breach in results:
                                    sources = breach.get('sources', [])
                                    source_name = ", ".join(sources) if isinstance(sources, list) else str(sources)
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:#fff; border:2px solid #000; padding:10px; margin-bottom:8px; box-shadow:2px 2px 0px #000;">
                                            <b style="font-family:'Chicago', sans-serif;">📂 SOURCE: {source_name}</b><br>
                                            <span style="font-family:'Monaco', monospace; font-size:0.8rem;">
                                                <b>Password Leaked:</b> {"✅ YES" if breach.get('has_password') else "❌ NO"}<br>
                                                <b>Hash Type:</b> {breach.get('hash_type', 'N/A')}
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                            else:
                                st.success("Clear Scan: No exposure found in this database.")
                        else:
                            st.info(data.get('message', "No records found for this identifier."))
                    
                    else:
                        st.error(f"System Error: HTTP {r.status_code}")
                        if r.status_code == 307:
                            st.info("The server is still redirecting. Please check if your RapidAPI endpoint URL has changed.")
                
                except Exception as e:
                    st.error(f"Search Failed: {str(e)}")
streamlit>=1.35.0
httpx[http2]>=0.27.0
dnspython>=2.6.1
phonenumbers>=8.13.39
anyio>=4.3.0
h2>=4.1.0

"""
╔══════════════════════════════════════════════════════════════╗
║         G.H.O.S.T  //  OSINT Reconnaissance Dashboard       ║
║         RobCo Industries Pip-Boy Terminal Edition            ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import asyncio
import httpx
import dns.resolver
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import re
import socket
import time
from datetime import datetime
import urllib.parse
import platform
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# ─────────────────────────────────────────────
#  SYSTEM MEMORY  
# ─────────────────────────────────────────────

if 'pivot_email' not in st.session_state:
    st.session_state.pivot_email = ""

# ─────────────────────────────────────────────
#  SYSTEM CONFIGURATION (API KEYS)
# ─────────────────────────────────────────────
CONFIG = {
    "OTX_KEY": "cec0f6c86ef2ee22f1ab3a3734cacd8c2e96846622cf808ef4c07a2f712e25d9",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    "OPENCTI_URL": "http://localhost:8080", 
    "VT_KEY": "70f961af90b0a23b61b4d22fa1223b64694304a105925e25e61b3b22ecc23e22", 
    "BREACH_KEY": "591a17a2cemsh80a79611e6132c2p100379jsnf0065f1d3d92", 
    "GITHUB_TOKEN": "", 
    "OPENCTI_TOKEN": "9d29da5c-d768-4f22-b765-b891e53b8313" 
}

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ROBCO TERMINAL // GHOST",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — FALLOUT PIP-BOY THEME
# ─────────────────────────────────────────────
PIPBOY_CSS = """
<style>
/* ── Import Retro Terminal Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

/* ── Root Palette ── */
:root {
    --pip-bg:       #0a120a;
    --pip-green:    #39ff14;
    --pip-dim:      #1a4220;
    --pip-dark:     #0d1f12;
    --font-term:    'VT323', 'Courier New', Courier, monospace;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-term) !important;
    color: var(--pip-green) !important;
    background-color: var(--pip-bg) !important;
    letter-spacing: 1px;
}

/* ── CRT Scanlines Overlay ── */
.stApp::after {
    content: " ";
    display: block;
    position: absolute;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    z-index: 99999;
    background-size: 100% 2px, 3px 100%;
    pointer-events: none;
}

/* ── Terminal Text Glow ── */
p, span, h1, h2, h3, h4, label, div {
    text-shadow: 0 0 4px rgba(57, 255, 20, 0.4) !important;
}

/* ── Custom RobCo Window Header ── */
.mac-window-header {
    background: var(--pip-green);
    border: 2px solid var(--pip-green);
    height: 30px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    margin-bottom: 5px;
    position: relative;
    z-index: 10;
}

.mac-title-text {
    background: var(--pip-green);
    color: var(--pip-bg) !important;
    padding: 0 15px;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    font-family: var(--font-term);
    font-size: 1.4rem;
    font-weight: bold;
    text-transform: uppercase;
    white-space: nowrap;
    text-shadow: none !important;
}

/* ── Pip-Boy Terminal Blocks ── */
.block-container {
    background-color: var(--pip-bg) !important;
    border: 2px solid var(--pip-green) !important;
    box-shadow: 0 0 10px rgba(57, 255, 20, 0.2), inset 0 0 20px rgba(57, 255, 20, 0.05) !important;
    padding: 2rem 3rem !important;
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
    border-radius: 8px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--pip-dark) !important;
    border-right: 2px solid var(--pip-green) !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}
/* Selected radio item */
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
    background-color: var(--pip-green) !important;
}

/* ── Headers ── */
h1 { font-size: 2.8rem !important; border-bottom: 2px solid var(--pip-green); padding-bottom: 5px; text-transform: uppercase; }
h2 { font-size: 2rem !important; text-transform: uppercase; }

/* ── Text inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-family: var(--font-term) !important;
    font-size: 1.2rem !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}

/* ── Buttons ── */
.stButton button {
    background-color: var(--pip-dim) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-family: var(--font-term) !important;
    font-size: 1.4rem !important;
    text-transform: uppercase;
    border-radius: 0px !important;
    padding: 0.4rem 1.2rem !important;
    transition: all 0.2s !important;
}
.stButton button:hover, .stButton button:active {
    background-color: var(--pip-green) !important;
    color: var(--pip-bg) !important;
    box-shadow: 0 0 10px var(--pip-green) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div { background: var(--pip-green) !important; }
.stProgress > div > div { background-color: var(--pip-dark) !important; border: 1px solid var(--pip-green) !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: var(--pip-dim) !important;
    border: 1px solid var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-size: 1.2rem !important;
}
.streamlit-expanderContent {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    border-top: none !important;
}

/* ── Dividers ── */
hr { border-color: var(--pip-green) !important; border-width: 1px !important; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background-color: var(--pip-dark) !important;
    border: 1px solid var(--pip-green) !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stMetricLabel"] {
    color: var(--pip-green) !important;
    font-size: 1rem !important;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: var(--pip-green) !important;
    font-size: 2.2rem !important;
}

/* ── Code blocks ── */
.stCodeBlock, code, pre {
    background-color: var(--pip-dark) !important;
    border: 1px dashed var(--pip-green) !important;
    color: var(--pip-green) !important;
    font-size: 1.1rem !important;
}

/* ── Success / warning / error ── */
.stSuccess, .stWarning, .stError, .stInfo { 
    background-color: var(--pip-dim) !important; 
    border: 1px solid var(--pip-green) !important; 
    color: var(--pip-green) !important;
    border-radius: 0px !important;
}
.stSuccess p, .stWarning p, .stError p, .stInfo p {
    color: var(--pip-green) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 12px; }
::-webkit-scrollbar-track { background: var(--pip-bg); border-left: 1px solid var(--pip-green); }
::-webkit-scrollbar-thumb { background: var(--pip-green); }

/* ── Custom RobCo Dialog Box ── */
#mac-modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(10, 18, 10, 0.8);
    z-index: 1000;
}
.mac-dialog {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: var(--pip-bg);
    border: 2px solid var(--pip-green);
    box-shadow: 0 0 20px rgba(57, 255, 20, 0.5);
    width: 400px;
    padding: 20px;
    text-align: center;
}
.mac-dialog-title {
    font-size: 1.5rem;
    margin-bottom: 15px;
    text-transform: uppercase;
    display: block;
    color: var(--pip-bg);
    background: var(--pip-green);
    padding: 5px;
}
.mac-dialog-text {
    font-size: 1.2rem;
    margin-bottom: 20px;
    display: block;
}
.mac-dialog-ok {
    background: var(--pip-dim);
    border: 1px solid var(--pip-green);
    color: var(--pip-green);
    padding: 5px 25px;
    font-family: var(--font-term);
    font-size: 1.2rem;
    cursor: pointer;
    text-transform: uppercase;
}
.mac-dialog-ok:hover {
    background: var(--pip-green);
    color: var(--pip-bg);
}

/* ── Vault Boy Image Filter ── */
.vault-boy {
    width: 150px;
    filter: sepia(100%) hue-rotate(80deg) saturate(500%) brightness(0.8) contrast(1.2);
    margin-bottom: 10px;
}
</style>
"""

st.markdown(PIPBOY_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  GLOBAL UI COMPONENTS (Modal & Title Bar)
# ─────────────────────────────────────────────

st.markdown(
    """
    <div id="mac-modal-overlay">
        <div class="mac-dialog">
            <span class="mac-dialog-title" id="modal-title">RobCo Alert</span>
            <span class="mac-dialog-text" id="modal-msg">Error.</span>
            <button class="mac-dialog-ok" onclick="closeMacModal()">ACCEPT</button>
        </div>
    </div>
    <script>
        function showMacModal(title, msg) {
            const overlay = document.getElementById('mac-modal-overlay');
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-msg').innerText = msg;
            overlay.style.display = 'block';
        }
        function closeMacModal() {
            document.getElementById('mac-modal-overlay').style.display = 'none';
        }
    </script>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="mac-window-header">
        <div class="mac-title-text">ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
#  HELPER: render a styled "card" block
# ─────────────────────────────────────────────
def card(title: str, content: str):
    st.markdown(
        f"""
        <div style="
            background:var(--pip-dark);
            border:1px solid var(--pip-green);
            padding:0.75rem 1rem;
            margin-bottom:0.8rem;
            color:var(--pip-green);
        ">
            <span style="font-weight:bold;text-transform:uppercase;border-bottom:1px solid var(--pip-green);">{title}</span><br>
            <span style="font-size:1.1rem;display:block;margin-top:4px;">{content}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def badge(label: str, value: str, ok: bool = True):
    bg = "var(--pip-green)" if ok else "var(--pip-dark)"
    fg = "var(--pip-bg)" if ok else "var(--pip-green)"
    icon = "[OK]" if ok else "[ERR]"
    st.markdown(
        f"""
        <div style="display:inline-block;margin:3px 4px;">
            <span style="
                background:{bg};
                border:1px solid var(--pip-green);
                color:{fg};
                padding:4px 8px;
                font-size:1rem;
                text-transform:uppercase;
            ">{icon} {label}: {value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(text: str):
    st.markdown(
        f"""
        <div style="
            background:var(--pip-green);
            color:var(--pip-bg);
            padding:4px 10px;
            margin:1.5rem 0 1rem 0;
            display:inline-block;
            font-size:1.4rem;
            text-transform:uppercase;
            font-weight:bold;
            text-shadow:none !important;
        ">
            > {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  SIDEBAR — NAVIGATION (PIP-BOY EDITION)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <img src="https://icon2.cleanpng.com/20180802/yqg/3dc04be0578b48f51c4a8d7e9b18136d.webp" class="vault-boy">
            <div style="
                font-size:2.5rem;
                text-transform:uppercase;
                line-height:1;
                font-weight:bold;
                margin-top: 10px;
            ">PIP-OS v7.3</div>
            <div style="
                font-size:1.2rem;
                margin-top:5px;
            ">G.H.O.S.T. Reconnaissance</div>
            <div style="
                font-size:0.9rem;
                margin-top:5px;
                color:var(--pip-dim) !important;
            ">VAULT-TEC KEEPS YOU SAFE ONLINE</div>
        </div>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    MODULE = st.radio(
        "Select Application:",
        [
            "🏠  Control Panel",
            "👤  Username Search",
            "🌐  Network Utility & Recon",
            "📞  Phone Intelligence",
            "📧  Email Discovery",
            "🔍  Google Dorking",
            "☢️  Threat Intelligence",
            "👾  Malware Sandbox",
            "🐙  GitHub Secret Scanner",
            "🖼️  Image Forensics",
            "💸  Financial Intelligence",
            "🔐  Data Breach Search"
        ],
        label_visibility="visible",
    )

    st.markdown(
        """
        <hr>
        <div style="
            font-size:0.9rem;
            text-align:center;
            padding-top:0.5rem;
            border: 1px solid var(--pip-green);
            padding: 5px;
            background: var(--pip-dark);
        ">
            ☢️ VAULT-TEC AUTHORIZED USE ONLY.<br>
            Respect local wasteland laws.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════
#  MODULE 0 — OSINT CONTROL PANEL
# ════════════════════════════════════════════
if MODULE == "🏠  Control Panel":
    st.markdown("<h1>VAULT-TEC OSINT Control Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem;'>Open-Source Intelligence Framework | Vault-Tec Edition v1.3</p>", unsafe_allow_html=True)
    
    row1_cols = st.columns(4)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sys_info = platform.system() + " " + platform.release()
    with row1_cols[0]: st.metric("System Status", "ONLINE")
    with row1_cols[1]: st.metric("Active Modules", "11") 
    with row1_cols[2]: st.metric("System Time", now)
    with row1_cols[3]: st.metric("Host OS", sys_info)

    row2_cols = st.columns(3)
    vt_status = "OK" if CONFIG.get("VT_KEY") != "YOUR_VIRUSTOTAL_API_KEY" else "MISSING"
    rapid_status = "OK" if "591a" in CONFIG.get("BREACH_KEY", "") else "OFFLINE"
    
    with row2_cols[0]: st.metric("API Handshake", f"VT:{vt_status} | BD:{rapid_status}")
    with row2_cols[1]: st.metric("Memory Banks", " OK")
    with row2_cols[2]: st.metric("CPU Architecture", "SUFFICIENT")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:1.2rem 1.5rem;">
            <div style="font-size:1.8rem; border-bottom:1px solid var(--pip-green); margin-bottom:10px; text-transform:uppercase;">
                RobCo Application Registry
            </div>
            <table style="width:100%; font-size:1.1rem; border-collapse:collapse; text-align:left;">
                <tr style="border-bottom:1px solid var(--pip-green); background:var(--pip-dim);">
                    <th style="padding:8px;">Application</th>
                    <th style="padding:8px;">Forensic Technique</th>
                    <th style="padding:8px;">Primary Provider</th>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">👤 Username Search</td><td>HTTP Probing (Async)</td><td>Sherlock DB</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🌐 Network Utility</td><td>GeoIP + DNS Resolver</td><td>ip-api.com</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">📞 Phone Intel</td><td>Local Metadata Extraction</td><td>Libphonenumber</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">📧 Email Discovery</td><td>MX/SPF DNS Lookup</td><td>Public DNS</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🔐 Data Breach</td><td>Identity Leak Correlation</td><td>BreachDirectory</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🔍 Google Dorking</td><td>Query Generation</td><td>Google Dork Engine</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">☢️ Threat Intel</td><td>Reputation Analysis</td><td>AlienVault OTX</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">👾 Malware Sandbox</td><td>Multi-Engine Scan (v3)</td><td>VirusTotal</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🐙 Secret Scanner</td><td>Recursive String Hunt</td><td>GitHub API</td>
                </tr>
                <tr style="border-bottom:1px dashed var(--pip-dim);">
                    <td style="padding:8px;">🖼️ Image Forensics</td><td>EXIF + Rev. Geocoding</td><td>Pillow / Nominatim</td>
                </tr>
                <tr>
                    <td style="padding:8px;">💸 Financial Intel</td><td>Routing & UPI Validation</td><td>Razorpay / VPA</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════
#  MODULE 1  — USERNAME SEARCH
# ════════════════════════════════════════════
elif MODULE == "👤  Username Search":
    PLATFORMS = {
        "GitHub":        ("https://github.com/{u}",             "Not Found"),
        "GitLab":        ("https://gitlab.com/{u}",             "404"),
        "Twitter/X":     ("https://x.com/{u}",                  "This account"),
        "Reddit":        ("https://www.reddit.com/user/{u}",    "page not found"),
        "Instagram":     ("https://www.instagram.com/{u}/",     "Sorry"),
        "TikTok":        ("https://www.tiktok.com/@{u}",        "couldn't find"),
        "Pinterest":     ("https://www.pinterest.com/{u}/",     "404"),
        "Twitch":        ("https://www.twitch.tv/{u}",          "404"),
        "YouTube":       ("https://www.youtube.com/@{u}",       "404"),
        "SoundCloud":    ("https://soundcloud.com/{u}",         "404"),
        "Dev.to":        ("https://dev.to/{u}",                 "404"),
        "Keybase":       ("https://keybase.io/{u}",             "Not Found"),
        "Pastebin":      ("https://pastebin.com/u/{u}",         "Not Found"),
        "HackerNews":    ("https://news.ycombinator.com/user?id={u}", "No such user"),
        "ProductHunt":   ("https://www.producthunt.com/@{u}",  "404"),
        "Kaggle":        ("https://www.kaggle.com/{u}",         "404"),
        "Replit":        ("https://replit.com/@{u}",            "404"),
        "Medium":        ("https://medium.com/@{u}",            "404"),
        "Substack":      ("https://{u}.substack.com",           "404"),
        "Steam":         ("https://steamcommunity.com/id/{u}",  "The specified profile"),
        "AngelList":     ("https://angel.co/{u}", "404"),
        "Fiverr":          ("https://www.fiverr.com/{u}",            "404"),
        "Upwork":          ("https://www.upwork.com/freelancers/~{u}", "404"),
        "Bandcamp":        ("https://bandcamp.com/{u}", "404"),
        "HuggingFace":     ("https://huggingface.co/{u}", "404"),
        "DockerHub":       ("https://hub.docker.com/u/{u}", "404"),
        "npm":             ("https://www.npmjs.com/~{u}", "404"),
        "PyPI":            ("https://pypi.org/user/{u}/", "404"),
    }

    HEADERS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 PIP-OS/7.1" }

    async def check_platform(client: httpx.AsyncClient, name: str, url: str, not_found_text: str):
        try:
            r = await client.get(url, timeout=8.0, follow_redirects=True, headers=HEADERS)
            if r.status_code == 200 and not_found_text.lower() not in r.text.lower():
                return name, url, True
            return name, url, False
        except Exception:
            return name, url, False

    async def run_username_scan(username: str):
        results = []
        async with httpx.AsyncClient(http2=True) as client:
            tasks = []
            for name, (url_tpl, nf) in PLATFORMS.items():
                url = url_tpl.replace("{u}", username)
                tasks.append(check_platform(client, name, url, nf))
            results = await asyncio.gather(*tasks)
        return results

    st.markdown("<h1>Global Identity Search</h1>", unsafe_allow_html=True)
    username = st.text_input("Enter Target Alias:", placeholder="e.g. johndoe")

    if st.button("Execute Async Probe"):
        if not username.strip():
            st.error("Error: Subject alias required.")
        else:
            progress_bar = st.progress(0, text="Establishing uplink...")
            status_text  = st.empty()
            t0 = time.perf_counter()

            status_text.markdown(f"> **Scanning databanks for: {username}**", unsafe_allow_html=True)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(run_username_scan(username))
            loop.close()

            elapsed = time.perf_counter() - t0
            progress_bar.progress(1.0, text="Probe sequence complete.")

            found = [r for r in results if r[2]]
            not_found = [r for r in results if not r[2]]

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Vectors Scanned", len(PLATFORMS))
            with c2: st.metric("Positive Hits", len(found))
            with c3: st.metric("Uplink Time", f"{elapsed:.2f}s")

            section_header("Confirmed Identities")
            if found:
                for name, url, _ in found:
                    st.markdown(
                        f"""
                        <div style="
                            background:var(--pip-dark);border:1px solid var(--pip-green);
                            padding:8px 12px;margin-bottom:8px;font-size:1.2rem;
                        ">
                            <span>[HIT] {name}</span>
                            <a href="{url}" target="_blank"
                               style="float:right;color:var(--pip-green);text-decoration:none;">
                                [ LINK ]
                            </a>
                        </div>
                        """, unsafe_allow_html=True
                    )
            else:
                st.warning("Subject is a ghost. No data found.")

            with st.expander("View Null Returns"):
                for name, url, _ in not_found:
                    st.markdown(f"[NULL] {name}", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MODULE 2 — NETWORK UTILITY
# ════════════════════════════════════════════
elif MODULE == "🌐  Network Utility & Recon":
    async def fetch_ip_geo(target: str) -> dict:
        url = f"http://ip-api.com/json/{target}?fields=status,message,continent,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=8.0)
            return r.json()

    def resolve_dns(domain: str) -> dict:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype, lifetime=5.0)
                results[rtype] = [str(r) for r in answers]
            except Exception:
                results[rtype] = []
        return results

    def resolve_ptr(ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "N/A"

    st.markdown("<h1>Network Topography</h1>", unsafe_allow_html=True)
    target = st.text_input("Enter Node Address (IP/Domain):", placeholder="e.g. 8.8.8.8")

    col_a, col_b = st.columns(2)
    run_ip  = col_a.button("[ TRACE IP ]")
    run_dns = col_b.button("[ DUMP DNS ]")

    if run_ip and target.strip():
        with st.spinner("Pinging Satellites..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            geo = loop.run_until_complete(fetch_ip_geo(target.strip()))
            loop.close()

        if geo.get("status") == "success":
            section_header("Node Telemetry")
            c1, c2, c3 = st.columns(3)
            c1.metric("Node IP", geo.get("query", "—"))
            c2.metric("Territory", geo.get("country", "—"))
            c3.metric("Sector", geo.get("city", "—"))

            card("ISP Routing", geo.get("isp", "—"))
            card("Coordinates", f"Lat {geo.get('lat','—')} / Lon {geo.get('lon','—')}")
            card("Reverse DNS", resolve_ptr(geo.get("query", target.strip())))

            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Security Posture (OTX)")
            try:
                otx_r = httpx.get(f"https://otx.alienvault.com/api/v1/indicators/IPv4/{target.strip()}/general", headers={"X-OTX-API-KEY": CONFIG["OTX_KEY"]}, timeout=5.0)
                pulses = otx_r.json().get('pulse_info', {}).get('count', 0)
                badge("Threat Level", f"{pulses} Pulses", ok=(pulses == 0))
                if pulses > 0:
                    st.error(f"⚠ Caution: This IP is associated with {pulses} known threat pulses.")
            except:
                st.warning("OTX Uplink severed.")
        else:
            st.error(f"Routing Error: {geo.get('message','Unknown')}")

    if run_dns and target.strip():
        domain = re.sub(r"^https?://", "", target.strip()).split("/")[0]
        with st.spinner(f"Accessing Domain Registries for {domain}..."):
            records = resolve_dns(domain)

        section_header("DNS Topology")
        for rtype, values in records.items():
            if values:
                with st.expander(f"[{rtype}] Records Found ({len(values)})"):
                    for v in values:
                        st.code(v, language=None)

# ════════════════════════════════════════════
#  MODULE 3  — PHONE INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "📞  Phone Intelligence":
    def analyse_phone(raw: str) -> dict:
        try:
            parsed = phonenumbers.parse(raw, None)
            return {
                "valid": phonenumbers.is_valid_number(parsed),
                "region": geocoder.description_for_number(parsed, "en") or "Unknown",
                "carrier": carrier.name_for_number(parsed, "en") or "Unknown",
                "country_code": parsed.country_code,
                "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                "error": None,
            }
        except Exception as e:
            return {"error": str(e)}

    st.markdown("<h1>Comms Intercept</h1>", unsafe_allow_html=True)
    phone_raw = st.text_input("Enter Comm Frequency (+Country Code):", placeholder="+1 415 555 0100")

    if st.button("Decrypt Frequency"):
        if not phone_raw.strip():
            st.error("Frequency missing.")
        else:
            result = analyse_phone(phone_raw.strip())
            if result.get("error"):
                st.error(f"Decryption failed: {result['error']}")
            else:
                section_header("Signal Origin")
                c1, c2 = st.columns(2)
                with c1: st.metric("Status", "VALID" if result["valid"] else "INVALID")
                with c2: st.metric("Region", result["region"])
                
                card("Tower Operator", result["carrier"])
                card("Routing Format", result["e164"])

# ════════════════════════════════════════════
#  MODULE 4  — EMAIL DISCOVERY
# ════════════════════════════════════════════
elif MODULE == "📧  Email Discovery":
    st.markdown("<h1>Electronic Mail Trace</h1>", unsafe_allow_html=True)
    email_input = st.text_input("Enter Target Address:", placeholder="target@example.com")

    if st.button("Trace Route"):
        if not email_input.strip():
            st.error("Address missing.")
        else:
            domain = email_input.split("@")[1] if "@" in email_input else ""
            with st.spinner("Pinging Mail Exchangers..."):
                try:
                    answers = dns.resolver.resolve(domain, "MX", lifetime=6.0)
                    mx_records = [str(r.exchange) for r in answers]
                    
                    section_header("Server Topology")
                    st.metric("Mail Servers", "ACTIVE")
                    for mx in mx_records:
                        card("MX Node", mx)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("[ Pivot to Breach Analysis ]"):
                        st.session_state.pivot_email = email_input.strip()
                        st.query_params["module"] = "🔐  Data Breach Search"
                        st.rerun()

                except Exception:
                    st.error("No active mail servers found for domain.")

# ════════════════════════════════════════════
#  MODULE 5  — GOOGLE DORKING
# ════════════════════════════════════════════
elif MODULE == "🔍  Google Dorking":

    DORK_TEMPLATES = {
        "Sensitive Files": [
            ('Exposed .env files',        'filetype:env "{target}"'),
            ('Exposed credentials',       'filetype:txt intext:"password" intext:"username" site:{target}'),
            ('Database dumps',            'filetype:sql "{target}"'),
            ('Config files',              'filetype:xml OR filetype:yml "{target}" intext:"password"'),
            ('Log files',                 'filetype:log "{target}"'),
            ('Backup files',              'filetype:bak OR filetype:backup "{target}"'),
        ],
        "Directory Listings": [
            ('Open index pages',          'intitle:"index of" "{target}"'),
            ('Apache directory listing',  'intitle:"index of /" "{target}"'),
            ('FTP open directories',      'intitle:"index of" inurl:ftp "{target}"'),
        ],
        "Login & Admin Panels": [
            ('Admin panels',              'site:{target} inurl:admin'),
            ('Login pages',               'site:{target} inurl:login'),
            ('phpMyAdmin',                'site:{target} inurl:phpmyadmin'),
            ('WordPress admin',           'site:{target} inurl:wp-admin'),
        ],
        "Cloud & Infrastructure": [
            ('AWS S3 buckets',            '"{target}" site:s3.amazonaws.com'),
            ('Azure blobs',               '"{target}" site:blob.core.windows.net'),
            ('GCP buckets',               '"{target}" site:storage.googleapis.com'),
            ('Exposed Grafana dashboards','site:{target} intitle:"Grafana"'),
            ('Jenkins CI',                'site:{target} intitle:"Dashboard [Jenkins]"'),
        ],
        "Personal & Social": [
            ('Email addresses on site',   'site:{target} intext:"@{target}"'),
            ('LinkedIn employees',        'site:linkedin.com intitle:"{target}"'),
            ('Social profiles',           '"{target}" site:twitter.com OR site:facebook.com OR site:instagram.com'),
            ('Resume/CVs',                '"{target}" filetype:pdf intitle:"CV" OR intitle:"Resume"'),
        ],
        "Code & Repositories": [
            ('GitHub repositories',       'site:github.com "{target}"'),
            ('Pastebin leaks',            'site:pastebin.com "{target}"'),
            ('Source code leaks',         'site:github.com OR site:gitlab.com "{target}" password'),
        ],
    }

    def build_dork_url(dork: str) -> str:
        return "https://www.google.com/search?q=" + urllib.parse.quote_plus(dork)

    st.markdown("<h1>Query Generation</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Construct advanced search operators for data extraction from global indexes.</span>
        </div>
        """, unsafe_allow_html=True
    )

    col_t, col_cat = st.columns([2, 1])
    with col_t:
        dork_target = st.text_input("Target Domain/Name:", placeholder="example.com  or  John Smith")
    with col_cat:
        selected_cat = st.selectbox("Category:", list(DORK_TEMPLATES.keys()))

    show_all = st.checkbox("Show all categories")

    if st.button("Generate Operators"):
        if not dork_target.strip():
            st.error("Error: Please enter a target.")
        else:
            target_val = dork_target.strip()
            cats = DORK_TEMPLATES if show_all else {selected_cat: DORK_TEMPLATES[selected_cat]}

            for cat_name, dorks in cats.items():
                section_header(cat_name)
                for label, dork_tpl in dorks:
                    dork = dork_tpl.replace("{target}", target_val)
                    url  = build_dork_url(dork)
                    st.markdown(
                        f"""
                        <div style="
                            background:var(--pip-dark);border:1px solid var(--pip-green);
                            padding:10px;margin-bottom:10px;
                        ">
                            <span style="font-weight:bold;text-transform:uppercase;">{label}</span><br>
                            <code>{dork}</code><br><br>
                            <a href="{url}" target="_blank"
                               style="color:var(--pip-bg);font-weight:bold;text-decoration:none;background:var(--pip-green);padding:4px 8px;">
                                [ EXECUTE SEARCH ]
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# ════════════════════════════════════════════
#  MODULE 6  — THREAT INTELLIGENCE
# ════════════════════════════════════════════
elif MODULE == "☢️  Threat Intelligence":
    st.markdown("<h1>OTX Threat Feed</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Querying global threat nodes (AlienVault OTX) for malicious signatures.</span>
        </div>
        """, unsafe_allow_html=True
    )

    num_pulses = st.slider("Pulse Display Limit:", 5, 50, 10)
    target = st.text_input("Enter Indicator (IP, Domain, or Hash):", placeholder="e.g. apple.com")
    
    if st.button("☣️ Query Nodes"):
        if not target.strip():
            st.error("Missing indicator value.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                ind_type, otx_path = "IPv4", "IPv4"
            elif "@" in target:
                ind_type, otx_path = "Email", "email"
            else:
                ind_type, otx_path = "Domain", "domain"

            headers = {"X-OTX-API-KEY": CONFIG["OTX_KEY"]}
            url = f"https://otx.alienvault.com/api/v1/indicators/{otx_path}/{target.strip()}/general"
            
            with st.spinner("Accessing Global Intelligence Feed..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=12.0)
                    data = r.json()
                    
                    section_header(f"Reputation Analysis: {target}")
                    
                    pulse_info = data.get('pulse_info', {})
                    total_pulses = pulse_info.get('count', 0)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("Indicator Type", ind_type)
                    with c2: st.metric("Active Pulses", total_pulses)
                    with c3: st.metric("Reputation", "MALICIOUS" if total_pulses > 0 else "CLEAN")

                    if total_pulses > 0:
                        st.warning(f"System Alert: Indicator identified in {total_pulses} community threat pulses.")
                        
                        for pulse in pulse_info.get('pulses', [])[:num_pulses]:
                            pulse_name = pulse.get('name', 'Unnamed Pulse')
                            
                            with st.expander(f"📁 Pulse: {pulse_name}"):
                                author = pulse.get('author_name', 'Anonymous')
                                created = (pulse.get('created') or "N/A")[:10]
                                tags = pulse.get('tags', [])
                                indicators = pulse.get('indicators', [])
                                
                                st.markdown(f"**Author:** {author}")
                                st.markdown(f"**Date:** {created}")
                                st.markdown(f"**Tags:** {', '.join(tags) if tags else 'None'}")
                                
                                st.markdown("---")
                                st.info(pulse.get('description', 'No description available.'))
                                
                                if indicators:
                                    st.markdown(f"**Related Indicators ({len(indicators)} total):**")
                                    for ioc in indicators[:5]:
                                        st.code(f"[{ioc.get('type')}] {ioc.get('indicator')}", language=None)
                    else:
                        st.success("No known malicious associations found in OTX database.")
                except Exception as e:
                    st.error(f"OTX Connectivity Error: {str(e)}")

# ════════════════════════════════════════════
#  MODULE 7  — MALWARE SANDBOX
# ════════════════════════════════════════════
elif MODULE == "👾  Malware Sandbox":
    st.markdown("<h1>VirusTotal Isolation</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Cross-references indicators against 70+ antivirus scanners using VirusTotal v3 API.</span>
        </div>
        """, unsafe_allow_html=True
    )

    target = st.text_input("Enter Hash, Domain, or IP:", placeholder="e.g. 44d88612fea8a8f36de82e1278abb02f")

    if st.button("🔎 Execute Scan"):
        if not target.strip():
            st.error("Please provide a target for the sandbox.")
        elif CONFIG["VT_KEY"] == "YOUR_VIRUSTOTAL_API_KEY":
            st.warning("SYSTEM ERROR: VirusTotal API Key missing in CONFIG.")
        else:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                vt_type = "ip_addresses"
            elif "." in target and "@" not in target:
                vt_type = "domains"
            else:
                vt_type = "files"

            url = f"https://www.virustotal.com/api/v3/{vt_type}/{target.strip()}"
            headers = {"x-apikey": CONFIG["VT_KEY"]}

            with st.spinner("Uploading to multi-engine sandbox..."):
                try:
                    r = httpx.get(url, headers=headers, timeout=15.0)
                    if r.status_code == 200:
                        data = r.json()['data']['attributes']
                        stats = data.get('last_analysis_stats', {})
                        
                        section_header(f"Security Report: {target}")
                        
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.metric("Malicious", stats.get('malicious', 0))
                        with c2: st.metric("Suspicious", stats.get('suspicious', 0))
                        with c3: st.metric("Harmless", stats.get('harmless', 0))
                        with c4: st.metric("Undetected", stats.get('undetected', 0))

                        col_left, col_right = st.columns(2)
                        with col_left:
                            card("Reputation Score", str(data.get('reputation', 0)))
                            card("Provider Tags", ", ".join(data.get('tags', [])) if data.get('tags') else "None")
                        
                        with col_right:
                            card("Primary Label", data.get('meaningful_name', data.get('type_description', 'N/A')))
                            card("Last DNS Records", str(len(data.get('last_dns_records', []))))

                        if stats.get('malicious', 0) > 0:
                            st.markdown("---")
                            st.markdown("**Engine Flags:**")
                            results = data.get('last_analysis_results', {})
                            for engine, res in results.items():
                                if res['category'] == 'malicious':
                                    st.error(f"[ {engine} ] : {res['result']}")
                    
                    elif r.status_code == 404:
                        st.info("Indicator not found in VirusTotal database.")
                    else:
                        st.error(f"VT API Error: {r.status_code}")
                except Exception as e:
                    st.error(f"Sandbox Connectivity Failed: {str(e)}")    

# ════════════════════════════════════════════
#  MODULE 8  — GITHUB SECRET SCANNER
# ════════════════════════════════════════════
elif MODULE == "🐙  GitHub Secret Scanner":
    st.markdown("<h1>Repository Extraction</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Hunts for sensitive strings (AWS Keys, Private Keys, .env files) leaked in public GitHub repos.</span>
        </div>
        """, unsafe_allow_html=True
    )

    target_user = st.text_input("Enter GitHub Username/Org:", placeholder="e.g. apple or torvalds")
    
    DANGER_QUERIES = {
        "AWS Keys": "AKIA",
        "Private RSA Keys": "BEGIN RSA PRIVATE KEY",
        "Environment Files": "filename:.env",
        "GitHub Tokens": "ghp_",
        "Config w/ Passwords": "extension:config password"
    }

    if st.button("🚀 Hunt Secrets"):
        if not target_user.strip():
            st.error("Target username is required.")
        else:
            section_header(f"Scanning Repositories for: {target_user}")
            
            headers = {}
            if CONFIG["GITHUB_TOKEN"]:
                headers["Authorization"] = f"token {CONFIG['GITHUB_TOKEN']}"
            
            found_secrets = False
            
            with st.spinner(f"Analyzing {target_user}'s digital trail..."):
                for label, query in DANGER_QUERIES.items():
                    search_url = f"https://api.github.com/search/code?q={query}+user:{target_user}"
                    try:
                        r = httpx.get(search_url, headers=headers, timeout=15.0)
                        if r.status_code == 200:
                            data = r.json()
                            count = data.get('total_count', 0)
                            
                            if count > 0:
                                found_secrets = True
                                st.warning(f"⚠ {label} Detected: {count} potential leaks found.")
                                for item in data.get('items', [])[:3]:
                                    repo_name = item['repository']['full_name']
                                    file_path = item['path']
                                    file_url = item['html_url']
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:8px; margin-bottom:5px;">
                                            <span>
                                                <b>Repo:</b> {repo_name}<br>
                                                <b>File:</b> {file_path}<br>
                                                <a href="{file_url}" target="_blank" style="color:var(--pip-bg); background:var(--pip-green); padding:2px 5px; text-decoration:none; display:inline-block; margin-top:5px;">[ VIEW SOURCE ]</a>
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                        elif r.status_code == 403:
                            st.error("API Rate Limit Exceeded.")
                            break
                        time.sleep(2) 
                    except Exception as e:
                        st.error(f"Search Failed for {label}: {str(e)}")

            if not found_secrets:
                st.success("Clean Scan: No obvious secrets detected.")                    

# ════════════════════════════════════════════
#  MODULE 9 — IMAGE FORENSICS
# ════════════════════════════════════════════
elif MODULE == "🖼️  Image Forensics":
    st.markdown("<h1>EXIF Decoding</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Extracts metadata and pings Nominatim to convert raw GPS data into physical street addresses.</span>
        </div>
        """, unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Drop Evidence Image (JPG/TIFF):", type=["jpg", "jpeg", "tiff"])

    def get_decimal_from_dms(dms, ref):
        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0
        val = float(degrees + minutes + seconds)
        return -val if ref in ['S', 'W'] else val

    async def get_human_address(lat, lon):
        headers = {"User-Agent": "GHOST-OSINT-App/1.1 (Cybersecurity-Research)"}
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                r = await client.get(url, timeout=10.0)
                if r.status_code == 200:
                    return r.json().get('display_name', 'Address not found')
                return f"API Error: HTTP {r.status_code}"
            except Exception as e:
                return f"Connection Error: {str(e)}"

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Evidence", use_container_width=True)
        
        exif_data = image._getexif()
        
        if not exif_data:
            st.error("SYSTEM ERROR: No EXIF metadata found. Image may have been scrubbed.")
        else:
            section_header("Metadata Analysis")
            clean_exif, gps_info = {}, {}
            
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    for t in value:
                        gps_info[GPSTAGS.get(t, t)] = value[t]
                else:
                    clean_exif[decoded] = value

            row1 = st.columns(3)
            with row1[0]: st.metric("Device", clean_exif.get('Model', 'Unknown'))
            with row1[1]: st.metric("Software", str(clean_exif.get('Software', '1.0')))
            with row1[2]: st.metric("Timestamp", str(clean_exif.get('DateTime', 'N/A'))[:10])

            if gps_info and 'GPSLatitude' in gps_info:
                lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
                lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
                
                row2 = st.columns(3)
                with row2[0]: st.metric("Latitude", f"{lat:.6f}")
                with row2[1]: st.metric("Longitude", f"{lon:.6f}")
                with row2[2]: st.metric("GPS Status", "LOCKED", delta_color="normal")

                with st.spinner("Decoding GPS into physical address..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    address = loop.run_until_complete(get_human_address(lat, lon))
                    loop.close()

                st.markdown(f"""
                    <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:15px; margin-top:10px;">
                        <b>[📍] DETECTED ADDRESS:</b><br>
                        <span>{address}</span>
                    </div>
                """, unsafe_allow_html=True)

                maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; margin-top:10px; padding:10px;">[ VIEW SATELLITE IMAGERY ]</button></a>', unsafe_allow_html=True)
            else:
                st.info("No GPS coordinates detected for this asset.")

            with st.expander("📁 View Raw Metadata Dump"):
                for k, v in clean_exif.items():
                    st.write(f"**{k}:** {v}")

# ════════════════════════════════════════════
#  MODULE 10 — FINANCIAL INTELLIGENCE (INDIA)
# ════════════════════════════════════════════
elif MODULE == "💸  Financial Intelligence":
    st.markdown("<h1>Caps & Currency Trace</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Validates IFSC routing codes and analyzes UPI Virtual Payment Addresses (VPA) for the Indian subcontinent.</span>
        </div>
        """, unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["[ 🏦 IFSC Trace ]", "[ 💳 UPI Analysis ]"])

    with tab1:
        ifsc_input = st.text_input("Enter Routing Code (IFSC):", placeholder="e.g. HDFC0000007")
        if st.button("🔎 Trace Branch"):
            if len(ifsc_input) != 11:
                st.error("INVALID FORMAT: IFSC must be exactly 11 characters.")
            else:
                with st.spinner("Accessing RBI Routing Tables..."):
                    try:
                        r = httpx.get(f"https://ifsc.razorpay.com/{ifsc_input.strip()}", timeout=10.0)
                        if r.status_code == 200:
                            data = r.json()
                            section_header(f"Branch Details: {data.get('BANK')}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                card("Bank Name", data.get('BANK'))
                                card("Branch",    data.get('BRANCH'))
                                card("IFSC",      data.get('IFSC'))
                            with c2:
                                card("City",      data.get('CITY'))
                                card("District",  data.get('DISTRICT'))
                                card("State",     data.get('STATE'))
                            
                            st.info(f"📍 Address: {data.get('ADDRESS')}")
                            
                            addr_query = f"{data.get('BANK')} {data.get('BRANCH')} {data.get('CITY')}"
                            maps_url = f"https://www.google.com/maps/search/{addr_query.replace(' ', '+')}"
                            st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; padding:10px;">[ LOCATE ON MAP ]</button></a>', unsafe_allow_html=True)
                        else:
                            st.error(f"IFSC NOT FOUND: Ensure the code is correct (Status {r.status_code}).")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")

    with tab2:
        vpa_input = st.text_input("Enter UPI ID (VPA):", placeholder="username@bank")
        UPI_HANDLES = {
            "okicici": "ICICI Bank", "okaxis": "Axis Bank", "oksbi": "State Bank of India",
            "okhdfcbank": "HDFC Bank", "ybl": "Yes Bank", "ibl": "ICICI Bank (PhonePe)",
            "axl": "Axis Bank (PhonePe)", "paytm": "Paytm Payments Bank",
            "upl": "Union Bank", "postbank": "India Post Payments Bank"
        }

        if st.button("🧪 Analyze VPA"):
            if "@" not in vpa_input:
                st.error("INVALID FORMAT: UPI ID must contain an '@' symbol.")
            else:
                handle = vpa_input.split("@")[-1].lower()
                bank_partner = UPI_HANDLES.get(handle, "Unknown/Custom Provider")
                
                section_header(f"Analysis: {vpa_input}")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("Provider", bank_partner)
                with c2: st.metric("Format Status", "VALID" if len(vpa_input) > 3 else "INVALID")
                
                st.markdown(
                    """
                    <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:10px; margin-top:10px;">
                        <b>[ NOTE ]</b> In India, the handle reveals the processing bank. 
                        To verify the Legal Name, scan the QR below with a banking app.
                    </div>
                    """, unsafe_allow_html=True
                )
                
                upi_link = f"upi://pay?pa={vpa_input}&pn=GHOST_RECON&cu=INR"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={upi_link}"
                st.image(qr_url, caption="Scan to verify Legal Name in app")

# ════════════════════════════════════════════
#  MODULE 11 — DATA BREACH SEARCH (RAPID-API)
# ════════════════════════════════════════════
elif MODULE == "🔐  Data Breach Search":
    st.markdown("<h1>Breach Archives</h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background:var(--pip-dark); border:1px solid var(--pip-green); padding:10px; margin-bottom:20px;">
            <b style="font-size:1.2rem;">> SYSTEM DIRECTIVE:</b><br>
            <span>Querying external dark-web indices for compromised assets via BreachDirectory.</span>
        </div>
        """, unsafe_allow_html=True
    )

    pivot_val = st.session_state.get('pivot_email', "")
    query_input = st.text_input("Enter Identifier:", value=pivot_val, placeholder="e.g. target@example.com")
    
    if pivot_val:
        if st.button("[ Flush Memory ]"):
            st.session_state.pivot_email = ""
            st.rerun()

    if st.button("Execute Override"):
        target = query_input.strip()
        if not target:
            st.error("Input required.")
        else:
            api_url = "https://breachdirectory.p.rapidapi.com" 
            headers = {
                "x-rapidapi-key": CONFIG["BREACH_KEY"],
                "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PIP-OS/7.1"
            }
            query_params = {"func": "auto", "term": target}

            with st.spinner("Decrypting mainframe logs..."):
                try:
                    with httpx.Client(follow_redirects=True, timeout=25.0) as client:
                        r = client.get(api_url, headers=headers, params=query_params)
                    
                    if r.status_code == 200:
                        data = r.json()
                        if data.get('success') or 'result' in data:
                            results = data.get('result', [])
                            total_found = len(results)
                            
                            section_header(f"Compromise Report: {target}")
                            c1, c2 = st.columns(2)
                            with c1: st.metric("Leaks Found", total_found)
                            with c2: st.metric("Status", "COMPROMISED" if total_found > 0 else "SECURE")

                            if total_found > 0:
                                for breach in results:
                                    sources = breach.get('sources', [])
                                    source_name = ", ".join(sources) if isinstance(sources, list) else str(sources)
                                    
                                    st.markdown(
                                        f"""
                                        <div style="background:var(--pip-dark); border:1px dashed var(--pip-green); padding:10px; margin-bottom:8px;">
                                            <b>> DATABASE: {source_name}</b><br>
                                            <span style="font-size:1.1rem;">
                                                Password Leaked: {"[ YES ]" if breach.get('has_password') else "[ NO ]"}<br>
                                                Hash Type: {breach.get('hash_type', 'N/A')}
                                            </span>
                                        </div>
                                        """, unsafe_allow_html=True
                                    )
                            else:
                                st.success("Subject is clean. No records found.")
                        else:
                            st.info("No records match this identifier.")
                    else:
                        st.error(f"System Error {r.status_code}. Connection to archive failed.")
                except Exception as e:
                    st.error(f"Uplink Severed: {str(e)}")
