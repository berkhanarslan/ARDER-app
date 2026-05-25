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
# 2. MEGA-CACHE: STATİK ASSETLER VE MODERN CSS
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
    
    html = f"""<link rel="manifest" href="data:application/manifest+json;base64,{base64.b64encode(json.dumps(_manifest).encode()).decode()}"><meta name="theme-color" content="#ffffff"><style>html, body {{ overscroll-behavior-y: none !important; overscroll-behavior-x: none !important; }} header[data-testid="stHeader"] {{ background: transparent !important; }}.viewerBadge_container, .stAppViewFooter, footer {{ display: none !important; }}.main .block-container {{ max-width:480px; margin:auto; padding:1rem; padding-top:2rem; }}[data-testid="stAppViewContainer"] {{ background-color:#f5f8f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overscroll-behavior-y: none !important; }}div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {{ border-radius: 20px !important; border: 1px solid #e2e8f0 !important; background-color: #ffffff !important; padding: 4px 12px !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important; }}div[data-baseweb="select"] > div {{ border-radius: 25px !important; border: 1px solid #e2e8f0 !important; }}div.stButton>button {{ border-radius: 30px !important; font-weight: 700 !important; padding: 0.6rem 1rem !important; border: none !important; transition: all 0.3s ease; }}div.stButton>button:first-child {{ background: linear-gradient(135deg, #1976D2, #2DB5A0) !important; color: #fff !important; box-shadow: 0 4px 14px rgba(45, 181, 160, 0.3) !important; }}div.stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(45, 181, 160, 0.4) !important; }}.btn-danger>button {{ background: linear-gradient(135deg, #ef4444, #dc2626) !important; color: #fff !important; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3) !important; }}.btn-secondary>button {{ background: linear-gradient(135deg, #94a3b8, #64748b) !important; color: #fff !important; box-shadow: 0 4px 14px rgba(100, 116, 139, 0.3) !important; }}.app-header {{ background: #ffffff; border-radius: 24px; padding: 1rem 1.2rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.8rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}.app-header .brand-name {{ font-size: 1.15rem; font-weight: 900; color: #1A2744; line-height: 1.1; }}.app-header .brand-sub {{ font-size: 0.7rem; color: #2DB5A0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}.login-header {{ text-align: center; margin-bottom: 2rem; margin-top: 1rem; }}.stat-wrap {{ display:flex; gap:12px; margin:0.5rem 0 1.5rem 0; }}.stat-card {{ flex:1; background:#fff; border-radius:24px; box-shadow:0 8px 24px rgba(0,0,0,0.04); padding:1.2rem 0.8rem; text-align:center; display: flex; flex-direction: column; justify-content: center; }}.stat-card .label {{ font-size:0.7rem; color:#64748b; font-weight:600; margin-bottom:8px; }}.stat-card .value {{ font-size:1.8rem; font-weight:900; color:#1A2744; line-height:1; }}.stat-card .value.green {{ color: #2DB5A0; }}.task-card {{ background: #fff; border-radius: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.03); padding: 1.2rem; margin-bottom: 1rem; border-left: 6px solid #2DB5A0; position: relative; }}.task-card.done {{ border-left-color: #cbd5e1; opacity: 0.7; }}.task-title {{ font-weight: 800; color: #1A2744; font-size: 1rem; margin-bottom: 0.3rem; }}.task-meta {{ font-size: 0.8rem; color: #64748b; margin-bottom: 0.8rem; line-height: 1.4; }}.badge {{ display:inline-block; padding:0.25rem 0.7rem; border-radius:20px; font-size:0.7rem; font-weight:700; }}.badge-acil {{ background:#fee2e2; color:#b91c1c; }}.badge-yuksek {{ background:#fef3c7; color:#b45309; }}.badge-orta {{ background:#ccfbf1; color:#0f766e; }}.badge-dusuk {{ background:#e0f2fe; color:#0369a1; }}[data-testid="stTabs"] button {{ padding-bottom: 10px !important; }}[data-testid="stTabs"] button[aria-selected="true"] {{ color:#2DB5A0 !important; border-bottom: 3px solid #2DB5A0 !important; }}</style>"""
    return html, logo_html, login_logo_html

STATIC_HTML, LOGO_HTML, LOGIN_LOGO_HTML = get_static_assets()
st.markdown(STATIC_HTML, unsafe_allow_html=True)

# YENİLEME ENGELLEYİCİ JS KODU (Mobil için kesin çözüm)
components.html("""
<script>
if ('Notification' in window && Notification.permission === 'default') { Notification.requestPermission(); }

document.addEventListener('touchstart', function(e) {
    if (window.scrollY === 0 && e.touches[0].clientY > 0) {
        document.body.style.overscrollBehaviorY = 'none';
    }
}, { passive: true });

document.addEventListener('touchmove', function(e) {
    if (window.scrollY === 0 && e.touches[0].clientY > 0) {
        e.preventDefault();
    }
}, { passive: false });
</script>
""", height=0)

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
    status = Column(String, default="Bekliyor") 
    due_date = Column(String, default="")

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

@st.cache_resource
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            for stmt in [
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 10;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS alan VARCHAR DEFAULT 'Belirtilmedi';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR DEFAULT '';",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date VARCHAR DEFAULT '';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS lifetime_points INTEGER DEFAULT 0;",
                "UPDATE users SET lifetime_points = 0 WHERE lifetime_points IS NULL;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_assigned INTEGER DEFAULT 0;",
                "UPDATE users SET total_assigned = 0 WHERE total_assigned IS NULL;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_completed INTEGER DEFAULT 0;",
                "UPDATE users SET total_completed = 0 WHERE total_completed IS NULL;"
            ]:
                try: conn.execute(text(stmt)); conn.commit()
                except: pass
    except: pass 

init_db()

# ══════════════════════════════════════════════════════════
# 4. YARDIMCI FONKSİYONLAR VE MAİL SİSTEMİ
# ══════════════════════════════════════════════════════════
def send_email_notification(to_email, user_name, task_title, task_desc, priority, points, due_date):
    try:
        s_email, s_pass = st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass or not to_email: return False 
        
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = f"ARDER Sistem <{s_email}>", to_email, f"📌 Yeni Görev: {task_title}"
        
        body = f"""Merhaba {user_name},

Akademik Renkler Derneği sisteminde tarafına yeni bir görev atandı. İlgili detayları aşağıda bulabilirsin:

Görev Bilgileri:
📌 Başlık: {task_title}
⚡ Öncelik: {priority}
⭐ Puan: {points}
📅 Son Tarih: {due_date}

Açıklama:
{task_desc}

Lütfen uygulamaya giriş yapıp görevi detaylıca incele ve tamamlandığında sistem üzerinden işaretlemeyi unutma. Herhangi bir sorun olursa bize her zaman ulaşabilirsin.

Kolay gelsin!

Sevgiler,
Akademik Renkler Derneği Yönetimi"""

        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls(); server.login(s_email, s_pass); server.send_message(msg); server.quit()
    except Exception as e: 
        print(f"Mail Hatası: {e}")

def send_event_email_notification(to_email, event_title, event_desc, event_date):
    try:
        s_email, s_pass = st.secrets.get("EMAIL_USER", ""), st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass or not to_email: return False 
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = f"ARDER Sistem <{s_email}>", to_email, f"📌 Yeni Etkinlik Daveti: {event_title}"
        
        body = f"""Merhaba,

Derneğimiz kapsamında "{event_title}" adlı yeni bir etkinlik planlandı!

📅 Tarih: {event_date}
📍 Detaylar: {event_desc}

Sistem üzerinden (ARDER Uygulaması) 'Etkinlik' sekmesine girip katılım durumunu (LCV) bildirmeni rica ederiz. Seni aramızda görmekten mutluluk duyarız.

Görüşmek üzere,
Akademik Renkler Derneği Yönetimi"""
        
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls(); server.login(s_email, s_pass); server.send_message(msg); server.quit()
    except: pass

def trigger_background_email(*args): threading.Thread(target=send_email_notification, args=args).start()
def trigger_event_email(*args): threading.Thread(target=send_event_email_notification, args=args).start()

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
    <div style="color:#1A2744;font-size:20px;font-weight:900;margin-bottom:4px;">🏆 Liderlik Tablosu</div>
    <div style="color:#94a3b8;font-size:12px;margin-bottom:24px;font-weight:600;">Her ayın başında sıfırlanır</div>
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
            html += f"<div class='li'><div class='rb {rc}'>{r}</div><div class='av' style='width:40px;height:40px;font-size:16px;margin-bottom:0;margin-right:12px;border-radius:12px;'>{u['username'][0].upper()}</div><div style='overflow:hidden;'><div class='ln'>{u['username']}</div><div class='lr'>{u['role']} | {u['alan']}</div></div><div class='lp'>{u['points']}<span style='font-size:10px;color:#cbd5e1;'> pts</span></div></div>"
    html += "</div></body></html>"
    return html

def render_leaderboard(db):
    users = db.query(User).order_by(User.points.desc()).all()
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
        lu, lp = st.text_input("Kullanıcı Adı"), st.text_input("Şifre", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Giriş Yap", use_container_width=True):
            user = db.query(User).filter(User.username==lu.strip(), User.password==lp.strip()).first()
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
            if len(ru.strip())<3: st.warning("İsim çok kısa.")
            elif db.query(User).filter(User.username==ru.strip()).first(): st.warning("Bu isim kayıtlı.")
            else:
                db.add(User(username=ru.strip(), password=rp.strip(), email=rmail.strip(), role=role, alan=alan, points=0, lifetime_points=0, total_assigned=0, total_completed=0))
                db.commit(); st.success("Başarıyla kayıt olundu! Giriş sekmesinden devam edebilirsiniz.")

# ══════════════════════════════════════════════════════════
# 8. ANA PANELLER
# ══════════════════════════════════════════════════════════
else:
    cu = db.query(User).filter(User.username==st.session_state.username).first()
    if not cu: st.session_state.logged_in = False; st.rerun()

    show_header()
    BADGE = {"Acil":"badge-acil","Yüksek":"badge-yuksek","Orta":"badge-orta","Düşük":"badge-dusuk"}

    def render_stats(u_name):
        pending = db.query(Task).filter(Task.assigned_to==u_name, Task.status=="Bekliyor").count()
        done = db.query(Task).filter(Task.assigned_to==u_name, Task.status=="Tamamlandı").count()
        st.markdown(f"""
        <div class="stat-wrap">
          <div class="stat-card"><div class="label">Mevcut Puan</div><div class="value green">{cu.points}</div></div>
          <div class="stat-card"><div class="label">Bekleyen İş</div><div class="value">{pending}</div></div>
          <div class="stat-card"><div class="label">Tüm Zamanlar</div><div class="value" style="color:#f59e0b;">⭐ {cu.lifetime_points or 0}</div></div>
        </div>
        """, unsafe_allow_html=True)

    def render_profile_tab():
        st.markdown("<br>", unsafe_allow_html=True)
        completed = cu.total_completed or 0
        assigned = max(cu.total_assigned or 0, completed)
        
        overdue_count = 0
        today_d = datetime.now().date()
        my_pending = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all()
        for tsk in my_pending:
            if tsk.due_date:
                try:
                    if datetime.strptime(tsk.due_date, "%d.%m.%Y").date() < today_d:
                        overdue_count += 1
                except: pass
        
        st.markdown(f'<div style="text-align:center; padding: 2rem; background:#fff; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);"><div style="font-size: 50px; margin-bottom: 10px;">👤</div><h2 style="color:#1A2744; margin:0; font-weight:900;">{cu.username}</h2><p style="color:#64748b; font-weight:600; margin-top:5px;">{cu.role} • {cu.alan or ""}</p><div style="font-size: 24px; font-weight: 800; color: #2DB5A0; margin: 10px 0;">⭐ {cu.lifetime_points or 0} Toplam Puan</div></div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; text-align:center; background:#fff; padding:15px; border-radius:20px; margin-top:15px; box-shadow: 0 4px 16px rgba(0,0,0,0.03);'>
            <div><div style='font-size:11px; color:#64748b; font-weight:700;'>Verilen Görev</div><div style='font-weight:900; font-size:20px; color:#1A2744;'>{assigned}</div></div>
            <div><div style='font-size:11px; color:#64748b; font-weight:700;'>Tamamlanan</div><div style='font-weight:900; font-size:20px; color:#2DB5A0;'>{completed}</div></div>
            <div><div style='font-size:11px; color:#ef4444; font-weight:700;'>Süresi Geçen</div><div style='font-weight:900; font-size:20px; color:#ef4444;'>{overdue_count}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
        if st.button("Sistemden Çıkış Yap", use_container_width=True):
            controller.remove('arder_user'); st.session_state.update({"logged_in": False, "username": "", "role": ""}); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── ORTAK ETKİNLİK SEKMESİ ──
    def render_events_tab(is_admin=False):
        if is_admin:
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

        st.markdown("### 📅 Yaklaşan Etkinlikler (LCV)")
        events = db.query(Event).order_by(Event.id.desc()).all()
        if not events:
            st.markdown('<div style="text-align:center;padding:3rem;"><div style="font-size:40px; margin-bottom:10px;">🏝️</div><b style="color:#1A2744;">Yaklaşan etkinlik görünmüyor.</b></div>', unsafe_allow_html=True)
        else:
            for e in events:
                my_rsvp = db.query(EventRSVP).filter(EventRSVP.event_id == e.id, EventRSVP.username == cu.username).first()
                st.markdown(f'<div class="task-card"><div class="task-title">📅 {e.title}</div><div class="task-meta">{e.description}</div><div style="font-size:0.75rem; font-weight:800; color:#2DB5A0;">Tarih: {e.event_date}</div></div>', unsafe_allow_html=True)
                
                if my_rsvp:
                    st.info(f"**Durumunuz:** {my_rsvp.status} \n\n**İletilen Not:** {my_rsvp.reason or '-'}")
                    st.markdown("<div class='btn-secondary'>", unsafe_allow_html=True)
                    if st.button("Fikrimi Değiştir (Yanıtı Sil)", key=f"rev_{e.id}"):
                        db.delete(my_rsvp); db.commit(); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    with st.form(f"rsvp_form_{e.id}"):
                        status = st.radio("Bu etkinliğe katılabilecek misiniz?", ["Katılacağım", "Katılmayacağım"])
                        reason = st.text_input("Nedeniniz / Notunuz (İsteğe bağlı)")
                        if st.form_submit_button("Yanıtımı Gönder", use_container_width=True):
                            db.add(EventRSVP(event_id=e.id, username=cu.username, status=status, reason=reason))
                            db.commit(); st.success("Yanıtınız kaydedildi!"); time.sleep(1); st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # ── ROL BAZLI SEKME DAĞILIMI ──
    if cu.role == "Moderatör":
        t1, t2, t3, t4, t5, t6 = st.tabs(["Ata", "Yönet", "Üyeler", "Etkinlik", "Liderlik", "Profil"])
        with t1:
            users = db.query(User).filter(User.username != cu.username).all()
            if not users: st.info("Sistemde üye yok.")
            else:
                assigned_to = st.selectbox("Kime:", [f"{u.username} ({u.role})" for u in users]).rsplit(" (", 1)[0]
                tt, td = st.text_input("Başlık"), st.text_area("Detaylar", height=80)
                c1, c2 = st.columns(2)
                with c1: tp = st.selectbox("Öncelik", ["Acil","Yüksek","Orta","Düşük"])
                with c2: tpts = st.number_input("Puan", min_value=1, value=10)
                t_due = st.date_input("Son Tarih", value=date.today() + timedelta(days=7), min_value=date.today(), format="DD.MM.YYYY")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Görevi Gönder", use_container_width=True):
                    if not tt.strip(): st.warning("Başlık boş olamaz.")
                    else:
                        target_u = db.query(User).filter(User.username==assigned_to).first()
                        if target_u: target_u.total_assigned = (target_u.total_assigned or 0) + 1 
                        
                        formatted_t_due = t_due.strftime("%d.%m.%Y")
                        db.add(Task(assigned_to=assigned_to, assigned_by=cu.username, title=tt, description=td, priority=tp, points=tpts, status="Bekliyor", due_date=formatted_t_due))
                        db.commit()
                        if target_u and target_u.email: trigger_background_email(target_u.email, target_u.username, tt, td, tp, tpts, formatted_t_due)
                        st.success("Gönderildi!")
        with t2:
            all_t = db.query(Task).order_by(Task.id.desc()).limit(50).all()
            for t in all_t:
                status_color = "color:#2DB5A0;" if t.status == "Tamamlandı" else "color:#ef4444;" if t.status == "İptal Edildi" else "color:#eab308;"
                with st.expander(f"{t.title} -> {t.assigned_to}"):
                    st.markdown(f"**Puan:** {t.points} | **Veren:** {t.assigned_by} | <span style='{status_color}'>**Durum:** {t.status}</span><br><br>{t.description}", unsafe_allow_html=True)
                    if t.status != "İptal Edildi":
                        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                        if st.button("İptal Et", key=f"c_{t.id}"):
                            if t.status == "Tamamlandı":
                                target_u = db.query(User).filter(User.username == t.assigned_to).first()
                                if target_u:
                                    target_u.points = max(0, target_u.points - t.points)
                                    target_u.lifetime_points = max(0, (target_u.lifetime_points or 0) - t.points)
                                    target_u.total_completed = max(0, (target_u.total_completed or 0) - 1)
                            t.status = "İptal Edildi"
                            db.commit(); st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
        with t3:
            for u in db.query(User).filter(User.username != cu.username).all():
                with st.expander(f"👤 {u.username} ({u.role})"):
                    assigned, completed = u.total_assigned or 0, u.total_completed or 0
                    
                    overdue = 0
                    today_d = datetime.now().date()
                    usr_pending = db.query(Task).filter(Task.assigned_to==u.username, Task.status=="Bekliyor").all()
                    for tsk in usr_pending:
                        if tsk.due_date:
                            try:
                                if datetime.strptime(tsk.due_date, "%d.%m.%Y").date() < today_d:
                                    overdue += 1
                            except: pass

                    st.markdown(f"""
                    <div style='display:flex; justify-content:space-between; text-align:center; background:#f8fafc; padding:15px; border-radius:12px; margin-bottom:15px;'>
                        <div><div style='font-size:11px; color:#64748b; font-weight:700;'>Verilen</div><div style='font-weight:900; font-size:18px; color:#1A2744;'>{assigned}</div></div>
                        <div><div style='font-size:11px; color:#64748b; font-weight:700;'>Yapılan</div><div style='font-weight:900; font-size:18px; color:#2DB5A0;'>{completed}</div></div>
                        <div><div style='font-size:11px; color:#ef4444; font-weight:700;'>Geciken</div><div style='font-weight:900; font-size:18px; color:#ef4444;'>{overdue}</div></div>
                        <div><div style='font-size:11px; color:#64748b; font-weight:700;'>Tüm Puan</div><div style='font-weight:900; font-size:18px; color:#f59e0b;'>⭐ {u.lifetime_points or 0}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button("Kullanıcıyı Sil", key=f"d_{u.id}"):
                        db.query(Task).filter(Task.assigned_to == u.username).delete(); db.delete(u); db.commit(); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
            if st.button("Sistemi Sıfırla (Karneler Silinmez)", use_container_width=True):
                db.query(Task).delete(); db.query(User).update({User.points: 0}); db.commit(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with t4: render_events_tab(is_admin=True)
        with t5: render_leaderboard(db)
        with t6: render_profile_tab()

    elif cu.role == "Birim Başkanı":
        render_stats(cu.username)
        t1, t2, t3, t4, t5, t6 = st.tabs(["Görevler", "Ata", "Takip", "Etkinlik", "Liderlik", "Profil"])
        with t1:
            for t in db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all():
                st.markdown(f'<div class="task-card"><div class="task-title">{t.title}</div><div class="task-meta">{t.description}</div><span class="badge {BADGE.get(t.priority)}">{t.priority}</span> <span style="float:right; font-weight:800; color:#2DB5A0;">+{t.points} pts</span></div>', unsafe_allow_html=True)
                if st.button("Tamamla", key=f"bb_{t.id}", use_container_width=True):
                    t.status = "Tamamlandı"
                    cu.points = (cu.points or 0) + t.points; cu.lifetime_points = (cu.lifetime_points or 0) + t.points; cu.total_completed = (cu.total_completed or 0) + 1
                    db.commit(); st.rerun()
        with t2:
            members = db.query(User).filter(User.role == "Üye").all()
            if not members: st.info("Sistemde üye yok.")
            else:
                assigned_to = st.selectbox("Kime:", [f"{u.username} ({u.alan})" for u in members]).rsplit(" (", 1)[0]
                tt, td = st.text_input("Başlık"), st.text_area("Detaylar")
                c1, c2 = st.columns(2)
                with c1: tp = st.selectbox("Öncelik", ["Acil","Yüksek","Orta","Düşük"])
                with c2: tpts = st.number_input("Puan", min_value=1, value=10)
                t_due = st.date_input("Son Tarih", value=date.today() + timedelta(days=7), format="DD.MM.YYYY")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Görevi Gönder", use_container_width=True):
                    if not tt.strip(): st.warning("Başlık boş olamaz.")
                    else:
                        target_u = db.query(User).filter(User.username==assigned_to).first()
                        if target_u: target_u.total_assigned = (target_u.total_assigned or 0) + 1 
                        
                        formatted_t_due = t_due.strftime("%d.%m.%Y")
                        db.add(Task(assigned_to=assigned_to, assigned_by=cu.username, title=tt, description=td, priority=tp, points=tpts, status="Bekliyor", due_date=formatted_t_due))
                        db.commit()
                        if target_u and target_u.email: trigger_background_email(target_u.email, target_u.username, tt, td, tp, tpts, formatted_t_due)
                        st.success("Gönderildi!")
        with t3:
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
                                if datetime.strptime(tsk.due_date, "%d.%m.%Y").date() < today_d:
                                    overdue += 1
                            except: pass
                    st.markdown(f"**Verilen İş:** {assigned} | **Yapılan:** {completed} | **Geciken:** <span style='color:#ef4444;'>{overdue}</span> | **Tüm Puan:** ⭐ {u.lifetime_points or 0}", unsafe_allow_html=True)
            st.divider(); st.markdown("### Verdiğiniz Görevlerin Durumu")
            for t in db.query(Task).filter(Task.assigned_by==cu.username).order_by(Task.id.desc()).limit(20).all():
                st.markdown(f"<div style='background:#fff; padding:12px; border-radius:16px; margin-bottom:8px; font-weight:700;'>{t.title} <span style='font-size:11px; color:#64748b;'>-> {t.assigned_to} ({t.status})</span></div>", unsafe_allow_html=True)
        with t4: render_events_tab(is_admin=True)
        with t5: render_leaderboard(db)
        with t6: render_profile_tab()

    else:
        render_stats(cu.username)
        t1, t2, t3, t4, t5 = st.tabs(["Görevler", "Geçmiş", "Etkinlik", "Liderlik", "Profil"])
        with t1:
            tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all()
            if not tasks: st.markdown('<div style="text-align:center;padding:3rem;"><div style="font-size:40px; margin-bottom:10px;">✨</div><b style="color:#1A2744;">Bekleyen göreviniz bulunmuyor.</b></div>', unsafe_allow_html=True)
            for t in tasks:
                due_label = f"| Son: {t.due_date}" if t.due_date else ""
                st.markdown(f'<div class="task-card"><div class="task-title">{t.title}</div><div class="task-meta">{t.description}</div><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;"><span class="badge {BADGE.get(t.priority)}">{t.priority}</span> <span style="font-size:0.75rem; font-weight:800; color:#2DB5A0;">+{t.points} pts <span style="color:#94a3b8; font-weight:500;">{due_label}</span></span></div></div>', unsafe_allow_html=True)
                col_a, col_b = st.columns([3, 2])
                with col_a:
                    if st.button("Tamamla", key=f"u_{t.id}", use_container_width=True):
                        t.status = "Tamamlandı"
                        cu.points = (cu.points or 0) + t.points; cu.lifetime_points = (cu.lifetime_points or 0) + t.points; cu.total_completed = (cu.total_completed or 0) + 1
                        db.commit(); st.rerun()
                with col_b:
                    if t.due_date:
                        ics = make_ics(t.title, t.description or "", t.due_date)
                        st.download_button("Takvime Ekle", data=ics, file_name=f"arder_{t.id}.ics", mime="text/calendar", key=f"ics_{t.id}", use_container_width=True)
        with t2:
            done_tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Tamamlandı").order_by(Task.id.desc()).limit(20).all()
            for t in done_tasks: st.markdown(f'<div class="task-card done"><div class="task-title">✓ {t.title}</div><div class="task-meta" style="color:#2DB5A0; font-weight:700;">+{t.points} puan eklendi</div></div>', unsafe_allow_html=True)
        with t3: render_events_tab(is_admin=False)
        with t4: render_leaderboard(db)
        with t5: render_profile_tab()

db.close()
