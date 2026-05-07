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
    points = Column(Integer, default=10) # YENİ: Görev Puanı Sütunu
    status = Column(String, default="Bekliyor") # Bekliyor veya Tamamlandı

# --- 3. VERİTABANI BAŞLATMA VE GÜNCELLEME ---
def init_db():
    Base.metadata.create_all(bind=engine)
    # Eski tablolara yeni 'points' sütununu otomatik eklemek için güvenlik yaması
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 10;"))
            conn.commit()
    except Exception as e:
        pass # Eğer zaten varsa veya SQLite kullanılıyorsa yoksay

init_db()

# --- 4. OTURUM (SESSION) YÖNETİMİ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""

# Veritabanı oturumu açma/kapatma aracı
def get_session():
    return SessionLocal()

# --- 5. ARAYÜZ VE FONKSİYONLAR ---
db = get_session()

# GİRİŞ VE KAYIT EKRANI
if not st.session_state.logged_in:
    st.title("ARDER Görev Yönetim Sistemine Hoş Geldiniz")
    
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
    # Sol Menü (Sidebar)
    with st.sidebar:
        st.title("👤 Profilim")
        st.write(f"**Kullanıcı:** {st.session_state.username}")
        st.write(f"**Rol:** {st.session_state.role}")
        
        # Güncel Puanı Çekme
        current_user = db.query(User).filter(User.username == st.session_state.username).first()
        st.write(f"**Puan:** {current_user.points}")
        
        st.divider()
        if st.button("🚪 Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

    st.title("ARDER Kontrol Paneli 🚀")

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
                
                # YENİ ÖZELLİK: GÖREV PUANI BELİRLEME
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
            st.subheader("Liderlik Tablosu 🏆")
            all_users = db.query(User).order_by(User.points.desc()).all()
            user_data = []
            for i, u in enumerate(all_users):
                user_data.append([i+1, u.username, u.role, u.points])
            df_users = pd.DataFrame(user_data, columns=["Sıra", "Kullanıcı", "Rol", "Puan"])
            st.dataframe(df_users, use_container_width=True)

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
                            # Görevi tamamlandı olarak işaretle
                            t.status = "Tamamlandı"
                            
                            # Üyeye özel belirlenmiş görev puanını ekle
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
            st.subheader("Liderlik Tablosu 🏆")
            all_users = db.query(User).order_by(User.points.desc()).all()
            user_data = []
            for i, u in enumerate(all_users):
                user_data.append([i+1, u.username, u.role, u.points])
            df_users = pd.DataFrame(user_data, columns=["Sıra", "Kullanıcı", "Rol", "Puan"])
            st.dataframe(df_users, use_container_width=True)

db.close()
