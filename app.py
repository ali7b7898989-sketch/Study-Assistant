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

# 2. تخصيص التصميم والخطوط وتثبيت التبويبات بطريقة صحيحة بدون أخطاء بايثون
st.markdown("""
    <!-- وسم لمنع المتصفح من إظهار شريط الترجمة التلقائي -->
    <meta name="google" content="notranslate">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
    }
    
    h1 { 
        font-size: 1.7rem !important; 
        font-weight: 800; 
        text-align: center; 
        color: #6366F1; 
    }
    h2 { font-size: 1.2rem !important; color: #38BDF8; }
    h3 { font-size: 1.05rem !important; }
    
    /* تثبيت شريط التبويبات في أعلى الشاشة */
    div[data-baseweb="tab-highlight-container"] {
        position: sticky !important;
        top: 0 !important;
        background-color: #0E1117 !important;
        z-index: 99999 !important;
        padding-top: 8px !important;
        padding-bottom: 8px !important;
        border-bottom: 2px solid #1E293B !important;
    }

    div[data-baseweb="tab-list"] {
        position: sticky !important;
        top: 0 !important;
        z-index: 99999 !important;
        background-color: #0E1117 !important;
    }

    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    button[aria-selected="true"] {
        color: #38BDF8 !important;
    }

    /* بطاقات النصوص والزخرفة */
    .quran-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #D97706;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        color: #FDE68A;
        font-family: 'Amiri', serif;
        font-size: 1.2rem;
        line-height: 2.3;
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

# التبويبات الرئيسية
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

# --- 2. المؤقت + صوت المطر المباشر الصحيح ---
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
    st.subheader("🌧️ أجواء التركيز (صوت المطر الهادئ الصافي)")
    st.caption("💡 يمكنك الضغط على النقاط الثلاث بجانب المشغل وتفعيل **تكرار (Loop)** ليعمل بشكل مستمر أثناء الدراسة:")
    st.audio("https://www.soundjay.com/nature/sounds/rain-01.mp3", format="audio/mp3")

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

# --- 4. الروحي والأدعية ---
with tab_spiritual:
    st.subheader("🤲 الأدعية والتهيئة النفسية")
    
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
            "🌸 سور وآيات مباركة",
            "📜 زيارة عاشوراء"
        ],
        horizontal=True
    )

    st.write("")

    if "قبل الدراسة" in dua_option:
        st.write("### 📖 أدعية قبل بداية الدراسة")
        st.markdown('<div class="dua-box">« اللَّهُمَّ أَخْرِجْنِي مِنْ ظُلُمَاتِ الوَهْمِ، وَأَكْرِمْنِي بِنُورِ الفَهْمِ، اللَّهُمَّ افْتَحْ عَلَيْنَا أَبْوَابَ رَحْمَتِكَ، وَانْشُرْ عَلَيْنَا خَزَائِنَ عُلُومِكَ بِرَحْمَتِكَ يَا أَرْحَمَ الرَّاحِمِينَ »</div>', unsafe_allow_html=True)

    elif "بعد الدراسة" in dua_option:
        st.write("### ✍️ دعاء بعد الانتهاء من الدراسة")
        st.markdown('<div class="dua-box">« اللَّهُمَّ إِنِّي تَوَكَّلْتُ عَلَيْكَ، وَسَلَّمْتُ أَمْرِي إِلَيْكَ، لَا مَلْجَأَ وَلَا مَنْجَى مِنْكَ إِلَّا إِلَيْكَ.. اللَّهُمَّ إِنِّي أَسْتَوْدِعُكَ مَا قَرَأْتُ وَمَا حَفِظْتُ وَمَا تَعَلَّمْتُ، فَرُدَّهُ لِي عِنْدَ حَاجَتِي إِلَيْهِ، إِنَّكَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، وَحَسْبُنَا اللَّهُ وَنِعْمَ الوَكِيلُ »</div>', unsafe_allow_html=True)

    elif "بعد الصلاة" in dua_option:
        st.write("### 🕌 دعاء بعد كل صلاة لزيادة الحفظ")
        st.markdown('<div class="dua-box">« سُبْحَانَ مَنْ لَا يَعْتَدِي عَلَى أَهْلِ مَمْلَكَتِهِ، سُبْحَانَ مَنْ لَا يَأْخُذُ أَهْلَ الأَرْضِ بِأَلْوَانِ العَذَابِ، سُبْحَانَ الرَّؤُوفِ الرَّحِيمِ.. اللَّهُمَّ اجْعَلْ لِي فِي قَلْبِي نُوراً وَبَصَراً وَفَهْماً وَعِلْماً، إِنَّكَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ »</div>', unsafe_allow_html=True)

    elif "أدعية الامتحان" in dua_option:
        st.write("### 📝 أدعية الامتحان")
        st.markdown('<div class="dua-box">« رَبِّ أَدْخِلْنِي مُدْخَلَ صِدْقٍ، وَأَخْرِجْنِي مُخْرَجَ صِدْقٍ، وَاجْعَلْ لِي مِنْ لَدُنْكَ سُلْطَاناً نَصِيراً.. اللَّهُمَّ لَا سَهْلَ إِلَّا مَا جَعَلْتَهُ سَهْلاً، وَأَنْتَ تَجْعَلُ الحَزْنَ إِذَا شِئْتَ سَهْلاً »</div>', unsafe_allow_html=True)

    elif "سور وآيات" in dua_option:
        st.write("### 🌸 سور وآيات التيسير والحفظ")
        
        with st.expander("📖 سورة الفاتحة", expanded=True):
            st.markdown('<div class="quran-box">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ ۝ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ۝ الرَّحْمَنِ الرَّحِيمِ ۝ مَالِكِ يَوْمِ الدِّينِ ۝ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ ۝ اهْدِنا الصِّرَاطَ الْمُسْتَقِيمَ ۝ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ</div>', unsafe_allow_html=True)
            
        with st.expander("✨ سورة يس (قلب القرآن الكريم)"):
            st.markdown("""
                <div class="quran-box" style="text-align: justify; font-size: 1.1rem; line-height: 2.4;">
                بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ<br>
                يس ۝ وَالْقُرْآنِ الْحَكِيمِ ۝ إِنَّكَ لَمِنَ الْمُرْسَلِينَ ۝ عَلَى صِرَاطٍ مُسْتَقِيمٍ ۝ تَنْزِيلَ الْعَزِيزِ الرَّحِيمِ ۝ لِتُنْذِرَ قَوْمًا مَا أُنْذِرَ آبَاؤُهُمْ فَهُمْ غَافِلُونَ ۝ لَقَدْ حَقَّ الْقَوْلُ عَلَى أَكْثَرِهِمْ فَهُمْ لَا يُؤْمِنُونَ ۝ إِنَّا جَعَلْنَا فِي أَعْنَاقِهِمْ أَغْلَالًا فَهِيَ إِلَى الْأَذْقَانِ فَهُمْ مُقْمَحُونَ ۝ وَجَعَلْنَا مِنْ بَيْنِ أَيْدِيهِمْ سَدًّا وَمِنْ خَلْفِهِمْ سَدًّا فَأَغْشَيْنَاهُمْ فَهُمْ لَا يُبْصِرُونَ...<br><br>
                <i>(💡 يُنصح بقراءة السورة المباركة كاملة من المصحف الشريف قبل البدء بالمذاكرة لزيادة الفهم والبركة).</i>
                </div>
            """, unsafe_allow_html=True)

    elif "زيارة عاشوراء" in dua_option:
        st.write("### 📜 زيارة عاشوراء الشريفة")
        
        with st.expander("✨ اضغط هنا لقراءة نص زيارة عاشوراء", expanded=True):
            st.markdown("""
                <div class="quran-box" style="text-align: justify; font-size: 1.1rem; line-height: 2.4;">
                السَّلامُ عَلَيْكَ يا أبا عَبْدِ اللهِ، السَّلامُ عَلَيْكَ يابْنَ رَسُولِ اللهِ، السَّلامُ عَلَيْكَ يابْنَ أمِيرِ الماؤْمِنِينَ وَابْنَ سَيِّدِ الوَصِيِّينَ، السَّلامُ عَلَيْكَ يابْنَ فاطِمَةَ سَيِّدَةِ نِساءِ العالَمِينَ، السَّلامُ عَلَيْكَ يا ثارَ اللهِ وَابْنَ ثارِهِ وَالوِتْرَ المَوْتُورَ، السَّلامُ عَلَيْكَ وَعَلى الأَرْواحِ الَّتِي حَلَّتْ بِفِنائِكَ عَلَيْكُمْ مِنِّي جَمِيعاً سَلامُ اللهِ أَبَداً ما بَقِيتُ وَبَقِيَ اللَّيْلُ وَالنَّهارُ...<br><br>
                يا أبا عَبْدِ اللهِ، لَقَدْ عَظُمَتِ الرَّزِيَّةُ وَجَلَّتْ وَعَظُمَتِ المُصِيبَةُ بكَ عَلَيْنا وَعَلى جَمِيعِ أَهْلِ الإِسْلامِ، وَجَلَّتْ وَعَظُمَتْ مُصِيبَتُكَ فِي السَّماواتِ عَّلى جَمِيعِ أَهْلِ السَّماواتِ...<br><br>
                اللَّهُمَّ اجْعَلْنِي فِي مَقامِي هذا مِمَّنْ تَنالُهُ مِنْكَ صَلَواتٌ وَرَحْمَةٌ وَمَغْفِرَةٌ.. اللَّهُمَّ اجْعَلْ مَحْيايَ مَحْيا مُحَمَّدٍ وَآلِ مُحَمَّدٍ، وَمَماتِي مَماتَ مُحَمَّدٍ وَآلِ مُحَمَّدٍ.
                </div>
            """, unsafe_allow_html=True)

# --- 5. النصائح والإرشادات ---
with tab_tips:
    st.subheader("💡 نصائح وإرشادات التميز الدراسي")
    
    tip_category = st.radio(
        "اختر محور النصائح:",
        [
            "🧠 التفكير المعرفي",
            "⚡ تقوية الحفظ",
            "🕌 أهمية الصلوات الخمس",
            "📜 أثر زيارة عاشوراء للدراسة"
        ],
        horizontal=True
    )

    st.divider()

    if "زيارة عاشوراء" in tip_category:
        st.write("### 📜 أهمية وأثر قراءة زيارة عاشوراء يومياً وأثناء فترة الدراسة")
        st.success("🌸 **1. طمأنينة النفس وراحة البال:** المداومة اليومية على زيارة عاشوراء تبث في القلب السكينة وتزيل الخوف والقلق المتزايد من الامتحانات.")
        st.info("🧠 **2. صفاء الذهن والبرود العصبي:** تمنح الطالب ثباتاً انفعالياً وعصبي أثناء المذاكرة، مما يقلل من التشتت والنسيان السريع.")
        st.warning("🕊️ **3. التوفيق والبركة في الوقت:** تجعل في وقت المذاكرة بركة وتسييراً كبيراً، بحيث يستوعب الطالب الحفظ والفهم بسرعة.")

    elif "الصلوات الخمس" in tip_category:
        st.write("### 🕌 الصلوات الخمس: سرُّ البركة والسكينة")
        st.success("✨ **ميزان الوقت وتنظيمه:** أداء الصلاة في وقتها يبني جدول دراستك ببركة ونظام ممتاز لليوم.")
        st.info("🧠 **تجديد الطاقة وتصفية الذهن:** الوقوف بين يدي الله يفرغ عقلك من إجهاد الحفظ والتركيز.")

    else:
        st.write("### 🧠 العقلية الإيجابية وتقوية الحفظ")
        st.info("🔹 اختر مكاناً مريحاً وإضاءة ممتازة، واحرص على النوم المبكر وتنظيم وقتك بين الدراسة والراحة.")

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
            "التوقيت": ["6:30 ص - 7:30 ص", "8:00 ص - 1:00 م", "1:30 م - 3:00 م", "3:30 م - 6:00 م", "10:00 م"],
            "النشاط المقترح": ["⚡ مراجعة سريعة", "🏫 الدوام المدرسي الحضوري", "🍽️ استراحة وغداء", "🧠 المراجعة الفكرية والعلوم", "😴 النوم المبكر"]
        }
        st.table(pd.DataFrame(data_morning))
    else:
        st.write("### 🌤️ جدول الدوام الظهري")
        data_afternoon = {
            "التوقيت": ["7:00 ص - 8:30 ص", "9:00 ص - 11:30 ص", "1:00 م - 5:00 م", "7:00 م - 9:30 م", "10:30 م"],
            "النشاط المقترح": ["🌅 المواد العلمية والرياضيات", "📖 المواد النظرية والواجبات", "🏫 الدوام المدرسي الظهري", "📝 حل تمارين وتجهيز غداً", "😴 النوم واستراحة"]
        }
        st.table(pd.DataFrame(data_afternoon))
