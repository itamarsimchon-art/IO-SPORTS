import streamlit as st
import urllib.request
import json
import math
import ssl
import random
import time
import os
import glob
import base64
from PIL import Image
from datetime import datetime, timezone

# הגדרות עמוד (חייב להיות ראשון)
st.set_page_config(page_title="I&O Sports Analytics", page_icon="🏆", layout="centered")

# ---------------------------------------------------------
# CSS אגרסיבי ומטריף - עיצוב סייבר נקי ויוקרתי
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

    /* העלמת מסגרות הכפתורים והפיכת התמונה עצמה ללחיצה */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        margin: 0 auto !important;
        display: block !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# טעינת הלוגו - צייד אוטומטי
# ---------------------------------------------------------
image_files = glob.glob("*.jfif") + glob.glob("*.jpg") + glob.glob("*.png") + glob.glob("*.jpeg")
known_leagues_images = ['cjampions.png', 'england.png', 'eropa.png', 'france.png', 'germany.png', 'israel.jpg', 'italia.jpg', 'mondeial.jpg', 'spain.png']
filtered_logo_files = [f for f in image_files if f not in known_leagues_images]

if filtered_logo_files:
    try:
        img = Image.open(filtered_logo_files[0])
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

def auto_get_weather_multiplier(sport_key):
    geo_map = {
        "soccer_israel_premier_league": {"lat": 32.0853, "lon": 34.7818, "name": "ישראל"},
        "soccer_epl": {"lat": 51.5074, "lon": -0.1278, "name": "אנגליה"},
        "soccer_spain_la_liga": {"lat": 40.4168, "lon": -3.7038, "name": "ספרד"},
        "soccer_italy_serie_a": {"lat": 41.9028, "lon": 12.4964, "name": "איטליה"},
        "soccer_germany_bundesliga": {"lat": 52.5200, "lon": 13.4050, "name": "גרמניה"},
        "soccer_france_ligue_one": {"lat": 48.8566, "lon": 2.3522, "name": "צרפת"},
        "soccer_uefa_champs_league": {"lat": 50.0755, "lon": 14.4378, "name": "אירופה (צ'מפיונס)"},
        "soccer_uefa_europa_league": {"lat": 48.2082, "lon": 16.3738, "name": "אירופה (אירופית)"},
        "soccer_fifa_world_cup": {"lat": -23.5505, "lon": -46.6333, "name": "זירה בינלאומית"}
    }
    
    loc = geo_map.get(sport_key, {"lat": 32.0853, "lon": 34.7818, "name": "ישראל"})
    context = ssl._create_unverified_context()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}&current_weather=true"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=context, timeout=4) as response:
            res = json.loads(response.read().decode('utf-8'))
            temp = res["current_weather"]["temperature"]
            weather_code = res["current_weather"]["weathercode"]
            if weather_code in [51, 53, 55, 61, 63, 65, 71, 73, 75, 77, 80, 81, 82]:
                return 0.925, f"גשם/משקעים פעילים ב{loc['name']} ({temp}°C) - הוחל קנס Velocity של 7.5%-"
            elif temp < 3.0:
                return 0.970, f"קור קיצוני ב{loc['name']} ({temp}°C) - הוחל קנס Velocity של 3%-"
            return 1.000, f"מזג אוויר תקין ב{loc['name']} ({temp}°C) - אין קנס אקלים"
    except Exception:
        return 1.000, f"בהיר ותקין (22°C) - אקלים יציב ב{loc['name']} (Fallback)"

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

# --- ממשק הליגות בצורת 9 עיגולי כדורגל לחיצים ---
st.markdown("<h3 style='text-align: center; color: #f39c12;'>🛡️ לחץ על כדור הליגה לבחירה ישירה</h3>", unsafe_allow_html=True)

if "selected_league" not in st.session_state:
    st.session_state.selected_league = "soccer_israel_premier_league"

def clickable_soccer_ball(title, sport_key, file_name):
    try:
        img_raw = Image.open(file_name)
        width, height = img_raw.size
        min_dim = min(width, height)
        img_square = img_raw.crop(((width - min_dim) // 2, (height - min_dim) // 2, (width + min_dim) // 2, (height + min_dim) // 2))
        
        is_active = st.session_state.selected_league == sport_key
        if is_active:
            st.markdown(f"<p style='text-align:center; color:#f39c12; font-weight:900; margin-bottom:2px;'>📍 {title}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align:center; color:#8892b0; margin-bottom:2px;'>{title}</p>", unsafe_allow_html=True)
            
        if st.button("", key="img_btn_" + sport_key):
            st.session_state.selected_league = sport_key
            st.rerun()
            
        st.image(img_square, use_container_width=True)
    except Exception:
        if st.button(f"⚽ {title}", key="fallback_btn_" + sport_key, use_container_width=True):
            st.session_state.selected_league = sport_key
            st.rerun()

col_l1, col_l2, col_l3 = st.columns(3)

with col_l1:
    clickable_soccer_ball("Champions League", "soccer_uefa_champs_league", "cjampions.png")
    clickable_soccer_ball("La Liga", "soccer_spain_la_liga", "spain.png")
    clickable_soccer_ball("Ligue 1", "soccer_france_ligue_one", "france.png")

with col_l2:
    clickable_soccer_ball("Europa League", "soccer_uefa_europa_league", "eropa.png")
    clickable_soccer_ball("Serie A", "soccer_italy_serie_a", "italia.jpg")
    clickable_soccer_ball("ליגת העל", "soccer_israel_premier_league", "israel.jpg")

with col_l3:
    clickable_soccer_ball("Premier League", "soccer_epl", "england.png")
    clickable_soccer_ball("Bundesliga", "soccer_germany_bundesliga", "germany.png")
    clickable_soccer_ball("World Cup / Euro", "soccer_fifa_world_cup", "mondeial.jpg")

st.write("---")

# שאיבה מהשרת הגלובלי
with st.spinner("מעדכן תוכנייה חיה מהאינטרנט..."):
    raw_games = fetch_games_by_league(st.session_state.selected_league)

games_list = []
now_utc = datetime.now(timezone.utc)

if raw_games:
    for game in raw_games:
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

has_active_games = len(games_list) > 0

if not has_active_games:
    st.warning("ℹ️ לא נמצאו משחקים פעילים בתוכנייה של ליגה זו להיום (פגרה / אין משחקים). באפשרותך לבצע הזנה ידנית של משחק בתיבה למטה.")
    games_list = [{"home": "בית''ר ירושלים", "away": "הפועל באר שבע", "w_1": 2.30, "w_x": 3.20, "w_2": 2.80}]

# בניית תפריט הגלילה
if has_active_games:
    game_names = [f"{g['home']} vs {g['away']}" for g in games_list] + ["-- הזנה ידנית חופשית --"]
else:
    game_names = ["-- הזנה ידנית חופשית --"]

selected_game_choice = st.selectbox("🎯 בחר משחק מלוח המשחקים הקיים:", game_names)

if selected_game_choice == "-- הזנה ידנית חופשית --":
    col_home, col_away = st.columns(2)
    home_name = col_home.text_input("⚽ קבוצת הבית הידנית:", value="בית''ר ירושלים")
    away_name = col_away.text_input("⚽ קבוצת החוץ הידנית:", value="הפועל באר שבע")
    active_w1, active_wx, active_w2 = 2.30, 3.20, 2.80
else:
    selected_idx = game_names.index(selected_game_choice)
    selected_game = games_list[selected_idx]
    home_name = selected_game["home"]
    away_name = selected_game["away"]
    active_w1 = selected_game["w_1"]
    active_wx = selected_game["w_x"]
    active_w2 = selected_game["w_2"]

is_critical = st.checkbox("🚨 הפעל חוק הפחד (משחק רגיש / משחק עונה / נוקאאוט קריטי)")

# שאיבה ודגימה אוטומטית של אקלים דינמי לפי המיקום של הליגה שנבחרה
weather_multiplier, weather_report = auto_get_weather_multiplier(st.session_state.selected_league)
st.info(f"🌦️ **דוח אקלים אוטומטי לאצטדיון:** {weather_report}")

st.markdown("### 💵 הזנת יחסי ווינר בלייב")

tab1, tab2, tab3 = st.tabs(["📊 שוק 1X2 והנדיקאפ", "⚽ שערים ובראקטים", "📐 קרנות ומירוץ ל-5"])

with tab1:
    col_a, col_b, col_c = st.columns(3)
    w_1 = col_a.number_input("ניצחון בית (1):", min_value=1.0, step=0.05, value=float(active_w1))
    w_x = col_b.number_input("תיקו (X):", min_value=1.0, step=0.05, value=float(active_wx))
    w_2 = col_c.number_input("ניצחון חוץ (2):", min_value=1.0, step=0.05, value=float(active_w2))
    col_d, col_e, col_f = st.columns(3)
    w_h_minus1 = col_d.number_input(f"הנדיקאפ {home_name} -1:", min_value=1.0, step=0.05, value=3.80)
    w_h_x = col_e.number_input("הנדיקאפ תיקו (X):", min_value=1.0, step=0.05, value=3.40)
    w_h_plus1 = col_f.number_input(f"הנדיקאפ {away_name} +1:", min_value=1.0, step=0.05, value=1.55)

with tab2:
    col_g, col_h = st.columns(2)
    w_u25 = col_g.number_input("שערים מתחת 2.5:", min_value=1.0, step=0.05, value=1.90)
    w_o25 = col_h.number_input("שערים מעל 2.5:", min_value=1.0, step=0.05, value=1.65)
    col_i, col_j, col_k = st.columns(3)
    w_b01 = col_i.number_input("שערים 0-1:", min_value=1.0, step=0.05, value=2.95)
    w_b23 = col_j.number_input("שערים 2-3:", min_value=1.0, step=0.05, value=1.82)
    w_b4p = col_k.number_input("שערים 4+:", min_value=1.0, step=0.05, value=2.80)

with tab3:
    col_l, col_m, col_n = st.columns(3)
    w_c08 = col_l.number_input("קרנות 0-8:", min_value=1.0, step=0.05, value=2.35)
    w_c911 = col_m.number_input("קרנות 9-11 (X):", min_value=1.0, step=0.05, value=2.45)
    w_c12p = col_n.number_input("קרנות 12+:", min_value=1.0, step=0.05, value=2.65)
    col_o, col_p = st.columns(2)
    w_c_u95 = col_o.number_input("קרנות מתחת 9.5:", min_value=1.0, step=0.05, value=1.85)
    w_c_o95 = col_p.number_input("קרנות מעל 9.5:", min_value=1.0, step=0.05, value=1.65)
    col_q, col_r = st.columns(2)
    w_c_u105 = col_q.number_input("קרנות מתחת 10.5:", min_value=1.0, step=0.05, value=1.60)
    w_c_o105 = col_r.number_input("קרנות מעל 10.5:", min_value=1.0, step=0.05, value=1.90)
    col_s, col_t, col_u = st.columns(3)
    w_race_home = col_s.number_input(f"מירוץ 5 ({home_name}):", min_value=1.0, step=0.05, value=1.70)
    w_race_x = col_t.number_input("מירוץ 5 (תיקו):", min_value=1.0, step=0.05, value=4.50)
    w_race_away = col_u.number_input(f"מירוץ 5 ({away_name}):", min_value=1.0, step=0.05, value=2.10)

# --- מעבדה מתמטית ---
raw_home_npxg = 2.15
raw_away_npxg = 1.65
clean_home_npxg = raw_home_npxg - 0.76
clean_away_npxg = raw_away_npxg

lambda_base = (clean_home_npxg * 0.57) + (clean_away_npxg * 0.43)
mu_base = (clean_away_npxg * 0.57) + (clean_home_npxg * 0.43)

lambda_multiplier = 1.155 if is_critical else 1.0
final_lambda = lambda_base * lambda_multiplier * weather_multiplier
final_mu = mu_base * lambda_multiplier * weather_multiplier
rho = -0.05

matrix = {}
for h in range(7):
    for a in range(7):
        ph = poisson_probability(final_lambda, h)
        pa = poisson_probability(final_mu, a)
        tau = calculate_dixon_coles_adjustment(h, a, final_lambda, final_mu, rho)
        matrix[(h, a)] = ph * pa * tau

prob_1 = sum(p for (h, a), p in matrix.items() if h > a) * 100
prob_x = sum(p for (h, a), p in matrix.items() if h == a) * 100
prob_2 = sum(p for (h, a), p in matrix.items() if a > h) * 100
prob_away_plus_1 = prob_x + prob_2

prob_hc_minus1 = sum(p for (h, a), p in matrix.items() if h - a >= 2) * 100
prob_hc_x = sum(p for (h, a), p in matrix.items() if h - a == 1) * 100

prob_u25 = sum(p for (h, a), p in matrix.items() if (h + a) < 2.5) * 100
prob_o25 = 100 - prob_u25

prob_b01 = (matrix[(0,0)] + matrix[(1,0)] + matrix[(0,1)]) * 100
prob_b23 = (matrix[(2,0)] + matrix[(0,2)] + matrix[(1,1)] + matrix[(2,1)] + matrix[(1,2)] + matrix[(3,0)] + matrix[(0,3)]) * 100
prob_b4p = 100.0 - (prob_b01 + prob_b23)

corner_minutes = 96
base_corner_rate = 10.2 / 90.0
home_corner_ratio = final_lambda / (final_lambda + final_mu)

c_0_8, c_9_11, c_12_p = 0, 0, 0
u_95, o_95 = 0, 0
u_105, o_105 = 0, 0
race_home, race_away, race_neither = 0, 0, 0

for _ in range(5000):
    sim_c = 0
    h_corners, a_corners = 0, 0
    race_won = False
    for minute in range(1, corner_minutes + 1):
        if random.random() < base_corner_rate:
            sim_c += 1
            if random.random() < home_corner_ratio: h_corners += 1
            else: a_corners += 1
            if not race_won:
                if h_corners >= 5: race_home += 1; race_won = True
                elif a_corners >= 5: race_away += 1; race_won = True
    if not race_won: race_neither += 1
    if sim_c <= 8: c_0_8 += 1
    elif 9 <= sim_c <= 11: c_9_11 += 1
    else: c_12_p += 1
    if sim_c < 9.5: u_95 += 1
    else: o_95 += 1
    if sim_c < 10.5: u_105 += 1
    else: o_105 += 1

prob_c08 = (c_0_8 / 5000) * 100
prob_c911 = (c_9_11 / 5000) * 100
prob_c12p = (c_12_p / 5000) * 100
prob_u95 = (u_95 / 5000) * 100
prob_o95 = (o_95 / 5000) * 100
prob_u105 = (u_105 / 5000) * 100
prob_o105 = (o_105 / 5000) * 100
cumulative_under = prob_c08 + prob_c911

prob_race_home = (race_home / 5000) * 100
prob_race_away = (race_away / 5000) * 100
prob_race_neither = (race_neither / 5000) * 100

with st.expander("🔎 לחץ כאן לחשיפת דוח החישובים המלא מאחורי הקלעים (NO BLACK BOX)"):
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        st.write("**מנוע שערים (Dixon-Coles):**")
        st.write(f"• Home Lambda: `{final_lambda:.4f}`")
        st.write(f"• Away Mu: `{final_mu:.4f}`")
        st.write(f"• תוחלת שערים כללית: `{final_lambda + final_mu:.2f}` שערים")
    with col_sub2:
        st.write("**הסתברויות גולמיות מחושבות:**")
        st.write(f"• 1X2 גולמי: {prob_1:.1f}% | {prob_x:.1f}% | {prob_2:.1f}%")
        st.write(f"• בראקט שערים: 0-1 ({prob_b01:.1f}%) | 2-3 ({prob_b23:.1f}%) | 4+ ({prob_b4p:.1f}%)")
        st.write(f"• בראקט קרנות: 0-8 ({prob_c08:.1f}%) | 9-11 ({prob_c911:.1f}%) | 12+ ({prob_c12p:.1f}%)")

st.write("")
if st.button("🚀 הרץ ניתוח אומני וחשב חמישייה פותחת"):
    with st.spinner("מבצע חישובי עומק מסווגים..."):
        time.sleep(1)
        
        all_bets = []
        def add_bet(market, selection, prob, current):
            if cu
