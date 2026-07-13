import streamlit as st
import urllib.request
import json
import math
import ssl
import random
import time

# הגדרות עיצוב כלליות לאפליקציה יוקרתית
st.set_page_config(page_title="I&O Sports Analytics", page_icon="🏆", layout="centered")

# עיצוב CSS מותאם אישית למראה כהה ויוקרתי (כחול עמוק וזהב)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #f39c12 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button {
        background-color: #f39c12;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #e67e22; color: white; }
    .report-box {
        background-color: #1a1c23;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #f39c12;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# מנועי שאיבת נתונים (API ו-Scraping)
# ---------------------------------------------------------
def fetch_sterile_api_data(team_id, api_key):
    url = f"https://v3.football.api-sports.io/teams/statistics?league=39&season=2024&team={team_id}"
    req = urllib.request.Request(url, headers={'x-apisports-key': api_key})
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            raw = json.loads(response.read().decode('utf-8'))
            if not raw.get("response"): return None
            goals = raw["response"]["goals"]
            return {
                "avg_goals_for": float(goals["for"]["average"]["total"]),
                "avg_goals_against": float(goals["against"]["average"]["total"])
            }
    except:
        return None

# ---------------------------------------------------------
# מנוע מונטה קרלו - קרנות
# ---------------------------------------------------------
def run_monte_carlo_corners():
    base_rate = 10.5 
    simulations = 10000
    c08, c911, c12p = 0, 0, 0
    over85, over95, over105 = 0, 0, 0
    
    for _ in range(simulations):
        total_corners = sum(1 for _ in range(90) if random.random() < (base_rate / 90))
        if total_corners <= 8: c08 += 1
        elif 9 <= total_corners <= 11: c911 += 1
        else: c12p += 1
        
        if total_corners > 8.5: over85 += 1
        if total_corners > 9.5: over95 += 1
        if total_corners > 10.5: over105 += 1
        
    return (
        (c08/simulations)*100, 
        (c911/simulations)*100, 
        (c12p/simulations)*100,
        (over85/simulations)*100,
        (over95/simulations)*100, 
        (over105/simulations)*100
    )

# ---------------------------------------------------------
# תצוגת לוגו וכותרת
# ---------------------------------------------------------
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>I & O   S P O R T S   A N A L Y T I C S</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 18px;'>📈 הדיוק שלנו, הניצחון שלכם. | OMNI-PREDATOR V80.0</p>", unsafe_allow_html=True)
st.write("---")

# הזנת שמות קבוצות
col1, col2 = st.columns(2)
with col1:
    home_name = st.text_input("⚽ קבוצת הבית:", value="אנגליה")
with col2:
    away_name = st.text_input("⚽ קבוצת החוץ:", value="ארגנטינה")

is_critical = st.checkbox("🚨 משחק רגיש / קריטי? (גמר, נוקאאוט, מאבק ירידה קריטי)")

st.write("### 💵 הזנת יחסי ווינר (השאירו ריק לליין שאתם לא תוקפים)")

# חלוקה לכרטיסיות הזנה נוחות למניעת בלבול
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
    w_race_home = col_s.number_input(f"מירוץ ל-5 ({home_name}):", min_value=1.0, step=0.05, value=None)
    w_race_x = col_t.number_input("מירוץ ל-5 (תיקו):", min_value=1.0, step=0.05, value=None)
    w_race_away = col_u.number_input(f"מירוץ ל-5 ({away_name}):", min_value=1.0, step=0.05, value=None)

st.write("")
if st.button("🚀 הרץ ניתוח אומני וחשב חמישייה פותחת"):
    
    with st.spinner("מבצע חישובי סימולציה מורכבים ברקע..."):
        time.sleep(1) # הדמיה של עיבוד נתונים מהיר
        
        # משיכת נתונים קשיחה (מנוע גיבוי)
        api_key = "eb32c04ced27ba8ca18cded2adc4eb7b"
        home_data = fetch_sterile_api_data(33, api_key)
        away_data = fetch_sterile_api_data(49, api_key)
        
        lambda_home = (home_data["avg_goals_for"] + away_data["avg_goals_against"]) / 2 if home_data else 1.85
        mu_away = (away_data["avg_goals_for"] + home_data["avg_goals_against"]) / 2 if away_data else 1.25
        rho = -0.05
        
        # חוק הפחד
        if is_critical:
            lambda_home *= 0.85
            mu_away *= 0.85
            
        # דיקסון-קולס
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

        # מונטה קרלו קרנות
        prob_c08, prob_c911, prob_c12p, prob_co85, prob_co95, prob_co105 = run_monte_carlo_corners()
        prob_cu95 = 100 - prob_co95
        prob_cu105 = 100 - prob_co105
        prob_race_home, prob_race_x, prob_race_away = 45.0, 10.0, 45.0

        # איסוף הימורים
        all_bets = []
        def add_bet(market, selection, prob, current):
            if current:
                edge = prob - ((1 / current) * 100)
                if edge > 0: 
                    all_bets.append({"market": market, "selection": selection, "prob": prob, "odds": current, "edge": edge})

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
        add_bet("מירוץ קרנות", "תיקו/אף אחת", prob_race_x, w_race_x)
        add_bet("מירוץ קרנות", f"{away_name}", prob_race_away, w_race_away)

        all_bets.sort(key=lambda x: x["edge"], reverse=True)

        # פלט הדו"ח
        st.markdown("<div class='report-box'>", unsafe_allow_html=True)
        st.subheader("📋 פסק הדין הסופי - APEX VERDICT")
        st.write(f"📊 **תוחלת שערים מחושבת ($npxG$):** {lambda_home + mu_away:.2f}")
        st.write("---")
        
        st.write("### 🌟 החמישייה הפותחת (הימורים עם ערך חיובי):")
        if not all_bets:
            st.error("❌ המערכת לא מצאה אף הימור בעל ערך חיובי. חובה לדלג (SKIP)!")
        else:
            for i, bet in enumerate(all_bets[:5], 1):
                st.success(f"🎯 **[RANK {i}]** | **{bet['market']}**: {bet['selection']} | 📊 הסתברות: **{bet['prob']:.2f}%** | ווינר: **{bet['odds']:.2f}** | אדג': **+{bet['edge']:.2f}%**")

        st.write("---")
        if w_c911:
            st.warning("⛔ **[VETO]** הוחל איסור מוחלט על סימון X (9-11) בקרנות.")
        if w_b23 and 1.80 <= w_b23 <= 1.85:
            st.warning(f"⛔ **[VETO_185]** מלכודת 2-3 שערים הופעלה (יחס {w_b23:.2f}). נא להתרחק.")
            
        st.markdown("</div>", unsafe_allow_html=True)
