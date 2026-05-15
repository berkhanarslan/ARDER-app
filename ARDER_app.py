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
# 2. MEGA-CACHE: STATİK ASSETLER VE MODERN OVAL CSS
# ══════════════════════════════════════════════════════════
@st.cache_data
def get_static_assets():
    logo_b64 = ""
    for ext in ["logo.png","logo.jpg","logo.jpeg"]:
        if os.path.exists(ext):
            with open(ext,"rb") as f: logo_b64 = base64.b64encode(f.read()).decode()
            mime = "image/png" if ext.endswith(".png") else "image/jpeg"
            logo_html = f'<img src="data:{mime};base64,{logo_b64}" style="height:40px;object-fit:contain;">'
            login_logo_html = f'<img src="data:{mime};base64,{logo_b64}" style="height:140px;object-fit:contain;margin-bottom:10px;">'
            break
    else:
        logo_html = '<span style="font-size:40px;">🦚</span>'
        login_logo_html = '<div style="font-size:90px; text-align:center;">🦚</div>'

    _ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="100" fill="#ffffff"/><text x="256" y="370" text-anchor="middle" font-size="340" font-weight="900" fill="#2DB5A0" font-family="Arial,sans-serif">A</text></svg>"""
    _ICON_URI  = f"data:image/svg+xml;base64,{base64.b64encode(_ICON_SVG.encode()).decode()}"
    _manifest  = {"name":"ARDER","short_name":"ARDER","display":"standalone","background_color":"#f4f7f6","theme_color":"#ffffff","icons":[{"src":_ICON_URI,"sizes":"512x512","type":"image/svg+xml","purpose":"any maskable"}]}
    
    html = f"""
    <link rel="manifest" href="data:application/manifest+json;base64,{base64.b64encode(json.dumps(_manifest).encode()).decode()}">
    <meta name="theme-color" content="#ffffff">
    <style>
    /* SADECE GEREKSİZ BUTONLARI GİZLE, MENÜYÜ BOZMA */
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    .viewerBadge_container, .stAppViewFooter, footer {{ display: none !important; }}

    /* GENEL ARKA PLAN VE KISITLAMALAR */
    .main .block-container {{ max-width:480px; margin:auto; padding:1rem; padding-top:2rem; }}
    [data-testid="stAppViewContainer"] {{ background-color:#f5f8f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    
    /* INPUT KUTUCUKLARI (OVAL VE BEYAZ) */
    div[data-baseweb="input"] > div {{ border-radius: 25px !important; border: 1px solid #e2e8f0 !important; background-color: #ffffff !important; padding: 4px 12px !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important; }}
    div[data-baseweb="select"] > div {{ border-radius: 25px !important; border: 1px solid #e2e8f0 !important; }}
    
    /* BUTONLAR (OVAL VE SOFT) */
    div.stButton>button {{ border-radius: 30px !important; font-weight: 700 !important; padding: 0.6rem 1rem !important; border: none !important; transition: all 0.3s ease; }}
    div.stButton>button:first-child {{ background: #2DB5A0 !important; color: #fff !important; box-shadow: 0 4px 14px rgba(45, 181, 160, 0.3) !important; }}
    div.stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(45, 181, 160, 0.4) !important; }}
    .btn-danger>button {{ background: #ef4444 !important; color: #fff !important; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3) !important; }}

    /* MODERN BEYAZ HEADER (Uygulama İçi) */
    .app-header {{ background: #ffffff; border-radius: 24px; padding: 1rem 1.2rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.8rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
    .app-header .brand-name {{ font-size: 1.15rem; font-weight: 900; color: #1A2744; line-height: 1.1; }}
    .app-header .brand-sub {{ font-size: 0.7rem; color: #2DB5A0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}

    /* GİRİŞ EKRANI ÖZEL BAŞLIĞI */
    .login-header {{ text-align: center; margin-bottom: 2rem; margin-top: 1rem; }}
    .login-header h1 {{ color: #1A2744; font-size: 1.8rem; font-weight: 900; margin: 0; padding: 0; }}
    .login-header p {{ color: #2DB5A0; font-size: 0.85rem; font-weight: 700; margin: 0; padding: 0; letter-spacing: 1px; }}

    /* İSTATİSTİK KARTLARI (OVAL) */
    .stat-wrap {{ display:flex; gap:12px; margin:0.5rem 0 1.5rem 0; }}
    .stat-card {{ flex:1; background:#fff; border-radius:24px; box-shadow:0 8px 24px rgba(0,0,0,0.04); padding:1.2rem 0.8rem; text-align:center; display: flex; flex-direction: column; justify-content: center; }}
    .stat-card .label {{ font-size:0.7rem; color:#64748b; font-weight:600; margin-bottom:8px; }}
    .stat-card .value {{ font-size:1.8rem; font-weight:900; color:#1A2744; line-height:1; }}
    .stat-card .value.green {{ color: #2DB5A0; }}

    /* GÖREV KARTLARI (BEYAZ VE SOFT GÖLGE) */
    .task-card {{ background: #fff; border-radius: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.03); padding: 1.2rem; margin-bottom: 1rem; border-left: 6px solid #2DB5A0; position: relative; }}
    .task-card.done {{ border-left-color: #cbd5e1; opacity: 0.7; }}
    .task-title {{ font-weight: 800; color: #1A2744; font-size: 1rem; margin-bottom: 0.3rem; }}
    .task-meta {{ font-size: 0.8rem; color: #64748b; margin-bottom: 0.8rem; line-height: 1.4; }}
    
    /* ROZETLER (BADGES) */
    .badge {{ display:inline-block; padding:0.25rem 0.7rem; border-radius:20px; font-size:0.7rem; font-weight:700; }}
    .badge-acil {{ background:#fee2e2; color:#b91c1c; }} .badge-yuksek {{ background:#fef3c7; color:#b45309; }}
    .badge-orta {{ background:#ccfbf1; color:#0f766e; }} .badge-dusuk {{ background:#e0f2fe; color:#0369a1; }}
    
    /* SEKMELER (TABS) MODERNLEŞTİRME */
    [data-testid="stTabs"] button {{ padding-bottom: 10px !important; }}
    [data-testid="stTabs"] button[aria-selected="true"] {{ color:#2DB5A0 !important; border-bottom: 3px solid #2DB5A0 !important; }}
    </style>
    """
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
    points = Column(Integer, default=0)

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
            ]:
                try: conn.execute(text(stmt)); conn.commit()
                except: pass
    except: pass 

init_db()

# ══════════════════════════════════════════════════════════
# 4. YARDIMCI FONKSİYONLAR
# ══════════════════════════════════════════════════════════
def send_email_notification(to_email, task_title, task_desc, priority, points, due_date):
    try:
        s_email = st.secrets.get("EMAIL_USER", "")
        s_pass  = st.secrets.get("EMAIL_PASS", "")
        if not s_email or not s_pass or not to_email: return False 
        msg = MIMEMultipart()
        msg['From'] = f"ARDER Sistem <{s_email}>"
        msg['To'] = to_email
        msg['Subject'] = f"📌 Yeni Görev: {task_title}"
        msg.attach(MIMEText(f"Yeni Görev: {task_title}\nÖncelik: {priority}\nPuan: {points}\nSon: {due_date}\n\nAçıklama:\n{task_desc}", 'plain'))
        server = smtplib.SMTP(st.secrets.get("SMTP_SERVER", "smtp.gmail.com"), int(st.secrets.get("SMTP_PORT", 587)))
        server.starttls()
        server.login(s_email, s_pass)
        server.send_message(msg)
        server.quit()
    except: pass

def trigger_background_email(*args): 
    threading.Thread(target=send_email_notification, args=args).start()

def push_notification(title: str, body: str):
    st.session_state["_notif_title"] = title
    st.session_state["_notif_body"]  = body

def _flush_notification():
    t = st.session_state.get("_notif_title")
    b = st.session_state.get("_notif_body")
    if t and b:
        components.html(f"<script>(function(){{if (!('Notification' in window)) return; var fn = function() {{ new Notification({json.dumps(t)}, {{body:{json.dumps(b)}}}); }}; if (Notification.permission === 'granted') {{ fn(); }} else if (Notification.permission !== 'denied') {{ Notification.requestPermission().then(function(p){{ if (p==='granted') fn(); }}); }} }})();</script>", height=0)
        st.session_state["_notif_title"] = None
        st.session_state["_notif_body"]  = None

def make_ics(title, description, due_date_str):
    try: dt = datetime.strptime(due_date_str, "%Y-%m-%d")
    except: dt = datetime.now() + timedelta(days=7)
    dtstart = dt.strftime("%Y%m%d")
    dtend   = (dt + timedelta(days=1)).strftime("%Y%m%d")
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid     = f"{dtstamp}-arder-task@akademikreklerdernegi"
    desc    = (description or "").replace("\n", "\\n").replace(",", "\\,")
    return (f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ARDER//Gorev Yonetimi//TR\nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\nBEGIN:VEVENT\nUID:{uid}\nDTSTAMP:{dtstamp}\nDTSTART;VALUE=DATE:{dtstart}\nDTEND;VALUE=DATE:{dtend}\nSUMMARY:📌 {title}\nDESCRIPTION:{desc}\nSTATUS:CONFIRMED\nBEGIN:VALARM\nTRIGGER:-PT1H\nACTION:DISPLAY\nDESCRIPTION:ARDER Hatırlatma: {title}\nEND:VALARM\nEND:VEVENT\nEND:VCALENDAR\n").encode("utf-8")

def show_header():
    st.markdown(f'<div class="app-header">{LOGO_HTML}<div><div class="brand-name">ARDER</div><div class="brand-sub">Akademik Renkler</div></div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 5. LİDERLİK TABLOSU
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def generate_leaderboard_html(users_dict):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: transparent; margin: 0; padding: 0; }
    .pod{display:flex;justify-content:center;align-items:flex-end;gap:10px;height:210px;margin-bottom:18px;}
    .pc{display:flex;flex-direction:column;align-items:center;width:30%;max-width:110px;}
    .av{width:48px;height:48px;border-radius:16px;margin-bottom:6px;background:linear-gradient(135deg,#1976D2,#2DB5A0);color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900;}
    .pn{font-size:12px;font-weight:800;color:#1A2744;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;width:100%;}
    .pp{font-size:10px;color:#64748b;margin-bottom:5px;font-weight:600;}
    .blk{width:100%;display:flex;justify-content:center;padding-top:10px;font-weight:700;font-size:15px;border-radius:16px 16px 0 0;color:#fff;box-shadow:0 -4px 12px rgba(0,0,0,0.05);}
    .g{height:140px;background:linear-gradient(135deg,#f59e0b,#d97706);}
    .s{height:105px;background:#e2e8f0;color:#475569;}
    .b{height:80px;background:#d97706;}
    .li{display:flex;align-items:center;background:#fff;padding:12px 16px;border-radius:20px;margin-bottom:10px;box-shadow:0 4px 16px rgba(0,0,0,0.03);}
    .rb{width:32px;height:32px;display:flex;justify-content:center;align-items:center;border-radius:10px;font-weight:800;font-size:13px;color:#fff;margin-right:12px;flex-shrink:0;}
    .r1{background:#f59e0b;}
    .r2{background:#cbd5e1;color:#475569;}
    .r3{background:#d97706;}
    .rx{background:#f8fafc;color:#64748b;}
    .ln{font-weight:800;color:#1A2744;font-size:14px;}
    .lr{font-size:11px;color:#94a3b8;font-weight:500;}
    .lp{margin-left:auto;font-weight:900;color:#2DB5A0;font-size:18px;}
    </style>
    </head>
    <body>
    <div style="padding:4px;">
    <div style="color:#1A2744;font-size:20px;font-weight:900;margin-bottom:4px;">🏆 Liderlik Tablosu</div>
    <div style="color:#94a3b8;font-size:12px;margin-bottom:24px;font-weight:600;">Her ayın başında sıfırlanır</div>
    """
    
    if users_dict:
        u1 = users_dict[0]
        u2 = users_dict[1] if len(users_dict) > 1 else None
        u3 = users_dict[2] if len(users_dict) > 2 else None
        
        html += "<div class='pod'>"
        if u2: html += f"<div class='pc'><div class='av'>{u2['username'][0].upper()}</div><div class='pn'>{u2['username']}</div><div class='pp'>{u2['points']} Puan</div><div class='blk s'>🥈</div></div>"
        else: html += "<div class='pc'></div>"
        
        html += f"<div class='pc'><div class='av'>{u1['username'][0].upper()}</div><div class='pn'>{u1['username']}</div><div class='pp'>{u1['points']} Puan</div><div class='blk g'>🥇</div></div>"
        
        if u3: html += f"<div class='pc'><div class='av'>{u3['username'][0].upper()}</div><div class='pn'>{u3['username']}</div><div class='pp'>{u3['points']} Puan</div><div class='blk b'>🥉</div></div>"
        else: html += "<div class='pc'></div>"
        html += "</div>"
        
        for i, u in enumerate(users_dict):
            r = i + 1
            rc = f"r{r}" if r <= 3 else "rx"
            html += f"<div class='li'><div class='rb {rc}'>{r}</div><div class='av' style='width:40px;height:40px;font-size:16px;margin-bottom:0;margin-right:12px;border-radius:12px;'>{u['username'][0].upper()}</div><div style='overflow:hidden;'><div class='ln'>{u['username']}</div><div class='lr'>{u['role']} | {u['alan']}</div></div><div class='lp'>{u['points']}<span style='font-size:10px;color:#cbd5e1;'> pts</span></div></div>"
    
    html += "</div></body></html>"
    return html

def render_leaderboard(db):
    users = db.query(User).order_by(User.points.desc()).all()
    u_dict = [{"username": u.username, "points": u.points, "role": u.role, "alan": u.alan or "—"} for u in users]
    html_code = generate_leaderboard_html(u_dict)
    components.html(html_code, height=650, scrolling=True)

# ══════════════════════════════════════════════════════════
# 6. OTURUM BAŞLATMA
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
    time.sleep(0.4)
    st.session_state.first_load = True

saved_cookie = controller.get('arder_user')
if saved_cookie and not st.session_state.logged_in:
    u = db.query(User).filter(User.username == saved_cookie).first()
    if u:
        st.session_state.update({"logged_in": True, "username": u.username, "role": u.role})
        st.rerun()

# ══════════════════════════════════════════════════════════
# 7. GİRİŞ VE KAYIT EKRANI
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    
    # Giriş ekranı özel logo ve başlık
    st.markdown(f'<div class="login-header">{LOGIN_LOGO_HTML}<h1>AKADEMİK</h1><p>RENKLER DERNEĞİ</p></div>', unsafe_allow_html=True)
    
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
                push_notification("Hoş Geldin!", f"Merhaba {user.username}.")
                st.rerun()
            else: st.error("Bilgiler hatalı!")
            
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Duplicate ID Hatasını Çözen Key Eklemesi: key="kayit_sifre"
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
                db.add(User(username=ru.strip(), password=rp.strip(), email=rmail.strip(), role=role, alan=alan, points=0))
                db.commit()
                st.success("Başarıyla kayıt olundu! Giriş sekmesinden devam edebilirsiniz.")

# ══════════════════════════════════════════════════════════
# 8. ANA PANELLER
# ══════════════════════════════════════════════════════════
else:
    cu = db.query(User).filter(User.username==st.session_state.username).first()
    if not cu:
        st.session_state.logged_in = False
        st.rerun()

    show_header()
    BADGE = {"Acil":"badge-acil","Yüksek":"badge-yuksek","Orta":"badge-orta","Düşük":"badge-dusuk"}

    def render_stats(u_name):
        pending = db.query(Task).filter(Task.assigned_to==u_name, Task.status=="Bekliyor").count()
        done = db.query(Task).filter(Task.assigned_to==u_name, Task.status=="Tamamlandı").count()
        st.markdown(f"""
        <div class="stat-wrap">
          <div class="stat-card"><div class="label">Puanım</div><div class="value green">{cu.points}</div></div>
          <div class="stat-card"><div class="label">Bekleyen</div><div class="value">{pending}</div></div>
          <div class="stat-card"><div class="label">Tamamlanan</div><div class="value">{done}</div></div>
        </div>
        """, unsafe_allow_html=True)

    def render_profile_tab():
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; padding: 2rem; background:#fff; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);"><div style="font-size: 50px; margin-bottom: 10px;">👤</div><h2 style="color:#1A2744; margin:0; font-weight:900;">{cu.username}</h2><p style="color:#64748b; font-weight:600; margin-top:5px;">{cu.role} • {cu.alan or ""}</p><div style="font-size: 24px; font-weight: 800; color: #2DB5A0; margin: 20px 0;">⭐ {cu.points} Puan</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
        if st.button("Sistemden Çıkış Yap", use_container_width=True):
            controller.remove('arder_user')
            st.session_state.update({"logged_in": False, "username": "", "role": ""})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── MODERATÖR ──
    if cu.role == "Moderatör":
        t1, t2, t3, t4, t5 = st.tabs(["Ata", "Yönet", "Üyeler", "Liderlik", "Profil"])
        with t1:
            users = db.query(User).filter(User.username != cu.username).all()
            if not users: st.info("Sistemde üye yok.")
            else:
                assigned_to = st.selectbox("Kime:", [f"{u.username} ({u.role})" for u in users]).rsplit(" (", 1)[0]
                tt, td = st.text_input("Başlık"), st.text_area("Detaylar", height=80)
                c1, c2 = st.columns(2)
                with c1: tp = st.selectbox("Öncelik", ["Acil","Yüksek","Orta","Düşük"])
                with c2: tpts = st.number_input("Puan", min_value=1, value=10)
                t_due = st.date_input("Son Tarih", value=date.today() + timedelta(days=7), min_value=date.today())
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Görevi Gönder", use_container_width=True):
                    if not tt.strip(): st.warning("Başlık boş olamaz.")
                    else:
                        db.add(Task(assigned_to=assigned_to, assigned_by=cu.username, title=tt, description=td, priority=tp, points=tpts, status="Bekliyor", due_date=str(t_due)))
                        db.commit()
                        target = db.query(User).filter(User.username==assigned_to).first()
                        if target and target.email: trigger_background_email(target.email, tt, td, tp, tpts, str(t_due))
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
                                if target_u: target_u.points = max(0, target_u.points - t.points)
                            t.status = "İptal Edildi"
                            db.commit(); st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
        with t3:
            for u in db.query(User).filter(User.username != cu.username).all():
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"<div style='background:#fff; padding:10px; border-radius:12px; margin-bottom:8px; font-weight:700;'>{u.username}<br><span style='font-size:11px; font-weight:500; color:#64748b;'>{u.role}</span></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button("Sil", key=f"d_{u.id}"):
                        db.query(Task).filter(Task.assigned_to == u.username).delete()
                        db.delete(u); db.commit(); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
            if st.button("Sistemi Sıfırla (Görev/Puan)", use_container_width=True):
                db.query(Task).delete(); db.query(User).update({User.points: 0}); db.commit(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with t4: render_leaderboard(db)
        with t5: render_profile_tab()

    # ── BİRİM BAŞKANI ──
    elif cu.role == "Birim Başkanı":
        render_stats(cu.username)
        t1, t2, t3, t4, t5 = tabs = st.tabs(["Görevler", "Ata", "Takip", "Liderlik", "Profil"])
        with t1:
            for t in db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all():
                st.markdown(f'<div class="task-card"><div class="task-title">{t.title}</div><div class="task-meta">{t.description}</div><span class="badge {BADGE.get(t.priority)}">{t.priority}</span> <span style="float:right; font-weight:800; color:#2DB5A0;">+{t.points} pts</span></div>', unsafe_allow_html=True)
                if st.button("Tamamla", key=f"bb_{t.id}", use_container_width=True):
                    t.status, cu.points = "Tamamlandı", cu.points + t.points
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
                t_due = st.date_input("Son Tarih", value=date.today() + timedelta(days=7))
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Görevi Gönder", use_container_width=True):
                    if not tt.strip(): st.warning("Başlık boş olamaz.")
                    else:
                        db.add(Task(assigned_to=assigned_to, assigned_by=cu.username, title=tt, description=td, priority=tp, points=tpts, status="Bekliyor", due_date=str(t_due)))
                        db.commit()
                        target = db.query(User).filter(User.username==assigned_to).first()
                        if target and target.email: trigger_background_email(target.email, tt, td, tp, tpts, str(t_due))
                        st.success("Gönderildi!")
        with t3:
            for t in db.query(Task).filter(Task.assigned_by==cu.username).order_by(Task.id.desc()).limit(20).all():
                st.markdown(f"<div style='background:#fff; padding:12px; border-radius:16px; margin-bottom:8px; font-weight:700;'>{t.title} <span style='font-size:11px; color:#64748b;'>-> {t.assigned_to}</span></div>", unsafe_allow_html=True)
        with t4: render_leaderboard(db)
        with t5: render_profile_tab()

    # ── ÜYE ──
    else:
        render_stats(cu.username)
        t1, t2, t3, t4 = st.tabs(["Görevler", "Geçmiş", "Liderlik", "Profil"])
        with t1:
            tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all()
            if not tasks: st.markdown('<div style="text-align:center;padding:3rem;"><div style="font-size:40px; margin-bottom:10px;">✨</div><b style="color:#1A2744;">Bekleyen göreviniz bulunmuyor.</b></div>', unsafe_allow_html=True)
            for t in tasks:
                due_label = f"| Son: {t.due_date}" if t.due_date else ""
                st.markdown(f'<div class="task-card"><div class="task-title">{t.title}</div><div class="task-meta">{t.description}</div><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;"><span class="badge {BADGE.get(t.priority)}">{t.priority}</span> <span style="font-size:0.75rem; font-weight:800; color:#2DB5A0;">+{t.points} pts <span style="color:#94a3b8; font-weight:500;">{due_label}</span></span></div></div>', unsafe_allow_html=True)
                col_a, col_b = st.columns([3, 2])
                with col_a:
                    if st.button("Tamamla", key=f"u_{t.id}", use_container_width=True):
                        t.status, cu.points = "Tamamlandı", cu.points + t.points
                        db.commit(); st.rerun()
                with col_b:
                    if t.due_date:
                        ics = make_ics(t.title, t.description or "", t.due_date)
                        st.download_button("Takvime Ekle", data=ics, file_name=f"arder_{t.id}.ics", mime="text/calendar", key=f"ics_{t.id}", use_container_width=True)
        with t2:
            done_tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Tamamlandı").order_by(Task.id.desc()).limit(20).all()
            for t in done_tasks: st.markdown(f'<div class="task-card done"><div class="task-title">✓ {t.title}</div><div class="task-meta" style="color:#2DB5A0; font-weight:700;">+{t.points} puan eklendi</div></div>', unsafe_allow_html=True)
        with t3: render_leaderboard(db)
        with t4: render_profile_tab()

db.close()
