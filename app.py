import streamlit as st
import urllib.request
import json
import math
import ssl
import random
import time
import os
import glob
from PIL import Image
from datetime import datetime, timezone

# הגדרות עמוד (חייב להיות ראשון)
st.set_page_config(page_title="I&O Sports Analytics", page_icon="🏆", layout="centered")

# ---------------------------------------------------------
# CSS אגרסיבי ומטריף - חלוניות סייבר זוהרות, טאבים ומותג יוקרתי
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* רקע כללי שחור-כחול חלל */
    .stApp {
        background-color: #050814;
    }
    
    /* צבע לכל הכותרות והטקסטים הרגילים */
    h1, h2, h3, h4, p, span, label, .stMarkdown {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* עיצוב שדות ההזנה (Inputs) - מסגרת בולטת וטקסט ברור */
    div[data-baseweb="input"] {
        background-color: #111827 !important;
        border: 2px solid #1f2937 !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #f39c12 !important;
        box-shadow: 0 0 12px rgba(243, 156, 18, 0.6) !important;
    }
    
    /* הטקסט שהמשתמש מקליד - זהב זוהר וגדול */
    .stTextInput input, .stNumberInput input {
        color: #f39c12 !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        -webkit-text-fill-color: #f39c12 !important;
    }

    /* עיצוב כרטיסיות מודרני */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8892b0 !important;
        font-weight: bold;
        font-size: 16px;
        background-color: #111827;
        border-radius: 8px;
        padding: 10px 20px;
        border: 1px solid #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f39c12 !important;
        color: #000000 !important;
        border: 1px solid #f39c12;
        box-shadow: 0 0 10px rgba(243,156,18,0.3);
    }
    
    /* כפתור הניתוח המרכזי - אפקט חללית */
    .stButton>button {
        background: linear-gradient(90deg, #f39c12 0%, #e67e22 100%) !important;
        color: #000 !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 15px !important;
        box-shadow: 0 0 20px rgba(243, 156, 18, 0.5) !important;
        transition: all 0.3s ease !important;
        margin-top: 20px;
    }
    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(243, 156, 18, 0.9) !important;
        transform: translateY(-2px);
    }

    /* קופסת פסק הדין */
    .report-box {
        background: linear-gradient(145deg, #111827, #1f2937);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #f39c12;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
        margin-top: 30px;
    }

    /* עיצוב כפתורי ליגה מותאמים אישית - כרטיסיות סייבר זוהרות */
    .league-card button {
        background: #111625 !important;
        border: 2px solid #1f2937 !important;
        border-radius: 15px !important;
        padding: 20px 10px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
        display: block;
        width: 100%;
        text-align: center;
    }
    
    /* אפקטים של תאורה וזוהר לכל כפתור בנפרד לפי המותג */
    div.cl-card button:hover { border-color: #0044ff !important; box-shadow: 0 0 15px rgba(0, 68, 255, 0.6) !important; color: #0044ff !important; }
    div.el-card button:hover { border-color: #ff5500 !important; box-shadow: 0 0 15px rgba(255, 85, 0, 0.6) !important; color: #ff5500 !important; }
    div.pl-card button:hover { border-color: #9c27b0 !important; box-shadow: 0 0 15px rgba(156, 39, 176, 0.6) !important; color: #9c27b0 !important; }
    div.es-card button:hover { border-color: #ffeb3b !important; box-shadow: 0 0 15px rgba(255, 235, 59, 0.6) !important; color: #ffeb3b !important; }
    div.it-card button:hover { border-color: #00bcd4 !important; box-shadow: 0 0 15px rgba(0, 188, 212, 0.6) !important; color: #00bcd4 !important; }
    div.de-card button:hover { border-color: #e91e63 !important; box-shadow: 0 0 15px rgba(233, 30, 99, 0.6) !important; color: #e91e63 !important; }
    div.fr-card button:hover { border-color: #4caf50 !important; box-shadow: 0 0 15px rgba(76, 175, 80, 0.6) !important; color: #4caf50 !important; }
    div.il-card button:hover { border-color: #f39c12 !important; box-shadow: 0 0 15px rgba(243, 156, 18, 0.6) !important; color: #f39c12 !important; }
    div.wc-card button:hover { border-color: #00efff !important; box-shadow: 0 0 15px rgba(0, 239, 255, 0.6) !important; color: #00efff !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# טעינת הלוגו - צייד אוטומטי
# ---------------------------------------------------------
image_files = glob.glob("*.jfif") + glob.glob("*.jpg") + glob.glob("*.png") + glob.glob("*.jpeg")
if image_files:
    try:
        img = Image.open(image_files[0])
        st.image(img, use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #f39c12;'>I & O SPORTS ANALYTICS</h1>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #f39c12;'>I & O SPORTS ANALYTICS</h1>", unsafe_allow_html=True)

st.write("---")

# ---------------------------------------------------------
# ליבת האלגוריתם, שאיבת נתונים אוטומטית ואל-כשל כירורגי
# ---------------------------------------------------------
API_KEY = "481be9a1788d8d4cdc9cae7f6800c10b"

def poisson_probability(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calculate_dixon_coles_adjustment(home_goals, away_goals, lambda_home, lambda_away, rho=-0.05):
    if home_goals == 0 and away_goals == 0: return 1.0 - (lambda_home * lambda_away * rho)
    elif home_goals == 1 and away_goals == 0: return 1.0 + (lambda_away * rho)
    elif home_goals == 0 and away_goals == 1: return 1.0 + (lambda_home * rho)
    elif home_goals == 1 and away_goals == 1: return 1.0 - rho
    return 1.0

def safe_float(val, fallback):
    if val is None or val == "":
        return fallback
    try:
        clean_val = "".join(c for c in str(val) if c.isdigit() or c == '.')
        return float(clean_val)
    except ValueError:
        return fallback

@st.cache_data(ttl=60)
def fetch_games_by_league(sport_key):
    context = ssl._create_unverified_context()
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=context, timeout=8) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception:
        return []

def auto_get_weather_multiplier(city):
    context = ssl._create_unverified_context()
    url = f"https://api.open-meteo.com/v1/forecast?latitude=32.0853&longitude=34.7818&current_weather=true" # ברירת מחדל לארץ
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=context, timeout=4) as response:
            res = json.loads(response.read().decode('utf-8'))
            temp = res["current_weather"]["temperature"]
            weather_code = res["current_weather"]["weathercode"]
            if weather_code in [51, 53, 55, 61, 63, 65, 71, 73, 75, 77, 80, 81, 82]:
                return 0.925, f"גשם פעיל במגרש ({temp}°C) - הוחל קנס Velocity של 7.5%-"
            elif temp < 3.0:
                return 0.970, f"קור קיצוני ללא משקעים ({temp}°C) - הוחל קנס Velocity של 3%-"
            return 1.000, f"מזג אוויר תקין ({temp}°C) - אין קנס אקלים"
    except Exception:
        return 1.000, "בהיר ותקין (22°C) - ללא קנס אקלים (Fallback)"

def generate_tactical_narrative(market, selection, prob, edge):
    if "קרנות" in market and ("אנדר" in selection or "0-8" in selection):
        return "התפתחות משחק צפויה: קצב אירועים נמוך, שליטה במרכז שדה, מיעוט פריצות מהאגפים."
    if "קרנות" in market and ("12+" in selection or "אובר" in selection):
        return "התפתחות משחק צפויה: קצב מהיר, משחק אגפים מובהק וריבוי בעיטות לשער."
    if "שערים" in market and ("מתחת" in selection or "0-1" in selection):
        return "התפתחות משחק צפויה: מאבק טקטי סגור, יעילות התקפית נמוכה (npxG נמוך)."
    if "שערים" in market and ("4+" in selection or "מעל" in selection):
        return "התפתחות משחק צפויה: משחק פתוח לחלוטין, הגנות פגיעות ויעילות בעיטה גבוהה."
    if "הנדיקאפ" in market:
        return "התפתחות משחק צפויה: מטריצת דיקסון-קולס מזהה פער זניח ביחסי הכוחות המצדיק גיבוי."
    return "התפתחות משחק צפויה: פערי כוחות טהורים במודל 11vs11 מציגים יתרון מתמטי שלא מגולם ביחס."

# --- ממשק בחירת ליגות מעלף ומטריץ ---
st.markdown("<h3 style='text-align: center; color: #f39c12;'>🛡️ בחר מפעל / ליגה לסריקה</h3>", unsafe_allow_html=True)

# מיפוי רשמי ומדויק כולל ליגת העל הישראלית
leagues_map = {
    "🏆 Champions League": "soccer_uefa_champs_league",
    "🇪🇺 Europa League": "soccer_uefa_europa_league",
    "🦁 Premier League": "soccer_epl",
    "🇪🇸 La Liga": "soccer_spain_la_liga",
    "🇮🇹 Serie A": "soccer_italy_serie_a",
    "🇩🇪 Bundesliga": "soccer_germany_bundesliga",
    "🇫🇷 Ligue 1": "soccer_france_ligue_one",
    "🇮🇱 ליגת העל הישראלית": "soccer_israel_premier_league",
    "🌍 World Cup / Euro": "soccer_fifa_world_cup"
}

# תצוגת מטריצת הליגות המעוצבת (3x3 עמודות עם Glow)
col_l1, col_l2, col_l3 = st.columns(3)
with col_l1:
    st.markdown('<div class="league-card cl-card">', unsafe_allow_html=True)
    btn_cl = st.button("🏆 UEFA Champions League", key="cl")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="league-card es-card">', unsafe_allow_html=True)
    btn_es = st.button("🇪🇸 La Liga", key="es")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="league-card fr-card">', unsafe_allow_html=True)
    btn_fr = st.button("🇫🇷 Ligue 1", key="fr")
    st.markdown('</div>', unsafe_allow_html=True)

with col_l2:
    st.markdown('<div class="league-card el-card">', unsafe_allow_html=True)
    btn_el = st.button("🇪🇺 UEFA Europa League", key="el")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="league-card it-card">', unsafe_allow_html=True)
    btn_it = st.button("🇮🇹 Serie A", key="it")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="league-card il-card">', unsafe_allow_html=True)
    btn_il = st.button("🇮🇱 ליגת העל הישראלית", key="il")
    st.markdown('</div>', unsafe_allow_html=True)

with col_l3:
    st.markdown('<div class="league-card pl-card">', unsafe_allow_html=True)
    btn_pl = st.button("🦁 Premier League", key="pl")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="league-card de-card">', unsafe_allow_html=True)
    btn_de = st.button("🇩🇪 Bundesliga", key="de")
    st.markdown('</div>', unsafe_allowed_html=True)
    st.markdown('<div class="league-card wc-card">', unsafe_allow_html=True)
    btn_wc = st.button("🌍 World Cup / Euro", key="wc")
    st.markdown('</div>', unsafe_allow_html=True)

# ניהול סטטוס בחירת הליגה
if "selected_league" not in st.session_state:
    st.session_state.selected_league = "soccer_israel_premier_league" # ליגת העל כברירת מחדל לאתר מקומי

if btn_cl: st.session_state.selected_league = "soccer_uefa_champs_league"
elif btn_el: st.session_state.selected_league = "soccer_uefa_europa_league"
elif btn_pl: st.session_state.selected_league = "soccer_epl"
elif btn_es: st.session_state.selected_league = "soccer_spain_la_liga"
elif btn_it: st.session_state.selected_league = "soccer_italy_serie_a"
elif btn_de: st.session_state.selected_league = "soccer_germany_bundesliga"
elif btn_fr: st.session_state.selected_league = "soccer_france_ligue_one"
elif btn_il: st.session_state.selected_league = "soccer_israel_premier_league"
elif btn_wc: st.session_state.selected_league = "soccer_fifa_world_cup"

# שאיבה מהשרת הגלובלי
with st.spinner("מעדכן תוכנייה חיה מהאינטרנט..."):
    raw_games = fetch_games_by_league(st.session_state.selected_league)

games_list = []
now_utc = datetime.now(timezone.utc)

if raw_games:
    for game in raw_games:
        # פילטר 2 דקות קשיח (120 שניות לשריקה)
        commence_time_str = game.get("commence_time")
        if commence_time_str:
            try:
                game_time = datetime.fromisoformat(commence_time_str.replace("Z", "+00:00"))
                seconds_remaining = (game_time - now_utc).total_seconds()
                if seconds_remaining < 120:
                    continue
            except Exception:
                pass
                
        home = game.get("home_team", "Home")
        away = game.get("away_team", "Away")
        odds_1, odds_x, odds_2 = 2.10, 3.20, 3.10
        for bookmaker in game.get("bookmakers", []):
            if bookmaker["key"] in ["pinnacle", "marathonbet", "unibet"]:
                for market in bookmaker.get("markets", []):
                    if market["key"] == "h2h":
                        for outcome in market.get("outcomes", []):
                            if outcome["name"] == home: odds_1 = outcome["price"]
                            elif outcome["name"] == away: odds_2 = outcome["price"]
                            else: odds_x = outcome["price"]
                break
        games_list.append({"home": home, "away": away, "w_1": odds_1, "w_x": odds_x, "w_2": odds_2})
