import streamlit as st
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import string
from datetime import datetime
import re

# Initialize VADER Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Page Setup
st.set_page_config(
    page_title="Pre-Exam Anxiety Checker", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile-first responsive adjusting
st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 16px;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 20 Anxiety related keywords/phrases to boost the score
ANXIETY_KEYWORDS = {
    'nervous': 0.15,
    'panic': 0.25,
    'fail': 0.20,
    'failing': 0.20,
    'anxious': 0.15,
    "can't sleep": 0.20,
    'cannot sleep': 0.20,
    'scared': 0.15,
    'terrified': 0.25,
    'worried': 0.10,
    'overwhelmed': 0.20,
    'blank': 0.15,
    'sweat': 0.10,
    'racing heart': 0.20,
    'stress': 0.15,
    'stressed': 0.15,
    'pressure': 0.10,
    'dread': 0.20,
    'give up': 0.25,
    'doom': 0.25
}

def analyze_anxiety(text):
    """
    Analyzes the text to calculate an anxiety score and level.
    """
    if not text.strip():
        return 0.0, "Low"
    
    # 1. Preprocess: lower case for keyword matching
    text_lower = text.lower()
    
    # 2. VADER compound score (focusing on negative)
    # Compound ranges from -1 (most extreme negative) to +1 (most extreme positive)
    # We focus on the magnitude of the negative sentiment.
    sentiment = analyzer.polarity_scores(text)
    compound = sentiment['compound']
    
    # Base score: If compound is negative, we take its absolute value as base anxiety
    base_score = abs(compound) if compound < 0 else 0.0
    
    # 3. Keyword Boosting
    boost = 0.0
    for keyword, weight in ANXIETY_KEYWORDS.items():
        # Using word boundaries to avoid partial matches where possible
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            boost += weight
            
    # Final Score with cap at 1.0
    final_score = min(1.0, base_score + boost)
    
    # 4. Map to Level
    if final_score < 0.3:
        level = "Low"
    elif final_score <= 0.6:
        level = "Moderate"
    else:
        level = "High"
        
    return final_score, level

def get_tips(level):
    """
    Return personalized tips based on anxiety level.
    """
    if level == "Low":
        return [
            "Keep up the good work! You're in a manageable state.",
            "Review your notes lightly without cramming tomorrow.",
            "Ensure you get a good night's sleep before the exam."
        ]
    elif level == "Moderate":
        return [
            "Take a short break. Step away from your desk for 10-15 minutes.",
            "Drink some water and do light stretching to release tension.",
            "Remind yourself of what you have already accomplished and know well."
        ]
    else:
        return [
            "Deep breaths: Inhale 4s, hold 4s, exhale 4s.",
            "Ground yourself: Name 3 things you can see, 2 you can touch, 1 you can hear.",
            "Stop studying for now. Your brain needs rest to perform well; step away completely."
        ]

# Data Layer (In-memory via Streamlit Session State)
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar for History
with st.sidebar:
    st.header("Session History")
    if st.button("Clear History", use_container_width=True):
        st.session_state.history = []
        st.success("History cleared!")
    
    # Display last 5 analyses in reverse chronological order
    recent_history = list(reversed(st.session_state.history))[:5]
    if not recent_history:
        st.info("No analyses yet.")
    
    for item in recent_history:
        st.markdown(f"**{item['timestamp']}**")
        st.caption(f"Score: {item['score']:.2f} | Level: {item['level']}")
        st.text(f"\"{item['text'][:40]}...\"")
        st.markdown("---")

# Presentation Layer (Main UI)
st.title("Pre-Exam Anxiety Checker")
st.write("Share your thoughts or feelings about your upcoming exams. We'll analyze your anxiety level and provide instant tips.")

user_input = st.text_area(
    "How are you feeling right now?", 
    height=150, 
    placeholder="E.g., I'm so nervous about the exam tomorrow, I might fail everything."
)

if st.button("Analyze", type="primary", use_container_width=True):
    if user_input.strip():
        # Application Layer execution
        score, level = analyze_anxiety(user_input)
        
        # Save to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.history.append({
            "text": user_input,
            "score": score,
            "level": level,
            "timestamp": timestamp
        })
        
        st.divider()
        st.subheader("Analysis Results")
        
        # Level Badge/Notification
        if level == "Low":
            st.success(f"**Anxiety Level:** {level}")
        elif level == "Moderate":
            st.warning(f"**Anxiety Level:** {level}")
        else:
            st.error(f"**Anxiety Level:** {level}")
            
        # Score Bar
        st.progress(score)
        st.caption(f"**Anxiety Score:** {score:.2f} / 1.00")
        st.write("")
        
        # Personalized Tips
        st.markdown("### Calming Tips")
        tips = get_tips(level)
        for tip in tips:
            st.markdown(f"- {tip}")
            
    else:
        st.error("Please enter some text to analyze.")
