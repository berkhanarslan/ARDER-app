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

# ══════════════════════════════════════════════════════════
# 1. SAYFA YAPISI
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ARDER",
    page_icon="🦚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════
# 2. PWA MANİFEST + META ETİKETLER
# ══════════════════════════════════════════════════════════
_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="100" fill="#1A2744"/>
  <text x="256" y="370" text-anchor="middle" font-size="340" font-weight="900"
        fill="#2DB5A0" font-family="Arial,sans-serif">A</text>
  <text x="256" y="460" text-anchor="middle" font-size="68" font-weight="700"
        fill="#1976D2" font-family="Arial,sans-serif">ARDER</text>
</svg>"""
_ICON_B64  = base64.b64encode(_ICON_SVG.encode()).decode()
_ICON_URI  = f"data:image/svg+xml;base64,{_ICON_B64}"

_manifest  = {
    "name":             "ARDER - Akademik Renkler Derneği",
    "short_name":       "ARDER",
    "description":      "Akademik Renkler Derneği Görev Yönetim Sistemi",
    "start_url":        "/",
    "display":          "standalone",
    "background_color": "#f0f7f6",
    "theme_color":      "#1A2744",
    "orientation":      "portrait-primary",
    "icons": [
        {"src": _ICON_URI, "sizes": "192x192", "type": "image/svg+xml", "purpose": "any maskable"},
        {"src": _ICON_URI, "sizes": "512x512", "type": "image/svg+xml", "purpose": "any maskable"},
    ]
}
_mf_b64 = base64.b64encode(json.dumps(_manifest).encode()).decode()

st.markdown(f"""
<link rel="manifest" href="data:application/manifest+json;base64,{_mf_b64}">
<meta name="mobile-web-app-capable"          content="yes">
<meta name="apple-mobile-web-app-capable"    content="yes">
<meta name="apple-mobile-web-app-title"      content="ARDER">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="{_ICON_URI}">
<meta name="application-name"  content="ARDER">
<meta name="theme-color"       content="#1A2744">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 3. BİLDİRİM İZNİ (Uygulama İçi)
# ══════════════════════════════════════════════════════════
components.html("""
<script>
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
</script>
""", height=0)

# ══════════════════════════════════════════════════════════
# 4. CSS  (Mobil 500px + ARDER renk paleti)
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
.main .block-container { max-width:500px; margin:auto; padding:1rem; }
[data-testid="stAppViewContainer"] { background-color:#f0f7f6; }
[data-testid="stHeader"]           { background:transparent; }
[data-testid="stSidebar"] { background:#1A2744; }
[data-testid="stSidebar"] * { color:#f0f7f6 !important; }
[data-testid="stSidebar"] .stButton>button {
    background:#2DB5A0 !important; color:#1A2744 !important;
    font-weight:700 !important; border-radius:8px !important;
}
.app-header {
    background:linear-gradient(135deg,#1A2744 0%,#1976D2 55%,#2DB5A0 100%);
    border-radius:16px; padding:0.85rem 1rem;
    margin-bottom:1rem; display:flex; align-items:center; gap:0.8rem;
}
.app-header .brand-name { font-size:1.25rem; font-weight:900; color:#fff; line-height:1.1; }
.app-header .brand-sub  { font-size:0.72rem; color:rgba(255,255,255,0.75); }
.stat-card {
    background:#fff; border-radius:14px;
    box-shadow:0 4px 16px rgba(26,39,68,0.10);
    padding:1rem 1.2rem; margin:0.3rem 0;
    border-left:4px solid #2DB5A0;
}
.stat-card.blue { border-left-color:#1976D2; }
.stat-card .label { font-size:0.73rem; color:#5a7a76; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; }
.stat-card .value { font-size:1.9rem; font-weight:800; color:#1A2744; }
.task-card {
    background:#fff; border-radius:14px;
    box-shadow:0 3px 12px rgba(26,39,68,0.08);
    padding:1rem; margin-bottom:0.8rem;
    border-bottom:3px solid #2DB5A0;
}
.task-card.done { border-bottom-color:#a0cfcc; opacity:0.82; }
.task-title { font-weight:700; color:#1A2744; font-size:0.97rem; }
.task-meta  { font-size:0.79rem; color:#5a7a76; margin:0.3rem 0; }
.badge { display:inline-block; padding:0.18rem 0.6rem; border-radius:20px; font-size:0.7rem; font-weight:700; }
.badge-acil   { background:#fde8e8; color:#c0392b; }
.badge-yuksek { background:#fff3cd; color:#856404; }
.badge-orta   { background:#d4f1ec; color:#1A5C52; }
.badge-dusuk  { background:#e8f4fd; color:#1565C0; }
div.stButton>button { border-radius:8px !important; font-weight:600 !important; }
div.stButton>button:first-child { background:linear-gradient(90deg,#1A2744,#1976D2) !important; color:#fff !important; border:none !important; }
div.stButton>button:hover { background:linear-gradient(90deg,#2DB5A0,#1976D2) !important; box-shadow:0 4px 14px rgba(45,181,160,0.35) !important; }
div.stDownloadButton>button {
    background:linear-gradient(90deg,#f0f7f6,#d4f1ec) !important; color:#1A5C52 !important; border:1px solid #2DB5A0 !important; font-size:0.82rem !important;
}
[data-testid="stTabs"] button[aria-selected="true"] { color:#1976D2 !important; border-bottom:2px solid #2DB5A0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 5. VERİTABANI  (Supabase / PostgreSQL)
# ══════════════════════════════════════════════════════════
try:
    DB_URL = st.secrets["DB_URL"]
except Exception:
    st.error("⚠️ **DB_URL** bilgisini Streamlit Secrets kısmına ekleyin!")
    st.stop()

engine       = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email    = Column(String, default="") # YENİ: Bildirim E-Postası
    role     = Column(String)
    alan     = Column(String, default="Belirtilmedi")
    points   = Column(Integer, default=0)

class Task(Base):
    __tablename__ = "tasks"
    id          = Column(Integer, primary_key=True, index=True)
    assigned_to = Column(String)
    assigned_by = Column(String)
    title       = Column(String)
    description = Column(String)
    priority    = Column(String)
    points      = Column(Integer, default=10)
    status      = Column(String, default="Bekliyor")
    due_date    = Column(String, default="")

def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS points   INTEGER DEFAULT 10;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS alan     VARCHAR DEFAULT 'Belirtilmedi';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email    VARCHAR DEFAULT '';",
            "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date VARCHAR DEFAULT '';",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass

init_db()

# ══════════════════════════════════════════════════════════
# 6. ARKA PLAN E-POSTA GÖNDERME FONKSİYONU
# ══════════════════════════════════════════════════════════
def send_email_notification(to_email, task_title, task_desc, priority, points, due_date):
    """Görev atandığında kullanıcının Gmail adresine bildirim atar."""
    try:
        sender_email = st.secrets.get("EMAIL_USER", "")
        sender_pass  = st.secrets.get("EMAIL_PASS", "")
        
        if not sender_email or not sender_pass or not to_email:
            return False # Ayarlar eksikse çökmeyi önle, sessizce geç.

        msg = MIMEMultipart()
        msg['From'] = f"ARDER Sistem <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = f"📌 Yeni Görev Atandı: {task_title}"

        body = f"""Merhaba,

ARDER Görev Yönetim Sistemi üzerinden sana yeni bir görev atandı!

📌 Görev: {task_title}
⚡ Öncelik: {priority}
⭐ Puan: {points}
🗓 Son Teslim: {due_date}

Açıklama:
{task_desc if task_desc else 'Açıklama girilmedi.'}

Uygulamaya girerek görevi tamamlayabilirsin.
İyi çalışmalar!
"""
        msg.attach(MIMEText(body, 'plain'))

        # Gmail SMTP Sunucusuna bağlan
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"MAİL HATASI DETAYI: {e}") # Bize hatanın tam nedenini ekrana yazdıracak
        return False

# ══════════════════════════════════════════════════════════
# 7. SESSION STATE & DİĞER FONKSİYONLAR
# ══════════════════════════════════════════════════════════
_defaults = {"logged_in":False,"username":"","role":"","_notif_title":None,"_notif_body":None}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def get_session(): return SessionLocal()

def push_notification(title: str, body: str):
    st.session_state["_notif_title"] = title
    st.session_state["_notif_body"]  = body

def _flush_notification():
    t = st.session_state.get("_notif_title")
    b = st.session_state.get("_notif_body")
    if t and b:
        components.html(f"""
        <script>
        (function(){{
            var title = {json.dumps(t)};
            var body  = {json.dumps(b)};
            var icon  = "{_ICON_URI}";
            if (!('Notification' in window)) return;
            var fn = function() {{ new Notification(title, {{body:body, icon:icon}}); }};
            if (Notification.permission === 'granted') {{ fn(); }}
            else if (Notification.permission !== 'denied') {{
                Notification.requestPermission().then(function(p){{ if (p==='granted') fn(); }});
            }}
        }})();
        </script>
        """, height=0)
        st.session_state["_notif_title"] = None
        st.session_state["_notif_body"]  = None

def make_ics(title: str, description: str, due_date_str: str) -> bytes:
    try: dt = datetime.strptime(due_date_str, "%Y-%m-%d")
    except: dt = datetime.now() + timedelta(days=7)
    dtstart = dt.strftime("%Y%m%d")
    dtend   = (dt + timedelta(days=1)).strftime("%Y%m%d")
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid     = f"{dtstamp}-arder-task@akademikreklerdernegi"
    desc    = (description or "").replace("\n", "\\n").replace(",", "\\,")
    ics = (
        "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ARDER//Gorev Yonetimi//TR\nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\nBEGIN:VEVENT\n"
        f"UID:{uid}\nDTSTAMP:{dtstamp}\nDTSTART;VALUE=DATE:{dtstart}\nDTEND;VALUE=DATE:{dtend}\n"
        f"SUMMARY:📌 {title}\nDESCRIPTION:{desc}\nSTATUS:CONFIRMED\nBEGIN:VALARM\nTRIGGER:-PT1H\n"
        f"ACTION:DISPLAY\nDESCRIPTION:ARDER Hatırlatma: {title}\nEND:VALARM\nEND:VEVENT\nEND:VCALENDAR\n"
    )
    return ics.encode("utf-8")

def logo_html(size=42):
    for ext in ["logo.png","logo.jpg","logo.jpeg"]:
        if os.path.exists(ext):
            with open(ext,"rb") as f: b64 = base64.b64encode(f.read()).decode()
            mime = "image/png" if ext.endswith(".png") else "image/jpeg"
            return f'<img src="data:{mime};base64,{b64}" style="height:{size}px;border-radius:8px;object-fit:contain;">'
    return f'<span style="font-size:{size}px;">🦚</span>'

def render_leaderboard(db):
    users = db.query(User).order_by(User.points.desc()).all()
    html = """
    <style>
    .lb { font-family:sans-serif; padding:8px; }
    .lb-h { color:#1A2744; font-size:19px; font-weight:800; margin-bottom:2px; }
    .lb-s { color:#6b7280; font-size:12px; margin-bottom:18px; }
    .pod  { display:flex; justify-content:center; align-items:flex-end; gap:10px; height:210px; margin-bottom:18px; }
    .pc   { display:flex; flex-direction:column; align-items:center; width:30%; max-width:110px; }
    .av   { width:48px; height:48px; border-radius:8px; margin-bottom:6px; background:linear-gradient(135deg,#1976D2,#2DB5A0); color:#fff; display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:900; }
    .pn   { font-size:11px; font-weight:700; color:#1A2744; text-align:center; }
    .pp   { font-size:10px; color:#9ca3af; margin-bottom:5px; }
    .blk  { width:100%; display:flex; justify-content:center; align-items:flex-start; padding-top:10px; font-weight:700; font-size:15px; border-radius:6px 6px 0 0; color:#fff; }
    .g    { height:140px; background:linear-gradient(135deg,#f59e0b,#d97706); }
    .s    { height:105px; background:#cbd5e1; color:#475569; }
    .b    { height: 80px; background:#d97706; }
    .li   { display:flex; align-items:center; background:#fff; padding:9px 12px; border-radius:10px; margin-bottom:8px; box-shadow:0 2px 8px rgba(26,39,68,0.07); }
    .rb   { width:30px; height:30px; display:flex; justify-content:center; align-items:center; border-radius:6px; font-weight:700; font-size:12px; color:#fff; margin-right:10px; flex-shrink:0; }
    .r1 { background:linear-gradient(135deg,#f59e0b,#d97706); }
    .r2 { background:#cbd5e1; color:#475569; }
    .r3 { background:#d97706; }
    .rx { background:#f1f5f9; color:#64748b; }
    .ln { font-weight:700; color:#1A2744; font-size:13px; }
    .lr { font-size:10px; color:#6b7280; }
    .lp { margin-left:auto; font-weight:800; color:#2DB5A0; font-size:16px; }
    </style>
    <div class='lb'>
      <div class='lb-h'>🏆 Liderlik Tablosu</div>
      <div class='lb-s'>En çok puan kazanan üyeler</div>
    """
    if users:
        u1 = users[0]
        u2 = users[1] if len(users) > 1 else None
        u3 = users[2] if len(users) > 2 else None
        html += "<div class='pod'>"
        html += (f"<div class='pc'><div class='av'>{u2.username[0].upper()}</div><div class='pn'>{u2.username}</div><div class='pp'>{u2.points} puan</div><div class='blk s'>🥈</div></div>") if u2 else "<div class='pc'></div>"
        html += (f"<div class='pc'><div class='av'>{u1.username[0].upper()}</div><div class='pn'>{u1.username}</div><div class='pp'>{u1.points} puan</div><div class='blk g'>🥇</div></div>")
        html += (f"<div class='pc'><div class='av'>{u3.username[0].upper()}</div><div class='pn'>{u3.username}</div><div class='pp'>{u3.points} puan</div><div class='blk b'>🥉</div></div>") if u3 else "<div class='pc'></div>"
        html += "</div>"
        for i, u in enumerate(users):
            r   = i + 1
            rc  = f"r{r}" if r <= 3 else "rx"
            al  = u.alan or "Belirtilmedi"
            html += (f"<div class='li'><div class='rb {rc}'>{r}</div><div class='av' style='width:36px;height:36px;font-size:15px;margin-bottom:0;margin-right:10px;'>{u.username[0].upper()}</div><div><div class='ln'>{u.username}</div><div class='lr'>{u.role} | {al}</div></div><div class='lp'>{u.points}<span style='font-size:9px;color:#9ca3af;'> puan</span></div></div>")
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def show_header():
    st.markdown(f"""
    <div class="app-header">
      {logo_html(46)}
      <div><div class="brand-name">ARDER</div><div class="brand-sub">Akademik Renkler Derneği</div></div>
    </div>
    """, unsafe_allow_html=True)

_flush_notification()
db = get_session()

# ══════════════════════════════════════════════════════════
# 8. GİRİŞ / KAYIT EKRANI
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    show_header()
    st.markdown("#### Görev Yönetim Sistemine Hoş Geldiniz!")
    st.divider()

    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    with tab1:
        lu = st.text_input("Kullanıcı Adı", key="lu")
        lp = st.text_input("Şifre", type="password", key="lp")
        if st.button("Giriş Yap", use_container_width=True):
            user = db.query(User).filter(User.username==lu, User.password==lp).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.username  = user.username
                st.session_state.role      = user.role
                push_notification("ARDER'e Hoş Geldin! 👋", f"Merhaba {user.username}, başarıyla giriş yaptın.")
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")

    with tab2:
        ru   = st.text_input("Kullanıcı Adı", key="ru")
        rmail = st.text_input("Gmail Adresiniz (Bildirimler için)", key="rmail") # YENİ ALAN
        rp   = st.text_input("Şifre", type="password", key="rp")
        role = st.selectbox("Rolünüz", ["Üye","Moderatör"])
        
        if role == "Üye":
            alan = st.selectbox("Alanınız", ["Normal Üye","Sosyal Medya ve Tasarım","İletişim","İnsan Kaynakları","Projeler ve Koordinatörlükler","Etkinlik"])
        else:
            alan = st.selectbox("Yönetim Göreviniz", ["Başkan","Başkan Y.","Sayman","Genel Sekreter"])
            
        if st.button("Kayıt Ol", use_container_width=True):
            if len(ru) < 3 or len(rp) < 3:
                st.warning("Kullanıcı adı ve şifre en az 3 karakter olmalıdır.")
            elif "@" not in rmail:
                st.warning("Lütfen geçerli bir e-posta adresi giriniz.")
            elif db.query(User).filter(User.username==ru).first():
                st.warning("Bu kullanıcı adı alınmış!")
            else:
                db.add(User(username=ru, password=rp, email=rmail, role=role, alan=alan, points=0))
                db.commit()
                st.success("Kayıt başarılı! Giriş yapabilirsiniz.")

# ══════════════════════════════════════════════════════════
# 9. ANA PANEL
# ══════════════════════════════════════════════════════════
else:
    cu = db.query(User).filter(User.username==st.session_state.username).first()

    with st.sidebar:
        st.markdown(f"### 👤 {cu.username}")
        st.markdown(f"**Rol:** {cu.role}")
        st.markdown(f"**Alan:** {cu.alan or '—'}")
        st.markdown(f"**E-Posta:** {cu.email or 'Belirtilmedi'}")
        st.markdown(f"**Puan:** ⭐ {cu.points}")
        st.divider()
        if st.button("🚪 Çıkış Yap"):
            for k in ["logged_in","username","role"]:
                st.session_state[k] = "" if k != "logged_in" else False
            st.rerun()

    show_header()
    BADGE = {"Acil":"badge-acil","Yüksek":"badge-yuksek","Orta":"badge-orta","Düşük":"badge-dusuk"}

    # --- MODERATÖR PANELİ ---
    if st.session_state.role == "Moderatör":
        t1, t2, t3 = st.tabs(["📌 Görev Ata","📋 Tüm Görevler","🏆 Liderlik"])

        with t1:
            st.markdown("#### Yeni Görev Oluştur")
            members   = db.query(User).filter(User.role=="Üye").all()
            user_list = [f"{u.username} ({u.alan or '—'})" for u in members]

            if not user_list:
                st.info("Sistemde kayıtlı üye yok.")
            else:
                sel         = st.selectbox("Görevi Alacak Üye", user_list)
                assigned_to = sel.split(" (")[0]
                ttitle      = st.text_input("Görev Başlığı")
                tdesc       = st.text_area("Açıklama", height=80)
                tprio       = st.selectbox("Öncelik", ["Acil","Yüksek","Orta","Düşük"])
                tpts        = st.number_input("Puan", min_value=1, value=10, step=1)
                tdue        = st.date_input("Son Tarih (Deadline) 🗓", value=date.today() + timedelta(days=7), min_value=date.today())
                
                if st.button("📌 Görevi Ata", use_container_width=True):
                    if not ttitle.strip():
                        st.warning("Görev başlığı boş olamaz.")
                    else:
                        db.add(Task(
                            assigned_to=assigned_to, assigned_by=st.session_state.username,
                            title=ttitle, description=tdesc, priority=tprio, points=tpts,
                            status="Bekliyor", due_date=str(tdue)
                        ))
                        db.commit()
                        
                        # Uygulama içi tarayıcı bildirimi
                        push_notification("Görev Atandı ✅", f"'{ttitle}' → {assigned_to} ({tpts} puan, Son: {tdue})")
                        
                        # Arka Plan E-Posta Gönderimi
                        target_user = db.query(User).filter(User.username==assigned_to).first()
                        if target_user and target_user.email:
                            email_sent = send_email_notification(target_user.email, ttitle, tdesc, tprio, tpts, str(tdue))
                            if email_sent:
                                st.success(f"✅ Görev atandı ve {target_user.username} kişisine e-posta bildirimi gönderildi!")
                            else:
                                st.warning(f"✅ Görev atandı ancak e-posta gönderilemedi (Sunucu ayarları eksik olabilir).")
                        else:
                            st.success(f"✅ Görev '{assigned_to}' adlı üyeye atandı!")

        with t2:
            st.markdown("#### Tüm Görevler")
            all_t = db.query(Task).all()
            if all_t:
                df = pd.DataFrame(
                    [[t.id, t.assigned_to, t.title, t.priority, t.points, t.status, t.due_date or "—", t.assigned_by] for t in all_t],
                    columns=["ID","Atanan","Görev","Öncelik","Puan","Durum","Son Tarih","Atayan"]
                )
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Henüz görev yok.")

        with t3:
            render_leaderboard(db)

    # --- ÜYE PANELİ ---
    elif st.session_state.role == "Üye":
        pending_n   = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").count()
        completed_n = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Tamamlandı").count()

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"""<div class="stat-card"><div class="label">⭐ Puan</div><div class="value">{cu.points}</div></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="stat-card blue"><div class="label">📋 Bekleyen</div><div class="value">{pending_n}</div></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="stat-card" style="border-left-color:#1976D2"><div class="label">✅ Tamam</div><div class="value">{completed_n}</div></div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:0.6rem'></div>", unsafe_allow_html=True)
        u1, u2, u3 = st.tabs(["📋 Görevlerim","✅ Tamamlananlar","🏆 Liderlik"])

        with u1:
            my_tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Bekliyor").all()
            if not my_tasks:
                st.markdown("""<div style="text-align:center;padding:2rem 0;color:#5a7a76;">
                  <div style="font-size:3rem;">🎉</div><div style="font-weight:700;margin-top:0.5rem;">Bekleyen göreviniz yok!</div>
                </div>""", unsafe_allow_html=True)
            else:
                for t in my_tasks:
                    bc  = BADGE.get(t.priority, "badge-orta")
                    due = t.due_date or ""
                    days_left = None
                    if due:
                        try:
                            d = datetime.strptime(due, "%Y-%m-%d").date()
                            days_left = (d - date.today()).days
                        except: pass

                    due_label = ""
                    if days_left is not None:
                        if days_left < 0: due_label = f"⛔ {abs(days_left)} gün geçti"
                        elif days_left == 0: due_label = "🔴 Bugün son gün!"
                        elif days_left <= 2: due_label = f"🟠 {days_left} gün kaldı"
                        else: due_label = f"🗓 {days_left} gün kaldı ({due})"

                    st.markdown(f"""
                    <div class="task-card">
                      <div class="task-title">📌 {t.title}</div>
                      <div class="task-meta">{t.description or "—"}</div>
                      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                        <span class="badge {bc}">{t.priority}</span>
                        <span style="font-size:0.72rem;color:#5a7a76;">⭐ {t.points} puan &nbsp;|&nbsp; {due_label}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_a, col_b = st.columns([3, 2])
                    with col_a:
                        if st.button("✔ Tamamla", key=f"done_{t.id}"):
                            t.status    = "Tamamlandı"
                            cu.points  += t.points
                            db.commit()
                            push_notification("Tebrikler! 🎉", f"'{t.title}' tamamlandı. +{t.points} puan kazandın!")
                            st.rerun()
                    with col_b:
                        if due:
                            ics = make_ics(t.title, t.description or "", due)
                            st.download_button(label="📅 Takvime Ekle", data=ics, file_name=f"arder_{t.id}.ics", mime="text/calendar", key=f"ics_{t.id}")

        with u2:
            done_tasks = db.query(Task).filter(Task.assigned_to==cu.username, Task.status=="Tamamlandı").all()
            if done_tasks:
                for t in done_tasks:
                    st.markdown(f"""
                    <div class="task-card done">
                      <div class="task-title">✅ {t.title}</div><div class="task-meta" style="color:#2DB5A0;">+{t.points} puan kazanıldı</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Henüz tamamlanan görev yok.")

        with u3:
            render_leaderboard(db)

db.close()
