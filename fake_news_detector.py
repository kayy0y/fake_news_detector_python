import streamlit as st
import re
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .big-font {
        font-size: 50px !important;
        font-weight: bold;
        text-align: center;
        color: #1e3a8a;
    }
    </style>
    """, unsafe_allow_html=True)


class SimpleFakeNewsDetector:
    """Simplified NLP-based fake news detection system"""
    
    def __init__(self):
        # Fake news indicators 
        self.indicators = {
            'sensational': {
                'keywords': ['shocking', 'unbelievable', 'you won\'t believe', 'secret revealed', 
                           'they don\'t want you to know', 'amazing', 'incredible', 'must see', 
                           'breaking', 'exclusive', 'bombshell', 'stunning'],
                'weight': 2.0
            },
            'emotional': {
                'keywords': ['outraged', 'furious', 'devastated', 'terrified', 'shocked', 
                           'appalled', 'disgusted', 'horrified', 'enraged', 'panic'],
                'weight': 1.5
            },
            'clickbait': {
                'keywords': ['click here', 'find out', 'what happens next', 'number', 
                           'will shock you', 'hate him', 'this one trick', 'doctors hate',
                           'weird trick', 'you need to see'],
                'weight': 2.5
            },
            'absolute': {
                'keywords': ['always', 'never', 'everyone', 'nobody', 'all', 'none', 
                           'completely', 'totally', 'absolutely', 'definitely'],
                'weight': 1.0
            },
            'conspiracy': {
                'keywords': ['conspiracy', 'cover up', 'hidden agenda', 'illuminati', 
                           'deep state', 'they', 'them', 'wake up', 'sheeple', 'truth'],
                'weight': 3.0
            },
            'urgency': {
                'keywords': ['urgent', 'immediately', 'right now', 'hurry', 'limited time', 
                           'act fast', 'before it\'s too late', 'don\'t wait', 'last chance'],
                'weight': 1.5
            },
            'unnamed_sources': {
                'keywords': ['sources say', 'experts claim', 'studies show', 'people are saying',
                           'many believe', 'some say', 'it is believed', 'reportedly'],
                'weight': 2.0
            }
        }
        
        # Credibility indicators
        self.credibility_markers = {
            'attribution': ['according to', 'stated', 'said', 'reported', 'confirmed', 'announced'],
            'sources': ['university', 'institute', 'journal', 'research', 'study', 'published in'],
            'dates': ['2024', '2025', 'january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december']
        }
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        text = text.lower()
        text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
        return text
    
    def detect_fake_indicators(self, text):
        """Detect fake news indicators in text"""
        preprocessed = self.preprocess_text(text)
        indicator_counts = {}
        total_score = 0
        
        for category, data in self.indicators.items():
            count = 0
            found_keywords = []
            
            for keyword in data['keywords']:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, preprocessed)
                if matches:
                    count += len(matches)
                    found_keywords.append(keyword)
            
            if count > 0:
                indicator_counts[category] = {
                    'count': count,
                    'keywords': found_keywords,
                    'weight': data['weight']
                }
                total_score += count * data['weight']
        
        return indicator_counts, total_score
    
    def detect_credibility_markers(self, text):
        """Detect credibility markers"""
        preprocessed = self.preprocess_text(text)
        credibility_score = 0
        markers_found = {}
        
        for category, keywords in self.credibility_markers.items():
            count = 0
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, preprocessed)
                count += len(matches)
            
            if count > 0:
                markers_found[category] = count
                credibility_score += count
        
        return markers_found, credibility_score
    
    def analyze_text_features(self, text):
        """Analyze various text features"""
        words = text.split()
        sentences = text.split('.')
        
        # Count features
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        
        # Capitalization abuse
        caps_words = [word for word in words if word.isupper() and len(word) > 2]
        caps_ratio = len(caps_words) / max(word_count, 1)
        
        # Excessive punctuation
        excessive_punct = len(re.findall(r'[!?]{2,}', text))
        
        # Question ratio
        questions = len([s for s in sentences if s.strip().endswith('?')])
        question_ratio = questions / max(sentence_count, 1)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'caps_ratio': caps_ratio,
            'excessive_punctuation': excessive_punct,
            'question_ratio': question_ratio
        }
    
    def calculate_final_score(self, fake_score, credibility_score, text_features):
        """Calculate final fake news probability score"""
        # Normalize scores
        normalized_fake_score = min(100, (fake_score / 50) * 100)
        normalized_cred_score = min(100, (credibility_score / 20) * 100)
        
        # Text complexity bonus 
        complexity_bonus = 0
        if text_features['word_count'] > 100 and text_features['avg_word_length'] > 5:
            complexity_bonus = 10
        
        # Caps and punctuation penalty
        style_penalty = (text_features['caps_ratio'] * 20) + (text_features['excessive_punctuation'] * 5)
        
        # Calculate final score
        final_score = normalized_fake_score - (normalized_cred_score * 0.3) - complexity_bonus + style_penalty
        final_score = max(0, min(100, final_score))
        
        return round(final_score, 2)
    
    def get_verdict(self, score):
        """Get verdict based on score"""
        if score < 30:
            return {
                'label': '✅ Likely Reliable',
                'color': 'green',
                'description': 'This article shows characteristics of reliable news.',
                'recommendation': 'Still verify with multiple trusted sources.'
            }
        elif score < 60:
            return {
                'label': '⚠️ Questionable',
                'color': 'orange',
                'description': 'This article shows some red flags.',
                'recommendation': 'Verify information carefully before sharing.'
            }
        else:
            return {
                'label': '🚨 Likely Fake/Misleading',
                'color': 'red',
                'description': 'This article shows strong indicators of fake or misleading news.',
                'recommendation': 'Exercise extreme caution. Do not share without verification.'
            }
    
    def analyze(self, text):
        """Main analysis function"""
        if not text or len(text.strip()) < 10:
            return None
        
        # Run all analyses
        indicators, fake_score = self.detect_fake_indicators(text)
        markers, cred_score = self.detect_credibility_markers(text)
        text_features = self.analyze_text_features(text)
        
        # Calculate final score
        final_score = self.calculate_final_score(fake_score, cred_score, text_features)
        verdict = self.get_verdict(final_score)
        
        return {
            'score': final_score,
            'verdict': verdict,
            'indicators': indicators,
            'credibility_markers': markers,
            'text_features': text_features
        }


# Initialize detector
@st.cache_resource
def get_detector():
    return SimpleFakeNewsDetector()

detector = get_detector()

# App Header
st.markdown('<p class="big-font">📰 Fake News Detector</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b; font-size: 18px;">Advanced NLP-Powered Analysis for Detecting Misleading Content</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📋 About")
    st.write("""
    This app uses advanced Natural Language Processing (NLP) techniques to analyze news articles 
    and detect potential fake or misleading content.
    
    **Features:**
    - Pattern Recognition
    - Fake News Indicator Detection
    - Credibility Marker Analysis
    - Text Complexity Assessment
    - Style Analysis
    """)
    
    st.header("🔬 Analysis Methods")
    st.code("• Pattern Matching\n• Regex Analysis\n• Statistical Analysis")
    
    st.header("💡 Tips")
    st.info("""
    - Check multiple sources
    - Verify author credentials
    - Look for publication dates
    - Be skeptical of sensational headlines
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Enter News Article or Headline")
    text_input = st.text_area(
        "Paste your text here:",
        height=200,
        placeholder="Enter the news article or headline you want to analyze...",
        key="text_input"
    )
    
    # Example buttons
    st.write("**Try Examples:**")
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        if st.button("Reliable Example", key="ex1"):
            st.session_state.example_text = "Scientists at Harvard University published research in Nature journal showing climate change effects on coastal regions. The study, conducted over 5 years, analyzed data from 50 locations worldwide."
    
    with example_col2:
        if st.button("Fake Example", key="ex2"):
            st.session_state.example_text = "SHOCKING!!! You won't believe what they discovered! This one secret that THEY don't want you to know will change EVERYTHING! Click here now before it's too late!!!"
    
    with example_col3:
        if st.button("Mixed Example", key="ex3"):
            st.session_state.example_text = "According to a report released by the World Health Organization on January 15, 2024, vaccination rates have increased by 12% globally compared to last year."

# Display example text if button was clicked
if 'example_text' in st.session_state:
    text_input = st.session_state.example_text

with col2:
    st.subheader("🎯 Quick Stats")
    if text_input:
        char_count = len(text_input)
        word_count = len(text_input.split())
        st.metric("Characters", char_count)
        st.metric("Words", word_count)
    else:
        st.info("Enter text to see statistics")

# Analyze button
if st.button("🔍 Analyze Article", type="primary", use_container_width=True):
    if not text_input or len(text_input.strip()) < 10:
        st.error("⚠️ Please enter at least 10 characters of text to analyze.")
    else:
        with st.spinner("🔄 Analyzing text with NLP algorithms..."):
            result = detector.analyze(text_input)
            
            if result:
                st.markdown("---")
                st.subheader("📊 Analysis Results")
                
                # Score display
                score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
                
                with score_col2:
                    verdict = result['verdict']
                    st.markdown(f"<h1 style='text-align: center; color: {verdict['color']};'>{verdict['label']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align: center;'>{result['score']}/100</h2>", unsafe_allow_html=True)
                    
                    # Progress bar
                    st.progress(result['score'] / 100)
                    
                    if result['score'] < 30:
                        st.success(verdict['description'])
                    elif result['score'] < 60:
                        st.warning(verdict['description'])
                    else:
                        st.error(verdict['description'])
                    
                    st.info(f"**Recommendation:** {verdict['recommendation']}")
                
                # Detailed metrics
                st.markdown("---")
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric("Fake News Score", f"{result['score']}/100")
                    st.metric("Word Count", result['text_features']['word_count'])
                
                with metric_col2:
                    st.metric("Avg Word Length", f"{result['text_features']['avg_word_length']:.1f}")
                    st.metric("Sentences", result['text_features']['sentence_count'])
                
                with metric_col3:
                    st.metric("CAPS Abuse", f"{result['text_features']['caps_ratio']:.1%}")
                    st.metric("Exclamation Abuse", result['text_features']['excessive_punctuation'])
                
                # Red flags detected
                st.markdown("---")
                st.subheader("🚩 Red Flags Detected")
                
                if result['indicators']:
                    for category, data in sorted(result['indicators'].items(), key=lambda x: x[1]['count'], reverse=True):
                        with st.expander(f"**{category.replace('_', ' ').title()}** - Found {data['count']} times"):
                            st.write(f"**Severity Weight:** {data['weight']}")
                            st.write(f"**Keywords Found:** {', '.join(data['keywords'][:5])}")
                else:
                    st.success("✅ No major red flags detected!")
                
                # Credibility markers
                st.markdown("---")
                st.subheader("✅ Credibility Markers")
                
                if result['credibility_markers']:
                    cred_cols = st.columns(len(result['credibility_markers']))
                    for idx, (category, count) in enumerate(result['credibility_markers'].items()):
                        with cred_cols[idx]:
                            st.metric(category.title(), count)
                else:
                    st.warning("⚠️ No credibility markers found")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b;'>
    <p>Built with Python & Streamlit | Advanced NLP for Fake News Detection</p>
    <p>⚠️ This tool is for educational purposes. Always verify information from multiple trusted sources.</p>
</div>
""", unsafe_allow_html=True)
