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

    /* ⚽ סגנון תמונות עיגולי כדורגל ללא לחצני HTML שבירים */
    .soccer-ball-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #1f2937;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: 0.3s;
    }
    .active-ball-img {
        border-color: #f39c12 !important;
        box-shadow: 0 0 18px rgba(243, 156, 18, 0.8) !important;
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

def auto_get_weather_multiplier(city):
    context = ssl._create_unverified_context()
    url = f"https://api.open-meteo.com/v1/forecast?latitude=32.0853&longitude=34.7818&current_weather=true"
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
        return "התפתחות משחק צפויה:
