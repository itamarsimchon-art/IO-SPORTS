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

# הגדרות עמוד (חייב להיות ראשון)
st.set_page_config(page_title="I&O Sports Analytics", page_icon="🏆", layout="centered")

# ---------------------------------------------------------
# CSS אגרסיבי - עיצוב סייבר יוקרתי, שדות מוארים וטקסט בולט
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
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# טעינת הלוגו - צייד אוטומטי (מחפש כל קובץ תמונה בתיקייה)
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
# ליבת האלגוריתם והממשק
# ---------------------------------------------------------
def run_monte_carlo_corners():
    base_rate = 10.5 
    simulations = 10000
    c08, c911, c12p, over85, over95, over105 = 0, 0, 0, 0, 0, 0
    for _ in range(simulations):
        total_corners = sum(1 for _ in range(90) if random.random() < (base_rate / 90))
        if total_corners <= 8: c08 += 1
        elif 9 <= total_corners <= 11: c911 += 1
        else: c12p += 1
        if total_corners > 8.5: over85 += 1
        if total_corners > 9.5: over95 += 1
        if total_corners > 10.5: over105 += 1
    return ((c08/simulations)*100, (c911/simulations)*100, (c12p/simulations)*100,
            (over85/simulations)*100, (over95/simulations)*100, (over105/simulations)*100)

col1, col2 = st.columns(2)
with col1:
    home_name = st.text_input("⚽ קבוצת הבית:", value="אנגליה")
with col2:
    away_name = st.text_input("⚽ קבוצת החוץ:", value="ארגנטינה")

is_critical = st.checkbox("🚨 הפעל חוק הפחד (משחק רגיש / גמר / מאבק קריטי)")

st.markdown("### 💵 הזנת יחסי ווינר בלייב")

tab1, tab2, tab3 = st.tabs(["📊 שוק 1X2 והנדיקאפ", "⚽ שערים ובראקטים", "📐 קרנות ומירוץ ל-5"])

with tab1:
    col_a, col_b, col_c = st.columns(3)
    w_1 = col_a.number_input("ניצחון בית (1):", min_value=1.0, step=0.05, value=None)
    w_x = col_b.number_input("תיקו (X):", min_value=1.0, step=0.05, value=None)
    w_2 = col_c.number_input("ניצחון חוץ (2):", min_value=1.0, step=0.05, value=None)
    col_d, col_e, col_f = st.columns(3)
    w_h_minus1 = col_d.number_input(f"הנדיקאפ {home_name} -1:", min_value=1.0, step=0.05, value=None)
    w_h_x = col_e.number_input("הנדיקאפ תיקו (X):", min_value=1.0, step=0.05, value=None)
    w_h_plus1 = col_f.number_input(f"הנדיקאפ {away_name} +1:", min_value=1.0, step=0.05, value=None)

with tab2:
    col_g, col_h = st.columns(2)
    w_u25 = col_g.number_input("שערים מתחת 2.5:", min_value=1.0, step=0.05, value=None)
    w_o25 = col_h.number_input("שערים מעל 2.5:", min_value=1.0, step=0.05, value=None)
    col_i, col_j, col_k = st.columns(3)
    w_b01 = col_i.number_input("שערים 0-1:", min_value=1.0, step=0.05, value=None)
    w_b23 = col_j.number_input("שערים 2-3:", min_value=1.0, step=0.05, value=None)
    w_b4p = col_k.number_input("שערים 4+:", min_value=1.0, step=0.05, value=None)

with tab3:
    col_l, col_m, col_n = st.columns(3)
    w_c08 = col_l.number_input("קרנות 0-8:", min_value=1.0, step=0.05, value=None)
    w_c911 = col_m.number_input("קרנות 9-11 (X):", min_value=1.0, step=0.05, value=None)
    w_c12p = col_n.number_input("קרנות 12+:", min_value=1.0, step=0.05, value=None)
    col_o, col_p = st.columns(2)
    w_c_u95 = col_o.number_input("קרנות מתחת 9.5:", min_value=1.0, step=0.05, value=None)
    w_c_o95 = col_p.number_input("קרנות מעל 9.5:", min_value=1.0, step=0.05, value=None)
    col_q, col_r = st.columns(2)
    w_c_u105 = col_q.number_input("קרנות מתחת 10.5:", min_value=1.0, step=0.05, value=None)
    w_c_o105 = col_r.number_input("קרנות מעל 10.5:", min_value=1.0, step=0.05, value=None)
    col_s, col_t, col_u = st.columns(3)
    w_race_home = col_s.number_input(f"מירוץ 5 ({home_name}):", min_value=1.0, step=0.05, value=None)
    w_race_x = col_t.number_input("מירוץ 5 (תיקו):", min_value=1.0, step=0.05, value=None)
    w_race_away = col_u.number_input(f"מירוץ 5 ({away_name}):", min_value=1.0, step=0.05, value=None)

st.write("")
if st.button("🚀 הרץ ניתוח אומני וחשב חמישייה פותחת"):
    with st.spinner("מבצע חישובי עומק מסווגים..."):
        time.sleep(1)
        lambda_home, mu_away, rho = 1.85, 1.25, -0.05
        if is_critical: lambda_home *= 0.85; mu_away *= 0.85
            
        def get_dc_prob(h, a, l, m, r):
            ph = (math.exp(-l) * (l**h)) / math.factorial(h)
            pa = (math.exp(-m) * (m**a)) / math.factorial(a)
            corr = 1.0
            if h==0 and a==0: corr = 1 - (l*m*r)
            elif h==1 and a==0: corr = 1 + (m*r)
            elif h==0 and a==1: corr = 1 + (l*r)
            elif h==1 and a==1: corr = 1 - r
            return ph * pa * corr

        prob_1 = sum(get_dc_prob(h, a, lambda_home, mu_away, rho) for h in range(6) for a in range(6) if h > a) * 100
        prob_x = sum(get_dc_prob(h, a, lambda_home, mu_away, rho) for h in range(6) for a in range(6) if h == a) * 100
        prob_2 = sum(get_dc_prob(h, a, lambda_home, mu_away, rho) for h in range(6) for a in range(6) if a > h) * 100
        prob_away_plus_1 = prob_x + prob_2
        prob_u25 = sum(get_dc_prob(h, a, lambda_home, mu_away, rho) for h in range(6) for a in range(6) if (h + a) < 2.5) * 100
        prob_o25 = 100 - prob_u25
        prob_b01 = sum(get_dc_prob(h, a, lambda_home, mu_away, rho) for h in range(6) for a in range(6) if 0 <= (h + a) <= 1) * 100
        prob_b23 = sum(get_dc_prob(h, a, lambda_home, mu_away, rho) for h in range(6) for a in range(6) if 2 <= (h + a) <= 3) * 100
        prob_b4p = sum(get_dc_prob(h, a, lambda_home, mu_away, rho) for h in range(6) for a in range(6) if (h + a) >= 4) * 100

        prob_c08, prob_c911, prob_c12p, prob_co85, prob_co95, prob_co105 = run_monte_carlo_corners()
        prob_cu95, prob_cu105 = 100 - prob_co95, 100 - prob_co105
        prob_race_home, prob_race_x, prob_race_away = 45.0, 10.0, 45.0

        all_bets = []
        def add_bet(market, selection, prob, current):
            if current:
                edge = prob - ((1 / current) * 100)
                if edge > 0: all_bets.append({"market": market, "selection": selection, "prob": prob, "odds": current, "edge": edge})

        add_bet("1X2", f"{home_name}", prob_1, w_1)
        add_bet("1X2", "תיקו", prob_x, w_x)
        add_bet("1X2", f"{away_name}", prob_2, w_2)
        add_bet("הנדיקאפ", f"{home_name} -1", prob_1, w_h_minus1)
        add_bet("הנדיקאפ", "X", prob_x, w_h_x)
        add_bet("הנדיקאפ", f"{away_name} +1", prob_away_plus_1, w_h_plus1)
        add_bet("שערים", "מתחת 2.5", prob_u25, w_u25)
        add_bet("שערים", "מעל 2.5", prob_o25, w_o25)
        add_bet("בראקט שערים", "0-1", prob_b01, w_b01)
        add_bet("בראקט שערים", "2-3", prob_b23, w_b23)
        add_bet("בראקט שערים", "4+", prob_b4p, w_b4p)
        add_bet("בראקט קרנות", "0-8", prob_c08, w_c08)
        add_bet("בראקט קרנות", "12+", prob_c12p, w_c12p)
        add_bet("קרנות 9.5", "מתחת", prob_cu95, w_c_u95)
        add_bet("קרנות 9.5", "מעל", prob_co95, w_c_o95)
        add_bet("קרנות 10.5", "מתחת", prob_cu105, w_c_u105)
        add_bet("קרנות 10.5", "מעל", prob_co105, w_c_o105)
        add_bet("מירוץ קרנות", f"{home_name}", prob_race_home, w_race_home)
        add_bet("מירוץ קרנות", "תיקו", prob_race_x, w_race_x)
        add_bet("מירוץ קרנות", f"{away_name}", prob_race_away, w_race_away)

        all_bets.sort(key=lambda x: x["edge"], reverse=True)

        st.markdown("<div class='report-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #f39c12; margin-top: 0;'>📋 פסק הדין הסופי - APEX VERDICT</h2>", unsafe_allow_html=True)
        st.write(f"📊 **תוחלת שערים מחושבת ($npxG$):** {lambda_home + mu_away:.2f}")
        st.write("---")
        st.markdown("### 🌟 החמישייה הפותחת:")
        
        if not all_bets:
            st.error("❌ המערכת לא מצאה הימורים בעלי ערך חיובי. חובה לדלג (SKIP)!")
        else:
            for i, bet in enumerate(all_bets[:5], 1):
                st.success(f"🎯 **[RANK {i}]** | **{bet['market']}**: {bet['selection']} | 📊 הסתברות: **{bet['prob']:.2f}%** | ווינר: **{bet['odds']:.2f}** | אדג': **+{bet['edge']:.2f}%**")

        st.write("---")
        if w_c911: st.warning("⛔ **[VETO]** הוחל איסור מוחלט על סימון X (9-11) בקרנות.")
        if w_b23 and 1.80 <= w_b23 <= 1.85: st.warning(f"⛔ **[VETO_185]** מלכודת 2-3 שערים הופעלה. נא להתרחק.")
        st.markdown("</div>", unsafe_allow_html=True)
