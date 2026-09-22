import streamlit as st
import google.generativeai as genai
import json
import os
import pandas as pd

# 1. ضبط إعدادات الصفحة
st.set_page_config(
    page_title="المساعد الدراسي",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تخصيص الألوان والتصميم وتثبيت شريط الخانات (Tabs) في الأعلى
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

    /* تثبيت شريط التنقل العلوي للـ Tabs */
    div[data-baseweb="tab-list"] {
        position: sticky !important;
        top: 0 !important;
        background-color: #0E1117 !important;
        z-index: 99999 !important;
        padding-top: 8px !important;
        padding-bottom: 8px !important;
        border-bottom: 2px solid #1E293B !important;
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

# الخانات الرئيسية (مثبتة في الأعلى)
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

        # مربع الكتابة في الأعلى
        with st.form(key="chat_form", clear_on_submit=True):
            user_query = st.text_area(
                "", 
                height=90, 
                placeholder="اكتب سؤالك أو المادة التي تريد شرحها...",
                label_visibility="collapsed"
            )
            send_btn = st.form_submit_button("🚀 إرسال السؤال", use_container_width=True)

        if send_btn and user_query.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_query})

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
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    save_history(st.session_state.chat_history)
                    st.rerun()
                else:
                    st.error("لم يتم استلام رد من النموذج، حاول مرة أخرى.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {e}")

        st.divider()

        # عرض المحادثات
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

# --- الخانة الثالثة: الجانب الروحي والنفسي ---
with tab_spiritual:
    st.subheader("🤲 أدعية وتهيئة نفسية")
    st.write("📖 **دعاء قبل الدراسة:**")
    st.info("«اللهم إنّي أسألك فهم النبيّين، وحفظ المرسلين والإلهام...»")

# --- الخانة الرابعة: الجداول والتوقيتات العلمية ---
with tab_schedule:
    st.subheader("📅 الجداول والدراسة اليومية")
    st.caption("جداول مصممة وفقاً لأعلى أوقات التركيز الاستيعابي للذاكرة")

    shift_option = st.radio(
        "اختر نظام دوامك المدرسي:", 
        ["☀️ الدوام الصباحي (8:00 ص - 1:00 م)", "🌤️ الدوام الظهري (1:00 م - 5:00 م)"],
        horizontal=True
    )

    st.divider()

    if "الصباحي" in shift_option:
        st.write("### ☀️ جدول الدوام الصباحي")
        data_morning = {
            "التوقيت": [
                "6:30 ص - 7:30 ص",
                "8:00 ص - 1:00 م",
                "1:30 م - 3:00 م",
                "3:30 م - 6:00 م",
                "6:00 م - 7:00 م",
                "7:30 م - 9:30 م",
                "10:00 م"
            ],
            "النشاط المقترح": [
                "⚡ مراجعة سريعة للمركزات / حفظ مصطلحات",
                "🏫 الدوام المدرسي الحضوري",
                "🍽️ العودة، استراحة وغداء",
                "🧠 المراجعة الفكرية العميق (رياضيات / فيزياء / كيمياء)",
                "🏃 استراحة حركة وتنقّل (مشافي/رياضة خفيفة)",
                "📚 المواد الحفظية واللغات (إنكليزي / عربي / فرنسي)",
                "😴 النوم المبكر لتجديد الطاقة الذكائية"
            ]
        }
        st.table(pd.DataFrame(data_morning))
    else:
        st.write("### 🌤️ جدول الدوام الظهري")
        data_afternoon = {
            "التوقيت": [
                "7:00 ص - 8:30 ص",
                "9:00 ص - 11:30 ص",
                "11:30 ص - 12:30 م",
                "1:00 م - 5:00 م",
                "5:30 م - 6:30 م",
                "7:00 م - 9:30 م",
                "10:30 م"
            ],
            "النشاط المقترح": [
                "🌅 قمة صفاء الذهن: المواد العلمية (رياضيات / تحليل)",
                "📖 المواد النظرية والواجبات اليومية",
                "🍱 التهيؤ والغداء للدوام",
                "🏫 الدوام المدرسي الظهري",
                "☕ العودة، استراحة وتناول المشروب المفضل",
                "📝 حل تمارين المدرسة + مراجعة دروس الغد",
                "😴 النوم والاستعداد لليوم التالي"
            ]
        }
        st.table(pd.DataFrame(data_afternoon))

    st.divider()
    st.info("💡 **نصيحة ذهبية:** أوقات الصباح الباكر تحتوي على أعلى نسبة تركيز للذاكرة طويلة المدى، استغلها دائماً للمواد الصعبة.")
