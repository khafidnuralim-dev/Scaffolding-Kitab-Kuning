import streamlit as st
import time
import database as db

# Set Konfigurasi Halaman (Mobile Responsive)
st.set_page_config(
    page_title="Tahkik Fathul Qorib - Prototype V1",
    page_icon="📖",
    layout="centered"
)

# Inisialisasi Database
db.init_db()

# -----------------------------------------------------------------------------
# DATA SAMPLE (Kalimat: ضَرَبَ زَيْدٌ عَمْرًا)
# -----------------------------------------------------------------------------
SAMPLE_SENTENCE = {
    "id": "SAMP_001",
    "text_display": "ضَرَبَ زَيْدٌ عَمْرًا",
    "words": [
        {
            "id": "w1",
            "token": "ضَرَبَ",
            "meaning_correct": "Telah memukul",
            "type": "Fi'il",
            "fiil_type": "Madhi",
            "mabni_type": "Mabni 'Ala Al-Fath",
            "fail_type": "Dzahir"
        },
        {
            "id": "w2",
            "token": "زَيْدٌ",
            "meaning_correct": "Zaid",
            "type": "Isim",
            "isim_type": "Mu'rab",
            "irab": "Marfu'",
            "kedudukan": "Fa'il (Pelaku)",
            "tanda_irab": "Dhammah Dzahirah"
        },
        {
            "id": "w3",
            "token": "عَمْرًا",
            "meaning_correct": "Amr",
            "type": "Isim",
            "isim_type": "Mu'rab",
            "irab": "Manshub",
            "kedudukan": "Maf'ul Bih (Objek)",
            "tanda_irab": "Fathah Dzahirah"
        }
    ]
}

# -----------------------------------------------------------------------------
# SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "username" not in st.session_state:
    st.session_state.username = "santri_01"
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "PHASE_1"  # PHASE_1 (Mufrodat), PHASE_2 (Analisis), COMPLETED
if "start_p1_time" not in st.session_state:
    st.session_state.start_p1_time = time.time()
if "p1_duration" not in st.session_state:
    st.session_state.p1_duration = 0.0
if "start_p2_time" not in st.session_state:
    st.session_state.start_p2_time = 0.0
if "p2_duration" not in st.session_state:
    st.session_state.p2_duration = 0.0

# -----------------------------------------------------------------------------
# HEADER & SIDEBAR
# -----------------------------------------------------------------------------
st.title("📖 Tahkik Kitab Fathul Qorib")
st.caption("Sistem Adaptif Pembelajaran Bahasa Arab (Prototype V1 - Vertical Slice)")

with st.sidebar:
    st.header("👤 Profil Santri")
    username_input = st.text_input("Username", value=st.session_state.username)
    if username_input != st.session_state.username:
        st.session_state.username = username_input
        st.rerun()

    st.markdown("---")
    st.subheader("📜 Riwayat Latihan")
    history = db.get_user_history(st.session_state.username)
    if history:
        for item in history[:5]:
            st.write(f"• **{item[0]}**: Skor {item[1]:.0f}% ({item[2]:.1f} dtk)")
    else:
        st.write("Belum ada riwayat.")

# -----------------------------------------------------------------------------
# TAMPILAN UTAMA KALIMAT
# -----------------------------------------------------------------------------
st.subheader("Kalimat Sampel Analisis:")
st.markdown(
    f"""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; font-size: 32px; font-weight: bold; font-family: 'Amiri', 'Traditional Arabic', serif; margin-bottom: 20px; border: 1px solid #e0e0e0;">
        {SAMPLE_SENTENCE['text_display']}
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# FASE 1: PERSIAPAN MUFRODAT (TIMER OFF)
# -----------------------------------------------------------------------------
if st.session_state.app_stage == "PHASE_1":
    st.info("💡 **Fase 1: Persiapan Mufrodat.** Tentukan arti kata terlebih dahulu. Kolom I'rab masih terkunci.")
    
    all_mufrodat_filled = True
    for w in SAMPLE_SENTENCE["words"]:
        st.markdown(f"**Kata:** `<span style='font-size:20px;'>{w['token']}</span>`", unsafe_allow_html=True)
        ans = st.text_input(f"Arti untuk '{w['token']}'", key=f"muf_{w['id']}")
        if not ans.strip():
            all_mufrodat_filled = False

    st.markdown("---")
    if st.button("🚀 Mulai Analisis Sintaksis (Timer ON)", type="primary", disabled=not all_mufrodat_filled):
        st.session_state.p1_duration = time.time() - st.session_state.start_p1_time
        st.session_state.start_p2_time = time.time()
        st.session_state.app_stage = "PHASE_2"
        st.rerun()
    elif not all_mufrodat_filled:
        st.caption("⚠️ Isi seluruh arti kata terlebih dahulu untuk membuka tombol Fase Analisis.")

# -----------------------------------------------------------------------------
# FASE 2: ANALISIS SINTAKSIS & I'RAB (TIMER ON - CASCADING DROPDOWNS)
# -----------------------------------------------------------------------------
elif st.session_state.app_stage == "PHASE_2":
    st.success("⏱️ **Fase 2: Analisis Sintaksis Berlangsung!** Waktu analisis sedang dihitung...")
    
    answers = {}
    
    for idx, w in enumerate(SAMPLE_SENTENCE["words"]):
        st.markdown(f"### {idx+1}. Kata: <span style='font-size:26px; color:#1E88E5;'>{w['token']}</span>", unsafe_allow_html=True)
        
        # --- CASCADING LEVEL 1: Jenis Kata ---
        jenis_key = f"jenis_{w['id']}"
        jenis_kata = st.selectbox(
            "Jenis Kata (نوع الكلمة):",
            ["-- Pilih --", "Isim", "Fi'il", "Harf"],
            key=jenis_key
        )
        
        w_ans = {"jenis": jenis_kata}
        
        # --- CASCADING LEVEL 2: CABANG FI'IL ---
        if jenis_kata == "Fi'il":
            fiil_type = st.selectbox(
                "Jenis Fi'il:",
                ["-- Pilih --", "Madhi", "Mudhari'", "Amr"],
                key=f"fiil_type_{w['id']}"
            )
            w_ans["fiil_type"] = fiil_type
            
            if fiil_type == "Madhi":
                st.caption("📌 Fi'il Madhi terkunci: **Mabni 'Ala Al-Fath**")
                w_ans["mabni_type"] = "Mabni 'Ala Al-Fath"
                
                fail_type = st.selectbox(
                    "Jenis Fa'il:",
                    ["-- Pilih --", "Dzahir", "Mustatir"],
                    key=f"fail_type_{w['id']}"
                )
                w_ans["fail_type"] = fail_type
                
                if fail_type == "Mustatir":
                    taqdir = st.selectbox(
                        "Taqdir Fa'il (مستتر جوازا/وجوبا):",
                        ["-- Pilih --", "هو", "هي", "أنا", "نحن"],
                        key=f"taqdir_{w['id']}"
                    )
                    w_ans["taqdir"] = taqdir

        # --- CASCADING LEVEL 2: CABANG ISIM ---
        elif jenis_kata == "Isim":
            isim_type = st.selectbox(
                "Sifat Isim:",
                ["-- Pilih --", "Mu'rab", "Mabni"],
                key=f"isim_type_{w['id']}"
            )
            w_ans["isim_type"] = isim_type
            
            if isim_type == "Mu'rab":
                irab = st.selectbox(
                    "Hukum I'rab:",
                    ["-- Pilih --", "Marfu'", "Manshub", "Majrur"],
                    key=f"irab_{w['id']}"
                )
                w_ans["irab"] = irab
                
                kedudukan = st.selectbox(
                    "Kedudukan (Jabatan Kata):",
                    ["-- Pilih --", "Fa'il (Pelaku)", "Maf'ul Bih (Objek)", "Mubtada'", "Khabar"],
                    key=f"kedudukan_{w['id']}"
                )
                w_ans["kedudukan"] = kedudukan
                
                tanda_irab = st.selectbox(
                    "Tanda I'rab Utama:",
                    ["-- Pilih --", "Dhammah Dzahirah", "Fathah Dzahirah", "Kasrah Dzahirah"],
                    key=f"tanda_{w['id']}"
                )
                w_ans["tanda_irab"] = tanda_irab

        # --- CABANG HARF ---
        elif jenis_kata == "Harf":
            st.caption("📌 Harf terkunci: **Laa Mahalla Lahu Minal I'rab**")
            w_ans["status"] = "Mabni / Laa Mahalla Lahu"

        answers[w["id"]] = w_ans
        st.markdown("---")

    # SUBMIT ANALYSIS
    if st.button("✅ Submit Analisis Sintaksis", type="primary"):
        st.session_state.p2_duration = time.time() - st.session_state.start_p2_time
        
        # Evaluasi Skor Sederhana (Rule-based Matching V1)
        correct_count = 0
        total_checks = 0
        
        for w in SAMPLE_SENTENCE["words"]:
            user = answers.get(w["id"], {})
            # Check Jenis Kata
            total_checks += 1
            if user.get("jenis") == w.get("type"):
                correct_count += 1
            
            # Check Sub-properties
            if w.get("type") == "Fi'il":
                total_checks += 2
                if user.get("fiil_type") == w.get("fiil_type"):
                    correct_count += 1
                if user.get("fail_type") == w.get("fail_type"):
                    correct_count += 1
            elif w.get("type") == "Isim":
                total_checks += 3
                if user.get("irab") == w.get("irab"):
                    correct_count += 1
                if user.get("kedudukan") == w.get("kedudukan"):
                    correct_count += 1
                if user.get("tanda_irab") == w.get("tanda_irab"):
                    correct_count += 1

        score_percentage = (correct_count / total_checks) * 100 if total_checks > 0 else 0
        
        # Simpan ke SQLite
        db.save_attempt(
            username=st.session_state.username,
            sentence_id=SAMPLE_SENTENCE["id"],
            p1_time=st.session_state.p1_duration,
            p2_time=st.session_state.p2_duration,
            score=score_percentage,
            answers=answers
        )
        
        st.session_state.last_score = score_percentage
        st.session_state.app_stage = "COMPLETED"
        st.rerun()

# -----------------------------------------------------------------------------
# FASE 3: HASIL & METRIK PERFORMANSI (MASTERY EVALUATION)
# -----------------------------------------------------------------------------
elif st.session_state.app_stage == "COMPLETED":
    st.balloons()
    st.header("📊 Hasil Analisis Sintaksis")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Skor Akurasi", f"{st.session_state.last_score:.0f}%")
    col2.metric("Durasi Mufrodat (Fase 1)", f"{st.session_state.p1_duration:.1f} dtk")
    col3.metric("Durasi Analisis (Fase 2)", f"{st.session_state.p2_duration:.1f} dtk")

    st.markdown("---")
    st.subheader("💡 Evaluasi Adaptif Engine")
    
    if st.session_state.last_score >= 80 and st.session_state.p2_duration <= 30:
        st.success("🟢 **Rekomendasi:** OTOMATISASI SINTAKSIS TINGGI. Santri siap naik ke level berikutnya/Fading Scaffolding.")
    elif st.session_state.last_score >= 80 and st.session_state.p2_duration > 30:
        st.warning("🟡 **Rekomendasi:** AKURASI TINGGI, KECEPATAN LAMBAT (Pemantapan). Berikan teks variasi baru dengan struktur identik (Parallel Corpus).")
    else:
        st.error("🔴 **Rekomendasi:** AKURASI RENDAH (Remedial). Kembali ke Tutor Mode untuk penguatan kaidah Nahwu/Sharaf dasar.")

    if st.button("🔄 Ulangi Latihan"):
        st.session_state.app_stage = "PHASE_1"
        st.session_state.start_p1_time = time.time()
        st.rerun()
        
