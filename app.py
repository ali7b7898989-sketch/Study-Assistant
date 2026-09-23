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

# 2. تخصيص التصميم والخطوط والـ CSS (مع تثبيت الشريط العلوي للأقسام)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
    }
    
    h1 { font-size: 1.7rem !important; font-weight: 800; text-align: center; color: #6366F1; }
    h2 { font-size: 1.2rem !important; color: #38BDF8; }
    h3 { font-size: 1.05rem !important; }
    
    /* تثبيت شريط التبويبات العلوي */
    div[data-baseweb="tab-list"] {
        position: sticky !important;
        top: 0 !important;
        background-color: #0E1117 !important;
        z-index: 9999 !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
        border-bottom: 1px solid #334155 !important;
    }

    button[data-baseweb="tab"] {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
    }
    
    button[aria-selected="true"] {
        color: #38BDF8 !important;
    }

    /* بطاقة الزخرفة القرآنية والروحية */
    .quran-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #D97706;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        color: #FDE68A;
        font-family: 'Amiri', serif;
        font-size: 1.25rem;
        line-height: 2.2;
        box-shadow: 0 4px 15px rgba(217, 119, 6, 0.15);
        margin-bottom: 15px;
    }

    .dua-box {
        background-color: #1E293B;
        border-right: 4px solid #38BDF8;
        border-radius: 10px;
        padding: 14px;
        color: #F8FAFC;
        font-family: 'Amiri', serif;
        font-size: 1.15rem;
        line-height: 2.0;
        margin-bottom: 12px;
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

# 3. تهيئة API الخاص بـ Gemini
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

# الخانات الرئيسية
tab_home, tab_timer, tab_ai, tab_spiritual, tab_tips, tab_schedule = st.tabs([
    "🏠 المهام", 
    "⏱️ المؤقت",
    "🤖 المساعد", 
    "🤲 الروحي", 
    "💡 نصائح",
    "📅 الجداول"
])

# --- 1. المهام اليومية ---
with tab_home:
    st.subheader("📋 قائمة المهام اليومية (Checklist)")
    
    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    col_input, col_add = st.columns([3, 1])
    with col_input:
        new_task = st.text_input("إضافة مهمة جديدة:", placeholder="مثال: مراجعة رياضيات", label_visibility="collapsed")
    with col_add:
        if st.button("➕ إضافة", use_container_width=True):
            if new_task:
                st.session_state.tasks.append({"task": new_task, "done": False})
                st.rerun()

    st.divider()

    if st.session_state.tasks:
        completed_tasks = sum(1 for t in st.session_state.tasks if t["done"])
        progress = completed_tasks / len(st.session_state.tasks)
        st.write(f"📊 **نسبة الإنجاز اليومي:** {int(progress * 100)}%")
        st.progress(progress)

        for idx, t in enumerate(st.session_state.tasks):
            col_check, col_del = st.columns([5, 1])
            with col_check:
                is_done = st.checkbox(t["task"], value=t["done"], key=f"task_{idx}")
                if is_done != t["done"]:
                    st.session_state.tasks[idx]["done"] = is_done
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_task_{idx}"):
                    del st.session_state.tasks[idx]
                    st.rerun()
    else:
        st.info("لا توجد مهام حالياً. أضف أهدافك لليوم واستمتع بإنجازها! 💪")

# --- 2. المؤقت المطور ---
with tab_timer:
    st.subheader("⏱️ مؤقت التركيز (Pomodoro)")
    
    col_study, col_break = st.columns(2)
    with col_study:
        study_m = st.number_input("جلسة الدراسة (دقائق):", value=25, min_value=1, step=5)
    with col_break:
        break_m = st.number_input("وقت الاستراحة (دقائق):", value=5, min_value=1, step=1)

    if st.button("🚀 ابدأ جلسة التركيز", use_container_width=True):
        st.success(f"🎯 بدأت الجلسة! {study_m} دقيقة تركيز، تليها {break_m} دقائق استراحة.")

    st.divider()
    st.subheader("🌧️ أجواء التركيز (صوت المطر)")
    st.write("شغّل صوت المطر الهادئ ليزيد تركيزك ويمنع المشتتات:")
    st.audio("https://www.soundjay.com/nature/rain-01.mp3", format="audio/mp3")

# --- 3. المساعد الذكي ---
with tab_ai:
    st.subheader("🤖 المساعد الدراسي الذكي")
    
    if not api_key:
        st.error("⚠️ لم يتم العثور على `GEMINI_API_KEY` في قسم Secrets.")
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

        i = 0
        while i < len(st.session_state.chat_history):
            msg = st.session_state.chat_history[i]
            if msg["role"] == "user":
                col_msg, col_del = st.columns([11, 1])
                with col_msg:
                    with st.chat_message("user"):
                        st.write(msg["content"])
                with col_del:
                    if st.button("❌", key=f"del_{i}", help="حذف"):
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

        user_query = st.chat_input("اكتب سؤالك هنا...")

        if user_query:
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

# --- 4. الروحي والأدعية (مزخرف وبالخط القرآني) ---
with tab_spiritual:
    st.subheader("🤲 الأدعية والتهيئة النفسية")
    
    # آية الشرح الثابتة والمزخرفة في الأعلى
    st.markdown("""
        <div class="quran-box">
            ﴿ رَبِّ اشْرَحْ لِي صَدْرِي ۝ وَيَسِّرْ لِي أَمْرِي ۝ وَاحْلُلْ عُقْدَةً مِّن لِّسَانِي ۝ يَفْقَهُوا قَوْلِي ﴾
        </div>
    """, unsafe_allow_html=True)

    dua_option = st.radio(
        "اختر القسم:", 
        [
            "📖 قبل الدراسة", 
            "✍️ بعد الدراسة", 
            "🕌 بعد الصلاة (للحفظ)",
            "📝 أدعية الامتحان", 
            "🌸 سور وآيات مباركة"
        ],
        horizontal=True
    )

    st.write("")

    if "قبل الدراسة" in dua_option:
        st.write("### 📖 أدعية قبل بداية الدراسة")
        st.markdown('<div class="dua-box">« اللَّهُمَّ أَخْرِجْنِي مِنْ ظُلُمَاتِ الوَهْمِ، وَأَكْرِمْنِي بِنُورِ الفَهْمِ، اللَّهُمَّ افْتَحْ عَلَيْنَا أَبْوَابَ رَحْمَتِكَ، وَانْشُرْ عَلَيْنَا خَزَائِنَ عُلُومِكَ بِرَحْمَتِكَ يَا أَرْحَمَ الرَّاحِمِينَ »</div>', unsafe_allow_html=True)
        st.markdown('<div class="dua-box">« اللَّهُمَّ إِنِّي أَسْأَلُكَ فَهْمَ النَّبِيِّينَ، وَحِفْظَ المُرْسَلِينَ، وَالمَلَائِكَةِ المُقَرَّبِينَ.. اللَّهُمَّ اجْعَلْ أَلْسِنَتَنَا عَامِرَةً بِذِكْرِكَ، وَقُلُوبَنَا بِخَشْيَتِكَ، وَأَسْرَارَنَا بِطَاعَتِكَ، إِنَّكَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، وَحَسْبُنَا اللَّهُ وَنِعْمَ الوَكِيلُ »</div>', unsafe_allow_html=True)

    elif "بعد الدراسة" in dua_option:
        st.write("### ✍️ دعاء بعد الانتهاء من الدراسة")
        st.markdown('<div class="dua-box">« اللَّهُمَّ إِنِّي تَوَكَّلْتُ عَلَيْكَ، وَسَلَّمْتُ أَمْرِي إِلَيْكَ، لَا مَلْجَأَ وَلَا مَنْجَى مِنْكَ إِلَّا إِلَيْكَ.. اللَّهُمَّ إِنِّي أَسْتَوْدِعُكَ مَا قَرَأْتُ وَمَا حَفِظْتُ وَمَا تَعَلَّمْتُ، فَرُدَّهُ لِي عِنْدَ حَاجَتِي إِلَيْهِ، إِنَّكَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، وَحَسْبُنَا اللَّهُ وَنِعْمَ الوَكِيلُ »</div>', unsafe_allow_html=True)

    elif "بعد الصلاة" in dua_option:
        st.write("### 🕌 دعاء بعد كل صلاة لزيادة الحفظ")
        st.markdown('<div class="dua-box">« سُبْحَانَ مَنْ لَا يَعْتَدِي عَلَى أَهْلِ مَمْلَكَتِهِ، سُبْحَانَ مَنْ لَا يَأْخُذُ أَهْلَ الأَرْضِ بِأَلْوَانِ العَذَابِ، سُبْحَانَ الرَّؤُوفِ الرَّحِيمِ.. اللَّهُمَّ اجْعَلْ لِي فِي قَلْبِي نُوراً وَبَصَراً وَفَهْماً وَعِلْماً، إِنَّكَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ »</div>', unsafe_allow_html=True)

    elif "أدعية الامتحان" in dua_option:
        st.write("### 📝 أدعية الامتحان (مرتبة حسب المرحلة)")
        st.markdown('**1️⃣ عند التوجه إلى الامتحان:**')
        st.markdown('<div class="dua-box">« اللَّهُمَّ إِنِّي تَوَكَّلْتُ عَلَيْكَ، وَفَوَّضْتُ أَمْرِي إِلَيْكَ، لَا مَلْجَأَ وَلَا مَنْجَى مِنْكَ إِلَّا إِلَيْكَ »</div>', unsafe_allow_html=True)
        
        st.markdown('**2️⃣ عند دخول قاعة الامتحان:**')
        st.markdown('<div class="dua-box">« رَبِّ أَدْخِلْنِي مُدْخَلَ صِدْقٍ، وَأَخْرِجْنِي مُخْرَجَ صِدْقٍ، وَاجْعَلْ لِي مِنْ لَدُنْكَ سُلْطَاناً نَصِيراً »</div>', unsafe_allow_html=True)
        
        st.markdown('**3️⃣ عند بداية الإجابة:**')
        st.markdown('<div class="dua-box">« رَبِّ اشْرَحْ لِي صَدْرِي، وَيَسِّرْ لِي أَمْرِي، وَاحْلُلْ عُقْدَةً مِنْ لِسَانِي يَفْقَهُوا قَوْلِي.. بِسْمِ اللَّهِ الفَتَّاحِ.. اللَّهُمَّ لَا سَهْلَ إِلَّا مَا جَعَلْتَهُ سَهْلاً، وَأَنْتَ تَجْعَلُ الحَزْنَ إِذَا شِئْتَ سَهْلاً، سَهِّلْ أُمُورَنَا وَارْحَمْنَا بِرَحْمَتِكَ يَا أَرْحَمَ الرَّاحِمِينَ »</div>', unsafe_allow_html=True)
        
        st.markdown('**4️⃣ عند تعسر الإجابة أو النسيان:**')
        st.markdown('<div class="dua-box">« لَا إِلَهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ.. يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ.. اللَّهُمَّ يَا جَامِعَ النَّاسِ فِي يَوْمٍ لَا رَيْبَ فِيهِ اجْمَعْ عَلَيَّ ضَالَّتِي »</div>', unsafe_allow_html=True)
        
        st.markdown('**5️⃣ عند الانتهاء من الإجابة:**')
        st.markdown('<div class="dua-box">« الحَمْدُ لِلَّهِ الَّذِي هَدَانَا لِهَذَا وَمَا كُنَّا لِنَهْتَدِيَ لَوْلَا أَنْ هَدَانَا اللَّهُ »</div>', unsafe_allow_html=True)

    elif "سور وآيات" in dua_option:
        st.write("### 🌸 سور وآيات التيسير والحفظ")
        st.markdown("#### 📖 سورة الفاتحة")
        st.markdown("""
            <div class="quran-box">
                بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ ۝ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ۝ الرَّحْمَنِ الرَّحِيمِ ۝ مَالِكِ يَوْمِ الدِّينِ ۝ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ ۝ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ ۝ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📖 آية الكرسي كاملة")
        st.markdown("""
            <div class="quran-box">
                اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ مَنْ ذَا الَّذِي يَشْفَعُ عِنْدَهُ إِلَّا بِإِذْنِهِ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِنْ عِلْمِهِ إِلَّا بِمَا شَاءَ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا وَهُوَ الْعَلِيُّ الْعَظِيمُ ۝ لَا إِكْرَاهَ فِي الدِّينِ قَدْ تَبَيَّنَ الرُّشْدُ مِنَ الْغَيِّ فَمَنْ يَكْفُرْ بِالطَّاغُوتِ وَيُؤْمِنْ بِاللَّهِ فَقَدِ اسْتَمْسَكَ بِالْعُرْوَةِ الْوُثْقَى لَا انْفِصَامَ لَهَا وَاللَّهُ سَمِيعٌ عَلِيمٌ ۝ اللَّهُ وَلِيُّ الَّذِينَ آمَنُوا يُخْرِجُهُمْ مِنَ الظُّلُمَاتِ إِلَى النُّورِ وَالَّذِينَ كَفَرُوا أَوْلِيَاؤُهُمُ الطَّاغُوتُ يُخْرِجُونَهُمْ مِنَ النُّورِ إِلَى الظُّلُمَاتِ أُولَئِكَ أَصْحَابُ النَّارِ هُمْ فِيهَا خَالِدُونَ
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📖 سورة الشرح")
        st.markdown("""
            <div class="quran-box">
                أَلَمْ نَشْرَحْ لَكَ صَدْرَكَ ۝ وَوَضَعْنَا عَنْكَ وِزْرَكَ ۝ الَّذِي أَنْقَضَ ظَهْرَكَ ۝ وَرَفَعْنَا لَكَ ذِكْرَكَ ۝ فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ۝ إِنَّ مَعَ الْعُسْرِ يُسْرًا ۝ فَإِذَا فَرَغْتَ فَانْصَبْ ۝ وَإِلَى رَبِّكَ فَارْغَبْ
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📖 سورة يس")
        st.info("💡 يُستحب قراءة سورة يس صباحاً لتيسير الأمور والانشراح برحمة الله.")

# --- 5. النصائح والإرشادات ---
with tab_tips:
    st.subheader("💡 نصائح وإرشادات التميز الدراسي")
    
    tip_category = st.radio(
        "اختر محور النصائح:",
        [
            "🧠 التفكير المعرفي والبيئة",
            "⚡ خطوات تقوية الحفظ (9 أسباب)",
            "🕌 أهمية الصلوات الخمس",
            "🎯 إرشادات يوم الامتحان"
        ],
        horizontal=True
    )

    st.divider()

    if "التفكير المعرفي" in tip_category:
        st.write("### 🧠 العقلية الإيجابية وبيئة الدراسة")
        st.info("🔹 **العلم لا ينزع:** اعلم تماماً أن الإنسان قد يُسلب منه كل شيء في الدنيا إلا علمه ودينه، فابنِ تفكيراً معرفياً إيجابياً نحو التعلم.")
        st.write("📌 **عوامل يجب مراجعتها وتعديلها فوراً:**")
        st.markdown("- **مكان ووقت الدراسة:** اختر مكاناً مريحاً وإضاءة ممتازة.")
        st.markdown("- **رفاق الدراسة:** اختر من يشجعك على الإنجاز والالتزام.")
        st.markdown("- **أسلوب المتابعة:** اعتمد التلخيص المباشر والتذكر الفعال.")

    elif "تقوية الحفظ" in tip_category:
        st.write("### ⚡ الأسباب الطبيعية لتنشيط الذاكرة وتقوية الحفظ")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("1️⃣ **تنظيم الوقت:** قسّم وقتك بين الدراسة والراحة ولا تضغط نفسك.")
            st.markdown("2️⃣ **الابتعاد عن الملهيات:** اغلق الهاتف وتجنب وسائل التواصل أثناء الحفظ.")
            st.markdown("3️⃣ **التكرار والمراجعة:** التكرار اليومي يثبت المعلومة في الذهن.")
            st.markdown("4️⃣ **النوم الجيد:** احرص على نوم (6-8 ساعات) لتثبيت المعلومات.")
            st.markdown("5️⃣ **التدرج في الحفظ:** ابدأ بصفحة أو موضوع قليل ثم زد بالتدريج.")
        with col_b:
            st.markdown("6️⃣ **ممارسة الرياضة:** المشي ينشط الدورة الدموية ويزيد تدفق الدم للدماغ.")
            st.markdown("7️⃣ **التنفس العميق:** يزود المخ بالأكسجين ويحسن الأداء العقلي.")
            st.markdown("8️⃣ **الاستعانة بالكتابة:** كتابة ما تحفظه تجعله راسخاً في الذاكرة.")
            st.markdown("9️⃣ **الثقة والتوكل:** ثق بقدراتك وابتعد عن الخوف والقلق.")

    elif "الصلوات الخمس" in tip_category:
        st.write("### 🕌 الصلوات الخمس: سرُّ البركة والسكينة في رحلتك الدراسية")
        st.success("✨ **ميزان الوقت وتنظيمه:** أداء الصلاة في وقتها يبني جدول دراستك ببركة ونظام ممتاز لليوم.")
        st.info("🧠 **تجديد الطاقة وتصفية الذهن:** الوقوف بين يدي الله يفرغ عقلك من إجهاد الحفظ والتركيز، ويمنحك استراحة إيمانية هادئة.")
        st.warning("🕊️ **طرد القلق وطمأنينة القلب:** الصلاة هي الملجأ الأول لخلق الطمأنينة الداخلية (﴿أَلا بِذِكرِ اللَّهِ تَطمَئِنُّ القُلوبُ﴾).")

    elif "يوم الامتحان" in tip_category:
        st.write("### 🎯 إرشادات ووصايا يوم الامتحان")
        st.success("💧 **1. الطهارة والوضوء:** كن على وضوء دائماً أثناء المراجعة وفي قاعة الامتحان.")
        st.success("🕊️ **2. الاستغفار والتحوقل:** كرر دائماً: (أستغفر الله وأتوب إليه، ولا حول ولا قوة إلا بالله).")
        st.success("🌸 **3. الصلاة على النبي:** أكثر من قول: (اللهم صلِّ على محمد وآل محمد).")
        st.success("📝 **4. عدم التأجيل:** أنجز واجباتك يومياً لتشعر بالرغبة والراحة النفسية.")

# --- 6. الجداول المدرسية ---
with tab_schedule:
    st.subheader("📅 الجداول والدراسة اليومية")
    
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
                "🏃 استراحة حركة وتنقّل",
                "📚 المواد الحفظية واللغات",
                "😴 النوم المبكر"
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
