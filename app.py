import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="المساعد الدراسي",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تحسين المظهر العام بلمسات CSS لتصغير الخطوط وترتيب البطاقات
st.markdown("""
    <style>
    /* تصغير العناوين لتناسب الموبايل */
    h1 { font-size: 1.8rem !important; font-weight: 700; text-align: center; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    /* تصميم البطاقات المخصصة */
    .stCard {
        background-color: #1e222d;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #2e3440;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.title("🎓 المساعد الدراسي")
st.caption("✨ منصتك الذكية لتنظيم الوقت، الدراسة، والراحة النفسية")

# الخانات الرئيسية (Tabs)
tab_home, tab_ai, tab_spiritual, tab_schedule = st.tabs([
    "🏠 الواجهة", 
    "🤖 المساعد", 
    "🤲 الروحي", 
    "📅 الجداول"
])

# --- الخانة الأولى: الواجهة الرئيسية ---
with tab_home:
    # بطاقة النوتات السريعة
    with st.container():
        st.subheader("📝 ملاحظات اليوم والأهداف")
        notes = st.text_area(
            "", 
            height=100, 
            placeholder="اكتب أهدافك السريعة هنا... (مثال: مراجعة فصل الرياضيات)",
            label_visibility="collapsed"
        )
        if notes:
            st.success(f"📌 **الهدف المكتوب:** {notes}")

    st.divider()

    # بطاقة المؤقت
    with st.container():
        st.subheader("⏱️ مؤقت التركيز (Pomodoro)")
        col_time, col_btn = st.columns([2, 1])
        with col_time:
            study_time = st.number_input("المدة (دقائق):", value=25, min_value=1, step=5)
        with col_btn:
            st.write("") # مسافة للضبط
            st.write("") 
            if st.button("🚀 ابدأ", use_container_width=True):
                st.warning(f"بدأت الجلسة! {study_time} دقيقة تركيز بدون مشتتات 💪")

# --- الخانة الثانية: المساعد الذكي ---
with tab_ai:
    st.subheader("🤖 المساعد الدراسي الذكي")
    st.info("💡 اسأل عن أي مادة، مسألة، أو تلخيص فصل وسأجيبك فوراً!")

# --- الخانة الثالثة: الجانب الروحي والنفسي ---
with tab_spiritual:
    st.subheader("🤲 أدعية وتهيئة نفسية")
    st.write("📖 **دعاء قبل الدراسة:**")
    st.info("«اللهم إنّي أسألك فهم النبيّين، وحفظ المرسلين والإلهام...»")

# --- الخانة الرابعة: الجداول ---
with tab_schedule:
    st.subheader("📅 الجداول والتوقيتات")
    st.write("تنظيم أوقات الدوام والمراجعة اليومية.")
