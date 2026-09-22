import streamlit as st
import google.generativeai as genai
import json
import os

# 1. ضبط إعدادات الصفحة
st.set_page_config(
    page_title="المساعد الدراسي",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تخصيص الألوان والتصميم بالـ CSS المتقدم لتثبيت حقل الكتابة في الأسفل
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

    /* تثبيت الحاوية الخاصة بالإدخال في الأسفل */
    .fixed-bottom {
        position: sticky;
        bottom: 0;
        background-color: #0E1117;
        padding-top: 10px;
        padding-bottom: 10px;
        z-index: 999;
        border-top: 1px solid #1E293B;
    }
    </style>
""", unsafe_allow_html=True)

# 3. تهيئة مفتاح API الخاص بـ Gemini
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

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
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = load_history()

        col_clear, _ = st.columns([1, 3])
        with col_clear:
            if st.button("🗑️ مسح الكل"):
                st.session_state.chat_history = []
                save_history([])
                st.rerun()

        st.divider()

        # منطقة عرض المحادثة
        chat_container = st.container()

        with chat_container:
            i = 0
            while i < len(st.session_state.chat_history):
                msg = st.session_state.chat_history[i]
                
                if msg["role"] == "user":
                    col_msg, col_del = st.columns([11, 1])
                    with col_msg:
                        with st.chat_message("user"):
                            st.write(msg["content"])
                    with col_del:
                        if st.button("❌", key=f"del_{i}", help="حذف هذا السؤال وإجابته"):
                            if i + 1 < len(st.session_state.chat_history) and st.session_state.chat_history[i+1]["role"] == "assistant":
                                del st.session_state.chat_history[i:i+2]
                            else:
                                del st.session_state.chat_history[i]
                            save_history(st.session_state.chat_history)
                            st.rerun()
                else:
                    with st.chat_message("assistant"):
                        st.write(msg["content"])
                i += 1

        # خانة الكتابة المثبتة في الأسفل
        st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
        user_query = st.text_area(
            "", 
            height=90, 
            placeholder="اكتب سؤالك أو المادة التي تريد شرحها...",
            key="input_box",
            label_visibility="collapsed"
        )
        send_btn = st.button("🚀 إرسال السؤال", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if send_btn and user_query.strip():
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("جاري التفكير والتوضيح... 💡"):
                        system_instruction = (
                            "أنت مساعد دراسي ونفسي محفز وودود للطلاب. "
                            "أجب عن جميع أسئلة الطالب بوضوح وبساطة، ووجّهه دائماً نحو النجاح والتركيز."
                        )
                        
                        try:
                            model = genai.GenerativeModel(
                                model_name="gemini-3.6-flash",
                                system_instruction=system_instruction
                            )
                            
                            formatted_history = []
                            for h in st.session_state.chat_history[:-1]:
                                role = "user" if h["role"] == "user" else "model"
                                formatted_history.append({"role": role, "parts": [h["content"]]})
                                
                            chat = model.start_chat(history=formatted_history)
                            response = chat.send_message(user_query)
                            
                            if response and response.text:
                                st.write(response.text)
                                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                                save_history(st.session_state.chat_history)
                                st.rerun()
                            else:
                                st.error("لم يتم استلام رد من النموذج، حاول مرة أخرى.")
                        except Exception as e:
                            st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {e}")

# --- الخانة الثالثة: الجانب الروحي والنفسي ---
with tab_spiritual:
    st.subheader("🤲 أدعية وتهيئة نفسية")
    st.write("📖 **دعاء قبل الدراسة:**")
    st.info("«اللهم إنّي أسألك فهم النبيّين، وحفظ المرسلين والإلهام...»")

# --- الخانة الرابعة: الجداول والتوقيتات ---
with tab_schedule:
    st.subheader("📅 الجداول والتوقيتات")
    st.write("تنظيم أوقات الدوام والمراجعة اليومية.")
