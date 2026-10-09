import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import base64
import json
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
from streamlit_cookies_controller import CookieController

# ══════════════════════════════════════════════════════════
# 1. SAYFA YAPISI VE ÇEREZ YÖNETİCİSİ
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="ARDER", page_icon="🦚", layout="centered", initial_sidebar_state="collapsed")
controller = CookieController()

# ══════════════════════════════════════════════════════════
# 2. MEGA-CACHE VE GELİŞMİŞ MOBİL CSS
# ══════════════════════════════════════════════════════════
@st.cache_data
def get_static_assets():
    logo_b64 = ""
    for ext in ["logo.png","logo.jpg","logo.jpeg", "LOGO.png"]:
        if os.path.exists(ext):
            with open(ext,"rb") as f: logo_b64 = base64.b64encode(f.read()).decode()
            mime = "image/png" if ext.lower().endswith(".png") else "image/jpeg"
            logo_html = f'<img src="data:{mime};base64,{logo_b64}" style="height:40px;object-fit:contain;mix-blend-mode:multiply;">'
            login_logo_html = f'<img src="data:{mime};base64,{logo_b64}" style="height:140px;object-fit:contain;margin-bottom:10px;mix-blend-mode:multiply;">'
            break
    else:
        logo_html = '<span style="font-size:40px;">🦚</span>'
        login_logo_html = '<div style="font-size:90px; text-align:center;">🦚</div>'

    _ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="100" fill="#ffffff"/><text x="256" y="370" text-anchor="middle" font-size="340" font-weight="900" fill="#2DB5A0" font-family="Arial,sans-serif">A</text></svg>"""
    _ICON_URI  = f"data:image/svg+xml;base64,{base64.b64encode(_ICON_SVG.encode()).decode()}"
    _manifest  = {"name":"ARDER","short_name":"ARDER","display":"standalone","background_color":"#f4f7f6","theme_color":"#ffffff","icons":[{"src":_ICON_URI,"sizes":"512x512","type":"image/svg+xml","purpose":"any maskable"}]}
    
    html = f"""<link rel="manifest" href="data:application/manifest+json;base64,{base64.b64encode(json.dumps(_manifest).encode()).decode()}"><meta name="theme-color" content="#ffffff"><style>
    html, body {{ overscroll-behavior-y: none !important; overscroll-behavior-x: none !important; touch-action: none !important; position: fixed !important; width: 100vw !important; height: 100vh !important; overflow: hidden !important; }} 
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    .viewerBadge_container, .stAppViewFooter, footer {{ display: none !important; }}
    .main .block-container {{ max-width:480px; margin:auto; padding:0.5rem; padding-top:2rem; }}
    [data-testid="stAppViewContainer"] {{ background-color:#f5f8f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overscroll-behavior-y: none !important; touch-action: pan-y !important; height: 100vh !important; overflow-y: auto !important; -webkit-overflow-scrolling: touch !important; }}
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {{ border-radius: 20px !important; border: 1px solid #e2e8f0 !important; background-color: #ffffff !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important; }}
    div.stButton>button {{ border-radius: 30px !important; font-weight: 700 !important; padding: 0.6rem 1rem !important; border: none !important; transition: all 0.3s ease; }}
    div.stButton>button:first-child {{ background: linear-gradient(135deg, #1976D2, #2DB5A0) !important; color: #fff !important; box-shadow: 0 4px 14px rgba(45, 181, 160, 0.3) !important; }}
    div.stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(45, 181, 160, 0.4) !important; }}
    .btn-danger>button {{ background: linear-gradient(135deg, #ef4444, #dc2626) !important; color: #fff !important; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3) !important; }}
    .btn-secondary>button {{ background: linear-gradient(135deg, #94a3b8, #64748b) !important; color: #fff !important; box-shadow: 0 4px 14px rgba(100, 116, 139, 0.3) !important; }}
    .app-header {{ background: #ffffff; border-radius: 24px; padding: 1rem 1.2rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.8rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
    .app-header .brand-name {{ font-size: 1.15rem; font-weight: 900; color: #1A2744; line-height: 1.1; }}
    .app-header .brand-sub {{ font-size: 0.7rem; color: #2DB5A0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}
    .login-header {{ text-align: center; margin-bottom: 2rem; margin-top: 1rem; }}
    .stat-wrap {{ display:flex; gap:12px; margin:0.5rem 0 1.5rem 0; }}
    .stat-card {{ flex:1; background:#fff; border-radius:24px; box-shadow:0 8px 24px rgba(0,0,0,0.04); padding:1.2rem 0.8rem; text-align:center; display: flex; flex-direction: column; justify-content: center; }}
    .stat-card .label {{ font-size:0.7rem; color:#64748b; font-weight:600; margin-bottom:8px; }}
    .stat-card .value {{ font-size:1.8rem; font-weight:900; color:#1A2744; line-height:1; }}
    .stat-card .value.green {{ color: #2DB5A0; }}
    .task-card {{ background: #fff; border-radius: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.03); padding: 1.2rem; margin-bottom: 1rem; border-left: 6px solid #2DB5A0; position: relative; }}
    .task-card.done {{ border-left-color: #cbd5e1; opacity: 0.7; }}
    .task-title {{ font-weight: 800; color: #1A2744; font-size: 1rem; margin-bottom: 0.3rem; }}
    .task-meta {{ font-size: 0.8rem; color: #64748b; margin-bottom: 0.8rem; line-height: 1.4; }}
    .badge {{ display:inline-block; padding:0.25rem 0.7rem; border-radius:20px; font-size:0.7rem; font-weight:700; }}
    .badge-acil {{ background:#fee2e2; color:#b91c1c; }} .badge-yuksek {{ background:#fef3c7; color:#b45309; }}
    .badge-orta {{ background:#ccfbf1; color:#0f766e; }} .badge-dusuk {{ background:#e0f2fe; color:#0369a1; }}
    
    .section-title {{ font-size: 15px; font-weight: 900; color: #1A2744; margin: 1.5rem 0 0.8rem 0; padding-left: 5px; }}
    .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 1rem; }}
    .grid-item {{ background: #fff; padding: 15px; border-radius: 20px; text-align: left; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; }}
    .grid-icon {{ font-size: 24px; margin-bottom: 8px; }}
    .grid-text {{ font-size: 12px; font-weight: 800; color: #64748b; margin-bottom: 2px; }}
    .grid-val {{ font-size: 20px; font-weight: 900; color: #1A2744; line-height: 1; }}
    
    .event-v2 {{ display: flex; background: #fff; border-radius: 20px; padding: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.03); margin-bottom: 12px; align-items: center; border: 1px solid #f1f5f9; }}
    .e-date {{ background: #f8fafc; border-radius: 14px; padding: 12px 10px; min-width: 65px; text-align: center; border: 1px solid #e2e8f0; margin-right: 15px; }}
    .e-day {{ font-size: 22px; font-weight: 900; color: #1A2744; line-height: 1; }}
    .e-month {{ font-size: 11px; font-weight: 800; color: #2DB5A0; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px;}}
    .e-info {{ flex: 1; }}
    .e-title {{ font-weight: 800; color: #1A2744; font-size: 15px; margin-bottom: 4px; }}
    .e-desc {{ font-size: 12px; color: #64748b; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
    
    .board-card {{ display: flex; align-items: center; background: #fff; border-radius: 16px; padding: 12px 15px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); border: 1px solid #f8fafc; }}
    .b-avatar {{ width: 44px; height: 44px; border-radius: 14px; background: linear-gradient(135deg, #1976D2, #2DB5A0); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 900; margin-right: 15px; flex-shrink: 0; box-shadow: 0 4px 10px rgba(45,181,160,0.2); }}
    .b-name {{ font-weight: 800; color: #1A2744; font-size: 14px; margin-bottom: 2px; }}
    .b-title {{ font-size: 11px; color: #64748b; font-weight: 600; }}

    .ann-card {{ background: linear-gradient(to right, #f8fafc, #ffffff); border-left: 4px solid #f59e0b; padding: 15px; border-radius: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }}
    .a-title {{ font-weight: 800; color: #1A2744; font-size: 14px; margin-bottom: 6px; }}
    .a-date {{ font-size: 10px; color: #94a3b8; font-weight: 700; margin-bottom: 8px; display:inline-block; background:#fff; padding:2px 8px; border-radius:10px; border:1px solid #e2e8f0; }}
    .a-content {{ font-size: 13px; color: #475569; line-height: 1.5; }}
    
    /* GRID MENÜ BUTON TASARIMLARI */
    .menu-grid-btn > button {{
        height: 105px !important;
        border-radius: 18px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        background: #ffffff !important;
        border: 1px solid #f1f5f9 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
        color: #1A2744 !important;
        gap: 8px !important;
        padding: 5px !important;
    }}
    .menu-grid-btn > button:hover {{
        background: #f8fafc !important;
        border-color: #2DB5A0 !important;
        transform: translateY(-3px);
    }}
    .menu-grid-btn > button p {{
        font-size: 13px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
        text-align: center !important;
        line-height: 1.2 !important;
    }}
    
    /* Geri dön butonu */
    .back-btn > button {{
        background: transparent !important;
        color: #64748b !important;
        box-shadow: none !important;
        border: 2px solid #e2e8f0 !important;
        font-size: 13px !important;
        padding: 0.4rem 1rem !important;
    }}
    </style>"""
    return html, logo_html, login_logo_html

STATIC_HTML, LOGO_HTML, LOGIN_LOGO_HTML = get_static_assets()
st.markdown(STATIC_HTML, unsafe_allow_html=True)
components.html("<script>if ('Notification' in window && Notification.permission === 'default') { Notification.requestPermission(); }</script>", height=0)

# ══════════════════════════════════════════════════════════
# 3. VERİTABANI BAĞLANTISI VE MODELLER
# ══════════════════════════════════════════════════════════
try: DB_URL = st.secrets["DB_URL"]
except: st.stop()

@st.cache_resource
def init_connection(): return create_engine(DB_URL, pool_pre_ping=True)

engine = init_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AppSettings(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True, index=True)
    last_reset_month = Column(String, default="")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, default="") 
    role = Column(String) 
    alan = Column(String, default="Belirtilmedi")
    avatar = Column(String, default="")
    points = Column(Integer, default=0)
    lifetime_points = Column(Integer, default=0)
    total_assigned = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    assigned_to = Column(String)
    assigned_by = Column(String)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    points = Column(Integer, default=10)
    earned_points = Column(Integer, default=0) 
    status = Column(String, default="Bekliyor") 
    due_date = Column(String, default="")
    steps = Column(String, default="")
    report = Column(String, default="")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    event_date = Column(String)
    created_by = Column(String)

class EventRSVP(Base):
    __tablename__ = "event_rsvps"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer)
    username = Column(String)
    status = Column(String)
    reason = Column(String)

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    date = Column(String)
    author = Column(String)

class Partner(Base):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    discount = Column(String)
    details = Column(String)
    icon = Column(String, default="🏪")

@st.cache_resource
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            for stmt in [
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 10;",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS earned_points INTEGER DEFAULT 0;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS alan VARCHAR DEFAULT 'Belirtilmedi';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR DEFAULT '';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar VARCHAR DEFAULT '';",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date VARCHAR DEFAULT '';",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS steps VARCHAR DEFAULT '';",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS report VARCHAR DEFAULT '';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS lifetime_points INTEGER DEFAULT 0;",
                "UPDATE users SET lifetime_points = 0 WHERE lifetime_points IS NULL;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_assigned INTEGER DEFAULT 0;",
                "UPDATE users SET total_assigned = 0 WHERE total_assigned IS NULL;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_completed INTEGER DEFAULT 0;",
                "UPDATE users SET total_completed = 0 WHERE total_completed IS NULL;",
                "UPDATE tasks SET earned_points = points WHERE status = 'Tamamlandı' AND (earned_points = 0 OR earned_points IS NULL);"
            ]:
                try: conn.execute(text(stmt)); conn.commit()
                except: pass
    except: pass 

init_db()

# ══════════════════════════════════════════════════════════
# 4. YARDIMCI FONKSİYONLAR
# ══════════════════════════════════════════════════════════
def send_email_notification(to_email, user_name, task_title, task_desc, priority, points, due_date):
    try:
        s_email, s_pass = st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass or not to_email: return False 
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = f"ARDER Sistem <{s_email}>", to_email, f"📌 Yeni Görev: {task_title}"
        body = f"Sayın {user_name}, Akademik Renkler Derneği bünyesinde tarafınıza yeni bir görev atanmıştır.\n\nGörev Bilgileri:\n📌 Başlık: {task_title}\n⚡ Öncelik: {priority}\n⭐ Maksimum Puan: {points}\n📅 Son Teslim Tarihi: {due_date}\n\nGörev Açıklaması: \n{task_desc}\n\nLütfen uygulamaya giriş yaparak görevinizin detaylarını inceleyiniz.\nSaygılarımızla,\nAkademik Renkler Derneği Yönetimi"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls(); server.login(s_email, s_pass); server.send_message(msg); server.quit()
    except: pass

def send_report_email_notification(task_title, completed_by, assigned_by_username, report_text, earned_pts, max_pts):
    try:
        db_session = SessionLocal()
        assigner = db_session.query(User).filter(User.username == assigned_by_username).first()
        baskan = db_session.query(User).filter(User.alan == "Başkan").first()
        emails_to_send = []
        if assigner and assigner.email: emails_to_send.append(assigner.email)
        if baskan and baskan.email and baskan.email not in emails_to_send: emails_to_send.append(baskan.email)
        db_session.close()
        if not emails_to_send: return
        s_email, s_pass = st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass: return
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls(); server.login(s_email, s_pass)
        for to_email in emails_to_send:
            msg = MIMEMultipart()
            msg['From'] = f"ARDER Sistem <{s_email}>"
            msg['To'] = to_email
            msg['Subject'] = f"✅ Görev Raporu: {task_title}"
            body = f"Merhaba,\n\nEkip üyelerimizden {completed_by}, \"{task_title}\" görevini tamamladı ve sistem üzerinden aşağıdaki raporu iletti.\n\nKazanılan Puan: {earned_pts} / {max_pts}\n\n📋 GÖREV RAPORU\n-------------------------------------------------\n{report_text}\n-------------------------------------------------\n\nBilgilerinize sunarız,\nAkademik Renkler Derneği Yönetimi"
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            server.send_message(msg)
        server.quit()
    except: pass

def send_event_email_notification(to_email, event_title, event_desc, event_date):
    try:
        s_email, s_pass = st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass or not to_email: return False 
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = f"ARDER Sistem <{s_email}>", to_email, f"📌 Yeni Etkinlik Daveti: {event_title}"
        body = f"Değerli Akademik Renkler Derneği Üyesi,\n\nDerneğimiz kapsamında \"{event_title}\" adlı yeni bir etkinlik planlanmıştır.\n\n📅 Tarih: {event_date}\n📍 Detaylar ve Konum: {event_desc}\n\nSistem üzerinden 'Etkinlik' sekmesine girerek katılım durumunuzu bildirmenizi önemle rica ederiz.\n\nİyi çalışmalar dileriz,\nAkademik Renkler Derneği Yönetimi"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls(); server.login(s_email, s_pass); server.send_message(msg); server.quit()
    except: pass

def send_announcement_email_notification(to_email, title, content, author, date):
    try:
        s_email, s_pass = st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass or not to_email: return False 
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = f"ARDER Sistem <{s_email}>", to_email, f"📢 Yeni Duyuru: {title}"
        body = f"Değerli Akademik Renkler Derneği Üyesi,\n\nSisteme yeni bir duyuru eklenmiştir.\n\n📌 Başlık: {title}\n👤 Yazar: {author}\n📅 Tarih: {date}\n\nİçerik:\n{content}\n\nİyi çalışmalar dileriz,\nAkademik Renkler Derneği Yönetimi"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls(); server.login(s_email, s_pass); server.send_message(msg); server.quit()
    except: pass

def send_partner_email_notification(to_email, name, discount, details):
    try:
        s_email, s_pass = st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass or not to_email: return False 
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = f"ARDER Sistem <{s_email}>", to_email, f"🤝 Yeni Kurum Fırsatı: {name}"
        body = f"Değerli Akademik Renkler Derneği Üyesi,\n\nSisteme yeni bir kurum anlaşması / fırsatı eklenmiştir.\n\n🏪 Kurum Adı: {name}\n💸 İndirim/Fırsat: {discount}\n📝 Detaylar: {details}\n\nİyi çalışmalar dileriz,\nAkademik Renkler Derneği Yönetimi"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls(); server.login(s_email, s_pass); server.send_message(msg); server.quit()
    except: pass

def trigger_background_email(*args): threading.Thread(target=send_email_notification, args=args).start()
def trigger_event_email(*args): threading.Thread(target=send_event_email_notification, args=args).start()
def trigger_report_email(*args): threading.Thread(target=send_report_email_notification, args=args).start()
def trigger_announcement_email(*args): threading.Thread(target=send_announcement_email_notification, args=args).start()
def trigger_partner_email(*args): threading.Thread(target=send_partner_email_notification, args=args).start()

def push_notification(title: str, body: str):
    st.session_state["_notif_title"], st.session_state["_notif_body"] = title, body

def _flush_notification():
    t, b = st.session_state.get("_notif_title"), st.session_state.get("_notif_body")
    if t and b:
        components.html(f"<script>(function(){{if (!('Notification' in window)) return; var fn = function() {{ new Notification({json.dumps(t)}, {{body:{json.dumps(b)}}}); }}; if (Notification.permission === 'granted') {{ fn(); }} else if (Notification.permission !== 'denied') {{ Notification.requestPermission().then(function(p){{ if (p==='granted') fn(); }}); }} }})();</script>", height=0)
        st.session_state["_notif_title"] = st.session_state["_notif_body"] = None

def make_ics(title, description, due_date_str):
    try:
        if "-" in due_date_str: dt = datetime.strptime(due_date_str, "%Y-%m-%d")
        else: dt = datetime.strptime(due_date_str, "%d.%m.%Y")
    except: dt = datetime.now() + timedelta(days=7)
    dtstart, dtend = dt.strftime("%Y%m%d"), (dt + timedelta(days=1)).strftime("%Y%m%d")
    dtstamp, uid = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"), f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-arder-task@akademikreklerdernegi"
    desc = (description or "").replace("\n", "\\n").replace(",", "\\,")
    return (f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ARDER//Gorev Yonetimi//TR\nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\nBEGIN:VEVENT\nUID:{uid}\nDTSTAMP:{dtstamp}\nDTSTART;VALUE=DATE:{dtstart}\nDTEND;VALUE=DATE:{dtend}\nSUMMARY:📌 {title}\nDESCRIPTION:{desc}\nSTATUS:CONFIRMED\nBEGIN:VALARM\nTRIGGER:-PT1H\nACTION:DISPLAY\nDESCRIPTION:ARDER Hatırlatma: {title}\nEND:VALARM\nEND:VEVENT\nEND:VCALENDAR\n").encode("utf-8")

def format_event_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        aylar = ["", "OCA", "ŞUB", "MAR", "NİS", "MAY", "HAZ", "TEM", "AĞU", "EYL", "EKİ", "KAS", "ARA"]
        return str(dt.day).zfill(2), aylar[dt.month]
    except: return "00", "BİL"

def show_header():
    st.markdown(f'<div class="app-header">{LOGO_HTML}<div><div class="brand-name">ARDER</div><div class="brand-sub">Akademik Renkler</div></div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 5. LİDERLİK TABLOSU HTML
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def generate_leaderboard_html(users_dict):
    html = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: transparent; margin: 0; padding: 0; }
    .pod{display:flex;justify-content:center;align-items:flex-end;gap:10px;height:210px;margin-bottom:18px;}
    .pc{display:flex;flex-direction:column;align-items:center;width:30%;max-width:110px;}
    .av{width:48px;height:48px;border-radius:16px;margin-bottom:6px;background:linear-gradient(135deg,#1976D2,#2DB5A0);color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900;}
    .pn{font-size:12px;font-weight:800;color:#1A2744;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;width:100%;}
    .pp{font-size:10px;color:#64748b;margin-bottom:5px;font-weight:600;}
    .blk{width:100%;display:flex;justify-content:center;padding-top:10px;font-weight:700;font-size:15px;border-radius:16px 16px 0 0;color:#fff;box-shadow:0 -4px 12px rgba(0,0,0,0.05);}
    .g{height:140px;background:linear-gradient(135deg,#48c6b4,#2DB5A0);} .s{height:105px;background:#e2e8f0;color:#475569;} .b{height:80px;background:linear-gradient(135deg,#94a3b8,#64748b);}
    .li{display:flex;align-items:center;background:#fff;padding:12px 16px;border-radius:20px;margin-bottom:10px;box-shadow:0 4px 16px rgba(0,0,0,0.03);}
    .rb{width:32px;height:32px;display:flex;justify-content:center;align-items:center;border-radius:10px;font-weight:800;font-size:13px;color:#fff;margin-right:12px;flex-shrink:0;}
    .r1{background:#2DB5A0;} .r2{background:#cbd5e1;color:#475569;} .r3{background:#64748b;} .rx{background:#f8fafc;color:#64748b;}
    .ln{font-weight:800;color:#1A2744;font-size:14px;} .lr{font-size:11px;color:#94a3b8;font-weight:500;} .lp{margin-left:auto;font-weight:900;color:#2DB5A0;font-size:18px;}
    </style></head><body><div style="padding:4px;">
    """
    if users_dict:
        u1 = users_dict[0]; u2 = users_dict[1] if len(users_dict) > 1 else None; u3 = users_dict[2] if len(users_dict) > 2 else None
        html += "<div class='pod'>"
        if u2: html += f"<div class='pc'><div class='av'>{u2['username'][0].upper()}</div><div class='pn'>{u2['username']}</div><div class='pp'>{u2['points']} Puan</div><div class='blk s'>🥈</div></div>"
        else: html += "<div class='pc'></div>"
        html += f"<div class='pc'><div class='av'>{u1['username'][0].upper()}</div><div class='pn'>{u1['username']}</div><div class='pp'>{u1['points']} Puan</div><div class='blk g'>🥇</div></div>"
        if u3: html += f"<div class='pc'><div class='av'>{u3['username'][0].upper()}</div><div class='pn'>{u3['username']}</div><div class='pp'>{u3['points']} Puan</div><div class='blk b'>🥉</div></div>"
        else: html += "<div class='pc'></div>"
        html += "</div>"
        for i, u in enumerate(users_dict):
            r = i + 1; rc = f"r{r}" if r <= 3 else "rx"
            html += f"<div class='li'><div class='rb {rc}'>{r}</div><div class='av' style='width:40px;height:40px;font-size:16px;margin-bottom:0;margin-right:12px;border-radius:12px;'>{u['username'][0].upper()}</div><div style='overflow:hidden;'><div class='ln'>{u['username']}</div><div class='lr'>{u['alan']}</div></div><div class='lp'>{u['points']}<span style='font-size:10px;color:#cbd5e1;'> pts</span></div></div>"
    html += "</div></body></html>"
    return html

def render_leaderboard(db_session):
    users = db_session.query(User).order_by(User.points.desc()).all()
    u_dict = [{"username": u.username, "points": u.points, "role": u.role, "alan": u.alan or "—"} for u in users]
    components.html(generate_leaderboard_html(u_dict), height=650, scrolling=True)

# ══════════════════════════════════════════════════════════
# 6. OTURUM VE AYLIK SIFIRLAMA
# ══════════════════════════════════════════════════════════
for k in ["logged_in","username","role"]:
    if k not in st.session_state: st.session_state[k] = False if k=="logged_in" else ""

db = SessionLocal()

def check_monthly_reset(db):
    current_month = datetime.now().strftime("%Y-%m")
    setting = db.query(AppSettings).first()
    if not setting:
        db.add(AppSettings(last_reset_month=current_month))
        db.commit()
    elif setting.last_reset_month != current_month:
        db.query(User).update({User.points: 0})
        setting.last_reset_month = current_month
        db.commit()

check_monthly_reset(db)
_flush_notification()

if 'first_load' not in st.session_state:
    time.sleep(0.4); st.session_state.first_load = True

saved_cookie = controller.get('arder_user')
if saved_cookie and not st.session_state.logged_in:
    u = db.query(User).filter(User.username == saved_cookie).first()
    if u:
        st.session_state.update({"logged_in": True, "username": u.username, "role": u.role}); st.rerun()

# ══════════════════════════════════════════════════════════
# 7. GİRİŞ VE KAYIT EKRANI
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown(f'<div class="login-header">{LOGIN_LOGO_HTML}</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        # BÖLÜM 1: Kullanıcı Adı yerine E-Posta ile giriş.
        lu, lp = st.text_input("E-Posta Adresi"), st.text_input("Şifre", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Giriş Yap", use_container_width=True):
            # BÖLÜM 2: Veritabanında E-Posta eşleşmesi aranıyor.
            user = db.query(User).filter(User.email==lu.strip(), User.password==lp.strip()).first()
            if user:
                controller.set('arder_user', user.username, max_age=2592000) 
                st.session_state.update({"logged_in": True, "username": user.username, "role": user.role})
                push_notification("Hoş Geldin!", f"Merhaba {user.username}."); st.rerun()
            else: st.error("Bilgiler hatalı!")
            
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        ru, rmail, rp = st.text_input("Ad Soyad"), st.text_input("E-Posta"), st.text_input("Şifre", type="password", key="kayit_sifre")
        role = st.selectbox("Görev Dağılımı", ["Üye", "Birim Başkanı", "Moderatör"])
        alanlar = {"Üye": ["Üye", "Sosyal Medya", "İletişim", "İnsan Kaynakları", "Projeler", "Etkinlik"],
                   "Birim Başkanı": ["Sosyal Medya Başkanı", "İletişim Başkanı", "İK Başkanı", "Projeler Başkanı", "Etkinlik Başkanı"],
                   "Moderatör": ["Başkan", "Başkan Yardımcısı", "Sayman", "Genel Sekreter", "Uygulama Yöneticisi"]}
        alan = st.selectbox("Birim", alanlar[role])
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Kayıt Ol", use_container_width=True):
            # BÖLÜM 3: Ekstra geçerli E-Posta formatı ve Mükerrer E-Posta güvenlik kontrolleri.
            if len(ru.strip())<3: st.warning("İsim çok kısa.")
            elif len(rmail.strip())<5 or "@" not in rmail: st.warning("Geçerli bir e-posta adresi giriniz.")
            elif db.query(User).filter(User.username==ru.strip()).first(): st.warning("Bu isim sistemde kayıtlı.")
            elif db.query(User).filter(User.email==rmail.strip()).first(): st.warning("Bu e-posta adresi sistemde zaten kayıtlı.")
            else:
                db.add(User(username=ru.strip(), password=rp.strip(), email=rmail.strip(), role=role, alan=alan, points=0, lifetime_points=0, total_assigned=0, total_completed=0))
                db.commit(); st.success("Başarıyla kayıt olundu! Giriş sekmesinden devam edebilirsiniz.")

# ══════════════════════════════════════════════════════════
# 8. ANA PANELLER VE RENDER FONKSİYONLARI
# ══════════════════════════════════════════════════════════
else:
    cu = db.query(User).filter(User.username==st.session_state.username).first()
    if not cu: st.session_state.logged_in = False; st.rerun()

    show_header()
    BADGE = {"Acil":"badge-acil","Yüksek":"badge-yuksek","Orta":"badge-orta","Düşük":"badge-dusuk"}

    def render_home_tab(db_session):
        pending = db_session.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").count()
        
        st.markdown("""
        <div class="grid-container">
            <div class="grid-item"><div class="grid-icon">📋</div><div class="grid-text">BEKLEYEN İŞ</div><div class="grid-val">{}</div></div>
            <div class="grid-item"><div class="grid-icon">🏆</div><div class="grid-text">AYLIK PUAN</div><div class="grid-val" style="color:#2DB5A0;">{}</div></div>
            <div class="grid-item"><div class="grid-icon">⭐</div><div class="grid-text">TÜM ZAMANLAR</div><div class="grid-val" style="color:#f59e0b;">{}</div></div>
            <div class="grid-item"><div class="grid-icon">✅</div><div class="grid-text">BİTİRİLEN</div><div class="grid-val">{}</div></div>
        </div>
        """.format(pending, cu.points, cu.lifetime_points or 0, cu.total_completed or 0), unsafe_allow_html=True)

        st.markdown('<div class="section-title">📢 Panodaki Duyurular</div>', unsafe_allow_html=True)
        announcements = db_session.query(Announcement).order_by(Announcement.id.desc()).limit(3).all()
        if not announcements:
            st.info("Henüz bir duyuru bulunmuyor.")
        for a in announcements:
            st.markdown(f'<div class="ann-card"><div class="a-title">{a.title}</div><div class="a-date">{a.date} - {a.author}</div><div class="a-content">{a.content}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🏆 Liderlik Tablosu</div>', unsafe_allow_html=True)
        render_leaderboard(db_session)

    def render_board_tab(db_session):
        st.markdown('<div class="section-title">👔 Yönetim Kurulu</div>', unsafe_allow_html=True)
        board_order = ["Başkan", "Başkan Yardımcısı", "Genel Sekreter", "Sayman"]
        board_members = db_session.query(User).filter(User.alan.in_(board_order)).all()
        board_members.sort(key=lambda x: board_order.index(x.alan))
        
        for bm in board_members:
            if bm.avatar:
                avatar_html = f'<img src="{bm.avatar}" style="width: 44px; height: 44px; border-radius: 14px; margin-right: 15px; flex-shrink: 0; object-fit: cover; box-shadow: 0 4px 10px rgba(45,181,160,0.2);">'
            else:
                avatar_html = f'<div class="b-avatar">{bm.username[0].upper()}</div>'
                
            st.markdown(f'<div class="board-card">{avatar_html}<div><div class="b-name">{bm.username}</div><div class="b-title">{bm.alan}</div></div></div>', unsafe_allow_html=True)

    def render_tuzuk_tab():
        st.markdown('<div class="section-title">📜 Dernek Tüzüğü</div>', unsafe_allow_html=True)
        
        tuzuk_metni = """
**AKADEMİK RENKLER DERNEĞİ TÜZÜĞÜ**

**Derneğin Adı ve Merkezi**
**Madde 1-** Derneğin Adı: "AKADEMİK RENKLER Derneği" dir.
Derneğin merkezi Denizli'dir. Şubesi açılabilir.

**Derneğin Amacı ve Bu Amacı Gerçekleştirmek İçin Dernekçe Sürdürülecek Çalışma Konuları ve Biçimleri ile Faaliyet Alanı**
**Madde 2**
**2.1 - Derneğin Amacı**
Dernek; ulusal ve uluslararası düzeyde gençlerin kültür, sanat, akademik ve toplumsal gelişimlerine katkı sağlamak; onların yaratıcılığını, farkındalığını ve kişisel gelişimlerini güçlendirmek için girişimlerde bulunmak ve bu çalışmaları yaygınlaştırmak amacıyla kurulmuştur.
2.1.1. Dernek yönetim kurulu içerisinde yetkin birim yapılanmaları oluşturularak, derneğin etkin ve uzun süreli varlığını sürdürmek,
2.1.2. Derneğimiz; dünyada ve ülkemizde eğitim sektöründeki gelişmeleri akademik boyutta dernek yönetim kurulu üyeleri tarafından etkinlik ve projelerimize katılan üyelerimizi bilgilendirmek amacıyla, aktif ulusal ve uluslararası köprü görevini üstlenir,
2.1.3. Diğer sektörlere ait kurum, kuruluş ve topluluklar ile eş düzeyde, olumlu ilişki yönetimi gerçekleştirmek,
2.1.4. Derneğimiz, katılımcı olan tüm üyelerimizin; kendini geliştirmesini, hayatın güzel yönlerini keşfetmesini, birey ve toplum olarak daha yaşanabilir bir dünya için çalışmasını amaçlar. Bunun yanında her alanda akademik hayatı ve kariyeri için derneğe aykırı olmayan projeleri destekler
2.1.5. Dernek üyelerimiz için faaliyetlerimizle sosyal girişimlerine katkı sağlamak,
2.1.6. Üyelerinin, mesleki bilgi ve birikimlerini, yeteneklerini geliştirmelerine yardımcı olmak üzere gerekli çalışmaları yapmak, yapılanlara katkı sağlamak,
2.1.7. Üyeler arasında maddi ve manevi yönden dayanışma, yardımlaşma ve iş birliği sağlamak, "Dernekçe Sürdürülecek Çalışma Konuları ve Biçimleri" ile "Derneğin Faaliyet Alanları" içerinde geçen alanların güçlendirilmesi, yaygınlaştırılması ve geliştirilmesi yönünde çalışmalar yapmak, bu alanlarda gerekli görülürse ortak platformlar oluşturmak ve ortak çalışma bilinci oluşturulmasında katkıda bulunmak,
2.1.8. Faaliyetlerin yetkin, dürüst, tarafsız ve bağımsız bir şekilde icra edilebilmesi, güçlü ve etkin bir şekilde yürütülmesini sağlamak üzere ortak platformlar oluşturmak, üyelerine bu konularda destek vermek ve yardımcı olmak.

**2.2 Dernekçe Sürdürülecek Çalışma Konuları ve Biçimleri**
2.2.1. Faaliyetlerinin etkinleştirilmesi ve geliştirilmesi için araştırmalar yapmak,
2.2.2. Kurs, seminer, konferans ve panel gibi eğitim çalışmaları düzenlemek,
2.2.3. Amacın gerçekleştirilmesi için gerekli olan her türlü bilgi, belge, doküman ve yayınları temin etmek, dokümantasyon merkezi oluşturmak, çalışmalarını duyurmak için amaçları doğrultusunda gazete, dergi, kitap ve bülten gibi yayınlar çıkarmak,
2.2.4. Amacın gerçekleştirilmesi için sağlıklı bir çalışma ortamını sağlamak, her türlü teknik araç ve gereci, demirbaş ve kırtasiye malzemelerini temin etmek,
2.2.5. Gerekli izinler alınmak şartıyla yardım toplama faaliyetlerinde bulunmak ve yurt içinden ve yurt dışından bağış kabul etmek,
2.2.6. Tüzük amacının gerçekleştirilmesi için ihtiyaç duyulan gelirleri temin etmek amacıyla iktisadi, ticari ve sanayi işletmeler kurmak ve işletmek,
2.2.7. Üyelerinin yararlanmaları ve boş zamanlarını değerlendirebilmeleri için lokal açmak, sosyal ve kültürel tesisler kurmak ve bunları tefriş etmek,
2.2.8. Üyleri arasında sosyal ilişkilerin geliştirilmesi ve devam ettirilmesi için yemekli toplantılar, konser, balo, tiyatro, sergi, spor, gibi eğlenceli etkinlikler düzenlemek veya üyelerinin bu tür etkinliklerden yararlanmalarını sağlamak,
2.2.9. Dernek faaliyetleri için ihtiyaç duyulan taşınır, taşınmaz mal satın almak, satmak, kiralamak, kiraya vermek ve taşınmazlar üzerinde ayni hak tesis etmek,
2.2.10. Amacın gerçekleştirilmesi için gerek görülmesi durumunda yurt içinde ve yurt dışında vakıf kurmak, federasyon kurmak veya kurulu bir federasyona katılmak, gerekli izin alınarak derneklerin kurabileceği tesisleri kurmak,
2.2.11. Uluslararası faaliyette bulunmak, yurt dışındaki dernek veya kuruluşlara üye olmak ve bu kuruluşlarla ortak çalışmalar yapmak veya yardımlaşmak,
2.2.12. Amacın gerçekleştirilmesi için gerek görülmesi halinde, 5072 sayılı Dernek ve Vakıfların Kamu Kurum ve Kuruluşları ile İlişkilerine Dair Kanun hükümleri saklı kalmak üzere, kamu kurum ve kuruluşları ile görev alanlarına giren konularda ortak projeler yürütmek,
2.2.13. Gerekli görülen yerlerde temsilcilikler açmak,
2.2.14. Derneğin amacı ile ilgisi bulunan ve kanunlarla yasaklanmayan alanlarda, diğer derneklerle veya vakıf, sendika ve benzeri sivil toplum kuruluşlarıyla ortak bir amacı gerçekleştirmek için plâtformlar oluşturmak,
2.2.15. Proje hazırlama, yazma, uygulama ve değerlendirme konusunda sivil toplum kuruluşları, kamu kurumları ve üniversiteler arasında farkındalık yaratmak,
2.2.16. Bölgesel kalkınma projeleri hazırlamak, bu konudaki projelere ortak veya iştirakçi olarak katılmak,
2.2.17. Gençlik alanında, Gençlik Ulusal Ajansları, Eğitim, Görsel-İşitsel ve Kültür Yürütme Ajansı, Salto Kaynak Merkezleri, Eurodesk Ağı, Avrupa Komisyonu ve Avrupa Konseyi ile iş birliği ve ortak çalışmalar yürütmek. Genç bireylerin ulusal ve uluslararası sosyal sorumluluk projeleri geliştirmelerine yardımcı olacak etkinlikler düzenlemek ve bu projeleri hayata geçirirken gençlere destek sağlamak,
2.2.18. Yetişkin eğitimine katılımı artırmak amacıyla, özellikle yaşlılar ve temel nitelikleri kazanamadan eğitimlerini yarıda bırakan bireyler gibi kırılgan sosyal gruplara destek sağlamak,
2.2.19. Engelliler, göçmenler ve dezavantajlı bölgelerde yaşayanlar gibi toplumun her kesiminin karar alma süreçlerine katılabileceği sistemler geliştirmek,
2.2.20. Dezavantajlı genç bireyler (sokak çocukları, kimsesiz çocuklar, bağımlı çocuklar, ıslah edilen çocuklar, bedensel ve zihinsel engelli çocuklar, taciz ve şiddet mağduru çocuklar) için ulusal ve uluslararası sosyal sorumluluk projeleri oluşturmak ve bu projeleri gençlerle birlikte yürütmek,
2.2.21. Sağlıklı bir nesil yetiştirmek amacıyla spor kulüpleri kurmak, spor turnuvaları düzenlemek, yaz aylarında çocuklarımızın ve gençlerimizin zamanlarını verimli geçirmelerini sağlamak için kamp programları düzenlemek, yaz kursları açmak, sosyal, spor ve kültürel etkinlikler düzenlemek, gerektiğinde bu alanlarla ilgili resmî kurumlarla iletişime geçerek ortak organizasyonlar gerçekleştirmek,
2.2.22. Kütüphane kurmak, öğrencilere kitap temin etmek, fakir öğrencilere burs ve kredi temin etmek, öğrenciler için sportif tesis ve faaliyetler tahsis etmek, öğrencilerin milli ve mahalli örf ve adetlerimize göre yetişmesini sağlamak için konferanslar tertip etmek,
2.2.23. Girişimcilik konusunda bilgilendirme çalışmaları yapmak ve teşvik etmek,
2.2.24. Girişimcilik bilincinin yaygınlaştırılması amacıyla; girişimcilik konusunda seminerler, atölyeler, paneller, eğitim programları ve benzeri bilgilendirme çalışmaları düzenlemek; girişimcilik faaliyetlerini teşvik edici projeler geliştirmek, iş birliği ağları oluşturmak ve girişimci bireyleri desteklemek.

**2.3 Derneğin Faaliyet Alanı**
Dernek, sanat, kariyer, mimarlık, arkeoloji, dil, kültür, maliye, psikoloji, teknoloji, mühendislik, sosyoloji, tasarım gibi alanlarda yurt içinde ve yurt dışında faaliyet gösterir.
2.3.1. Eğitimler ve Atölyeler: Eğitimler açısından öncelikli çalışmamız, kurum ve kuruluşların temin edebileceği eğitim verilir. Belgesi olan eğitmen veya kursiyer tarafından üyelerimize; başta sanat eğitimleri olmak üzere CV için kullanabilecekleri MEB onaylı, E-devlet üzerinden görülebilen sertifikalı eğitimler verilmesidir. Bunun dışında üniversitemiz bünyesinde yer alan ön lisans, lisans öğrencileri, gelecekte eğitmenlik yapmalarına yönelik eğitim verebilir belgesi olmadan tecrübe kazanması adına, sanat eğitimleri başta olmak üzere tüm eğitimler için kursiyer veya eğitmen olarak da görev alabilirler.
2.3.2. Diğer Eğitim Alanları:
Sanat Eğitimleri: Sanatın toplum üzerindeki etkisini artırmak için çeşitli sanat dallarında eğitimler ve atölyeler düzenlenilir. Bu eğitimler, uzman eğitmenler tarafından verilir ve katılımcılara sertifika sağlanır.
Mesleki Gelişim Kursları: Üyelerin kariyerlerinde ilerlemelerine yardımcı olacak mesleki gelişim kursları, seminerler ve çalıştaylar düzenlenilir.
2.3.3. Sosyal Sorumluluk Projeleri:
Topluma Hizmet Projeleri: Sosyal sorumluluk bilincini yaymak için çevre temizliği, hayvan hakları savunuculuğu, yaşlı bakım merkezlerinde etkinlikler gibi projeler düzenlenilir.
Çocuklara Yönelik Etkinlikler: Çocuklara yönelik yaratıcı ve eğitici etkinlikler düzenlenerek, onların sanata olan ilgileri artırılır.
2.3.4. Kültürel Etkinlikler:
Sergi ve Gösteriler: Üyelerin eserlerinin sergilendiği sanat sergileri, müzik ve tiyatro gösterileri gibi etkinlikler düzenlenilir. Bu etkinlikler, sanata olan ilgiyi artırmak ve toplumda sanatın değerini vurgulamak için kullanılır.
Festival ve Şenlikler: Toplumun çeşitli kesimlerini bir araya getiren kültürel festival ve şenlikler düzenlenir.
2.3.5. Araştırma ve Yayınlar:
Araştırma Destek Programları: Akademik çalışmalar yapan üyelere destek sağlanarak, sanatın toplumsal etkileri üzerine araştırmalar yapılabilir ve bu çalışmalar yayınlanır.
Sanat ve Toplum Üzerine Yayınlar: Sanatın toplum üzerindeki etkisini irdeleyen makaleler, raporlar ve kitaplar yayınlanır.
2.3.6. İş birlikleri ve Ortaklıklar:
Yerel Yönetimler ve STK'larla İş birliği: Yerel yönetimler ve diğer sivil toplum kuruluşları ile iş birliği yaparak ortak projeler geliştirilir. Bu iş birlikleri, toplumsal sorunlara çözümler üretmek için kullanılır.
Uluslararası Projeler: Uluslararası düzeyde faaliyet gösteren kuruluşlarla ortak projeler geliştirerek, global ölçekte sanat ve kültür projelerine katkı sağlanılır.

**Üye Olma Hakkı ve Üyelik İşlemleri**
**Madde 3**
3.1 Fiil ehliyetine sahip bulunan ve derneğin amaç ve ilkelerini benimseyerek bu doğrultuda çalışmayı kabul eden ve Mevzuatın öngördüğü koşullarını taşıyan her gerçek ve tüzel kişi bu derneğe üye olma hakkına sahiptir. Ancak, yabancı gerçek kişilerin üye olabilmesi için Türkiye'de yerleşme hakkına sahip olması da gerekir. Onursal üyelik için bu koşul aranmaz.
3.2 Dernek yönetimine başvuru formu üzerinden yapılacak üyelik başvurusu, dernek yönetim kurulunca en çok otuz gün içinde üyeliğe kabul veya reddi şeklinde karara bağlanır ve sonuç yazıyla başvuru sahibine bildirilir. Başvurusu kabul edilen üye bu amaçla tutulacak deftere kaydedilir.
3.3 Derneğin asıl üyeleri, derneğin kurucuları ile müracaatları üzerine yönetim kurulunca üyeliğe kabul edilen kişilerdir.
3.4 Derneğe maddi ve manevi bakımdan önemli destek sağlamış bulunanlar yönetim kurulu kararı ile onursal üye olarak kabul edilebilir.

**Üyelikten Çıkma**
**Madde 4**
4.1 Her üye yazılı olarak bildirmek kaydıyla, dernekten çıkma hakkına sahiptir.
4.2 Üyenin istifa dilekçesi yönetim kuruluna ulaştığı anda çıkış işlemleri sonuçlanmış sayılır.
4.3 Üyelikten ayrılma, üyenin derneğe olan birikmiş borçlarını sona erdirmez.

**Üyelikten Çıkarılma**
**Madde 5-** Dernek üyeliğinden çıkarılmayı gerektiren haller;
5.1. Dernek tüzüğüne aykırı davranışlarda bulunmak,
5.2. Verilen görevlerden sürekli kaçınmak,
5.3. Yazılı ikazlara rağmen üyelik aidatını altı ay içinde ödememek,
5.4. Dernek organlarınca verilen kararlara uymamak,
5.5. Üye olma şartlarını kaybetmiş olmak,
5.6. Derneğin ismini karalayıcı; yazılı, görsel, işitsel ve sosyal medya vb. platformlarda dernek hakkında uygun olmayan yorumlar/yazılar paylaşmak,
5.7. Dernek amacına aykırı hareketleri tespit edilen, Derneğin onur ve itibarıyla bağdaşmayan fiil ve hareketlerde bulunan, dernek faaliyetlerini işletilmesini engelleyen üyeler ile halkın değer yargılarına ve Türk Ceza Kanunu'na göre yüz kızartıcı ve utanç verici fiiller içinde bulunmak,
5.8. Vefat eden üyeler için, ilk Yönetim Kurulunda üyelikten düşürme kararı verilir ve üye kayıt defterinden silinir. Vefat eden üyelerin Derneğe olan borçları da silinir.
Yukarıda sayılan durumlardan birinin tespiti halinde yönetim kurulu kararı ile üyelikten çıkarılır. Dernekten çıkan veya çıkarılanlar, üye kayıt defterinden silinir ve dernek malvarlığında hak iddia edemez.

**Dernek Organları**
**Madde 6-** Derneğin organları aşağıda gösterilmiştir.
6.1. Dernek Genel kurul,
6.2. Yönetim kurulu,
6.3. Denetim kurulu,

**Dernek Genel Kurulunun Kuruluş Şekli, Toplanma Zamanı ve Çağrı ve Toplantı Usulü**
**Madde 7-** Genel kurul, derneğin en yetkili karar organı olup; derneğe kayıtlı üyelerden oluşur.
7.1.Genel kurul;
7.1.1. Bu tüzükte belli edilen zamanda olağan,
7.1.2. Yönetim veya denetim kurulunun gerekli gördüğü hallerde veya dernek üyelerinden beşte birinin yazılı isteği üzerine otuz gün içinde olağanüstü toplanır.
7.1.3. Olağan genel kurul, 3 yılda bir, ARALIK ayı içerisinde, yönetim kurulunca belirlenecek gün yer ve saatte toplanır.
7.1.4. Genel kurul toplantıya yönetim kurulunca çağrılır.
7.1.5. Yönetim kurulu, genel kurulu toplantıya çağırmazsa; üyelerden birinin başvurusu üzerine sulh hakimi, üç üyeyi genel kurulu toplantıya çağırmakla görevlendirir.
7.2. Çağrı Usulü
7.2.1. Yönetim kurulu, dernek tüzüğüne göre genel kurula katılma hakkı bulunan üyelerin listesini düzenler. Genel kurula katılma hakkı bulunan üyeler, en az onbeş gün önceden, toplantının günü, saati, yeri ve gündemi en az bir gazetede veya derneğin internet sayfasında ilan edilmek, yazılı olarak bildirilmek, üyenin bildirdiği elektronik posta adresine ya da iletişim numarasına mesaj gönderilmek veya mahalli yayın araçları kullanılmak suretiyle toplantıya çağrılır. Bu çağrıda, çoğunluk sağlanamaması sebebiyle toplantı yapılamazsa, ikinci toplantının hangi gün, saat ve yerde yapılacağı da belirtilir. İlk toplantı ile ikinci toplantı arasındaki süre yedi günden az, altmış günden fazla olamaz.
7.2.2. Toplantı, çoğunluk sağlanamaması sebebinin dışında başka bir nedenle geri bırakılırsa, bu durum geri bırakma sebepleri de belirtilmek suretiyle, ilk toplantı için yapılan çağrı usulüne uygun olarak üyelere duyurulur. İkinci toplantının geri bırakma tarihinden itibaren en geç altı ay içinde yapılması zorunludur. Üyeler ikinci toplantıya, birinci fıkrada belirtilen esaslara göre yeniden çağrılır. Genel kurul toplantısı bir defadan fazla geri bırakılamaz.
7.3. Toplantı Usulü
7.3.1. Genel kurul, katılma hakkı bulunan üyelerin salt çoğunluğunun, tüzük değişikliği ve derneğin feshi hallerinde ise üçte ikisinin katılımıyla toplanır; çoğunluğun sağlanamaması sebebiyle toplantının ertelenmesi durumunda ikinci toplantıda çoğunluk aranmaz. Ancak, bu toplantıya katılan üye sayısı, yönetim ve denetim kurulları üye tam sayısının iki katından az olamaz.
7.3.2. Genel kurula katılma hakkı bulunan üyelerin listesi toplantı yerinde hazır bulundurulur. Toplantı yerine girecek üyelerin resmi makamlarca verilmiş kimlik belgeleri, yönetim kurulu üyeleri veya yönetim kurulunca görevlendirilecek görevliler tarafından kontrol edilir. Üyeler, yönetim kurulunca düzenlenen listedeki adları karşısına imza koyarak toplantı yerine girerler.
7.3.3. Toplantı yeter sayısı sağlanmışsa durum bir tutanakla tespit edilir ve toplantı yönetim kurulu başkanı veya görevlendireceği yönetim kurulu üyelerinden biri tarafından açılır. Toplantı yeter sayısı sağlanamaması halinde de yönetim kurulunca bir tutanak düzenlenir.
7.3.4. Açılıştan sonra, toplantıyı yönetmek üzere bir başkan ve yeteri kadar başkan vekili ile yazman seçilerek divan heyeti oluşturulur.
7.3.5. Dernek organlarının seçimi için yapılacak oylamalarda, oy kullanan üyelerin divan heyetine kimliklerini göstermeleri ve hazırun listesindeki isimlerinin karşılarını imzalamaları zorunludur.
7.3.6. Toplantının yönetimi ve güvenliğinin sağlanması divan başkanına aittir.
7.3.7. Genel kurulda, yalnızca gündemde yer alan maddeler görüşülür. Ancak toplantıda hazır bulunan üyelerin onda biri tarafından görüşülmesi yazılı olarak istenen konuların gündeme alınması zorunludur.
7.3.8. Genel kurulda her üyenin bir oy hakkı vardır; üye oyunu şahsen kullanmak zorundadır. Onursal üyeler genel kurul toplantılarına katılabilir ancak oy kullanamazlar. Tüzel kişinin üye olması halinde, tüzel kişinin yönetim kurulu başkanı veya temsille görevlendireceği kişi oy kullanır.
7.3.9. Toplantıda görüşülen konular ve alınan kararlar bir tutanağa yazılır ve divan başkanı ile yazmanlar tarafından birlikte imzalanır. Toplantı sonunda, tutanak ve diğer belgeler yönetim kurulu başkanına teslim edilir. Yönetim kurulu başkanı bu belgelerin korunmasından ve yeni seçilen yönetim kuruluna yedi gün içinde teslim etmekten sorumludur.

**Genel Kurulun Oy kullanma ve Karar Alma Usul ve Şekilleri**
**Madde 8-** Genel kurulda, aksine karar alınmamışsa, oylamalar açık olarak yapılır. Açık oylamada, genel kurul başkanının belirteceği yöntem uygulanır. Gizli oylama yapılacak olması durumunda ise, toplantı başkanı tarafından mühürlenmiş kağıtlar veya oy pusulaları üyeler tarafından gereği yapıldıktan sonra içi boş bir kaba atılır ve oy vermenin bitiminden sonra açık dökümü yapılarak sonuç belirlenir.
Genel kurul kararları, toplantıya katılan üyelerin salt çoğunluğuyla alınır. Şu kadar ki, tüzük değişikliği ve derneğin feshi kararları, ancak toplantıya katılan üyelerin üçte iki çoğunluğuyla alınabilir.
8.1. Toplantısız veya Çağrısız Alınan Kararlar: Bütün üyelerin bir araya gelmeksizin yazılı katılımıyla alınan kararlar ile dernek üyelerinin tamamının bu tüzükte yazılı çağrı usulüne uymaksızın bir araya gelerek aldığı kararlar geçerlidir. Bu şekilde karar alınması olağan toplantı yerine geçmez.

**Genel Kurulun Görev ve Yetkileri**
**Madde 9-** Aşağıda yazılı hususlar genel kurulca görüşülüp karara bağlanır.
9.1. Dernek organlarının seçilmesi,
9.2. Dernek tüzüğünün değiştirilmesi,
9.3. Yönetim ve denetim kurulları raporlarının görüşülmesi ve yönetim kurulunun ibrası,
9.4. Yönetim kurulunca hazırlanan bütçenin görüşülüp aynen veya değiştirilerek kabul edilmesi,
9.5. Dernek için gerekli olan taşınmaz malların satın alınması veya mevcut taşınmaz malların satılması hususunda yönetim kuruluna yetki verilmesi,
9.6. Yönetim kurulunca dernek çalışmaları ile ilgili olarak hazırlanacak yöneltmelikleri inceleyip aynen veya değiştirilerek onaylanması,
9.7. Dernek yönetim ve denetim kurullarının kamu görevlisi olmayan başkan ve üyelerine verilecek ücret ile her türlü ödenek, yolluk ve tazminatlar ile dernek hizmetleri için görevlendirilecek üyelere verilecek gündelik ve yolluk miktarlarının tespit edilmesi,
9.8. Derneğin federasyona katılması ve ayrılmasının kararlaştırılması,
9.9. Derneğin uluslararası faaliyette bulunması, yurt dışındaki dernek ve kuruluşlara üye olarak katılması veya ayrılması,
9.10. Derneğin vakıf kurması,
9.11. Derneğin fesih edilmesi,
9.12. Yönetim kurulunun diğer önerilerinin incelenip karara bağlanması,
9.13. Mevzuatta genel kurulca yapılması belirtilen diğer görevlerin yerine getirilmesi,
Genel kurul, derneğin diğer organlarını denetler ve onları haklı sebeplerle her zaman görevden alabilir. Genel kurul, üyeliğe kabul ve üyelikten çıkarma hakkında son kararı verir. Derneğin en yetkili organı olarak derneğin diğer bir organına verilmemiş olan işleri görür ve yetkileri kullanır.

**Yönetim Kurulunun Teşkili, Görev ve Yetkileri**
**Madde 10-** Yönetim kurulu, beş asıl ve beş yedek üye olarak genel kurulca seçilir. Yönetim kurulu, seçimden sonraki ilk toplantısında bir kararla görev bölüşümü yaparak başkan, başkan yardımcısı, sekreter, sayman ve üye'yi belirler. Yönetim kurulu asıl üyeliğinde istifa veya başka sebeplerden dolayı boşalma olduğu taktirde genel kurulda aldığı oy çokluğu sırasına göre yedek üyelerin göreve çağrılması mecburidir.
10.1. Yönetim Kurulunun Görev ve Yetkileri
Yönetim kurulu aşağıdaki hususları yerine getirir.
10.1.1. Derneği temsil etmek veya bu hususta kendi üyelerinden bir veya birkaçına yetki vermek,
10.1.2. Gelir ve gider hesaplarına ilişkin işlemleri yapmak ve gelecek döneme ait bütçeyi hazırlayarak genel kurula sunmak,
10.1.3. Derneğin çalışmaları ile ilgili yönetmelikleri hazırlayarak genel kurul onayına sunmak
10.1.4. Genel kurulun verdiği yetki ile taşınmaz mal satın almak, derneğe ait taşınır ve taşınmaz malları satmak, bina veya tesis inşa ettirmek, kira sözleşmesi yapmak, dernek lehine rehin ipotek veya ayni haklar tesis ettirmek,
10.1.5. Gerekli görülen yerlerde temsilcilik açılmasını sağlamak
10.1.6. Genel kurulda alınan kararları uygulamak,
10.1.7. Her faaliyet yılı sonunda derneğin işletme hesabı tablosu veya bilanço ve gelir tablosu ile yönetim kurulu çalışmalarını açıklayan raporunu düzenlemek, toplandığında genel kurula sunmak,
10.1.8. Bütçenin uygulanmasını sağlamak,
10.1.9. Derneğe üye alınması veya üyelikten çıkarılma hususlarında karar vermek.
10.1.10. Derneğin amacını gerçekleştirmek için her çeşit kararı almak ve uygulamak,
10.1.11. Mevzuatın kendisine verdiği diğer görevleri yapmak ve yetkileri kullanmak.

**Denetim Kurulunun Teşkili, Görev ve Yetkileri**
**Madde 11-** Denetim kurulu, üç asıl ve üç yedek üye olarak genel kurulca seçilir. Denetim kurulu asıl üyeliğinde istifa veya başka sebeplerden dolayı boşalma olduğu taktirde genel kurulda aldığı oy çokluğu sırasına göre yedek üyelerin göreve çağrılması mecburidir.
11.1. Denetim Kurulunun Görev ve Yetkileri
Denetim kurulu; derneğin, tüzüğünde gösterilen amaç ve amacın gerçekleştirilmesi için sürdürüleceği belirtilen çalışma konuları doğrultusunda faaliyet gösterip göstermediğini, defter, hesap ve kayıtların mevzuata ve dernek tüzüğüne uygun olarak tutulup tutulmadığını, dernek tüzüğünde tespit edilen esas ve usullere göre ve bir yılı geçmeyen aralıklarla denetler ve denetim sonuçlarını bir rapor halinde yönetim kuruluna ve toplandığında genel kurula sunar. Denetim kurulu; gerektiğinde genel kurulu toplantıya çağırır.

**Derneğin Gelir Kaynakları**
**Madde 12-** Derneğin gelir kaynakları aşağıda sayılmıştır.
12.1. Üye Aidatı: Üyelerden giriş ödentisi olarak 50 TL, aylık olarak ta 10 TL aidat alınır. Bu miktarları artırmaya veya eksiltmeye genel kurul yetkilidir.
12.2. Gerçek ve tüzel kişilerin kendi isteği ile derneğe yaptıkları bağış ve yardımlar.
12.3. Dernek tarafından tertiplenen çay ve yemekli toplantı, gezi ve eğlence, temsil, konser, spor yarışması ve konferans gibi faaliyetlerden sağlanan gelirler,
12.4. Derneğin mal varlığından elde edilen gelirler,
12.5. Yardım toplama hakkındaki mevzuat hükümlerine uygun olarak toplanacak bağış ve yardımlar.
12.6. Derneğin, amacını gerçekleştirmek için ihtiyaç duyduğu geliri temin etmek amacıyla giriştiği ticari faaliyetlerden elde edilen kazançlar.
12.7. Diğer gelirler.

**Derneğin Defter Tutma Esas ve Usulleri ve Tutulacak Defterler**
**Madde 13-** Defter tutma esasları; Dernekte, işletme hesabı esasına göre defter tutulur. Ancak, yıllık brüt gelirin Dernekler Yönetmeliğinin 31. Maddesinde belirtilen haddi aşması durumunda takip eden hesap döneminden başlayarak bilanço esasına göre defter tutulur. Bilanço esasına geçilmesi durumunda, üst üste iki hesap döneminde yukarıda belirtilen haddin altına düşülürse, takip eden yıldan itibaren işletme hesabı esasına dönülebilir. Yukarıda belirtilen hadde bağlı kalmaksızın yönetim kurulu kararı ile bilanço esasına göre defter tutulabilir. Derneğin ticari işletmesi açılması durumunda, bu ticari işletme için, ayrıca Vergi Usul Kanunu hükümlerine göre defter tutulur.
13.1. Kayıt Usulü: Derneğin defter ve kayıtları Dernekler Yönetmeliğinde belirtilen usul ve esasa uygun olarak tutulur.
13.2. Tutulacak Defterler: Dernekte, aşağıda yazılı defterler tutulur.
A. İşletme hesabı esasında tutulacak defterler ve uyulacak esaslar aşağıdaki gibidir:
A.1. Karar Defteri: Yönetim kurulu kararları tarih ve numara sırasıyla bu deftere yazılır ve kararların altı toplantıya katılan üyelerce imzalanır.
A.2. Üye Kayıt Defteri: Derneğe üye olarak girenlerin kimlik bilgileri, derneğe giriş ve çıkış tarihleri bu deftere işlenir. Üyelerin ödedikleri giriş ve yıllık aidat miktarları bu deftere işlenebilir.
A.3. Evrak Kayıt Defteri: Gelen ve giden evraklar, tarih ve sıra numarası ile bu deftere kaydedilir. Gelen evrakın asılları ve giden evrakın kopyaları dosyalanır. Elektronik posta yoluyla gelen veya giden evraklar çıktısı alınmak suretiyle saklanır.
A.4. İşletme Hesabı Defteri: Dernek adına alınan gelirler ve yapılan giderler açık ve düzenli olarak bu deftere işlenir.
B. Bilanço esasında tutulacak defterler ve uyulacak esaslar aşağıdaki gibidir:
B.1. (a) bendinin 1, 2 ve 3 üncü alt bentlerinde kayıtlı defterler bilanço esasında defter tutulması durumunda da tutulur.
B.2. Yevmiye Defteri ve Büyük Defter: Bu defterlerin tutulma usulü ile kayıt şekli Vergi Usul Kanunu ile bu Kanununun Maliye Bakanlığına verdiği yetkiye istinaden yayımlanan Muhasebe Sistemi Uygulama Genel Tebliğleri esaslarına göre yapılır.
13.3. Defterlerin Tasdiki: Dernekte, tutulması zorunlu olan defterler (Büyük Defter hariç), kullanmaya başlamadan önce il sivil toplumla ilişkiler müdürlüğüne veya notere tasdik ettirilir. Bu defterlerin kullanılmasına sayfaları bitene kadar devam edilir ve defterlerin ara tasdiki yapılmaz. Ancak, bilanço esasına göre tutulan Yevmiye Defteri'nin kullanılacağı yıldan önce gelen son ayda, her yıl yeniden tasdik ettirilmesi zorunludur.
13.4. Gelir Tablosu ve Bilanço Düzenlenmesi: İşletme hesabı esasına göre kayıt tutulması durumunda yıl sonlarında (31 Aralık) (Dernekler Yönetmeli EK-16'da belirtilen) "İşletme Hesabı Tablosu" düzenlenir. Bilanço esasına göre defter tutulması durumunda ise, yılsonlarında (31 Aralık), Maliye Bakanlığınca yayımlanan Muhasebe Sistemi Uygulama Genel Tebliğlerini esas alarak bilanço ve gelir tablosu düzenlenir.

**Derneğin Gelir ve Gider İşlemleri**
**Madde 14-** Gelir ve gider belgeleri; Dernek gelirleri, (Dernekler Yönetmeliği EK- 17'de örneği bulunan) "Alındı Belgesi" ile tahsil edilir. Dernek gelirlerinin bankalar aracılığı ile tahsili halinde banka tarafından düzenlenen dekont veya hesap özeti gibi belgeler alındı belgesi yerine geçer. Dernek giderleri ise fatura, perakende satış fişi, serbest meslek makbuzu gibi harcama belgeleri ile yapılır. Ancak derneğin, Gelir Vergisi Kanunu'nun 94'üncü maddesi kapsamında bulunan ödemeleri için Vergi Usul Kanunu hükümlerine göre gider pusulası, bu kapsamda da bulunmayan ödemeleri için (Dernekler Yönetmeliği EK-13'te örneği buluna) "Gider Makbuzu" veya "Banka Dekontu" gibi belgeler harcama belgesi olarak kullanılır. Dernek tarafından kişi, kurum veya kuruluşlara yapılacak bedelsiz mal ve hizmet teslimleri (Dernekler Yönetmeliği EK-14'te örneği bulunan) "Ayni Yardım Teslim Belgesi" ile yapılır. Kişi, kurum veya kuruluşlar tarafından derneğe yapılacak bedelsiz mal ve hizmet teslimleri ise (Dernekler Yönetmeliği EK-15'te örneği bulunan) "Ayni Bağış Alındı Belgesi" ile kabul edilir. Bu belgeler; Ek-13, Ek-14 ve Ek-15'te gösterilen biçim ve ebatta, müteselsil seri ve sıra numarası taşıyan, kendinden karbonlu elli asıl ve elli koçan yaprağından meydana gelen ciltler veya elektronik sistemler ve yazı makineleri aracılığıyla yazdırılacak form veya sürekli form şeklinde bastırılır. Form veya sürekli form şeklinde bastırılacak belgelerin, belirtilen nitelikte olması zorunludur.
14.1. Alındı Belgeleri: Dernek gelirlerinin tahsilinde kullanılacak "Alındı Belgeleri" (Dernekler Yönetmeliği EK-17'de gösterilen biçim ve ebatta) yönetim kurulu kararıyla, matbaaya bastırılır. Alındı belgelerinin bastırılması ve kontrolü, matbaadan teslim alınması, deftere kaydedilmesi, eski ve yeni saymanlar arasında devir teslimi ve alındı belgesi ile dernek adına gelir tahsil edecek kişi veya kişiler tarafından bu alındı belgelerinin kullanımına ve toplanılan gelirlerin teslimine ilişkin hususlarda Dernekler Yönetmeliğinin ilgili hükümlerine göre hareket edilir.
14.2. Yetki Belgesi: Yönetim kurulu asıl üyeleri hariç, dernek adına gelir tahsil edecek kişi veya kişiler, yetki süresi de belirtilmek suretiyle, yönetim kurulu kararı ile tespit edilir. Gelir tahsil edecek kişilerin açık kimliği, imzası ve fotoğraflarını ihtiva eden (Dernekler Yönetmeliği Ek-19'da yer alan) "Yetki Belgesi" dernek tarafından iki nüsha olarak düzenlenerek, dernek yönetim kurulu başkanınca onaylanır. Yönetim kurulu asıl üyeleri yetki belgesi olmadan gelir tahsil edebilir. Yetki belgelerinin süresi yönetim kurulu tarafından en çok bir yıl olarak belirlenir. Süresi biten yetki belgeleri birinci fıkraya göre yenilenir. Yetki belgesinin süresinin bitmesi veya adına yetki belgesi düzenlenen kişinin görevinden ayrılması, ölümü, işine veya görevine son verilmesi gibi hallerde, verilmiş olan yetki belgelerinin dernek yönetim kuruluna bir hafta içinde teslimi zorunludur. Ayrıca, gelir toplama yetkisi yönetim kurulu kararı ile her zaman iptal edilebilir."
14.3. Gelir ve Gider Belgelerinin Saklama Süresi; Defterler hariç olmak üzere, dernek tarafından kullanılan alındı belgeleri, harcama belgeleri ve diğer belgeler özel kanunlarda belirtilen süreler saklı kalmak üzere, kaydedildikleri defterlerdeki sayı ve tarih düzenine uygun olarak 5 yıl süreyle saklanır.

**Beyanname Verilmesi**
**Madde 15-** Derneğin, bir önceki yıla ait faaliyetleri ile gelir ve gider işlemlerinin yıl sonu itibarıyla sonuçlarına ilişkin (Dernekler Yönetmeliği EK-21'de bulunan) "Dernek Beyannamesi" dernek yönetim kurulu tarafından doldurarak, her takvim yılının ilk dört ayı içinde dernek başkanı tarafından mahallin mülki idare amirliğine verilir.

**Bildirim Yükümlülüğü**
**Madde 16-** Mülki amirliğe yapılacak bildirimler;
16.1. Genel Kurul Sonuç Bildirimi: Olağan veya olağanüstü genel kurul toplantılarını izleyen kırk beş gün içinde, yönetim ve denetim kurulları ile diğer organlara seçilen asıl ve yedek üyeleri içeren (Dernekler Yönetmeliği Ek-3'te yer alan) Genel Kurul Sonuç Bildirimi mülki idare amirliğine verilir. Genel kurul toplantısında tüzük değişikliği yapılması halinde; genel kurul toplantı tutanağı, tüzüğün değişen maddelerinin eski ve yeni şekli, her sayfası yönetim kurulu üyelerinin salt çoğunluğunca imzalanmış dernek tüzüğünün son şekli, bu fıkrada belirtilen süre içinde ve bir yazı ekinde mülki idare amirliğine verilir.
16.2. Taşınmazların Bildirilmesi: Derneğin edindiği taşınmazlar tapuya tescilinden itibaren otuz gün içinde (Dernekler Yönetmeliği EK-26'da sunulan) "Taşınmaz Mal Bildirimi"ni doldurmak suretiyle mülki idare amirliğine bildirilir.
16.3. Yurtdışından Yardım Alma Bildirimi: Dernek tarafından, yurtdışından yardım alınacak olması durumunda yardım alınmadan önce (Dernekler Yönetmeliği EK-4'te belirtilen) "Yurtdışından Yardım Alma Bildirimi" doldurup mülki idare amirliğine bildirimde bulunulur. Nakdi yardımların bankalar aracılığıyla alınması ve kullanılmadan önce bildirim şartının yerine getirilmesi zorunludur.
16.4. Kamu kurum ve kuruluşları ile yürütülen ortak projeler: Derneklerin, görev alanlarına ilişkin konularda kamu kurum ve kuruluşlarıyla iş birliği yapabilmesi, ortak bir projenin yürütülmesi şeklinde olur. Ancak, 5072 sayılı Dernek ve Vakıfların Kamu Kurum ve Kuruluşları ile İlişkilerine Dair Kanun hükümleri saklıdır. Projelerin, toplumun ihtiyaç ve sorunlarına yönelik çözümler üretecek ve toplumsal gelişmeye katkı sağlayacak nitelikte olması şarttır. Yapılacak protokol çerçevesinde, projenin yürütülmesinden sorumlu olan, kamu kurum ve kuruluşu ile derneğin eşit sayıda temsilcilerinden oluşan ve tercihen koordinatörlüğünü dernek temsilcilerinden birinin yaptığı bir proje yönetim grubu oluşturulur. Protokolde, proje yönetim grubunda proje saymanı olarak dernek saymanının yer alması zorunludur. Kamu kurum ve kuruluşları ile yürütecek ortak projelerde kendi kanunlarında aksine hüküm bulunmadığı hallerde, ortaklık anlaşması çerçevesinde, proje maliyetine sağlayacakları nakdi katkılar ortak bir hesapta bloke edilir. Kamu kurum ve kuruluşları projelere en fazla ayni veya nakdi yüzde elli katkıda bulunabilirler. Kamu kurum ve kuruluşları proje süresini geçmemek şartıyla, ortak projeye arsa tahsisinde bulunabilir. Proje çerçevesinde yapılacak harcamaların bir bankada açılacak ortak bir hesaptan yapılması, harcamaların belgelendirilmesi ve bu belgelerin asıl suretlerinin dernekler ile ilgili kamu kurum ve kuruluşunda saklanması zorunludur. Bu şekilde yürütülen projelerin gerçekleşme durumu ve bu projeler için yapılan harcamalar ilgili kamu kurum ve kuruluşu tarafından denetlenebileceği gibi, mülki idare amirleri tarafından da denetlenebilir.
16.5. Değişikliklerin Bildirilmesi: Derneğin yerleşim yerinde meydana gelen değişiklik (Dernekler Yönetmeliği EK-24'te belirtilen) "Yerleşim Yeri Değişiklik Bildirimi"; genel kurul toplantısı dışında dernek organlarında meydana gelen değişiklikler (Dernekler Yönetmeliği EK-25'te belirtilen) "Dernek Organlarındaki Değişiklik Bildirimi" doldurulmak suretiyle, değişikliği izleyen kırk beş gün içinde mülki idare amirliğine bildirilir. Dernek tüzüğünde yapılan değişiklikler de tüzük değişikliğinin yapıldığı genel kurul toplantısını izleyen kırk beş gün içinde, genel kurul sonuç bildirimi ekinde mülki idare amirliğine bildirilir.

**Temsilcilik Açma**
**Madde 17-** Dernek, gerekli gördüğü yerlerde dernek faaliyetlerini yürütmek amacıyla yönetim kurulu kararıyla temsilcilik açabilir. Temsilciliğin adresi, yönetim kurulu kararıyla temsilci olarak görevlendirilen kişi veya kişiler tarafından o yerin mülkî idare amirliğine yazılı olarak bildirilir. Temsilcilik, dernek genel kurulunda temsil edilmez.

**Derneğin İç Denetimi**
**Madde 18-** Dernekte genel kurul, yönetim kurulu veya denetim kurulu tarafından iç denetim yapılabileceği gibi, bağımsız denetim kuruluşlarına da denetim yaptırılabilir. Genel kurul, yönetim kurulu veya bağımsız denetim kuruluşlarınca denetim yapılmış olması, denetim kurulunun yükümlülüğünü ortadan kaldırmaz. Denetim kurulu tarafından en geç yılda bir defa derneğin denetimi gerçekleştirilir. Genel kurul veya yönetim kurulu, gerek görülen hallerde denetim yapabilir veya bağımsız denetim kuruluşlarına denetim yaptırabilir.

**Derneğin Borçlanma Usulleri**
**Madde 19-** Dernek amacını gerçekleştirmek ve faaliyetlerini yürütebilmek için ihtiyaç duyulması halinde yönetim kurulu kararı ile borçlanma yapabilir. Bu borçlanma kredili mal ve hizmet alımı konularında olabileceği gibi nakit olarak ta yapılabilir. Ancak bu borçlanma, derneğin gelir kaynakları ile karşılanamayacak miktarlarda ve derneği ödeme güçlüğüne düşürecek nitelikte yapılamaz.

**Derneğin Şubelerinin Kuruluşu**
**Madde 20-** Dernek, gerekli görülen yerlerde genel kurul kararıyla şube açabilir. Bu amaçla dernek yönetim kurulunca yetki verilen en az üç kişilik kurucular kurulu, Dernekler Yönetmeliği'nde belirtilen şube kuruluş bildirimini ve gerekli belgeleri, şube açılacak yerin en büyük mülki amirliğine verir.

**Şubelerin Görev ve Yetkileri**
**Madde 21-** Şubeler, tüzel kişiliği olamayan, dernek amaç ve hizmet konuları doğrultusunda özerk faaliyetlerde bulunmakla görev ve yetkili, tüm işlemlerinden doğan alacak ve borçlarından ötürü kendisinin sorumlu olduğu dernek iç örgütüdür.

**Şubelerin Organları ve Şubelere Uygulanacak Hükümler**
**Madde 22-** Şubenin organları, genel kurul, yönetim kurulu ve denetim kurulu'dur. Genel kurul, şubenin kayıtlı üyelerinden oluşur. Yönetim kurulu, beş asıl ve beş yedek, denetim kurulu ise üç asıl ve üç yedek üye olarak şube genel kurulunca seçilir. Bu organların görev ve yetkileri ile bu tüzükte yer alan dernekle ilgili diğer hükümler, mevzuatın öngördüğü çerçevede şube'de de uygulanır.

**Şubelerin Genel Kurullarının Toplanma Zamanı ve Genel Merkez Genel Kurulunda Nasıl Temsil Edileceği**
**Madde 23-** Şubeler, genel kurul olağan toplantılarını genel merkez genel kurulu toplantısından en az iki ay önce bitirmek zorundadırlar. Şubelerin olağan genel kurulu, 3 yılda bir, AĞUSTOS ayı içeresinde, şube yönetim kurulunca belirlenecek gün yer ve saatte toplanır. Şubeler, genel kurul sonuç bildiriminin bir örneğini toplantının yapıldığı tarihi izleyen kırk beş gün içinde mülki idare amirliğine ve dernek genel merkezine bildirmek zorundadırlar. Şubeler, şube sayısı üçe kadar genel merkez genel kurulunda tüm üyelerin doğrudan katılımı ile; şube sayısı üçten fazla olması durumunda ise, şubede kayıtlı her yirmi (20) üye için üç (3), arta kalan üye sayısı 10'dan fazla ise bu üyeler içinde bir olmak üzere şube genel kurulunda seçilecek delegeler aracılığı ile genel merkez genel kuruluna katılma hakkına sahiptir. Genel merkez genel kuruluna en son şube genel kurulunda seçilen delegeler katılır. Genel merkez yönetim ve denetim kurulu üyeleri genel merkez genel kuruluna katılır, ancak şube adına delege seçilmedikleri sürece oy kullanamazlar. Şubelerin yönetim veya denetim kurulunda görevli olanlar genel merkez yönetim veya denetim kuruluna seçildiklerinde şubedeki görevinden ayrılırlar.

**Temsilcilik Açma**
**Madde 24-** Dernek, gerekli gördüğü yerlerde dernek faaliyetlerini yürütmek amacıyla yönetim kurulu kararıyla temsilcilik açabilir. Temsilciliğin adresi, yönetim kurulu kararıyla temsilci olarak görevlendirilen kişi veya kişiler tarafından o yerin mülkî idare amirliğine yazılı olarak bildirilir. Temsilcilik, dernek genel kurulunda temsil edilmez. Şubeler temsilcilik açamazlar.

**Tüzüğün Ne Şekilde Değiştirileceği**
**Madde 25-** Tüzük değişikliği genel kurul kararı ile yapılabilir. Genel kurulda tüzük değişikliği yapılabilmesi için genel kurula katılma hakkı bulunan üyelerin 2/3 çoğunluğu aranır. Çoğunluğun sağlanamaması sebebiyle toplantının ertelenmesi durumunda ikinci toplantıda çoğunluk aranmaz. Ancak, bu toplantıya katılan üye sayısı, yönetim ve denetim kurulları üye tam sayısının iki katından az olamaz. Tüzük değişikliği için gerekli olan karar çoğunluğu toplantıya katılan ve oy kullanma hakkı bulunan üyelerin oylarının 2/3 3'ü'dür. Genel kurulda tüzük değişikliği oylaması açık olarak yapılır.

**Derneğin Feshi ve Mal Varlığının Tasfiye Şekli**
**Madde 26-** Genel kurul, her zaman derneğin feshine karar verebilir. Genel kurulda fesih konusunun görüşülebilmesi için genel kurula katılma hakkı bulunan üyelerin 2/3 çoğunluğu aranır. Çoğunluğun sağlanamaması sebebiyle toplantının ertelenmesi durumunda ikinci toplantıda çoğunluk aranmaz. Ancak, bu toplantıya katılan üye sayısı, yönetim ve denetim kurulları üye tam sayısının iki katından az olamaz. Fesih kararının alınabilmesi için gerekli olan karar çoğunluğu toplantıya katılan ve oy kullanma hakkı bulunan üyelerin oylarının 2/3 3'ü'dür. Genel kurulda fesih kararı oylaması açık olarak yapılır.
26.1. Tasfiye İşlemleri: Genel kurulca fesih kararı verildiğinde, derneğin para, mal ve haklarının tasfiyesi son yönetim kurulu üyelerinden oluşan tasfiye kurulunca yapılır. Bu işlemlere, feshe ilişkin genel kurul kararının alındığı veya kendiliğinden sona erme halinin kesinleştiği tarihten itibaren başlanır. Tasfiye süresi içinde bütün işlemlerde dernek adında "Tasfiye Halinde Akademik Renkler Derneği" ibaresi kullanılır. Tasfiye kurulu, mevzuata uygun olarak derneğin para, mal ve haklarının tasfiyesi işlemlerini baştan sonuna kadar tamamlamakla görevli ve yetkilidir. Bu kurul, önce derneğin hesaplarını inceler. İnceleme esnasında derneğe ait defterler, alındı belgeleri, harcama belgeleri, tapu ve banka kayıtları ile diğer belgelerinin tespiti yapılarak varlık ve yükümlülükleri bir tutanağa bağlanır. Tasfiye işlemeleri sırasında derneğin alacaklılarına çağrıda bulunulur ve varsa malları paraya çevrilerek alacaklılara ödenir. Derneğin alacaklı olması durumunda alacaklar tahsil edilir. Alacakların tahsil edilmesi ve borçların ödenmesinden sonra kalan tüm para, mal ve hakları, genel kurulda belirlenen yere devredilir. Genel kurulda, devredilecek yer belirlenmemişse derneğin bulunduğu ildeki amacına en yakın ve fesih edildiği tarihte en fazla üyeye sahip derneğe devredilir. Tasfiyeye ilişkin tüm işlemler tasfiye tutanağında gösterilir ve tasfiye işlemleri, mülki idare amirliklerince haklı bir nedene dayanılarak verilen ek süreler hariç üç ay içinde tamamlanır. Derneğin para, mal ve haklarının tasfiye ve intikal işlemlerinin tamamlanmasını müteakip tasfiye kurulu tarafından durumun yedi gün içinde bir yazı ile dernek merkezinin bulunduğu yerin mülki idare amirliğine bildirilmesi ve bu yazıya tasfiye tutanağının da eklenmesi zorunludur. Derneğin defter ve belgelerini tasfiye kurulu sıfatıyla son yönetim kurulu üyeleri saklamakla görevlidir. Bu görev, bir yönetim kurulu üyesine de verilebilir. Bu defter ve belgelerin saklanma süresi beş yıldır.

**Hüküm Eksikliği**
**Madde 27-** Bu tüzükte belirtilmemiş hususlarda Dernekler Kanunu, Türk Medeni Kanunu ve bu Kanunlara atfen çıkartılmış olan Dernekler Yönetmeliği ve ilgili diğer mevzuatın dernekler hakkındaki hükümleri uygulanır.

**Geçici Madde 1-** 14 Haziran 2025 tarihinde gerçekleştirilen 2.Olağanüstü Genel Kurul Toplantısı sonunda dernek organları oluşturulmuştur. Oluşturulan Yönetim Kurulu aşağıdaki belirtilmiştir.

**Yönetim Kurulu Üyeleri:**
- Fatih BARIŞ (Başkan)
- Sevde KOZALIOĞLU (Başkan Yardımcısı)
- İlayda OLĞUN (Sayman)
- Betül MUTLU (Sekreter)

Bu tüzük 27 (Yirmiyedi) madde ve 1 (Bir) geçici maddeden ibarettir.
        """
        
        st.markdown(f'<div style="background:#fff; padding:20px; border-radius:16px; box-shadow:0 4px 12px rgba(0,0,0,0.03); border:1px solid #f1f5f9; font-size:13px; color:#475569; line-height:1.6; max-height: 65vh; overflow-y: auto;">{tuzuk_metni}</div>', unsafe_allow_html=True)

    def render_profile_tab():
        st.markdown("<br>", unsafe_allow_html=True)
        avatar_html = f'<img src="{cu.avatar}" style="width:100px; height:100px; border-radius:50%; object-fit:cover; margin-bottom:10px;">' if cu.avatar else '<div style="font-size: 60px; margin-bottom: 10px;">👤</div>'
        st.markdown(f'<div style="text-align:center; padding: 2rem; background:#fff; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #f8fafc;">{avatar_html}<h2 style="color:#1A2744; margin:0; font-weight:900;">{cu.username}</h2><p style="color:#64748b; font-weight:600; margin-top:5px; font-size:14px;">{cu.role} • {cu.alan or ""}</p></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📷 Profil Fotoğrafını Değiştir"):
            uploaded_file = st.file_uploader("Bir fotoğraf seçin", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                if st.button("Fotoğrafı Kaydet", use_container_width=True):
                    base64_img = base64.b64encode(uploaded_file.read()).decode("utf-8")
                    mime_type = "image/png" if uploaded_file.name.lower().endswith(".png") else "image/jpeg"
                    cu.avatar = f"data:{mime_type};base64,{base64_img}"
                    db.commit()
                    st.success("Profil fotoğrafı başarıyla güncellendi!")
                    time.sleep(1)
                    st.rerun()

        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
        if st.button("Sistemden Çıkış Yap", use_container_width=True):
            controller.remove('arder_user'); st.session_state.update({"logged_in": False, "username": "", "role": ""}); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    def render_pano_tab(is_admin=False):
        if is_admin:
            with st.expander("➕ Yeni Duyuru / Kurum Ekle"):
                tab_d, tab_k = st.tabs(["📢 Duyuru", "🤝 Kurum Ekle"])
                with tab_d:
                    with st.form("new_ann"):
                        a_title = st.text_input("Duyuru Başlığı")
                        a_content = st.text_area("İçerik")
                        if st.form_submit_button("Duyuruyu Yayınla ve Bildir", use_container_width=True):
                            today_str = datetime.now().strftime("%d.%m.%Y")
                            db.add(Announcement(title=a_title, content=a_content, date=today_str, author=cu.username))
                            db.commit()
                            
                            all_users = db.query(User).filter(User.email != "").all()
                            for usr in all_users:
                                trigger_announcement_email(usr.email, a_title, a_content, cu.username, today_str)
                                
                            st.success("Yayınlandı ve herkese mail iletildi!"); time.sleep(1.5); st.rerun()
                with tab_k:
                    with st.form("new_part"):
                        p_name = st.text_input("Kurum Adı (Örn: Pamuk Kafe)")
                        p_disc = st.text_input("İndirim/Fırsat (Örn: %15 İndirim)")
                        p_det = st.text_area("Detaylar")
                        p_icon = st.text_input("İkon (Emoji olarak, Örn: ☕)", value="🏪")
                        if st.form_submit_button("Kurumu Ekle ve Bildir", use_container_width=True):
                            db.add(Partner(name=p_name, discount=p_disc, details=p_det, icon=p_icon))
                            db.commit()
                            
                            all_users = db.query(User).filter(User.email != "").all()
                            for usr in all_users:
                                trigger_partner_email(usr.email, p_name, p_disc, p_det)
                                
                            st.success("Eklendi ve herkese mail iletildi!"); time.sleep(1.5); st.rerun()

            st.markdown("### 👑 Yönetici Paneli")
            with st.expander("➕ Yeni Etkinlik Duyurusu Oluştur"):
                with st.form("new_event_form"):
                    e_title = st.text_input("Etkinlik Adı")
                    e_desc = st.text_area("Etkinlik Açıklaması & Konumu")
                    e_date = st.date_input("Etkinlik Tarihi", min_value=date.today(), format="DD.MM.YYYY")
                    if st.form_submit_button("🚀 Yayınla ve Herkese Mail At", use_container_width=True):
                        if e_title.strip():
                            formatted_e_date = e_date.strftime("%d.%m.%Y")
                            db.add(Event(title=e_title, description=e_desc, event_date=formatted_e_date, created_by=cu.username))
                            db.commit()
                            all_users = db.query(User).filter(User.email != "").all()
                            for usr in all_users:
                                trigger_event_email(usr.email, e_title, e_desc, formatted_e_date)
                            st.success("Etkinlik yayınlandı ve tüm üyelere mail gönderiliyor!"); time.sleep(1.5); st.rerun()
                        else: st.warning("Başlık boş olamaz.")
            
            with st.expander("📋 Etkinlik Raporları (Kimler Geliyor?)"):
                events = db.query(Event).order_by(Event.id.desc()).all()
                if not events: st.info("Sistemde kayıtlı etkinlik yok.")
                for e in events:
                    rsvps = db.query(EventRSVP).filter(EventRSVP.event_id == e.id).all()
                    katilanlar = [r for r in rsvps if r.status == "Katılacağım"]
                    katilmayanlar = [r for r in rsvps if r.status == "Katılmayacağım"]
                    st.markdown(f"**📅 {e.title} ({e.event_date})**")
                    st.markdown(f"✅ **Katılacaklar ({len(katilanlar)} kişi):**")
                    for k in katilanlar: st.markdown(f"- {k.username} *(Not: {k.reason or '-'})*")
                    st.markdown(f"❌ **Katılmayacaklar ({len(katilmayanlar)} kişi):**")
                    for k in katilmayanlar: st.markdown(f"- {k.username} *(Neden: {k.reason or '-'})*")
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button("Etkinliği Sil", key=f"del_e_{e.id}"):
                        db.query(EventRSVP).filter(EventRSVP.event_id == e.id).delete()
                        db.delete(e); db.commit(); st.rerun()
                    st.markdown("</div><hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">📅 Yaklaşan Etkinlikler</div>', unsafe_allow_html=True)
        events = db.query(Event).order_by(Event.id.desc()).all()
        if not events:
            st.markdown('<div style="text-align:center;padding:3rem;"><div style="font-size:40px; margin-bottom:10px;">🏝️</div><b style="color:#1A2744;">Yaklaşan etkinlik görünmüyor.</b></div>', unsafe_allow_html=True)
        else:
            for e in events:
                my_rsvp = db.query(EventRSVP).filter(EventRSVP.event_id == e.id, EventRSVP.username == cu.username).first()
                d_day, d_month = format_event_date(e.event_date)
                
                st.markdown(f"""
                <div class="event-v2">
                    <div class="e-date"><div class="e-day">{d_day}</div><div class="e-month">{d_month}</div></div>
                    <div class="e-info"><div class="e-title">{e.title}</div><div class="e-desc">{e.description}</div></div>
                </div>
                """, unsafe_allow_html=True)
                
                if my_rsvp:
                    st.info(f"**Durumunuz:** {my_rsvp.status} \n\n**İletilen Not:** {my_rsvp.reason or '-'}")
                    st.markdown("<div class='btn-secondary'>", unsafe_allow_html=True)
                    if st.button("Fikrimi Değiştir (Yanıtı Sil)", key=f"rev_{e.id}"):
                        db.delete(my_rsvp); db.commit(); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    with st.form(f"rsvp_form_{e.id}"):
                        status = st.radio("Bu etkinliğe katılabilecek misiniz?", ["Katılacağım", "Katılmayacağım"], horizontal=True)
                        reason = st.text_input("Nedeniniz / Notunuz (İsteğe bağlı)")
                        if st.form_submit_button("Yanıtımı Gönder", use_container_width=True):
                            db.add(EventRSVP(event_id=e.id, username=cu.username, status=status, reason=reason))
                            db.commit(); st.success("Yanıtınız kaydedildi!"); time.sleep(1); st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # 9. SAYFA YÖNLENDİRME SİSTEMİ (STATE MANAGEMENT)
    # ══════════════════════════════════════════════════════════
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Menü"

    def go_to_page(page_name):
        st.session_state.current_page = page_name

    # --- ANA MENÜ (GRID BUTONLARI) ---
    if st.session_state.current_page == "Menü":
        avatar_html = f'<img src="{cu.avatar}" style="width:90px; height:90px; border-radius:50%; object-fit:cover; margin: 0 auto 10px auto; display:block; box-shadow: 0 4px 14px rgba(0,0,0,0.1);">' if cu.avatar else '<div style="font-size: 60px; text-align:center; margin-bottom: 10px;">👤</div>'
        st.markdown(f'<div style="text-align:center; padding: 1rem 0 2rem 0;">{avatar_html}<h3 style="color:#1A2744; margin:0; font-weight:900;">{cu.username}</h3><p style="color:#2DB5A0; font-weight:700; margin-top:3px; font-size:13px;">{cu.role} • {cu.alan or ""}</p></div>', unsafe_allow_html=True)

        st.markdown("<div class='menu-grid-btn'>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🏠\nAna Ekran", use_container_width=True): go_to_page("Ana Ekran"); st.rerun()
        with c2:
            if st.button("👔\nYönetim", use_container_width=True): go_to_page("Yönetim"); st.rerun()
        with c3:
            if st.button("📝\nGörevlerim", use_container_width=True): go_to_page("Görevlerim"); st.rerun()
            
        c4, c5, c6 = st.columns(3)
        with c4:
            if st.button("📅\nPano", use_container_width=True): go_to_page("Pano"); st.rerun()
        with c5:
            if st.button("📜\nTüzük", use_container_width=True): go_to_page("Tüzük"); st.rerun()
        with c6:
            if st.button("👤\nProfilim", use_container_width=True): go_to_page("Profilim"); st.rerun()

        if cu.role in ["Moderatör", "Birim Başkanı"]:
            c7, c8, c9 = st.columns(3)
            with c7:
                if st.button("🎯\nGörev Ata", use_container_width=True): go_to_page("Görev Ata"); st.rerun()
            with c8:
                if st.button("⚙️\nEkip Takip", use_container_width=True): go_to_page("Ekip Takip"); st.rerun()
            with c9:
                if cu.role == "Moderatör":
                    if st.button("👥\nÜyeler", use_container_width=True): go_to_page("Üyeler"); st.rerun()
                else:
                    st.empty() 
        st.markdown("</div>", unsafe_allow_html=True)

    # --- İÇ SAYFALAR ---
    else:
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        if st.button("⬅️ Menüye Dön"):
            go_to_page("Menü"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

        if st.session_state.current_page == "Ana Ekran": 
            render_home_tab(db)
            
        elif st.session_state.current_page == "Yönetim": 
            render_board_tab(db)
            
        elif st.session_state.current_page == "Tüzük": 
            render_tuzuk_tab()
            
        elif st.session_state.current_page == "Pano": 
            render_pano_tab(is_admin=(cu.role in ["Moderatör", "Birim Başkanı"]))
            
        elif st.session_state.current_page == "Profilim": 
            render_profile_tab()
            
        elif st.session_state.current_page == "Görevlerim":
            st.markdown('<div class="section-title">📋 Bekleyen Görevleriniz</div>', unsafe_allow_html=True)
            tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all()
            if not tasks: st.markdown('<div style="text-align:center;padding:2rem;"><div style="font-size:40px; margin-bottom:10px;">✨</div><b style="color:#1A2744;">Bekleyen göreviniz bulunmuyor.</b></div>', unsafe_allow_html=True)
            for t in tasks:
                due_label = f"| Son: {t.due_date}" if t.due_date else ""
                st.markdown(f'<div class="task-card"><div class="task-title">{t.title}</div><div class="task-meta">{t.description}</div><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;"><span class="badge {BADGE.get(t.priority)}">{t.priority}</span> <span style="font-size:0.75rem; font-weight:800; color:#2DB5A0;">Maks Puan: {t.points} <span style="color:#94a3b8; font-weight:500;">{due_label}</span></span></div></div>', unsafe_allow_html=True)
                with st.expander("📝 Görevi Tamamla ve Raporla"):
                    with st.form(f"rep_form_{t.id}"):
                        step_results = []
                        if getattr(t, 'steps', ""):
                            st.markdown("**📌 Görev Adımlarını İşaretleyin:**")
                            for i, step in enumerate(json.loads(t.steps)):
                                res = st.radio(step, ["Yaptım", "Yapamadım"], key=f"rad_{cu.username}_{t.id}_{i}", horizontal=True)
                                step_results.append((step, res))
                        rep_txt = st.text_area("Görev Raporu", placeholder="Neler yaptınız? Varsa yapamadığınız veya eksik kalan kısımlar nelerdir?")
                        if st.form_submit_button("Raporu Gönder ve Tamamla", use_container_width=True):
                            if len(rep_txt.strip()) < 3: st.error("Lütfen kısaca da olsa bir rapor yazın.")
                            else:
                                total_s = len(step_results)
                                done_s = sum(1 for s, r in step_results if r == "Yaptım")
                                pct = (done_s / total_s) if total_s > 0 else 1.0
                                earned = int(t.points * pct)
                                final_report = f"📊 **Görev Başarısı:** %{int(pct*100)} ({earned}/{t.points} Puan)\n\n**📌 ADIMLAR:**\n"
                                for s, r in step_results: final_report += f"{'✅' if r == 'Yaptım' else '❌'} {s}\n"
                                final_report += f"\n**📝 RAPOR:**\n{rep_txt.strip()}"
                                t.status = "Tamamlandı"
                                t.report = final_report
                                t.earned_points = earned
                                cu.points = (cu.points or 0) + earned
                                cu.lifetime_points = (cu.lifetime_points or 0) + earned
                                cu.total_completed = (cu.total_completed or 0) + 1
                                db.commit()
                                trigger_report_email(t.title, cu.username, t.assigned_by, final_report, earned, t.points)
                                st.success("Görev ve rapor başarıyla iletildi!"); time.sleep(1.5); st.rerun()
                if t.due_date:
                    ics = make_ics(t.title, t.description or "", t.due_date)
                    st.download_button("Takvime Ekle", data=ics, file_name=f"arder_{t.id}.ics", mime="text/calendar", key=f"ics_{t.id}", use_container_width=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">✔️ Tamamlanan Görevler</div>', unsafe_allow_html=True)
            done_tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Tamamlandı").order_by(Task.id.desc()).limit(20).all()
            if not done_tasks: st.info("Henüz tamamlanmış görev yok.")
            for t in done_tasks: 
                st.markdown(f'<div class="task-card done" style="margin-bottom:0.5rem;"><div class="task-title">✓ {t.title}</div><div class="task-meta" style="color:#2DB5A0; font-weight:700;">Kazanılan: +{t.earned_points or t.points} / {t.points} pts</div></div>', unsafe_allow_html=True)
                if getattr(t, 'report', ""): st.info(t.report)

        elif st.session_state.current_page == "Görev Ata" and cu.role in ["Moderatör", "Birim Başkanı"]:
            st.markdown('<div class="section-title">🎯 Yeni Görev Ata</div>', unsafe_allow_html=True)
            if cu.role == "Moderatör":
                target_user_pool = db.query(User).filter(User.username != cu.username).all()
            else:
                target_user_pool = db.query(User).filter(User.role == "Üye").all()

            if not target_user_pool: st.info("Sistemde atanacak kişi yok.")
            else:
                assign_mode = st.radio("Atama Türü Seçin:", ["Bireysel (Çoklu Seçim)", "Tüm Birime Ata"], horizontal=True)
                st.markdown("<hr style='margin:0.5rem 0;'>", unsafe_allow_html=True)
                with st.form("assign_task_form"):
                    target_usernames = []
                    if assign_mode == "Bireysel (Çoklu Seçim)":
                        selected_items = st.multiselect("Kime Görev Atanacak:", [f"{u.username} ({u.alan})" for u in target_user_pool])
                    else:
                        alanlar_list = sorted(list(set([u.alan for u in target_user_pool if u.alan])))
                        selected_alan = st.selectbox("Hangi Birime Görev Atanacak:", alanlar_list)
                    tt = st.text_input("Başlık")
                    td = st.text_area("Detaylar (Görevin Genel Amacı)", height=60)
                    t_steps = st.text_area("Görev Adımları (İsteğe bağlı. Her satıra 1 adım yazın)", height=100)
                    c1, c2 = st.columns(2)
                    with c1: tp = st.selectbox("Öncelik", ["Acil","Yüksek","Orta","Düşük"])
                    with c2: tpts = st.number_input("Maks. Puan", min_value=1, value=10)
                    t_due = st.date_input("Son Tarih", value=date.today() + timedelta(days=7), format="DD.MM.YYYY")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Görevi Gönder", use_container_width=True):
                        if not tt.strip(): st.warning("Başlık boş olamaz.")
                        else:
                            if assign_mode == "Bireysel (Çoklu Seçim)": target_usernames = [s.rsplit(" (", 1)[0] for s in selected_items]
                            else:
                                target_users_query = db.query(User).filter(User.alan == selected_alan).all()
                                target_usernames = [u.username for u in target_users_query]
                            if not target_usernames: st.error("Lütfen atanacak kişi veya birimi seçin!")
                            else:
                                formatted_t_due = t_due.strftime("%d.%m.%Y")
                                steps_str = json.dumps([s.strip() for s in t_steps.split('\n') if s.strip()]) if t_steps.strip() else ""
                                for uname in target_usernames:
                                    target_u = db.query(User).filter(User.username==uname).first()
                                    if target_u: target_u.total_assigned = (target_u.total_assigned or 0) + 1 
                                    db.add(Task(assigned_to=uname, assigned_by=cu.username, title=tt, description=td, steps=steps_str, priority=tp, points=tpts, status="Bekliyor", due_date=formatted_t_due))
                                    if target_u and target_u.email: trigger_background_email(target_u.email, target_u.username, tt, td, tp, tpts, formatted_t_due)
                                db.commit(); st.success(f"Görev başarıyla {len(target_usernames)} kişiye atandı ve mailleri gönderildi!")

        elif st.session_state.current_page == "Ekip Takip" and cu.role in ["Moderatör", "Birim Başkanı"]:
            if cu.role == "Moderatör":
                st.markdown("### 📊 Tüm Verileri Dışa Aktar")
                all_tasks_db = db.query(Task).order_by(Task.id.desc()).all()
                if all_tasks_db:
                    data = []
                    today_d = datetime.now().date()
                    for tk in all_tasks_db:
                        u_info = db.query(User).filter(User.username == tk.assigned_to).first()
                        gecikme = "Zamanında"
                        if tk.status == "Bekliyor" and tk.due_date:
                            try:
                                if datetime.strptime(tk.due_date, "%d.%m.%Y").date() < today_d: gecikme = "Gecikti"
                            except: pass
                        data.append({"Görev ID": tk.id, "Görev Başlığı": tk.title, "Atanan Kişi": tk.assigned_to, "Kişi Birimi": u_info.alan if u_info else "-", "Görev Veren": tk.assigned_by, "Durum": tk.status, "Öncelik": tk.priority, "Maks Puan": tk.points, "Kazanılan Puan": tk.earned_points or 0, "Son Tarih": tk.due_date, "Gecikme Durumu": gecikme})
                    df = pd.DataFrame(data)
                    csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
                    st.download_button(label="📥 Tüm Görev Raporlarını İndir (.csv Excel)", data=csv, file_name=f"arder_gorev_raporu_{date.today()}.csv", mime="text/csv", use_container_width=True)
                
                st.divider(); st.markdown("### 📋 Geçmiş Görev Kayıtları")
                for t in all_tasks_db:
                    status_color = "color:#2DB5A0;" if t.status == "Tamamlandı" else "color:#ef4444;" if t.status == "İptal Edildi" else "color:#eab308;"
                    with st.expander(f"{t.title} -> {t.assigned_to}"):
                        st.markdown(f"**Veren:** {t.assigned_by} | <span style='{status_color}'>**Durum:** {t.status}</span><br>**Açıklama:** {t.description}", unsafe_allow_html=True)
                        if getattr(t, 'report', ""): st.info(t.report)
                        if t.status != "İptal Edildi":
                            st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                            if st.button("İptal Et", key=f"c_{t.id}"):
                                target_u = db.query(User).filter(User.username == t.assigned_to).first()
                                if target_u: target_u.total_assigned = max(0, (target_u.total_assigned or 0) - 1)
                                if t.status == "Tamamlandı":
                                    if target_u:
                                        target_u.points = max(0, target_u.points - (t.earned_points or t.points))
                                        target_u.lifetime_points = max(0, (target_u.lifetime_points or 0) - (t.earned_points or t.points))
                                        target_u.total_completed = max(0, (target_u.total_completed or 0) - 1)
                                t.status = "İptal Edildi"
                                db.commit(); st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("### Ekibinizin Karneleri")
                for u in db.query(User).filter(User.role == "Üye").all():
                    with st.expander(f"👤 {u.username} ({u.alan})"):
                        completed = u.total_completed or 0
                        assigned = max(u.total_assigned or 0, completed)
                        overdue = 0
                        today_d = datetime.now().date()
                        usr_pending = db.query(Task).filter(Task.assigned_to==u.username, Task.status=="Bekliyor").all()
                        for tsk in usr_pending:
                            if tsk.due_date:
                                try:
                                    if datetime.strptime(tsk.due_date, "%d.%m.%Y").date() < today_d: overdue += 1
                                except: pass
                        st.markdown(f"**Verilen İş:** {assigned} | **Yapılan:** {completed} | **Geciken:** <span style='color:#ef4444;'>{overdue}</span> | **Tüm Puan:** ⭐ {u.lifetime_points or 0}", unsafe_allow_html=True)
                st.divider(); st.markdown("### Verdiğiniz Görevlerin Durumu")
                for t in db.query(Task).filter(Task.assigned_by==cu.username).order_by(Task.id.desc()).limit(20).all():
                    with st.expander(f"{t.title} -> {t.assigned_to} ({t.status})"):
                        st.markdown(f"**Açıklama:** {t.description}"); 
                        if getattr(t, 'report', ""): st.info(t.report)
            
        elif st.session_state.current_page == "Üyeler" and cu.role == "Moderatör":
            st.markdown('<div class="section-title">👥 Tüm Üyeler ve İstatistikleri</div>', unsafe_allow_html=True)
            for u in db.query(User).filter(User.username != cu.username).all():
                with st.expander(f"👤 {u.username} ({u.alan})"):
                    assigned, completed = u.total_assigned or 0, u.total_completed or 0
                    overdue = 0
                    today_d = datetime.now().date()
                    usr_pending = db.query(Task).filter(Task.assigned_to==u.username, Task.status=="Bekliyor").all()
                    for tsk in usr_pending:
                        if tsk.due_date:
                            try:
                                if datetime.strptime(tsk.due_date, "%d.%m.%Y").date() < today_d: overdue += 1
                            except: pass
                    st.markdown(f"<div style='display:flex; justify-content:space-between; text-align:center; background:#f8fafc; padding:15px; border-radius:12px; margin-bottom:15px;'><div><div style='font-size:11px; color:#64748b; font-weight:700;'>Verilen</div><div style='font-weight:900; font-size:18px; color:#1A2744;'>{assigned}</div></div><div><div style='font-size:11px; color:#64748b; font-weight:700;'>Yapılan</div><div style='font-weight:900; font-size:18px; color:#2DB5A0;'>{completed}</div></div><div><div style='font-size:11px; color:#ef4444; font-weight:700;'>Geciken</div><div style='font-weight:900; font-size:18px; color:#ef4444;'>{overdue}</div></div><div><div style='font-size:11px; color:#64748b; font-weight:700;'>Tüm Puan</div><div style='font-weight:900; font-size:18px; color:#f59e0b;'>⭐ {u.lifetime_points or 0}</div></div></div>", unsafe_allow_html=True)
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button("Kullanıcıyı Sil", key=f"d_{u.id}"): db.query(Task).filter(Task.assigned_to == u.username).delete(); db.delete(u); db.commit(); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
            if st.button("Sistemi Sıfırla (Karneler Silinmez)", use_container_width=True): db.query(Task).delete(); db.query(User).update({User.points: 0}); db.commit(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

db.close()
