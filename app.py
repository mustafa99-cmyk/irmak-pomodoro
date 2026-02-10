import streamlit as st
import time
import pandas as pd
import random
import os
import json
import csv
import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Irmak Focus RPG Pro", page_icon="🌲", layout="wide")

# --- GÖRSEL TEMİZLİK (HEADER, FOOTER, MENU GİZLEME) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {
                margin-top: -80px; /* Üstteki boşluğu azaltır */
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- AYARLAR VE DOSYA YOLU ---
CSV_DOSYA = "calisma_gecmisi.csv"
VERI_DOSYASI = "irmak_data_v2.json"

# --- CSS: MODERN LACİVERT TEMA VE ANİMASYONLAR ---
st.markdown("""
    <style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #020c1b;
        color: #ccd6f6;
    }
    
    /* Başlıklar */
    h1, h2, h3 {
        color: #64ffda !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Kart Görünümü */
    .css-1r6slb0, .stExpander, div[data-testid="stMetric"] {
        background-color: #112240;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #233554;
    }

    /* Butonlar */
    .stButton>button {
        background-color: #0a192f;
        color: #64ffda;
        border: 1px solid #64ffda;
        border-radius: 5px;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #64ffda;
        color: #0a192f;
        transform: translateY(-2px);
    }

    /* Zen Modu Nefes Egzersizi */
    .zen-circle {
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, #64ffda 0%, #112240 70%);
        border-radius: 50%;
        margin: 0 auto;
        box-shadow: 0 0 20px #64ffda;
        animation: breathe 8s infinite ease-in-out;
    }
    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(2); opacity: 0.9; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ YÖNETİMİ FONKSİYONLARI ---
def veri_dosyalarini_kontrol_et():
    # CSV Hazırlığı
    if not os.path.exists(CSV_DOSYA):
        with open(CSV_DOSYA, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Tarih", "Saat", "Sure_Dakika", "Etiket", "Tur", "Durum"])

    # JSON Hazırlığı (Başlangıç Verisi)
    if not os.path.exists(VERI_DOSYASI):
        baslangic_verisi = {
            "para": 100,
            "xp": 0,
            "level": 1,
            "agaclar": [], 
            "gorevler": [],
            "envanter": ["tree_oak"],
            "secili_agac": "tree_oak"
        }
        with open(VERI_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(baslangic_verisi, f)

def verileri_yukle():
    veri_dosyalarini_kontrol_et()
    with open(VERI_DOSYASI, 'r', encoding='utf-8') as f:
        return json.load(f)

def verileri_kaydet(data):
    with open(VERI_DOSYASI, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def oturum_kaydet(sure, etiket="Genel", durum="Tamamlandi"):
    with open(CSV_DOSYA, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        simdi = datetime.datetime.now()
        writer.writerow([simdi.strftime("%Y-%m-%d"), simdi.strftime("%H:%M"), sure, etiket, "Odak", durum])

# --- SESSION STATE BAŞLATMA ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = verileri_yukle()

# Veri kısayolları (Kod okunabilirliği için)
ud = st.session_state.user_data

# --- AĞAÇ TİPLERİ (MARKET) ---
tree_types = [
    {"id": "tree_oak", "name": "Meşe Ağacı", "price": 0, "icon": "🌳", "desc": "Başlangıç dostun."},
    {"id": "tree_pine", "name": "Çam Ağacı", "price": 250, "icon": "🌲", "desc": "Kışın bile yeşil."},
    {"id": "tree_cactus", "name": "Kaktüs", "price": 500, "icon": "🌵", "desc": "Zorlu şartlara dayanıklı."},
    {"id": "tree_palm", "name": "Palmiye", "price": 750, "icon": "🌴", "desc": "Tropikal odaklanma."},
    {"id": "tree_maple", "name": "Sonbahar", "price": 1000, "icon": "🍁", "desc": "Değişimin güzelliği."},
    {"id": "tree_cherry", "name": "Sakura", "price": 2000, "icon": "🌸", "desc": "Efsanevi güzellik."},
    {"id": "tree_mushroom", "name": "Mantar Ev", "price": 3500, "icon": "🍄", "desc": "Büyülü bir dokunuş."},
    {"id": "tree_crystal", "name": "Kristal", "price": 5000, "icon": "💎", "desc": "Sarsılmaz irade."},
    {"id": "tree_galaxy", "name": "Galaksi Ağacı", "price": 10000, "icon": "🌌", "desc": "Evrensel bilgi."}
]

# --- YAN MENÜ (PROFİL) ---
with st.sidebar:
    st.title("🛡️ Irmak Profil")
    
    # Level Hesabı
    req_xp = ud['level'] * 200
    prog = min(ud['xp'] / req_xp, 1.0)
    
    col_lvl, col_xp = st.columns(2)
    col_lvl.metric("Level", ud['level'])
    col_xp.metric("XP", f"{ud['xp']}/{req_xp}")
    
    st.progress(prog)
    
    st.markdown("---")
    st.metric("💰 Cüzdan", f"{ud['para']} TL")
    
    # Seçili Ağaç Gösterimi
    secili_agac_veri = next((t for t in tree_types if t["id"] == ud["secili_agac"]), tree_types[0])
    st.write(f"**Aktif Ağaç:** {secili_agac_veri['icon']} {secili_agac_veri['name']}")
    
    if st.button("💾 Verileri Kaydet"):
        verileri_kaydet(ud)
        st.toast("Veriler başarıyla kaydedildi!", icon="✅")

# --- ANA SEKMELER ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⏱️ ODAK", "📝 GÖREVLER", "🌲 ORMAN & MARKET", "📊 ANALİZ", "🧘 ZEN & MÜZİK"])

# ---------------- TAB 1: ODAK ZAMANI ----------------
with tab1:
    st.markdown("## ⚡ Odak Modunu Başlat")
    
    col_set1, col_set2, col_set3 = st.columns([1, 1, 1])
    with col_set1:
        focus_time = st.number_input("Odak (Dk)", min_value=1, value=25)
    with col_set2:
        etiket = st.text_input("Etiket (Ders/İş)", value="Genel")
    with col_set3:
        st.write("")
        st.write("")
        start_focus = st.button("🚀 BAŞLAT", use_container_width=True)
    
    if start_focus:
        timer_placeholder = st.empty()
        tree_placeholder = st.empty()
        bar = st.progress(0)
        total_sec = focus_time * 60
        
        # Geri Sayım Döngüsü
        for i in range(total_sec):
            remaining = total_sec - i
            mins, secs = divmod(remaining, 60)
            percentage = (i + 1) / total_sec
            
            # Zaman Göstergesi
            timer_placeholder.markdown(f"""
            <div style="text-align: center; font-size: 80px; font-weight: bold; color: #64ffda; text-shadow: 0 0 10px #64ffda;">
                {mins:02d}:{secs:02d}
            </div>
            """, unsafe_allow_html=True)
            
            # Ağaç Büyüme Animasyonu (Text boyutu ile)
            tree_size = 20 + (percentage * 100)
            tree_placeholder.markdown(f"""
            <div style="text-align: center; font-size: {tree_size}px; transition: font-size 1s;">
                {secili_agac_veri['icon']}
            </div>
            """, unsafe_allow_html=True)
            
            bar.progress(percentage)
            time.sleep(1) 
        
        # Süre Bittiğinde
        earned_money = focus_time * 5  # Dakika başı 5 TL
        earned_xp = focus_time * 10    # Dakika başı 10 XP
        
        ud['para'] += earned_money
        ud['xp'] += earned_xp
        
        # Level Up Kontrol
        if ud['xp'] >= req_xp:
            ud['level'] += 1
            ud['xp'] = 0
            st.balloons()
            st.success(f"TEBRİKLER! LEVEL ATLADIN! YENİ SEVİYE: {ud['level']}")
        
        # Ağacı Ormana Ekle
        ud['agaclar'].append({
            "type_id": ud['secili_agac'],
            "date": str(datetime.datetime.now()),
            "alive": True
        })
        
        # Kayıt İşlemleri
        oturum_kaydet(focus_time, etiket, "Tamamlandi")
        verileri_kaydet(ud)
        
        st.success(f"Oturum Tamamlandı! +{earned_money} TL ve +{earned_xp} XP kazandın!")
        st.rerun()

# ---------------- TAB 2: GÖREVLER ----------------
with tab2:
    st.subheader("📝 Yapılacaklar Listesi")
    
    c_input, c_btn = st.columns([3, 1])
    with c_input:
        new_task_text = st.text_input("Yeni Görev", key="new_task_input", placeholder="Örn: 50 sayfa kitap oku...")
    with c_btn:
        if st.button("Ekle"):
            if new_task_text:
                ud['gorevler'].append({"text": new_task_text, "done": False})
                verileri_kaydet(ud)
                st.rerun()

    if not ud['gorevler']:
        st.info("Henüz görev yok. Keyfine bak!")
    
    # Görev Listesi
    for i, task in enumerate(ud['gorevler']):
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.write(f"🔹 **{task['text']}**")
        with col_t2:
            if st.button("Bitir", key=f"done_{i}"):
                ud['gorevler'].pop(i)
                ud['para'] += 20
                ud['xp'] += 15
                verileri_kaydet(ud)
                st.toast("Görev Tamamlandı! +20 TL.", icon="✅")
                st.rerun()

# ---------------- TAB 3: ORMAN & MARKET ----------------
with tab3:
    col_forest, col_market = st.columns([1, 1])
    
    # ORMAN
    with col_forest:
        st.subheader("🌲 Senin Ormanın")
        st.markdown("Diktiğin ağaçlar burada birikir.")
        
        if not ud['agaclar']:
            st.warning("Ormanın boş. Odaklanmaya başla!")
        else:
            # Ormanı Grid Olarak Göster
            cols = st.columns(4)
            for idx, item in enumerate(ud['agaclar']):
                tree_def = next((t for t in tree_types if t["id"] == item["type_id"]), tree_types[0])
                with cols[idx % 4]:
                    st.markdown(f"<div style='font-size:30px; text-align:center;'>{tree_def['icon']}</div>", unsafe_allow_html=True)
    
    # MARKET
    with col_market:
        st.subheader("🛒 Fidanlık Market")
        st.caption("Kazandığın paralarla yeni türler aç.")
        
        for tree in tree_types:
            with st.container():
                c1, c2, c3 = st.columns([1, 2, 1])
                c1.markdown(f"<div style='font-size:30px;'>{tree['icon']}</div>", unsafe_allow_html=True)
                c2.write(f"**{tree['name']}**")
                c2.caption(tree['desc'])
                
                is_owned = tree['id'] in ud['envanter']
                is_selected = ud['secili_agac'] == tree['id']
                
                with c3:
                    if is_selected:
                        st.button("Seçili", key=f"sel_{tree['id']}", disabled=True)
                    elif is_owned:
                        if st.button("Seç", key=f"btn_sel_{tree['id']}"):
                            ud['secili_agac'] = tree['id']
                            verileri_kaydet(ud)
                            st.rerun()
                    else:
                        if st.button(f"Al ({tree['price']} TL)", key=f"buy_{tree['id']}"):
                            if ud['para'] >= tree['price']:
                                ud['para'] -= tree['price']
                                ud['envanter'].append(tree['id'])
                                verileri_kaydet(ud)
                                st.toast(f"{tree['name']} satın alındı!", icon="🎉")
                                st.rerun()
                            else:
                                st.error("Yetersiz Bakiye")
                st.markdown("---")

# ---------------- TAB 4: ANALİZ ----------------
with tab4:
    st.subheader("📊 Çalışma İstatistikleri")
    
    if os.path.exists(CSV_DOSYA):
        df = pd.read_csv(CSV_DOSYA)
        if not df.empty:
            # Temel Metrikler
            total_time = df["Sure_Dakika"].sum()
            total_sessions = len(df)
            
            m1, m2 = st.columns(2)
            m1.metric("Toplam Odaklanma (Dk)", total_time)
            m2.metric("Toplam Oturum", total_sessions)
            
            st.markdown("### Günlük Performans")
            # Tarihe göre grupla
            daily_stats = df.groupby("Tarih")["Sure_Dakika"].sum()
            st.bar_chart(daily_stats, color="#64ffda")
            
            st.markdown("### Son Kayıtlar")
            st.dataframe(df.tail(5), use_container_width=True)
        else:
            st.info("Henüz geçmiş verisi yok.")
    else:
        st.info("Veri dosyası oluşturuluyor...")

# ---------------- TAB 5: ZEN & MÜZİK ----------------
with tab5:
    col_z1, col_z2 = st.columns(2)
    
    with col_z1:
        st.subheader("🧘 Nefes Egzersizi")
        st.markdown("Rahatlamak için daireyi takip et.")
        st.write("")
        st.write("")
        # CSS Animasyonlu Daire
        st.markdown('<div class="zen-circle"></div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; margin-top:20px; color:#8892b0;'>Nefes Al... Tut... Ver...</p>", unsafe_allow_html=True)

    with col_z2:
        st.subheader("🎧 Odak Müziği")
        # --- İSTENEN VİDEO BURAYA EKLENDİ ---
        st.video("https://youtu.be/xlLIyoQzO2g") 
        
        st.subheader("🌧️ Yağmur Sesi")
        st.audio("https://ssl.gstatic.com/dictionary/static/sounds/20200429/rain--_gb_1.mp3") # Örnek ses

# --- FOOTER ---
st.markdown("---")
st.markdown("<center style='color: #8892b0; font-size: 12px;'>Irmak Focus RPG Pro v10.0 • Developed for Productivity</center>", unsafe_allow_html=True)