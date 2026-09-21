import base64
import json
import os
import re
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------
st.set_page_config(
    page_title="RIHLA | UAE Tourist Guide",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

USER_DB_FILE = "users_db.json"

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_user_db(db):
    with open(USER_DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "confirm_logout" not in st.session_state:
    st.session_state.confirm_logout = False

# ----------------------------------------------------------
# EXCHANGE RATES
# ----------------------------------------------------------
EXCHANGE_RATES = {
    "USD (US Dollar)": 0.2723,
    "EUR (Euro)": 0.25,
    "GBP (British Pound)": 0.21,
    "INR (Indian Rupee)": 22.80,
    "SAR (Saudi Riyal)": 1.02,
    "CAD (Canadian Dollar)": 0.37,
    "AUD (Australian Dollar)": 0.41,
    "AED (UAE Dirham)": 1.0
}

# ----------------------------------------------------------
# COLOR PALETTES
# ----------------------------------------------------------
is_dark = st.session_state.dark_mode

if is_dark:
    desk_bg = "#18101e"
    paper_bg = "#23182d"
    card_bg = "#30223d"
    text_color = "#fcebfa"
    subtext_color = "#e2b8dc"
    border_color = "#734c6b"
    input_bg = "#1b1222"
    accent_color = "#ff5ebd"
    popover_bg = "#30223d"
else:
    desk_bg = "#f6f2ec"
    paper_bg = "#fffcf7"
    card_bg = "#f8f4ec"
    text_color = "#4a3b32"
    subtext_color = "#8c7a6b"
    border_color = "#dfd5c5"
    input_bg = "#ffffff"
    accent_color = "#7a8c6b"
    popover_bg = "#fffefb"

# ----------------------------------------------------------
# ULTIMATE CSS OVERRIDES (Removing Ghost Bars & Fixing Pins)
# ----------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Quicksand:wght@500;600;700&display=swap');

[data-testid="stAppViewContainer"], .stApp, header, footer {{
    background-color: {desk_bg} !important;
    background-image: none !important;
    color: {text_color} !important;
    font-family: 'Quicksand', sans-serif !important;
}}

/* Completely eliminate Streamlit top wrapper boxes and ghost layout rectangles */
header[data-testid="stHeader"], 
[data-testid="stToolbar"], 
[data-testid="stDecoration"], 
#MainMenu, 
footer,
.stApp > header,
div[data-testid="stDecoration"],
div[data-testid="stToolbar"],
div[data-testid="stVerticalBlock"] > div:empty,
div[data-testid="stHorizontalBlock"] > div:empty,
section.main > div:first-child {{
    display: none !important;
    height: 0px !important;
    min-height: 0px !important;
    visibility: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    pointer-events: none !important;
}}

.block-container {{
    max-width: 1260px !important;
    margin: 0 auto !important;
    padding: 1.5rem 1.5rem !important;
    padding-top: 1rem !important;
}}

.scrapbook-master {{
    background-color: {paper_bg};
    border: 2.5px solid {border_color};
    border-radius: 32px;
    padding: 28px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.05);
    position: relative;
    margin-top: 0px;
}}

.inspo-header {{
    background: {card_bg};
    border: 2px solid {border_color};
    border-radius: 24px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
}}

h1, h2, h3, .heading-serif {{
    font-family: 'Playfair Display', serif !important;
    color: {text_color} !important;
}}

.cursive-note {{
    font-family: 'Caveat', cursive !important;
    color: {subtext_color} !important;
    font-size: 24px !important;
    line-height: 1.1 !important;
}}

p, label, span, div {{
    color: {text_color} !important;
    font-family: 'Quicksand', sans-serif !important;
}}

div[data-baseweb="input"], .stTextInput input, .stNumberInput input {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
    border: 2px solid {border_color} !important;
    border-radius: 20px !important;
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 600 !important;
}}

div[data-baseweb="select"] > div {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
    border: 2px solid {border_color} !important;
    border-radius: 20px !important;
}}

div[data-baseweb="select"] span {{
    color: {text_color} !important;
}}

div[data-baseweb="popover"], div[data-baseweb="popover"] ul, [data-baseweb="menu"] {{
    background-color: {popover_bg} !important;
    border: 2px solid {border_color} !important;
    border-radius: 20px !important;
}}

/* Top Navigation Buttons */
div.stButton > button {{
    width: 100% !important;
    border-radius: 24px !important;
    border: 2.5px solid {border_color} !important;
    background: {card_bg} !important;
    color: {text_color} !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    padding: 13px 20px !important;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}}

div.stButton > button:hover {{
    background: {input_bg} !important;
    border-color: {accent_color} !important;
    transform: translateY(-1px);
}}

div.stButton > button[kind="primary"] {{
    background: {accent_color} !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 16px rgba(0,0,0,0.1) !important;
}}

div.stButton > button[kind="primary"] span {{
    color: #ffffff !important;
}}

/* Scrapbook Card with Clean Paper Tape (No Bad Red Pushpins) */
.scrapbook-card {{
    background: {card_bg} !important;
    border: 2px solid {border_color} !important;
    border-radius: 26px !important;
    padding: 22px !important;
    box-shadow: {('0 8px 25px rgba(0, 0, 0, 0.15)' if is_dark else '0 8px 25px rgba(0, 0, 0, 0.03)')} !important;
    margin-bottom: 18px !important;
    position: relative;
}}

.scrapbook-card::before {{
    content: "";
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 70px;
    height: 18px;
    background: {border_color};
    opacity: 0.6;
    border-radius: 4px;
}}

.polaroid-container {{
    position: relative;
    background: {input_bg};
    border: 2px solid {border_color};
    border-radius: 22px;
    padding: 12px 12px 16px 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}}

.rect-img-wrapper {{
    border-radius: 16px;
    overflow: hidden;
    height: 160px;
    width: 100%;
}}

.rect-img-wrapper img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}

.stat-box {{
    background: {card_bg};
    border: 2px solid {border_color};
    border-radius: 22px;
    padding: 18px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    position: relative;
}}

.stat-box::before {{
    content: "";
    position: absolute;
    top: -9px;
    left: 50%;
    transform: translateX(-50%);
    width: 45px;
    height: 14px;
    background: {border_color};
    opacity: 0.5;
    border-radius: 3px;
}}

.stat-value {{
    font-family: 'Playfair Display', serif !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    margin: 4px 0 !important;
}}

.stat-label {{
    font-family: 'Quicksand', sans-serif !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    color: {subtext_color} !important;
}}

.tag-badge {{
    background: {input_bg};
    color: {text_color} !important;
    border: 1.5px solid {border_color};
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 14px;
    font-family: 'Playfair Display', serif;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# DATASET & IMAGE RESOLUTION
# ----------------------------------------------------------
@st.cache_data
def load_data():
    if os.path.exists("places.csv"):
        df_raw = pd.read_csv("places.csv")
    else:
        df_raw = pd.DataFrame({
            "Place": ["Sheikh Zayed Grand Mosque", "Burj Al Arab", "Al Qasba", "Al Jahili Fort", "Jebel Jais", "Dubai Miracle Garden", "Louvre Abu Dhabi", "Hatta Dam", "Al Fahidi Historical Neighbourhood"],
            "Emirate": ["Abu Dhabi", "Dubai", "Sharjah", "Al Ain", "Ras Al Khaimah", "Dubai", "Abu Dhabi", "Hatta", "Dubai"],
            "Category": ["Grand Mosque", "Luxury Hotel", "Waterfront", "Historical", "Mountain", "Garden", "Museum", "Nature", "Cultural"],
            "Rating": [4.9, 4.8, 4.7, 4.5, 4.7, 4.6, 4.8, 4.7, 4.6],
            "Timing": ["9AM - 10PM", "24/7", "10AM - 11PM", "9AM - 5PM", "Open Daily", "9AM - 9PM", "10AM - 6.30PM", "Open Daily", "24/7"],
            "Entry Fee": ["Free", "AED 250", "Free", "AED 10", "Free", "AED 75", "AED 63", "Free", "Free"],
            "Description": ["A magnificent masterpiece of modern Islamic architecture.", "World-famous luxury landmark hotel.", "Scenic canal waterfront with cafes and Ferris wheel.", "Historic defensive fort surrounded by lush gardens.", "The highest peak in the UAE with stunning views.", "The world's largest natural flower garden.", "Universal museum showcasing art and humanity.", "Stunning blue waters nestled in the Hajar mountains.", "Historic heritage district with traditional wind-tower architecture."]
        })
    for i, row in df_raw.iterrows():
        if pd.notna(row.get("Unnamed: 9")) and str(row.get("Unnamed: 9")).strip():
            df_raw.at[i, "Image"] = str(row["Unnamed: 9"]).strip()
    return df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')].copy()

df = load_data()
SEARCH_FOLDERS = ["Images", "images", "Documents/RIHLA/Images", "Documents/Images", ""]

def resolve_image(image_val, name_hint=""):
    candidates = []
    if image_val and pd.notna(image_val) and str(image_val).strip():
        val = str(image_val).strip()
        candidates.append(val)
        base, ext = os.path.splitext(val)
        if not ext:
            candidates.extend([f"{val}.jpg", f"{val}.JPG", f"{val}.png"])
        else:
            candidates.extend([f"{base}.jpg", f"{base}.JPG", f"{base}.png"])

    if name_hint:
        clean = str(name_hint).lower().strip().replace(" ", "_").replace("'", "").replace("-", "_")
        candidates.extend([f"{clean}.jpg", f"{clean}.JPG", f"{clean}.png"])

    for cand in candidates:
        if cand.startswith("http://") or cand.startswith("https://"):
            return cand
        for folder in SEARCH_FOLDERS:
            p = os.path.join(folder, cand) if folder else cand
            if os.path.exists(p):
                with open(p, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                ext = p.split('.')[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"

    return "https://images.unsplash.com/photo-1512453979798-5ea26e3a5323?auto=format&fit=crop&w=800&q=80"

# ----------------------------------------------------------
# SCREEN 1: LOGIN (Balanced Width, Nicely Proportionate Height)
# ----------------------------------------------------------
if not st.session_state.logged_in:
    l_col1, l_col2, l_col3 = st.columns([1, 1.1, 1])
    with l_col2:
        st.markdown(
            f'<div class="scrapbook-card" style="margin-top: 20px; padding: 36px 32px !important; text-align: center;">'
            f'<h1 style="font-size: 32px; margin: 0 0 2px 0; font-weight: 700;">RIHLA</h1>'
            f'<p class="cursive-note" style="margin: 0 0 22px 0; font-size: 24px !important;">Your personal UAE scrapbook travel companion</p>'
            f'<div style="background:{input_bg}; border: 2px solid {border_color}; border-radius: 18px; padding: 16px; margin-bottom: 20px; text-align: left;">'
            f'<p style="margin: 0; font-size: 12px; color:{text_color} !important; font-weight: 600; line-height: 1.5;">'
            f'<b>Login Security Rule:</b><br>'
            f'• Password must be a mix of letters, numbers, and characters (e.g., P@ssw0rd1!).'
            f'</p></div>',
            unsafe_allow_html=True
        )

        user_input = st.text_input("Username", placeholder="Enter any username", key="user_field")
        pass_input = st.text_input("Password", type="password", placeholder="••••••••", key="pass_field")

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        if st.button("Enter Rihla", type="primary", use_container_width=True):
            u = user_input.strip()
            p = pass_input.strip()

            has_alpha = any(c.isalpha() for c in p)
            has_digit = any(c.isdigit() for c in p)
            has_special = bool(re.search(r"[^a-zA-Z0-9]", p))

            if not u:
                st.error("Please enter a username.")
            elif not p:
                st.error("Please enter a password.")
            elif not (has_alpha and has_digit and has_special):
                st.error("Password must contain a mix of letters, numbers, and special characters.")
            else:
                user_db = load_user_db()
                user_db[u] = user_db.get(u, 0) + 1
                save_user_db(user_db)

                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------
# SCREEN 2: MAIN APP
# ----------------------------------------------------------
else:
    st.markdown('<div class="scrapbook-master">', unsafe_allow_html=True)

    # TOP NAVIGATION BAR
    st.markdown('<div class="inspo-header">', unsafe_allow_html=True)
    h_logo, h_home, h_exp, h_bud, h_stat, h_abt, h_mode, h_out = st.columns([1.6, 0.7, 0.7, 0.8, 0.7, 0.7, 0.8, 0.7])

    with h_logo:
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:8px;">'
            f'<div>'
            f'<div class="heading-serif" style="font-size:14px; font-weight:700; line-height:1;">RIHLA</div>'
            f'<div class="cursive-note" style="font-size:12px !important; font-weight:700;">UAE TOURIST GUIDE</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    nav_buttons = [
        (h_home, "Home", "Home"),
        (h_exp, "Explore", "Explore"),
        (h_bud, "Budget", "Budget Planner"),
        (h_stat, "Stats", "Statistics"),
        (h_abt, "About", "About")
    ]

    for col_ref, label_text, page_key in nav_buttons:
        with col_ref:
            is_active = (st.session_state.page == page_key and st.session_state.selected_place is None)
            if st.button(label_text, key=f"top_nav_{page_key}", type="primary" if is_active else "secondary"):
                st.session_state.page = page_key
                st.session_state.selected_place = None
                st.session_state.confirm_logout = False
                st.rerun()

    with h_mode:
        mode_label = "☀️ Light" if is_dark else "🌙 Dark"
        if st.button(mode_label, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    with h_out:
        if not st.session_state.confirm_logout:
            if st.button("Logout", key="logout_btn"):
                st.session_state.confirm_logout = True
                st.rerun()
        else:
            if st.button("Confirm?", key="confirm_out_btn", type="primary"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.selected_place = None
                st.session_state.confirm_logout = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------------
    # DESTINATION DETAIL VIEW
    # ----------------------------------------------------------
    if st.session_state.selected_place is not None:
        place_name = st.session_state.selected_place
        match_row = df[df["Place"] == place_name]

        if st.button("← Back to Home"):
            st.session_state.selected_place = None
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if not match_row.empty:
            row = match_row.iloc[0]
            img_url = resolve_image(row.get("Image", ""), row["Place"])
            
            d_col1, d_col2 = st.columns([1, 1.3])
            with d_col1:
                st.markdown(f'''
                    <div class="scrapbook-card">
                        <div class="polaroid-container">
                            <div class="rect-img-wrapper" style="height:230px;">
                                <img src="{img_url}" alt="{row['Place']}" />
                            </div>
                        </div>
                        <div style="margin-top:12px; display:flex; gap:8px; align-items:center;">
                            <span class="tag-badge">{str(row['Emirate']).upper()}</span>
                            <span class="tag-badge">★ {row['Rating']}</span>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)

            with d_col2:
                st.markdown(f'''
                    <div class="scrapbook-card">
                        <h2 style="font-size:24px; margin-top:0; margin-bottom:2px;">{row['Place']}</h2>
                        <p class="cursive-note" style="margin-bottom:10px;">Category: {row['Category']}</p>
                ''', unsafe_allow_html=True)

                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"<p style='margin:0; font-size:11px; color:{subtext_color}; font-weight:700;'>TIMING</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin:2px 0 0 0; font-weight:600; font-size:12.5px;'>{row.get('Timing', 'N/A')}</p>", unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"<p style='margin:0; font-size:11px; color:{subtext_color}; font-weight:700;'>ENTRY FEE</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin:2px 0 0 0; font-weight:600; font-size:12.5px;'>{row.get('Entry Fee', 'Free')}</p>", unsafe_allow_html=True)

                st.markdown(f"<hr style='border-color:{border_color}; margin:14px 0;'>", unsafe_allow_html=True)
                st.markdown("<h4 style='font-size:13.5px; margin-bottom:6px;'>About this Destination</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:12.5px; line-height:1.55;'>{row.get('Description', 'No detailed description available.')}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------------
    # HOME PAGE
    # ----------------------------------------------------------
    elif st.session_state.page == "Home":
        hero1, hero2 = st.columns([1.2, 1])

        with hero1:
            st.markdown(f'''
                <div class="scrapbook-card" style="padding: 28px !important;">
                    <p class="cursive-note" style="margin-bottom:2px;">Welcome to Rihla ♡</p>
                    <h1 style="font-size: 28px; line-height: 1.15; margin: 4px 0 6px 0; font-weight:700;">
                        DISCOVER THE<br>
                        UNITED ARAB EMIRATES
                    </h1>
                    <p style="color:{subtext_color} !important; font-size:12.5px; line-height:1.5; margin-bottom: 18px; margin-top: 10px;">
                        Explore breathtaking landmarks, beautiful beaches, historical forts, magnificent mosques, luxurious islands and unforgettable experiences across all seven emirates.
                    </p>
            ''', unsafe_allow_html=True)

            if st.button("START EXPLORING", type="primary"):
                st.session_state.page = "Explore"
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        with hero2:
            bourj_img = resolve_image("burj_khalifa", "Burj Khalifa")
            st.markdown(f'''
                <div class="scrapbook-card" style="padding:14px !important;">
                    <div class="polaroid-container">
                        <div class="rect-img-wrapper" style="height:205px;">
                            <img src="{bourj_img}" alt="Burj Khalifa" />
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f'<div class="stat-box"><div class="stat-value">7</div><div class="stat-label">EMIRATES ACROSS UAE</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="stat-box"><div class="stat-value">35</div><div class="stat-label">DESTINATIONS MUST-VISIT</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="stat-box"><div class="stat-value">4.3</div><div class="stat-label">AVG RATING FROM TRAVELERS</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;"><h3 style="margin:0; font-size:19px;">Featured Destinations ♡</h3></div>', unsafe_allow_html=True)

        featured_rows = list(df.head(6).iterrows())
        for i in range(0, len(featured_rows), 3):
            chunk = featured_rows[i:i+3]
            cols = st.columns(3)
            for col_idx, (idx, row) in enumerate(chunk):
                with cols[col_idx]:
                    img_url = resolve_image(row.get("Image", ""), row["Place"])
                    st.markdown(f'''
                        <div class="scrapbook-card" style="padding:14px !important;">
                            <div class="polaroid-container">
                                <div class="rect-img-wrapper" style="height:140px;">
                                    <img src="{img_url}" alt="{row['Place']}" />
                                </div>
                            </div>
                            <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
                                <span class="tag-badge" style="font-size:10px;">{str(row['Emirate']).upper()}</span>
                                <span style="font-size:10.5px; color:{subtext_color}; font-weight:700;">★ {row['Rating']}</span>
                            </div>
                            <h4 style="font-size:14px; margin:6px 0 4px 0; font-weight:700;">{row['Place']}</h4>
                            <p style="font-size:11px; color:{subtext_color} !important; margin:0 0 10px 0;">Entry: {row.get('Entry Fee', 'Free')}</p>
                    ''', unsafe_allow_html=True)
                    if st.button("View Details", key=f"home_feat_{idx}"):
                        st.session_state.selected_place = row['Place']
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # Green Footer Banner with Embedded Action Button Inside the Box
        st.markdown(
            f'<div class="scrapbook-card" style="background: {accent_color} !important; margin-top: 26px; padding: 24px 28px !important;">'
            f'<h3 style="color:#ffffff !important; margin:0; font-size:20px;">Plan smart. Travel better.</h3>'
            f'<p style="color:#f3eee2 !important; font-size:12px; margin:2px 0 14px 0;">Use our Budget Planner to create your perfect trip within your budget.</p>',
            unsafe_allow_html=True
        )
        if st.button("OPEN BUDGET PLANNER", key="banner_budget_btn", type="primary"):
            st.session_state.page = "Budget Planner"
            st.session_state.selected_place = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------------
    # EXPLORE PAGE
    # ----------------------------------------------------------
    elif st.session_state.page == "Explore":
        st.markdown(f'''
            <div class="scrapbook-card">
                <div style="display:flex; align-items:center; gap:8px;">
                    <h2 style="margin:0; font-size:20px;">Explore UAE Destinations</h2>
                </div>
                <p class="cursive-note" style="margin-top:2px;">Filter through emirates and discover hidden gems...</p>
            </div>
        ''', unsafe_allow_html=True)

        emirates_list = ["All Emirates"] + sorted(df["Emirate"].dropna().unique().tolist())
        selected_emirate = st.selectbox("Filter by Emirate", emirates_list, label_visibility="collapsed")

        filtered_df = df if selected_emirate == "All Emirates" else df[df["Emirate"] == selected_emirate]

        st.markdown("<br>", unsafe_allow_html=True)

        if filtered_df.empty:
            st.info(f"No destinations found for {selected_emirate}.")
        else:
            grid_cols = st.columns(3)
            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                col = grid_cols[idx % 3]
                with col:
                    img_url = resolve_image(row.get("Image", ""), row["Place"])
                    st.markdown(f'''
                        <div class="scrapbook-card" style="padding:14px !important;">
                            <div class="polaroid-container">
                                <div class="rect-img-wrapper" style="height:140px;">
                                    <img src="{img_url}" alt="{row['Place']}" />
                                </div>
                            </div>
                            <div style="margin-top:8px;"><span class="tag-badge">{str(row['Emirate']).upper()}</span></div>
                            <h4 style="font-size:14px; margin:6px 0 2px 0; font-weight:700;">{row['Place']}</h4>
                            <p style="font-size:11px; color:{subtext_color} !important; margin:0 0 10px 0;">Rating: {row['Rating']} • {row['Category']}</p>
                    ''', unsafe_allow_html=True)
                    if st.button("View Details", key=f"exp_{row['Place']}_{idx}"):
                        st.session_state.selected_place = row['Place']
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------------
    # BUDGET PLANNER
    # ----------------------------------------------------------
    elif st.session_state.page == "Budget Planner":
        st.markdown(f'''
            <div class="scrapbook-card">
                <div style="display:flex; align-items:center; gap:8px;">
                    <h2 style="margin:0; font-size:20px;">Travel Budget Calculator</h2>
                </div>
                <p class="cursive-note" style="margin-top:2px;">Track itinerary entry costs according to your destination selection...</p>
            </div>
        ''', unsafe_allow_html=True)

        b_col1, b_col2 = st.columns([1, 1.2])

        def parse_fee_aed(fee_val):
            if pd.isna(fee_val): return 0.0
            s = str(fee_val).lower().strip()
            if "free" in s or s == "0": return 0.0
            cleaned = "".join([c for c in s if c.isdigit() or c == '.'])
            try:
                return float(cleaned)
            except ValueError:
                return 0.0

        with b_col1:
            st.markdown('<div class="scrapbook-card">', unsafe_allow_html=True)
            st.markdown("<h3>Currency Setup</h3>", unsafe_allow_html=True)
            user_curr = st.selectbox("Select Your Base Currency:", list(EXCHANGE_RATES.keys()))
            rate = float(EXCHANGE_RATES[user_curr])
            curr_code = user_curr.split(" ")[0]

            home_budget = st.number_input(f"Your Target Budget ({curr_code}):", min_value=0.0, value=300.0, step=25.0)

            st.markdown("---")
            st.markdown("<h3>Select Destinations</h3>", unsafe_allow_html=True)
            selected_places = st.multiselect(
                "Choose places to visit:",
                options=df["Place"].tolist(),
                default=df["Place"].tolist()[:3] if len(df) >= 3 else df["Place"].tolist()
            )
            st.markdown('</div>', unsafe_allow_html=True)

        selected_df = df[df["Place"].isin(selected_places)].copy()
        selected_df["Fee_AED"] = selected_df["Entry Fee"].apply(parse_fee_aed).astype(float)
        selected_df[f"Fee_{curr_code}"] = selected_df["Fee_AED"] * rate

        total_aed = float(selected_df["Fee_AED"].sum())
        total_home_curr = total_aed * rate
        remaining_home = home_budget - total_home_curr
        pct_used = min(100.0, (total_home_curr / home_budget * 100)) if home_budget > 0 else 0.0

        with b_col2:
            st.markdown('<div class="scrapbook-card">', unsafe_allow_html=True)
            st.markdown("<h3>Budget Breakdown</h3>", unsafe_allow_html=True)
            st.metric(label=f"Total Estimated Cost ({curr_code})", value=f"{total_home_curr:.2f} {curr_code}", delta=f"{total_aed:.1f} AED")
            st.metric(label=f"Remaining Budget ({curr_code})", value=f"{remaining_home:.2f} {curr_code}")
            
            st.markdown(f"<p style='font-size:12px; font-weight:700; margin-bottom:4px;'>Budget Utilization: {pct_used:.1f}%</p>", unsafe_allow_html=True)
            st.progress(pct_used / 100.0)

            if not selected_df.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<h4>Selected Itinerary Costs</h4>", unsafe_allow_html=True)
                st.dataframe(selected_df[["Place", "Emirate", "Entry Fee", f"Fee_{curr_code}"]], use_container_width=True)
            else:
                st.info("Select at least one destination.")

            st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------------
    # STATISTICS PAGE
    # ----------------------------------------------------------
    elif st.session_state.page == "Statistics":
        st.markdown(f'''
            <div class="scrapbook-card">
                <div style="display:flex; align-items:center; gap:8px;">
                    <h2 style="margin:0; font-size:20px;">UAE Tourism Statistics & Insights</h2>
                </div>
                <p class="cursive-note" style="margin-top:2px;">Visualizing ratings and distributions...</p>
            </div>
        ''', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="scrapbook-card">', unsafe_allow_html=True)
            st.markdown("<h4>Destinations per Emirate</h4>", unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(5, 2.8))
            fig.patch.set_facecolor('none')
            ax.set_facecolor('none')
            
            counts = df["Emirate"].value_counts()
            sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="RdPu" if is_dark else "crest")
            ax.tick_params(colors=text_color, labelsize=8)
            plt.xticks(rotation=30)
            plt.tight_layout()
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="scrapbook-card">', unsafe_allow_html=True)
            st.markdown("<h4>Destination Categories</h4>", unsafe_allow_html=True)
            
            fig2, ax2 = plt.subplots(figsize=(5, 2.8))
            fig2.patch.set_facecolor('none')
            ax2.set_facecolor('none')
            
            cat_counts = df["Category"].value_counts().head(5)
            ax2.pie(cat_counts.values, labels=cat_counts.index, autopct='%1.1f%%', startangle=140, textprops={'color': text_color, 'fontsize': 8})
            plt.tight_layout()
            st.pyplot(fig2)
            st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------------
    # ABOUT PAGE
    # ----------------------------------------------------------
    elif st.session_state.page == "About":
        st.markdown(f'''
            <div class="scrapbook-card">
                <div style="display:flex; align-items:center; gap:8px;">
                    <h2 style="margin:0; font-size:20px;">About Rihla Explorer</h2>
                </div>
                <p class="cursive-note" style="margin-top:2px;">Your digital scrapbook companion for exploring the UAE.</p>
                <hr style="border-color:{border_color}; margin:10px 0;">
                <p style="font-size:12.5px; line-height:1.55;">
                    <b>Rihla</b> (Arabic for journey) is crafted to provide travelers and residents with an immersive, scrapbook-style guide to the seven emirates of the United Arab Emirates.
                </p>
                <p style="font-size:11.5px; color:{subtext_color}; margin-top:8px;">
                    Logged in as: <b>{st.session_state.username}</b>
                </p>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
