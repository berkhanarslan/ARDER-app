import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker

# --- 1. AYARLAR VE VERİTABANI BAĞLANTISI ---
st.set_page_config(page_title="ARDER Görev Yönetimi", layout="wide")

# Supabase Bağlantısı (Secrets'tan çekiliyor)
try:
    DB_URL = st.secrets["DB_URL"]
except:
    st.error("Lütfen Streamlit Secrets kısmına DB_URL bilginizi ekleyin!")
    st.stop()

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. VERİTABANI MODELLERİ ---
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String) # Moderatör veya Üye
    points = Column(Integer, default=0)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    assigned_to = Column(String)
    assigned_by = Column(String)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    points = Column(Integer, default=10)
    status = Column(String, default="Bekliyor") # Bekliyor veya Tamamlandı

# --- 3. VERİTABANI BAŞLATMA VE GÜNCELLEME ---
def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 10;"))
            conn.commit()
    except Exception as e:
        pass 

init_db()

# --- 4. OTURUM (SESSION) YÖNETİMİ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""

def get_session():
    return SessionLocal()

# --- LOGO VE BAŞLIK GÖSTERİM FONKSİYONU ---
def show_header():
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        try:
            # Dosya adını logo.jpg olarak güncelledik
            st.image("logo.jpg", width=70)
        except:
            pass 
    with col_title:
        st.header("Akademik Renkler Derneği")

# --- ÖZEL LİDERLİK TABLOSU TASARIMI (HTML/CSS) ---
def render_custom_leaderboard(db):
    all_users = db.query(User).order_by(User.points.desc()).all()
    
    html = """
    <style>
    .lb-container { font-family: sans-serif; background-color: #ffffff; padding: 20px; }
    .lb-title-wrap { display: flex; align-items: center; margin-bottom: 5px; }
    .lb-icon { font-size: 28px; margin-right: 10px; color: #0f766e; }
    .lb-title { color:#1e3a8a; margin-bottom:0; font-size: 24px; font-weight: bold; }
    .lb-subtitle { color:#6b7280; margin-top:0; margin-bottom: 30px; font-size: 14px; }
    
    .podium-wrapper { display: flex; justify-content: center; align-items: flex-end; gap: 10px; height: 230px; margin-bottom: 20px; }
    .podium-col { display: flex; flex-direction: column; align-items: center; width: 30%; max-width: 120px; }
    
    .avatar { width: 55px; height: 55px; background-color: #0d9488; color: white; display: flex; justify-content: center; align-items: center; font-size: 24px; font-weight: bold; margin-bottom: 8px; border-radius: 4px; }
    .name { font-size: 14px; font-weight: bold; color: #1e3a8a; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
    .pts { font-size: 12px; color: #9ca3af; margin-bottom: 8px; }
    
    .block { width: 100%; display: flex; justify-content: center; padding-top: 15px; color: white; font-weight: bold; font-size: 18px; border-radius: 4px 4px 0 0; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .block.silver { height: 110px; background: #cbd5e1; }
    .block.gold { height: 150px; background: #eab308; }
    .block.bronze { height: 90px; background: #d97706; }
    
    .list-wrapper { display: flex; flex-direction: column; gap: 15px; padding: 15px; border-radius: 4px; border: 1px solid #f3f4f6; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); }
    .list-item { display: flex; align-items: center; padding-bottom: 15px; border-bottom: 1px solid #f3f4f6; }
    .list-item:last-child { border-bottom: none; padding-bottom: 0; }
    
    .rank-box { width: 35px; height: 35px; display: flex; justify-content: center; align-items: center; font-weight: bold; color: white; margin-right: 15px; border-radius: 4px; font-size: 14px;}
    .rank-1 { background-color: #eab308; }
    .rank-2 { background-color: #cbd5e1; color: #475569; }
    .rank-3 { background-color: #d97706; }
    .rank-other { background-color: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
    
    .list-info { flex-grow: 1; display: flex; flex-direction: column; justify-content: center;}
    .list-name { font-weight: bold; color: #1e3a8a; font-size: 15px;}
    .list-role { font-size: 12px; color: #6b7280; }
    .list-points-wrap { display: flex; flex-direction: column; align-items: flex-end; justify-content: center;}
    .list-points { font-weight: bold; color: #0d9488; font-size: 18px; line-height: 1;}
    .pts-label { font-size: 11px; color: #9ca3af; margin-top: 2px;}
    </style>
    
    <div class='lb-container'>
        <div class='lb-title-wrap'>
            <div class='lb-icon'>🏆</div>
            <div class='lb-title'>Liderlik Tablosu</div>
        </div>
        <div class='lb-subtitle'>En çok puan kazanan üyeler</div>
    """
    
    if len(all_users) >= 1:
        u1 = all_users[0]
        u2 = all_users[1] if len(all_users) > 1 else None
        u3 = all_users[2] if len(all_users) > 2 else None

        html += "<div class='podium-wrapper'>"
        
        # Gümüş (2. Sıra)
        if u2:
            html += f"<div class='podium-col'><div class='avatar'>{u2.username[0].upper()}</div><div class='name'>{u2.username}</div><div class='pts'>{u2.points} pts</div><div class='block silver'>🥈 2</div></div>"
        else:
            html += "<div class='podium-col'></div>"
            
        # Altın (1. Sıra)
        html += f"<div class='podium-col'><div class='avatar'>{u1.username[0].upper()}</div><div class='name'>{u1.username}</div><div class='pts'>{u1.points} pts</div><div class='block gold'>🥇 1</div></div>"
        
        # Bronz (3. Sıra)
        if u3:
            html += f"<div class='podium-col'><div class='avatar'>{u3.username[0].upper()}</div><div class='name'>{u3.username}</div><div class='pts'>{u3.points} pts</div><div class='block bronze'>🥉 3</div></div>"
        else:
            html += "<div class='podium-col'></div>"
            
        html += "</div>"
        
    if len(all_users) > 0:
        html += "<div class='list-wrapper'>"
        for i, u in enumerate(all_users):
            r = i + 1
            rc = f"rank-{r}" if r <= 3 else "rank-other"
            html += f"""
            <div class='list-item'>
                <div class='rank-box {rc}'>{r}</div>
                <div class='avatar' style='width:45px; height:45px; font-size:18px; margin-bottom:0; margin-right:15px;'>{u.username[0].upper()}</div>
                <div class='list-info'>
                    <span class='list-name'>{u.username}</span>
                    <span class='list-role'>{u.role}</span>
                </div>
                <div class='list-points-wrap'>
                    <div class='list-points'>{u.points}</div>
                    <div class='pts-label'>puan</div>
                </div>
            </div>
            """
        html += "</div>"
        
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# --- 5. ARAYÜZ VE FONKSİYONLAR ---
db = get_session()

# GİRİŞ VE KAYIT EKRANI
if not st.session_state.logged_in:
    show_header()
    st.write("Görev Yönetim Sistemine Merhaba!")
    st.divider()
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        st.subheader("Kullanıcı Girişi")
        login_user = st.text_input("Kullanıcı Adı", key="login_user")
        login_pass = st.text_input("Şifre", type="password", key="login_pass")
        
        if st.button("Giriş"):
            user = db.query(User).filter(User.username == login_user, User.password == login_pass).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")

    with tab2:
        st.subheader("Yeni Hesap Oluştur")
        reg_user = st.text_input("Belirleyeceğiniz Kullanıcı Adı", key="reg_user")
        reg_pass = st.text_input("Şifre Belirleyin", type="password", key="reg_pass")
        reg_role = st.selectbox("Rolünüz", ["Üye", "Moderatör"])
        
        if st.button("Kayıt Ol"):
            existing_user = db.query(User).filter(User.username == reg_user).first()
            if existing_user:
                st.warning("Bu kullanıcı adı zaten alınmış!")
            elif len(reg_user) < 3 or len(reg_pass) < 3:
                st.warning("Kullanıcı adı ve şifre en az 3 karakter olmalıdır.")
            else:
                new_user = User(username=reg_user, password=reg_pass, role=reg_role, points=0)
                db.add(new_user)
                db.commit()
                st.success("Kayıt başarılı! Lütfen 'Giriş Yap' sekmesinden giriş yapın.")

# ANA PANEL (GİRİŞ YAPILDIKTAN SONRA)
else:
    with st.sidebar:
        st.title("👤 Profilim")
        st.write(f"**Kullanıcı:** {st.session_state.username}")
        st.write(f"**Rol:** {st.session_state.role}")
        
        current_user = db.query(User).filter(User.username == st.session_state.username).first()
        st.write(f"**Puan:** {current_user.points}")
        
        st.divider()
        if st.button("🚪 Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

    show_header()
    st.divider()

    # MODERATÖR PANELİ
    if st.session_state.role == "Moderatör":
        tab_mod1, tab_mod2, tab_mod3 = st.tabs(["Görev Ata", "Tüm Görevler", "Liderlik Tablosu"])
        
        with tab_mod1:
            st.subheader("Yeni Görev Oluştur")
            users = db.query(User).filter(User.role == "Üye").all()
            user_list = [u.username for u in users]
            
            if not user_list:
                st.info("Sistemde henüz kayıtlı 'Üye' bulunmuyor. Görev atamak için üyelerin kayıt olmasını bekleyin.")
            else:
                assigned_to = st.selectbox("Görevi Alacak Üye", user_list)
                task_title = st.text_input("Görev Başlığı")
                task_desc = st.text_area("Görev Açıklaması")
                task_priority = st.selectbox("Öncelik", ["Düşük", "Orta", "Yüksek", "Acil"])
                task_points = st.number_input("Bu görevin puanı ne kadar olsun?", min_value=1, value=10, step=1)
                
                if st.button("Görevi Ata"):
                    if task_title:
                        new_task = Task(
                            assigned_to=assigned_to,
                            assigned_by=st.session_state.username,
                            title=task_title,
                            description=task_desc,
                            priority=task_priority,
                            points=task_points,
                            status="Bekliyor"
                        )
                        db.add(new_task)
                        db.commit()
                        st.success(f"Görev '{assigned_to}' adlı üyeye başarıyla atandı! ({task_points} Puan)")
                    else:
                        st.warning("Lütfen görev başlığını girin.")

        with tab_mod2:
            st.subheader("Sistemdeki Tüm Görevler")
            all_tasks = db.query(Task).all()
            if all_tasks:
                task_data = []
                for t in all_tasks:
                    task_data.append([t.id, t.assigned_to, t.title, t.priority, t.points, t.status, t.assigned_by])
                df = pd.DataFrame(task_data, columns=["ID", "Atanan Kişi", "Görev", "Öncelik", "Puan", "Durum", "Atayan"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Henüz oluşturulmuş bir görev yok.")

        with tab_mod3:
            render_custom_leaderboard(db)

    # ÜYE PANELİ
    elif st.session_state.role == "Üye":
        tab_uye1, tab_uye2 = st.tabs(["Görevlerim", "Liderlik Tablosu"])
        
        with tab_uye1:
            st.subheader("Bana Atanan Görevler")
            my_tasks = db.query(Task).filter(Task.assigned_to == st.session_state.username, Task.status == "Bekliyor").all()
            
            if not my_tasks:
                st.success("Harika! Bekleyen hiçbir göreviniz yok. 🎉")
            else:
                for t in my_tasks:
                    with st.expander(f"📌 {t.title} - Öncelik: {t.priority} ({t.points} Puan)"):
                        st.write(f"**Açıklama:** {t.description}")
                        st.write(f"**Atayan Moderatör:** {t.assigned_by}")
                        
                        if st.button(f"Görevi Tamamla (ID: {t.id})", key=f"btn_{t.id}"):
                            t.status = "Tamamlandı"
                            current_user.points += t.points 
                            db.commit()
                            st.success(f"Tebrikler! Görevi tamamladınız ve {t.points} puan kazandınız!")
                            st.rerun()

            st.divider()
            st.subheader("Tamamladığım Görevler")
            completed_tasks = db.query(Task).filter(Task.assigned_to == st.session_state.username, Task.status == "Tamamlandı").all()
            if completed_tasks:
                for c in completed_tasks:
                    st.write(f"✅ {c.title} *(+{c.points} Puan)*")
            else:
                st.info("Henüz tamamladığınız bir görev yok.")

        with tab_uye2:
            render_custom_leaderboard(db)

db.close()
