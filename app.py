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
    /* تصغير العناوين لتناسب شاشات الهواتف */
    h1 { font-size: 1.7rem !important; font-weight: 800; text-align: center; color: #6366F1; }
    h2 { font-size: 1.2rem !important; color: #38BDF8; }
    h3 { font-size: 1.05rem !important; }
    
    /* تصميم البطاقات والحاويات */
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
    
    button[aria-selected="true"] {
        color: #38BDF8 !important;
    }

    /* تحسين الأزرار */
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
        # تهيئة سجل السجل للرسائل للحفظ الدائم طوال الجلسة
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # زر لمسح السجل إذا أراد الطالب البدء من جديد
        col_title, col_clear = st.columns([4, 1])
        with col_clear:
            if st.button("🗑️ مسح المحادثة"):
                st.session_state.chat_history = []
                st.rerun()

        # عرض جميع المحادثات المحفوظة سابقة
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # مدخل السؤال الجديد
        user_query = st.chat_input("اكتب سؤالك أو المادة التي تريد شرحها هنا...")

        if user_query:
            # إضافة سؤال الطالب للحافظة وعرضه
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            # إجابة المساعد
            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير والتوضيح... 💡"):
                    system_instruction = (
                        "أنت مساعد دراسي ونفسي محفز وودود للطلاب. "
                        "أجب عن جميع أسئلة الطالب بوضوح وبساطة سواء كانت دراسية أو عامة، "
                        "ووجّهه دائماً نحو النجاح والتركيز."
                    )
                    
                    # قائمة بأسماء النماذج لتجربتها بالترتيب المضمون
                    candidate_models = [
                        "gemini-1.5-flash",
                        "gemini-2.0-flash",
                        "gemini-2.5-flash",
                        "gemini-1.5-pro",
                        "gemini-pro"
                    ]
                    
                    response_text = None
                    last_err = None

                    # بناء نص محادثة تراكمي يتضمن السجل السابق ليتذكر المساعد ما سبق
                    full_prompt = f"التعليمات: {system_instruction}\n\n"
                    for h in st.session_state.chat_history:
                        role_name = "الطالب" if h["role"] == "user" else "المساعد"
                        full_prompt += f"{role_name}: {h['content']}\n"

                    for model_name in candidate_models:
                        try:
                            model = genai.GenerativeModel(model_name=model_name)
                            res = model.generate_content(full_prompt)
                            if res and res.text:
                                response_text = res.text
                                break
                        except Exception as e:
                            last_err = e

                    if response_text:
                        st.write(response_text)
                        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                    else:
                        st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {last_err}")

# --- الخانة الثالثة: الجانب الروحي والنفسي ---
with tab_spiritual:
    st.subheader("🤲 أدعية وتهيئة نفسية")
    st.write("📖 **دعاء قبل الدراسة:**")
    st.info("«اللهم إنّي أسألك فهم النبيّين، وحفظ المرسلين والإلهام...»")

# --- الخانة الرابعة: الجداول والتوقيتات ---
with tab_schedule:
    st.subheader("📅 الجداول والتوقيتات")
    st.write("تنظيم أوقات الدوام والمراجعة اليومية.")
