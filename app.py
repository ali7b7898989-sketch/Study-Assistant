import streamlit as st
import google.generativeai as genai

# 1. ضبط إعدادات الصفحة
st.set_page_config(
    page_title="المساعد الدراسي",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تخصيص الألوان والتصميم بالـ CSS
st.markdown("""
    <style>
    h1 { font-size: 1.7rem !important; font-weight: 800; text-align: center; color: #6366F1; }
    h2 { font-size: 1.2rem !important; color: #38BDF8; }
    h3 { font-size: 1.05rem !important; }
    
    div[data-testid="stForm"], div.stCard {
        background-color: #1E293B !important;
        border-radius: 14px !important;
        padding: 16px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }

    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    button[aria-selected="true"] {
        color: #38BDF8 !important;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #6366F1 0%, #4F46E5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. تهيئة مفتاح API الخاص بـ Gemini
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# دالة تلقائية لمسح التخزين المؤقت والعثور على نموذج عملي فعال
@st.cache_resource
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # اختيار أفضل نموذج متاح تلقائياً من الحساب
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-2.0-flash', 'models/gemini-1.5-pro']:
            if preferred in models:
                return preferred
        if models:
            return models[0]
    except Exception:
        pass
    return "models/gemini-1.5-flash"

# العنوان الرئيسي
st.title("🎓 المساعد الدراسي")
st.caption("<p style='text-align: center; color: #94A3B8;'>✨ منصتك الذكية لتنظيم الوقت والدراسة</p>", unsafe_allow_html=True)

# الخانات الرئيسية (Tabs)
tab_home, tab_ai, tab_spiritual, tab_schedule = st.tabs([
    "🏠 الواجهة", 
    "🤖 المساعد", 
    "🤲 الروحي", 
    "📅 الجداول"
])

# --- الخانة الأولى: الواجهة الرئيسية ---
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

# --- الخانة الثانية: المساعد الذكي (AI) ---
with tab_ai:
    st.subheader("🤖 المساعد الدراسي الذكي")
    st.caption("اسألني عن شرح مفهوم، حل مسألة، أو أي سؤال عام ودراسي!")

    if not api_key:
        st.error("⚠️ لم يتم العثور على `GEMINI_API_KEY` في قسم Secrets. يرجى إضافته في إعدادات Streamlit.")
    else:
        # تهيئة سجل المحادثات
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # أزرار تحكم بالكل
        col_clear, col_count = st.columns([1, 3])
        with col_clear:
            if st.button("🗑️ مسح الكل"):
                st.session_state.chat_history = []
                st.rerun()

        st.divider()

        # عرض الرسائل وحذف سؤال محدد
        for idx, msg in enumerate(st.session_state.chat_history):
            col_msg, col_del = st.columns([11, 1])
            with col_msg:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            with col_del:
                if msg["role"] == "user":
                    if st.button("❌", key=f"del_{idx}", help="حذف هذا السؤال مع إجابته"):
                        # حذف السؤال والإجابة التي تليه مباشرة
                        del st.session_state.chat_history[idx:idx+2]
                        st.rerun()

        # مدخل السؤال الجديد
        user_query = st.chat_input("اكتب سؤالك أو المادة التي تريد شرحها هنا...")

        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير والتوضيح... 💡"):
                    system_instruction = (
                        "أنت مساعد دراسي ونفسي محفز وودود للطلاب. "
                        "أجب عن جميع أسئلة الطالب بوضوح وبساطة، ووجّهه دائماً نحو النجاح والتركيز."
                    )
                    
                    try:
                        active_model_name = get_working_model()
                        model = genai.GenerativeModel(
                            model_name=active_model_name,
                            system_instruction=system_instruction
                        )
                        
                        # بناء السياق التراكمي
                        context_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])
                        
                        response = model.generate_content(context_prompt)
                        
                        if response and response.text:
                            st.write(response.text)
                            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                        else:
                            st.error("لم يتم استلام رد من النموذج، حاول مرة أخرى.")
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاتصال: {e}")

# --- الخانة الثالثة: الجانب الروحي والنفسي ---
with tab_spiritual:
    st.subheader("🤲 أدعية وتهيئة نفسية")
    st.write("📖 **دعاء قبل الدراسة:**")
    st.info("«اللهم إنّي أسألك فهم النبيّين، وحفظ المرسلين والإلهام...»")

# --- الخانة الرابعة: الجداول والتوقيتات ---
with tab_schedule:
    st.subheader("📅 الجداول والتوقيتات")
    st.write("تنظيم أوقات الدوام والمراجعة اليومية.")
