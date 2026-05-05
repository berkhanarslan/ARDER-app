import streamlit as st
import sqlite3
import hashlib
import os
from datetime import date

# ─────────────────────────────────────────────
# SAYFA YAPISI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Akademik Renkler Derneği",
    page_icon="🦚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# RENK PALETİ  (logo'dan alındı)
# --primary-teal : #2DB5A0   (tavuskuşu teal)
# --primary-blue : #1976D2   (A harfi mavi)
# --primary-dark : #1A2744   (koyu lacivert metin)
# --bg           : #f0f7f6   (açık teal-beyaz)
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Mobil kapsayıcı */
.main .block-container {
    max-width: 500px;
    margin: auto;
    padding: 1rem;
}

/* Arka plan */
[data-testid="stAppViewContainer"] {
    background-color: #f0f7f6;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Giriş kartı ── */
.login-card {
    background: #ffffff;
    border-radius: 20px;
    box-shadow: 0 8px 36px rgba(29,118,131,0.15);
    padding: 2rem 1.5rem 1.5rem 1.5rem;
    margin: 1.5rem 0;
}

/* ── Stat kartları ── */
.stat-card {
    background: #ffffff;
    border-radius: 15px;
    box-shadow: 0 4px 18px rgba(29,118,131,0.10);
    padding: 1rem 1.2rem;
    margin: 0.3rem 0;
    border-left: 4px solid #1A2744;
}
.stat-card.teal  { border-left-color: #2DB5A0; }
.stat-card.blue  { border-left-color: #1976D2; }
.stat-card .label {
    font-size: 0.78rem;
    color: #5a7a76;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.stat-card .value {
    font-size: 2rem;
    font-weight: 800;
    color: #1A2744;
    line-height: 1.2;
}

/* ── Görev kartları ── */
.task-card {
    background: #ffffff;
    border-radius: 14px;
    box-shadow: 0 3px 14px rgba(29,118,131,0.09);
    padding: 1rem 1.1rem 0.7rem 1.1rem;
    margin-bottom: 0.8rem;
    border-bottom: 3px solid #2DB5A0;
}
.task-title { font-size: 1rem; font-weight: 700; color: #1A2744; }
.task-desc  { font-size: 0.85rem; color: #495057; margin: 0.3rem 0 0.5rem 0; }

/* ── Öncelik etiketleri ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.badge-critical { background: #fde8e8; color: #c0392b; }
.badge-high     { background: #fff3cd; color: #856404; }
.badge-medium   { background: #d4f1ec; color: #1A5C52; }

/* ── Header ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #1A2744 0%, #1976D2 60%, #2DB5A0 100%);
    border-radius: 16px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    color: #ffffff;
}
.app-header .brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 800;
    font-size: 0.95rem;
    color: #ffffff;
    line-height: 1.2;
}
.app-header .brand small {
    display: block;
    font-size: 0.68rem;
    font-weight: 400;
    opacity: 0.8;
}
.app-header .user-info {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.8);
    text-align: right;
}
.app-header .user-info b { color: #a0e8df; }

/* ── Liderlik tablosu ── */
.lb-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
    border-radius: 10px;
    padding: 0.55rem 0.9rem;
    margin-bottom: 0.4rem;
    box-shadow: 0 2px 8px rgba(29,118,131,0.08);
}
.lb-rank { font-size: 1.1rem; font-weight: 800; color: #2DB5A0; width: 2rem; }
.lb-name { font-weight: 600; color: #1A2744; flex: 1; margin-left: 0.5rem; }
.lb-unit { font-size: 0.78rem; color: #6c757d; flex: 1; }
.lb-pts  { font-weight: 800; color: #1976D2; font-size: 1rem; }

/* ── Butonlar ── */
div.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:first-child {
    background: linear-gradient(90deg, #1A2744, #1976D2) !important;
    color: #ffffff !important;
    border: none !important;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, #2DB5A0, #1976D2) !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(45,181,160,0.35) !important;
}

/* ── Profil kartı ── */
.profile-card {
    background: #fff;
    border-radius: 15px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 4px 18px rgba(29,118,131,0.09);
    margin-bottom: 0.8rem;
}
.profile-row {
    display: flex;
    justify-content: space-between;
    padding: 0.4rem 0;
    border-bottom: 1px solid #e8f5f3;
    font-size: 0.9rem;
}
.profile-row:last-child { border-bottom: none; }
.profile-label { color: #5a7a76; font-weight: 600; }
.profile-val   { color: #1A2744; font-weight: 700; }

/* ── Başlık yardımcıları ── */
.center-title {
    text-align: center;
    color: #1A2744;
    font-size: 1.4rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
}

/* ── Giriş ekranı logo alanı ── */
.login-logo-area {
    text-align: center;
    margin-bottom: 1.2rem;
}
.login-logo-area .brand-name {
    font-size: 1.3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #1A2744, #1976D2, #2DB5A0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-top: 0.5rem;
}
.login-logo-area .brand-sub {
    font-size: 0.8rem;
    color: #5a7a76;
    margin-top: 0.1rem;
}

/* ── Sekme renkleri ── */
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #1976D2 !important;
    border-bottom: 2px solid #2DB5A0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VERİTABANI
# ─────────────────────────────────────────────
DB = "akademik_renkler.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'ÜYE',
            unit     TEXT,
            points   INTEGER NOT NULL DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            assigned_to TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'Bekliyor',
            priority    TEXT NOT NULL DEFAULT 'Orta',
            date        TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def get_user(email: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row

def register_user(name, email, password, role, unit):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name,email,password,role,unit,points) VALUES (?,?,?,?,?,0)",
            (name, email, hash_pw(password), role, unit)
        )
        conn.commit()
        return True, "Kayıt başarılı! Giriş yapabilirsiniz."
    except sqlite3.IntegrityError:
        return False, "Bu e-posta zaten kayıtlı."
    finally:
        conn.close()

def get_pending_tasks(email: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM tasks WHERE assigned_to=? AND status='Bekliyor' ORDER BY date DESC",
        (email,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def complete_task(task_id: int, email: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE tasks SET status='Tamamlandı' WHERE id=?", (task_id,))
    c.execute("UPDATE users SET points = points + 10 WHERE email=?", (email,))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, unit, points FROM users ORDER BY points DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_members():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, email FROM users WHERE role='ÜYE'")
    rows = c.fetchall()
    conn.close()
    return rows

def assign_task(title, desc, priority, assigned_to):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title,description,assigned_to,status,priority,date) VALUES (?,?,?,'Bekliyor',?,?)",
        (title, desc, assigned_to, priority, str(date.today()))
    )
    conn.commit()
    conn.close()

def count_pending(email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='Bekliyor'", (email,))
    n = c.fetchone()[0]
    conn.close()
    return n

# ─────────────────────────────────────────────
# LOGO YARDIMCISI
# ─────────────────────────────────────────────
def get_logo_b64():
    import base64
    for ext in ["logo.png", "logo.jpg", "logo.jpeg"]:
        if os.path.exists(ext):
            with open(ext, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            mime = "image/png" if ext.endswith(".png") else "image/jpeg"
            return f'<img src="data:{mime};base64,{data}" style="height:{{size}}px; border-radius:6px; object-fit:contain;">'
    return None

LOGO_TPL = get_logo_b64()

def logo_html(size=35):
    if LOGO_TPL:
        return LOGO_TPL.replace("{size}", str(size))
    return f'<span style="font-size:{size}px; line-height:1;">🦚</span>'

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "page"      not in st.session_state: st.session_state["page"]      = "login"
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "user"      not in st.session_state: st.session_state["user"]      = None

# ─────────────────────────────────────────────
# BADGE
# ─────────────────────────────────────────────
PRIORITY_CLASS = {"Kritik": "badge-critical", "Yüksek": "badge-high", "Orta": "badge-medium"}

def badge(priority):
    cls = PRIORITY_CLASS.get(priority, "badge-medium")
    return f'<span class="badge {cls}">{priority}</span>'

# ─────────────────────────────────────────────
# EKRAN 1: GİRİŞ / KAYIT
# ─────────────────────────────────────────────
def page_login():
    st.markdown(f"""
    <div class="login-card">
      <div class="login-logo-area">
        {logo_html(90)}
        <div class="brand-name">AKADEMİK RENKLER DERNEĞİ</div>
        <div class="brand-sub">Yönetim Sistemi</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Giriş Yap", "📝 Yeni Üye Kaydı"])

    with tab_login:
        email    = st.text_input("E-posta", placeholder="ornek@mail.com", key="li_email")
        password = st.text_input("Şifre", type="password", key="li_pw")
        if st.button("Giriş Yap", use_container_width=True, key="btn_login"):
            if not email or not password:
                st.warning("Lütfen e-posta ve şifrenizi girin.")
            else:
                user = get_user(email.strip().lower())
                if user and user[3] == hash_pw(password):
                    st.session_state["logged_in"] = True
                    st.session_state["user"]      = user
                    st.session_state["page"]      = "dashboard"
                    st.rerun()
                else:
                    st.error("E-posta veya şifre hatalı.")

    with tab_register:
        r_name  = st.text_input("Adınız Soyadınız", key="r_name")
        r_email = st.text_input("E-posta", placeholder="ornek@mail.com", key="r_email")
        r_pw    = st.text_input("Şifre", type="password", key="r_pw")
        r_pw2   = st.text_input("Şifre Tekrar", type="password", key="r_pw2")
        r_unit  = st.selectbox(
            "Birim",
            ["Eğitim", "Proje", "İletişim", "Organizasyon", "Finans", "Teknik"],
            key="r_unit"
        )
        r_role  = st.selectbox("Rol", ["ÜYE", "MODERATÖR"], key="r_role")
        if st.button("Kayıt Ol", use_container_width=True, key="btn_register"):
            if not all([r_name, r_email, r_pw, r_pw2]):
                st.warning("Tüm alanları doldurunuz.")
            elif r_pw != r_pw2:
                st.error("Şifreler eşleşmiyor.")
            elif len(r_pw) < 6:
                st.error("Şifre en az 6 karakter olmalıdır.")
            else:
                ok, msg = register_user(
                    r_name.strip(), r_email.strip().lower(), r_pw, r_role, r_unit
                )
                st.success(msg) if ok else st.error(msg)

# ─────────────────────────────────────────────
# EKRAN 2: DASHBOARD
# ─────────────────────────────────────────────
def page_dashboard():
    u = st.session_state["user"]
    uid, uname, uemail, _, urole, uunit, upoints = u

    fresh = get_user(uemail)
    if fresh:
        upoints = fresh[6]
        st.session_state["user"] = fresh

    pending_n = count_pending(uemail)

    # ── HEADER ──
    st.markdown(f"""
    <div class="app-header">
      <div class="brand">
        {logo_html(38)}
        <div>
          AKADEMİK RENKLER
          <small>Derneği</small>
        </div>
      </div>
      <div class="user-info">
        Hoş geldin,<br><b>{uname}</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Çıkış Yap", key="btn_logout"):
        st.session_state.update({"logged_in": False, "user": None, "page": "login"})
        st.rerun()

    # ── İSTATİSTİK KARTLARI ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card teal">
          <div class="label">⭐ Toplam Puanım</div>
          <div class="value">{upoints}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card blue">
          <div class="label">📋 Bekleyen Görev</div>
          <div class="value">{pending_n}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

    # ── SEKMELER ──
    tabs = st.tabs(["📋 Görevlerim", "🏆 Puan Tablosu", "👤 Profilim"])

    # ── GÖREVLERİM ──
    with tabs[0]:
        tasks = get_pending_tasks(uemail)
        if not tasks:
            st.markdown("""
            <div style="text-align:center; padding:2rem 0; color:#5a7a76;">
              <div style="font-size:2.5rem;">✅</div>
              <div style="font-weight:600; margin-top:0.5rem;">Bekleyen göreviniz yok!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for t in tasks:
                tid, ttitle, tdesc, _, _, tpriority, tdate = t
                st.markdown(f"""
                <div class="task-card">
                  <div class="task-title">{ttitle}</div>
                  <div class="task-desc">{tdesc or "—"}</div>
                  <div style="display:flex;align-items:center;justify-content:space-between;">
                    {badge(tpriority)}
                    <span style="font-size:0.75rem;color:#adb5bd;">{tdate or ""}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✔ Tamamlandı olarak işaretle", key=f"done_{tid}"):
                    complete_task(tid, uemail)
                    st.success(f"🎉 '{ttitle}' tamamlandı! +10 puan kazandınız.")
                    st.rerun()

    # ── PUAN TABLOSU ──
    with tabs[1]:
        st.markdown('<div class="center-title">🏆 Liderlik Tablosu</div>', unsafe_allow_html=True)
        lb = get_leaderboard()
        medals = ["🥇", "🥈", "🥉"]
        for i, (lname, lunit, lpts) in enumerate(lb):
            rank = medals[i] if i < 3 else f"{i+1}."
            # Giriş yapan kullanıcıyı vurgula
            highlight = "border: 2px solid #2DB5A0;" if lname == uname else ""
            st.markdown(f"""
            <div class="lb-row" style="{highlight}">
              <div class="lb-rank">{rank}</div>
              <div class="lb-name">{lname}</div>
              <div class="lb-unit">{lunit or "—"}</div>
              <div class="lb-pts">{lpts} <span style="font-size:0.7rem;color:#adb5bd;">puan</span></div>
            </div>
            """, unsafe_allow_html=True)

    # ── PROFİLİM ──
    with tabs[2]:
        st.markdown(f"""
        <div class="profile-card">
          <div style="text-align:center; margin-bottom:1.2rem;">
            {logo_html(60)}
            <div style="font-weight:800; font-size:1.1rem; color:#1A2744; margin-top:0.6rem;">{uname}</div>
            <div style="font-size:0.82rem; color:#2DB5A0; font-weight:700; margin-top:0.1rem;">{urole}</div>
          </div>
          <div class="profile-row">
            <span class="profile-label">📧 E-posta</span>
            <span class="profile-val">{uemail}</span>
          </div>
          <div class="profile-row">
            <span class="profile-label">🏢 Birim</span>
            <span class="profile-val">{uunit or "—"}</span>
          </div>
          <div class="profile-row">
            <span class="profile-label">👑 Rol</span>
            <span class="profile-val">{urole}</span>
          </div>
          <div class="profile-row">
            <span class="profile-label">⭐ Toplam Puan</span>
            <span class="profile-val" style="color:#1976D2;">{upoints}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── YÖNETİM PANELİ (SADECE MODERATÖR) ──
    if urole == "MODERATÖR":
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        with st.expander("👑 Yönetici Araçları", expanded=False):
            st.markdown("#### 📌 Üyeye Görev Ata")
            members = get_members()
            if not members:
                st.info("Sistemde kayıtlı üye bulunmuyor.")
            else:
                member_opts    = {f"{m[0]} ({m[1]})": m[1] for m in members}
                selected_label = st.selectbox("Üye Seç", list(member_opts.keys()), key="mod_member")
                selected_email = member_opts[selected_label]
                t_title = st.text_input("Görev Başlığı", key="mod_title")
                t_desc  = st.text_area("Görev Açıklaması", key="mod_desc", height=80)
                t_prio  = st.selectbox("Öncelik", ["Kritik", "Yüksek", "Orta"], key="mod_prio")
                if st.button("📌 Görevi Ata", use_container_width=True, key="btn_assign"):
                    if not t_title.strip():
                        st.warning("Görev başlığı boş olamaz.")
                    else:
                        assign_task(t_title.strip(), t_desc.strip(), t_prio, selected_email)
                        st.success(f"✅ Görev '{selected_label}' kişisine atandı!")
                        st.rerun()

# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
if st.session_state["page"] == "login" or not st.session_state["logged_in"]:
    page_login()
else:
    page_dashboard()