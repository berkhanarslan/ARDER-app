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
# 1. SAYFA YAPISI
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="ARDER", page_icon="🦚", layout="centered", initial_sidebar_state="collapsed")
controller = CookieController()

# ══════════════════════════════════════════════════════════
# 2. MEGA-CACHE: STATİK ASSETLER
# ══════════════════════════════════════════════════════════
@st.cache_data
def get_static_assets():
    logo_b64 = ""
    for ext in ["logo.png","logo.jpg","logo.jpeg"]:
        if os.path.exists(ext):
            with open(ext,"rb") as f: logo_b64 = base64.b64encode(f.read()).decode()
            mime = "image/png" if ext.endswith(".png") else "image/jpeg"
            logo_html = f'<img src="data:{mime};base64,{logo_b64}" style="height:46px;border-radius:8px;object-fit:contain;">'
            break
    else:
        logo_html = '<span style="font-size:46px;">🦚</span>'

    _ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="100" fill="#1A2744"/><text x="256" y="370" text-anchor="middle" font-size="340" font-weight="900" fill="#2DB5A0" font-family="Arial,sans-serif">A</text><text x="256" y="460" text-anchor="middle" font-size="68" font-weight="700" fill="#1976D2" font-family="Arial,sans-serif">ARDER</text></svg>"""
    _ICON_URI  = f"data:image/svg+xml;base64,{base64.b64encode(_ICON_SVG.encode()).decode()}"
    _manifest  = {"name":"ARDER","short_name":"ARDER","display":"standalone","background_color":"#f0f7f6","theme_color":"#1A2744","icons":[{"src":_ICON_URI,"sizes":"512x512","type":"image/svg+xml","purpose":"any maskable"}]}
    
    html = f"""
    <link rel="manifest" href="data:application/manifest+json;base64,{base64.b64encode(json.dumps(_manifest).encode()).decode()}">
    <meta name="theme-color" content="#1A2744">
    <style>
    .main .block-container {{ max-width:500px; margin:auto; padding:1rem; }}
    [data-testid="stAppViewContainer"] {{ background-color:#f0f7f6; }}
    [data-testid="stHeader"] {{ background:transparent; }}
    [data-testid="stSidebar"] {{ background:#1A2744; }}
    [data-testid="stSidebar"] * {{ color:#f0f7f6 !important; }}
    .app-header {{ background:linear-gradient(135deg,#1A2744 0%,#1976D2 55%,#2DB5A0 100%); border-radius:16px; padding:0.85rem 1rem; margin-bottom:1rem; display:flex; align-items:center; gap:0.8rem; }}
    .app-header .brand-name {{ font-size:1.25rem; font-weight:900; color:#fff; line-height:1.1; }}
    .app-header .brand-sub {{ font-size:0.72rem; color:rgba(255,255,255,0.75); }}
    .stat-wrap {{ display:flex; gap:10px; margin:0.3rem 0 1rem 0; }}
    .stat-card {{ flex:1; background:#fff; border-radius:14px; box-shadow:0 4px 16px rgba(26,39,68,0.10); padding:1rem 0.8rem; border-left:4px solid #2DB5A0; text-align:center; }}
    .stat-card.blue {{ border-left-color:#1976D2; }}
    .stat-card.dark {{ border-left-color:#1A2744; }}
    .stat-card .label {{ font-size:0.65rem; color:#5a7a76; font-weight:700; text-transform:uppercase; margin-bottom:5px; }}
    .stat-card .value {{ font-size:1.6rem; font-weight:900; color:#1A2744; line-height:1; }}
    .task-card {{ background:#fff; border-radius:14px; box-shadow:0 3px 12px rgba(26,39,68,0.08); padding:1rem; margin-bottom:0.8rem; border-bottom:3px solid #2DB5A0; }}
    .task-card.done {{ border-bottom-color:#a0cfcc; opacity:0.82; }}
    .task-card.canceled {{ border-bottom-color:#ef4444; opacity:0.6; }}
    .task-title {{ font-weight:700; color:#1A2744; font-size:0.97rem; }}
    .task-meta {{ font-size:0.79rem; color:#5a7a76; margin:0.3rem 0; }}
    .badge {{ display:inline-block; padding:0.18rem 0.6rem; border-radius:20px; font-size:0.7rem; font-weight:700; }}
    .badge-acil {{ background:#fde8e8; color:#c0392b; }} .badge-yuksek {{ background:#fff3cd; color:#856404; }}
    .badge-orta {{ background:#d4f1ec; color:#1A5C52; }} .badge-dusuk {{ background:#e8f4fd; color:#1565C0; }}
    div.stButton>button {{ border-radius:8px !important; font-weight:600 !important; width:100%; }}
    div.stButton>button:first-child {{ background:linear-gradient(90deg,#1A2744,#1976D2) !important; color:#fff !important; border:none !important; }}
    div.stButton>button:hover {{ background:linear-gradient(90deg,#2DB5A0,#1976D2) !important; box-shadow:0 4px 14px rgba(45,181,160,0.35) !important; transform:translateY(-1px); }}
    .btn-danger>button {{ background:linear-gradient(90deg,#ef4444,#dc2626) !important; color:#fff !important; }}
    [data-testid="stTabs"] button[aria-selected="true"] {{ color:#1976D2 !important; border-bottom:2px solid #2DB5A0 !important; }}
    </style>
    """
    return html, logo_html

STATIC_HTML, LOGO_HTML = get_static_assets()
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
# 4. YARDIMCI FONKSİYONLAR (Mail, ICS, Bildirim)
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
    st.markdown(f'<div class="app-header">{LOGO_HTML}<div><div class="brand-name">ARDER</div><div class="brand-sub">Akademik Renkler Derneği</div></div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 5. LİDERLİK TABLOSU (%100 GARANTİLİ HTML İSKELETİ)
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def generate_leaderboard_html(users_dict):
    # ÇÖZÜM: HTML iskeletini bağımsız bir mini sayfa (iframe) formatına çevirdik
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: transparent; margin: 0; padding: 0; }
    .pod{display:flex;justify-content:center;align-items:flex-end;gap:10px;height:210px;margin-bottom:18px;}
    .pc{display:flex;flex-direction:column;align-items:center;width:30%;max-width:110px;}
    .av{width:48px;height:48px;border-radius:8px;margin-bottom:6px;background:linear-gradient(135deg,#1976D2,#2DB5A0);color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900;}
    .pn{font-size:11px;font-weight:700;color:#1A2744;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;width:100%;}
    .pp{font-size:10px;color:#9ca3af;margin-bottom:5px;}
    .blk{width:100%;display:flex;justify-content:center;padding-top:10px;font-weight:700;font-size:15px;border-radius:6px 6px 0 0;color:#fff;}
    .g{height:140px;background:linear-gradient(135deg,#f59e0b,#d97706);}
    .s{height:105px;background:#cbd5e1;color:#475569;}
    .b{height:80px;background:#d97706;}
    .li{display:flex;align-items:center;background:#fff;padding:9px 12px;border-radius:10px;margin-bottom:8px;box-shadow:0 2px 8px rgba(0,0,0,0.05);}
    .rb{width:30px;height:30px;display:flex;justify-content:center;align-items:center;border-radius:6px;font-weight:700;font-size:12px;color:#fff;margin-right:10px;flex-shrink:0;}
    .r1{background:#f59e0b;}
    .r2{background:#cbd5e1;color:#475569;}
    .r3{background:#d97706;}
    .rx{background:#f1f5f9;color:#64748b;}
    .ln{font-weight:700;color:#1A2744;font-size:13px;}
    .lr{font-size:10px;color:#6b7280;}
    .lp{margin-left:auto;font-weight:800;color:#2DB5A0;font-size:16px;}
    </style>
    </head>
    <body>
    <div style="padding:8px;">
    <div style="color:#1A2744;font-size:19px;font-weight:800;">🏆 Liderlik Tablosu</div>
    <div style="color:#6b7280;font-size:12px;margin-bottom:18px;">Aylık olarak sıfırlanır!</div>
    """
    
    if users_dict:
        u1 = users_dict[0]
        u2 = users_dict[1] if len(users_dict) > 1 else None
        u3 = users_dict[2] if len(users_dict) > 2 else None
        
        html += "<div class='pod'>"
        if u2: html += f"<div class='pc'><div class='av'>{u2['username'][0].upper()}</div><div class='pn'>{u2['username']}</div><div class='pp'>{u2['points']} pts</div><div class='blk s'>🥈</div></div>"
        else: html += "<div class='pc'></div>"
        
        html += f"<div class='pc'><div class='av'>{u1['username'][0].upper()}</div><div class='pn'>{u1['username']}</div><div class='pp'>{u1['points']} pts</div><div class='blk g'>🥇</div></div>"
        
        if u3: html += f"<div class='pc'><div class='av'>{u3['username'][0].upper()}</div><div class='pn'>{u3['username']}</div><div class='pp'>{u3['points']} pts</div><div class='blk b'>🥉</div></div>"
        else: html += "<div class='pc'></div>"
        html += "</div>"
        
        for i, u in enumerate(users_dict):
            r = i + 1
            rc = f"r{r}" if r <= 3 else "rx"
            html += f"<div class='li'><div class='rb {rc}'>{r}</div><div class='av' style='width:36px;height:36px;font-size:15px;margin-bottom:0;margin-right:10px;'>{u['username'][0].upper()}</div><div style='overflow:hidden;'><div class='ln'>{u['username']}</div><div class='lr'>{u['role']} | {u['alan']}</div></div><div class='lp'>{u['points']}<span style='font-size:9px;color:#9ca3af;'> pts</span></div></div>"
    
    html += "</div></body></html>"
    return html

def render_leaderboard(db):
    users = db.query(User).order_by(User.points.desc()).all()
    u_dict = [{"username": u.username, "points": u.points, "role": u.role, "alan": u.alan or "—"} for u in users]
    html_code = generate_leaderboard_html(u_dict)
    # ÇÖZÜM: st.markdown yerine components.html kullanıyoruz, böylece ASLA bozulmaz.
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
    show_header()
    st.markdown("#### Görev Yönetim Sistemine Hoş Geldiniz!")
    st.divider()

    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])
    with tab1:
        lu, lp = st.text_input("Kullanıcı Adı"), st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            user = db.query(User).filter(User.username==lu, User.password==lp).first()
            if user:
                controller.set('arder_user', user.username, max_age=2592000) 
                st.session_state.update({"logged_in": True, "username": user.username, "role": user.role})
                push_notification("ARDER'e Hoş Geldin! 👋", f"Merhaba {user.username}, başarıyla giriş yaptın.")
                st.rerun()
            else: st.error("Kullanıcı adı veya şifre hatalı!")
            
    with tab2:
        ru, rmail, rp = st.text_input("Kullanıcı Adı (Yeni)"), st.text_input("E-Posta"), st.text_input("Şifre (Yeni)", type="password")
        role = st.selectbox("Statünüz", ["Üye", "Birim Başkanı", "Moderatör"])
        alanlar = {"Üye": ["Üye", "Sosyal Medya ve Tasarım", "İletişim", "İnsan Kaynakları", "Projeler ve Koordinatörlükler", "Etkinlik"],
                   "Birim Başkanı": ["Sosyal Medya ve Tasarım Başkanı", "İletişim Başkanı", "İnsan Kaynakları Başkanı", "Projeler ve Koordinatörlükler Başkanı", "Etkinlik Başkanı"],
                   "Moderatör": ["Başkan", "Başkan Yardımcısı", "Sayman", "Genel Sekreter", "Uygulama Moderatörü"]}
        alan = st.selectbox("Birim", alanlar[role])
        
        if st.button("Kayıt Ol"):
            if len(ru)<3: st.warning("İsim en az 3 karakter olmalı.")
            elif db.query(User).filter(User.username==ru).first(): st.warning("Bu kullanıcı adı alınmış!")
            else:
                db.add(User(username=ru, password=rp, email=rmail, role=role, alan=alan, points=0))
                db.commit()
                st.success("Kayıt başarılı! Lütfen giriş yapınız.")

# ══════════════════════════════════════════════════════════
# 8. ANA PANELLER (ÜYE, BİRİM BAŞKANI, MODERATÖR)
# ══════════════════════════════════════════════════════════
else:
    cu = db.query(User).filter(User.username==st.session_state.username).first()
    if not cu:
        st.session_state.logged_in = False
        st.rerun()

    with st.sidebar:
        st.markdown(f"### 👤 {cu.username}\n**{cu.role}** | {cu.alan or '—'}\n\n⭐ **{cu.points} Puan**")
        st.divider()
        if st.button("🚪 Çıkış Yap"):
            controller.remove('arder_user')
            st.session_state.update({"logged_in": False, "username": "", "role": ""})
            st.rerun()

    show_header()
    BADGE = {"Acil":"badge-acil","Yüksek":"badge-yuksek","Orta":"badge-orta","Düşük":"badge-dusuk"}

    def render_stats(u_name):
        pending = db.query(Task).filter(Task.assigned_to==u_name, Task.status=="Bekliyor").count()
        done = db.query(Task).filter(Task.assigned_to==u_name, Task.status=="Tamamlandı").count()
        st.markdown(f"""
        <div class="stat-wrap">
          <div class="stat-card"><div class="label">⭐ Puan</div><div class="value">{cu.points}</div></div>
          <div class="stat-card blue"><div class="label">⏳ Bekleyen</div><div class="value">{pending}</div></div>
          <div class="stat-card dark"><div class="label">✅ Tamam</div><div class="value">{done}</div></div>
        </div>
        """, unsafe_allow_html=True)

    # ── MODERATÖR PANELİ ──
    if cu.role == "Moderatör":
        t1, t2, t3, t4 = st.tabs(["📌 Görev Ata", "📋 Yönetim", "👥 Üyeler", "🏆 Lider"])
        with t1:
            users = db.query(User).filter(User.username != cu.username).all()
            if not users: st.info("Sistemde atanacak kimse yok.")
            else:
                assigned_to = st.selectbox("Görevi Alacak Kişi", [f"{u.username} ({u.role})" for u in users]).split(" ")[0]
                tt, td = st.text_input("Görev Başlığı"), st.text_area("Açıklama", height=70)
                c1, c2 = st.columns(2)
                with c1: tp = st.selectbox("Öncelik", ["Acil","Yüksek","Orta","Düşük"])
                with c2: tpts = st.number_input("Puan", min_value=1, value=10)
                t_due = st.date_input("Son Tarih (Deadline) 🗓", value=date.today() + timedelta(days=7), min_value=date.today())
                
                if st.button("📌 Görevi Ata", use_container_width=True):
                    if not ttitle.strip():
                        st.warning("Görev başlığı boş olamaz.")
                    else:
                        db.add(Task(assigned_to=assigned_to, assigned_by=cu.username, title=tt, description=td, priority=tp, points=tpts, status="Bekliyor", due_date=str(t_due)))
                        db.commit()
                        target = db.query(User).filter(User.username==assigned_to).first()
                        if target and target.email: trigger_background_email(target.email, tt, td, tp, tpts, str(t_due))
                        push_notification("Görev Atandı ✅", f"'{tt}' -> {assigned_to}")
                        st.success("Görev başarıyla atandı!")
                        
        with t2:
            all_t = db.query(Task).order_by(Task.id.desc()).limit(50).all()
            for t in all_t:
                status_color = "color:#2DB5A0;" if t.status == "Tamamlandı" else "color:#ef4444;" if t.status == "İptal Edildi" else "color:#eab308;"
                with st.expander(f"{t.title} -> {t.assigned_to} ({t.status})"):
                    st.markdown(f"**Puan:** {t.points} | **Ekleyen:** {t.assigned_by} | <span style='{status_color}'>**Durum:** {t.status}</span>\n\n{t.description}", unsafe_allow_html=True)
                    if t.status != "İptal Edildi":
                        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                        if st.button("🗑 İptal Et", key=f"c_{t.id}"):
                            if t.status == "Tamamlandı":
                                target_u = db.query(User).filter(User.username == t.assigned_to).first()
                                if target_u: target_u.points = max(0, target_u.points - t.points)
                            t.status = "İptal Edildi"
                            db.commit()
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                        
        with t3:
            st.info("💡 Buradan sildiğiniz kişilerin hesapları ve ona atanmış tüm görevler kalıcı olarak temizlenir.")
            users = db.query(User).filter(User.username != cu.username).all()
            for u in users:
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{u.username}**<br><span style='font-size:0.8rem; color:#6b7280;'>{u.role} | {u.alan}</span>", unsafe_allow_html=True)
                with c2:
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button("🗑 Sil", key=f"d_{u.id}"):
                        db.query(Task).filter(Task.assigned_to == u.username).delete()
                        db.delete(u)
                        db.commit()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            
            st.divider()
            st.markdown("#### ⚠️ SİSTEMİ SIFIRLAMA")
            st.warning("Aşağıdaki buton sistemdeki **TÜM GÖREVLERİ ve PUANLARI** sıfırlar. Üyelerin kayıtları SİLİNMEZ. Bu işlemin geri dönüşü yoktur!")
            if st.button("🚨 TÜM GÖREVLERİ VE PUANLARI SIFIRLA", type="primary"):
                # Sadece görevleri sil
                db.query(Task).delete()
                # Herkesin puanını sıfırla (üyeleri silme)
                db.query(User).update({User.points: 0})
                db.commit()
                st.success("Tüm görevler silindi ve puanlar sıfırlandı!")
                time.sleep(1)
                st.rerun()

        with t4: render_leaderboard(db)

    # ── BİRİM BAŞKANI PANELİ ──
    elif cu.role == "Birim Başkanı":
        render_stats(cu.username)
        t1, t2, t3, t4 = st.tabs(["📋 Görevlerim", "📌 Ata", "👁️ Verdiklerim", "🏆 Lider"])
        with t1:
            for t in db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all():
                st.markdown(f'<div class="task-card"><div class="task-title">📌 {t.title}</div><div class="task-meta">{t.description}</div><span class="badge {BADGE.get(t.priority)}">{t.priority}</span> ⭐ {t.points}</div>', unsafe_allow_html=True)
                if st.button("✔ Tamamla", key=f"bb_{t.id}"):
                    t.status, cu.points = "Tamamlandı", cu.points + t.points
                    db.commit(); push_notification("Tebrikler! 🎉", f"'{t.title}' tamamlandı."); st.rerun()
        with t2:
            members = db.query(User).filter(User.role == "Üye").all()
            if not members: st.info("Sistemde üye bulunmuyor.")
            else:
                assigned_to = st.selectbox("Üye Seç", [f"{u.username} ({u.alan})" for u in members]).split(" ")[0]
                tt, td = st.text_input("Başlık"), st.text_area("Açıklama")
                c1, c2 = st.columns(2)
                with c1: tp = st.selectbox("Öncelik", ["Acil","Yüksek","Orta","Düşük"])
                with c2: tpts = st.number_input("Puan", min_value=1, value=10)
                t_due = st.date_input("Son Tarih", value=date.today() + timedelta(days=7))
                if st.button("🚀 Görevi Gönder"):
                    db.add(Task(assigned_to=assigned_to, assigned_by=cu.username, title=tt, description=td, priority=tp, points=tpts, status="Bekliyor", due_date=str(t_due)))
                    db.commit()
                    target = db.query(User).filter(User.username==assigned_to).first()
                    if target and target.email: trigger_background_email(target.email, tt, td, tp, tpts, str(t_due))
                    push_notification("Görev Atandı ✅", f"'{tt}' -> {assigned_to}")
                    st.success("Görev atandı!")
        with t3:
            for t in db.query(Task).filter(Task.assigned_by==cu.username).order_by(Task.id.desc()).limit(20).all():
                st.write(f"**{t.title}** -> *{t.assigned_to}* ({t.status})")
        with t4: render_leaderboard(db)

    # ── ÜYE PANELİ ──
    else:
        render_stats(cu.username)
        t1, t2, t3 = st.tabs(["📋 Görevlerim", "✅ Tamamlananlar", "🏆 Liderlik"])
        with t1:
            tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all()
            if not tasks: st.markdown('<div style="text-align:center;padding:2rem;"><div style="font-size:3rem;">🎉</div><b>Bekleyen görevin yok!</b></div>', unsafe_allow_html=True)
            for t in tasks:
                due_label = f"| Son: {t.due_date}" if t.due_date else ""
                st.markdown(f'<div class="task-card"><div class="task-title">📌 {t.title}</div><div class="task-meta">{t.description}</div><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;"><span class="badge {BADGE.get(t.priority)}">{t.priority}</span> <span style="font-size:0.72rem;color:#5a7a76;">⭐ {t.points} puan {due_label}</span></div></div>', unsafe_allow_html=True)
                col_a, col_b = st.columns([3, 2])
                with col_a:
                    if st.button("✔ Tamamla", key=f"u_{t.id}"):
                        t.status, cu.points = "Tamamlandı", cu.points + t.points
                        db.commit(); push_notification("Tebrikler! 🎉", f"'{t.title}' tamamlandı."); st.rerun()
                with col_b:
                    if t.due_date:
                        ics = make_ics(t.title, t.description or "", t.due_date)
                        st.download_button(label="📅 Takvim", data=ics, file_name=f"arder_{t.id}.ics", mime="text/calendar", key=f"ics_{t.id}")
        with t2:
            done_tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Tamamlandı").order_by(Task.id.desc()).limit(20).all()
            if done_tasks:
                for t in done_tasks: st.markdown(f"""<div class="task-card done"><div class="task-title">✅ {t.title}</div><div class="task-meta" style="color:#2DB5A0;">+{t.points} puan kazanıldı</div></div>""", unsafe_allow_html=True)
            else: st.info("Henüz tamamlanan görev yok.")

        with t3: render_leaderboard(db)

db.close()
