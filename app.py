import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="المساعد الدراسي",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تخصيص الألوان والتصميم بلمسات عصرية
st.markdown("""
    <style>
    /* تصغير العناوين لتناسب شاشة الموبايل */
    h1 { font-size: 1.7rem !important; font-weight: 800; text-align: center; color: #6366F1; }
    h2 { font-size: 1.2rem !important; color: #38BDF8; }
    h3 { font-size: 1.05rem !important; }
    
    /* خلفية وتصميم البطاقات المخصصة */
    div[data-testid="stForm"], div.stCard {
        background-color: #1E293B !important;
        border-radius: 14px !important;
        padding: 16px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }

    /* تحسين تصميم التبويبات Tabs */
    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    /* لون التبويب المحدد */
    button[aria-selected="true"] {
        color: #38BDF8 !important;
    }

    /* تحسين زر التشغيل */
    div.stButton > button {
        background: linear-gradient(90deg, #6366F1 0%, #4F46E5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎓 المساعد الدراسي")
st.caption("<p style='text-align: center; color: #94A3B8;'>✨ منصتك الذكية لتنظيم الوقت والدراسة</p>", unsafe_allow_html=True)

# Tabs
tab_home, tab_ai, tab_spiritual, tab_schedule = st.tabs([
    "🏠 الواجهة", 
    "🤖 المساعد", 
    "🤲 الروحي", 
    "📅 الجداول"
])

# --- الخانة الأولى: الواجهة ---
with tab_home:
    st.subheader("📝 ملاحظات اليوم والأهداف")
    notes = st.text_area(
        "", 
        height=100, 
        placeholder="اكتب أهدافك السريعة هنا... (مثال: مراجعة الفصل الأول رياضيات)",
        label_visibility="collapsed"
    )
    if notes:
        st.success(f"📌 **الهدف المكتوب:** {notes}")

    st.divider()

    st.subheader("⏱️ مؤقت التركيز (Pomodoro)")
    col_time, col_btn = st.columns([2, 1])
    with col_time:
        study_time = st.number_input("المدة (دقائق):", value=25, min_value=1, step=5)
    with col_btn:
        st.write("") 
        st.write("") 
        if st.button("🚀 ابدأ", use_container_width=True):
            st.warning(f"بدأت الجلسة! {study_time} دقيقة تركيز بدون مشتتات 💪")

# --- الخانة الثانية: المساعد الذكي ---
with tab_ai:
    st.subheader("🤖 المساعد الدراسي الذكي")
    st.info("💡 اسأل عن أي مادة، مسألة، أو تلخيص فصل وسأجيبك فوراً!")

# --- الخانة الثالثة: الجانب الروحي ---
with tab_spiritual:
    st.subheader("🤲 أدعية وتهيئة نفسية")
    st.write("📖 **دعاء قبل الدراسة:**")
    st.info("«اللهم إنّي أسألك فهم النبيّين، وحفظ المرسلين والإلهام...»")

# --- الخانة الرابعة: الجداول ---
with tab_schedule:
    st.subheader("📅 الجداول والتوقيتات")
    st.write("تنظيم أوقات الدوام والمراجعة اليومية.")
