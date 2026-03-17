"""
Task 1: AI Video Generation Tool
Pipeline: Scrape trending news → Generate script via OpenAI → Create video with DALL-E generated images
"""

import streamlit as st
import requests
import json
import os
import tempfile
import textwrap
import traceback
import random
from pathlib import Path
from datetime import datetime
from io import BytesIO

# ── Optional heavy deps ───────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
    PIL_OK = True
except ImportError as e:
    PIL_OK = False
    PIL_ERROR = str(e)

try:
    from openai import OpenAI, AuthenticationError, RateLimitError
    OPENAI_OK = True
except ImportError as e:
    OPENAI_OK = False
    OPENAI_ERROR = str(e)

try:
    import cv2
    import numpy as np
    CV2_OK = True
except ImportError as e:
    CV2_OK = False
    CV2_ERROR = str(e)


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY-SPECIFIC MOCK DATA
# ─────────────────────────────────────────────────────────────────────────────
MOCK_NEWS_BY_CATEGORY = {
    "technology": [
        {
            "title": "Apple Unveils Revolutionary AI-Powered iPhone with On-Device Intelligence",
            "description": "The new iPhone features advanced AI capabilities that process data locally, enhancing privacy and performance.",
            "source": "TechCrunch",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Google's Quantum Computer Achieves Major Breakfast in Computing Speed",
            "description": "Sycamore processor solves complex problem in seconds that would take supercomputers 10,000 years.",
            "source": "Wired",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Meta Launches Open-Source AI Model Challenging GPT-4",
            "description": "Llama 3 shows competitive performance while being freely available to researchers.",
            "source": "The Verge",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Tesla's Optimus Robot Now Performs Complex Factory Tasks",
            "description": "Humanoid robot demonstrates advanced manipulation skills in manufacturing environment.",
            "source": "Tech Insider",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Breakthrough in Solid-State Battery Technology Promises 1000km Range",
            "description": "New electrolyte material could revolutionize electric vehicle industry.",
            "source": "Energy Tech",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        }
    ],
    "business": [
        {
            "title": "Stock Market Hits All-Time High as Tech Stocks Surge",
            "description": "Nasdaq leads gains with AI companies reporting record quarterly profits.",
            "source": "Financial Times",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Federal Reserve Signals Interest Rate Cuts Later This Year",
            "description": "Markets rally as central bank hints at easing monetary policy.",
            "source": "Bloomberg",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Microsoft Announces $50 Billion Share Buyback Program",
            "description": "Tech giant returns value to shareholders amid strong cloud computing growth.",
            "source": "Reuters",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Inflation Cools to 3-Year Low, Consumer Spending Remains Strong",
            "description": "Economic data suggests soft landing achieved without severe recession.",
            "source": "WSJ",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Tesla Overtakes Toyota as World's Most Valuable Automaker",
            "description": "EV manufacturer's market cap surges on delivery numbers and AI ambitions.",
            "source": "CNBC",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        }
    ],
    "science": [
        {
            "title": "NASA's Perseverance Rover Discovers Signs of Ancient Microbial Life on Mars",
            "description": "Organic molecules and unique rock formations suggest past habitable conditions.",
            "source": "NASA",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "CRISPR Gene Editing Successfully Treats Sickle Cell Disease",
            "description": "Clinical trial shows promising results for genetic disorder treatment.",
            "source": "Science Daily",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "New Quantum Entanglement Record Set at 50 Kilometers",
            "description": "Breakthrough brings quantum internet one step closer to reality.",
            "source": "Physics World",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Deep-Sea Expedition Discovers Over 100 New Species",
            "description": "Biodiversity hotspot found in previously unexplored Pacific trench.",
            "source": "Nature",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Fusion Energy Breakthrough: Net Energy Gain Achieved Again",
            "description": "National Ignition Facility replicates successful fusion experiment with higher yield.",
            "source": "Science",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        }
    ],
    "health": [
        {
            "title": "New Alzheimer's Drug Shows 35% Reduction in Cognitive Decline",
            "description": "Phase 3 trial results bring hope to millions of patients worldwide.",
            "source": "Medical News",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "WHO Declares New Variant of Interest as Cases Rise in Asia",
            "description": "Health officials monitor spread but say current vaccines remain effective.",
            "source": "WHO",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Breakthrough in Personalized Cancer Vaccine Shows Promise",
            "description": "mRNA technology trains immune system to target specific tumor types.",
            "source": "Health Weekly",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Study Reveals Mediterranean Diet Extends Lifespan by 10 Years",
            "description": "Long-term research confirms benefits of olive oil, nuts, and fish consumption.",
            "source": "Nutrition Journal",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Mental Health App Prescribed by NHS Shows 40% Improvement in Symptoms",
            "description": "Digital therapy proves effective for anxiety and depression treatment.",
            "source": "Psychiatry News",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        }
    ],
    "entertainment": [
        {
            "title": "Oppenheimer Wins Best Picture at Academy Awards",
            "description": "Christopher Nolan's biopic takes home seven Oscars including Best Director.",
            "source": "Variety",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Taylor Swift's Eras Tour Becomes Highest-Grossing Tour in History",
            "description": "Pop superstar surpasses $1 billion in ticket sales across 60 shows.",
            "source": "Billboard",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Netflix Gains 10 Million Subscribers Following Password-Sharing Crackdown",
            "description": "Streaming giant reports best quarter in years as ad-tier grows.",
            "source": "Hollywood Reporter",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Beyoncé's Country Album Debuts at Number One, Makes History",
            "description": "First Black woman to top Billboard country charts with 'Cowboy Carter'.",
            "source": "Rolling Stone",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "GTA VI Trailer Breaks Viewership Records Within 24 Hours",
            "description": "Rockstar Games' next installment becomes most-watched video game trailer.",
            "source": "IGN",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        }
    ],
    "sports": [
        {
            "title": "Super Bowl LVIII Sets Viewership Record with Overtime Thriller",
            "description": "Kansas City Chiefs defeat San Francisco 49ers in most-watched telecast in history.",
            "source": "ESPN",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Paris Olympics: USA Dominates Medal Count as Swimming and Athletics Shine",
            "description": "Team USA surpasses 100 medals including 35 golds in historic performance.",
            "source": "Olympics",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Lionel Messi Leads Inter Miami to First-Ever MLS Cup Victory",
            "description": "Argentine superstar scores brace in final to secure historic treble.",
            "source": "MLS",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Caitlin Clark Breaks NCAA All-Time Scoring Record",
            "description": "Iowa guard passes Pete Maravich's record in electrifying performance.",
            "source": "Sports Illustrated",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Formula 1: Max Verstappen Wins Fourth Consecutive World Championship",
            "description": "Red Bull driver dominates season with record 20 wins in 22 races.",
            "source": "F1",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        }
    ],
    "general": [
        {
            "title": "Global Leaders Reach Historic Climate Agreement at COP Summit",
            "description": "Nations commit to phasing out fossil fuels and tripling renewable energy.",
            "source": "BBC",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Massive Cyberattack Disrupts Critical Infrastructure Across Europe",
            "description": "Ransomware group claims responsibility for attack on energy grid.",
            "source": "Reuters",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Historic Peace Agreement Signed Between Long-Standing Rivals",
            "description": "US-brokered deal ends decades of conflict in landmark ceremony.",
            "source": "AP News",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Major Earthquake Hits Region, International Aid Pours In",
            "description": "Rescue efforts continue as world community mobilizes support.",
            "source": "CNN",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        },
        {
            "title": "Breakthrough in Plastic-Eating Enzyme Offers Hope for Ocean Cleanup",
            "description": "Modified enzyme breaks down PET plastic in days instead of centuries.",
            "source": "Guardian",
            "url": "#",
            "published": datetime.now().isoformat(),
            "image": ""
        }
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# API KEY VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────
def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Returns (is_valid, error_message). Makes a cheap test call."""
    if not api_key or not api_key.strip():
        return False, "No API key provided — running in demo mode."
    if not api_key.startswith("sk-"):
        return False, "Key format looks wrong (should start with `sk-`). Demo mode active."
    try:
        client = OpenAI(api_key=api_key)
        client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}],
        )
        return True, ""
    except AuthenticationError:
        return False, "❌ Invalid API key — check platform.openai.com."
    except Exception as e:
        return False, f"❌ API error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Video Generator (DALL-E)", page_icon="🎬",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%); }
    .card { background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
            border-radius:12px;padding:1.2rem;margin-bottom:1rem; }
    .headline { font-size:1rem;font-weight:600;color:#f0f0f0;margin-bottom:0.3rem; }
    .meta { font-size:0.78rem;color:#888; }
    .category-badge { display:inline-block;background:#3a86ff22;color:#3a86ff;
                      border:1px solid #3a86ff55;border-radius:20px;padding:2px 10px;
                      font-size:0.72rem;margin-right:4px; }
    .tag { display:inline-block;background:#00b09b22;color:#00b09b;
           border:1px solid #00b09b55;border-radius:20px;padding:2px 10px;
           font-size:0.72rem;margin-right:4px; }
    .step-badge { background:#3a86ff;color:white;border-radius:50%;width:28px;height:28px;
                  display:inline-flex;align-items:center;justify-content:center;
                  font-weight:700;margin-right:8px; }
    .script-box { background:#1e1e2e;border-left:4px solid #3a86ff;padding:1rem;
                  border-radius:0 8px 8px 0;font-family:'Courier New',monospace;
                  font-size:0.9rem;line-height:1.6;white-space:pre-wrap; }
    .success-banner { background:linear-gradient(90deg,#00b09b22,#96c93d22);
                      border:1px solid #00b09b55;border-radius:10px;padding:1rem;
                      text-align:center;color:#00b09b;font-size:1.1rem;font-weight:600; }
    .error-banner { background:linear-gradient(90deg,#ff444422,#ff000022);
                    border:1px solid #ff4444;border-radius:10px;padding:1rem;
                    text-align:center;color:#ff4444;font-size:1.1rem;font-weight:600; }
    h1 { color:#3a86ff !important; }
    h2,h3 { color:#c0c0c0 !important; }
    .stProgress > div > div > div > div { background-color: #3a86ff; }
    div[data-testid="stImage"] { border-radius: 8px; border: 2px solid #3a86ff; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZE SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "articles" not in st.session_state:
    st.session_state.articles = []
if "script" not in st.session_state:
    st.session_state.script = None
if "generated_images" not in st.session_state:
    st.session_state.generated_images = {}
if "article" not in st.session_state:
    st.session_state.article = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", key="openai_key_input")

    if openai_key and st.button("✅ Verify Key", use_container_width=True, key="verify_key_btn"):
        with st.spinner("Verifying…"):
            ok, msg = validate_api_key(openai_key)
            if ok:
                st.session_state.api_key_valid = True
                st.success("Key is valid!")
            else:
                st.session_state.api_key_valid = False
                st.error(msg)
    
    if not openai_key:
        st.session_state.api_key_valid = False
        st.info("🔑 No key entered — demo mode active")

    news_api_key = st.text_input("NewsAPI Key (optional)", type="password", placeholder="for live news", key="news_api_key_input")
    st.divider()
    
    st.markdown("### 🎬 Video Settings")
    vid_duration = st.slider("Max video duration (sec)", 20, 60, 45, key="vid_duration_slider")
    resolution = st.selectbox("Resolution", ["1280x720", "1920x1080", "854x480"], index=0, key="resolution_select")
    fps = st.select_slider("FPS", options=[24, 30, 60], value=30, key="fps_slider")
    
    # DALL-E Settings
    st.markdown("### 🎨 DALL-E Settings")
    image_style = st.selectbox(
        "Image Style",
        ["photorealistic", "cinematic", "anime", "digital art", "comic book", "vibrant"],
        index=1,
        key="image_style_select"
    )
    use_dalle = st.checkbox("Use DALL-E for images", value=True, key="use_dalle_checkbox")
    
    st.divider()
    
    st.markdown("### 📰 News Settings")
    news_category = st.selectbox(
        "Category",
        ["technology", "business", "science", "health", "entertainment", "sports", "general"],
        key="news_category_select"
    )
    max_articles = st.slider("Articles to fetch", 3, 10, 5, key="max_articles_slider")
    st.divider()
    
    # Debug mode toggle
    debug_mode = st.checkbox("🔧 Debug Mode", value=st.session_state.debug_mode, key="debug_mode_checkbox")
    st.session_state.debug_mode = debug_mode
    
    st.caption("💡 OpenAI key → platform.openai.com")
    st.caption("💡 NewsAPI key → newsapi.org")
    
    # Show dependency status
    with st.expander("📦 Dependency Status"):
        st.write(f"OpenAI: {'✅' if OPENAI_OK else '❌'}")
        st.write(f"PIL: {'✅' if PIL_OK else '❌'}")
        if not PIL_OK and 'PIL_ERROR' in locals():
            st.caption(PIL_ERROR)
        st.write(f"OpenCV: {'✅' if CV2_OK else '❌'}")
        if not CV2_OK and 'CV2_ERROR' in locals():
            st.caption(CV2_ERROR)
        st.write(f"NumPy: {'✅' if 'numpy' in dir() else '❌'}")


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []
    if not PIL_OK:
        missing.append("Pillow (PIL)")
    if not CV2_OK:
        missing.append("opencv-python")
    if not OPENAI_OK:
        missing.append("openai")
    
    if missing and st.session_state.debug_mode:
        st.warning(f"⚠️ Missing dependencies: {', '.join(missing)}")
        st.info("Install missing packages: `pip install pillow opencv-python openai`")
        return False
    return True


def fetch_trending_news(api_key: str, category: str, count: int) -> list[dict]:
    """Fetch trending news articles from NewsAPI or return category-specific mock data"""
    if api_key:
        url = (f"https://newsapi.org/v2/top-headlines"
               f"?category={category}&pageSize={count}&language=en&apiKey={api_key}")
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                arts = r.json().get("articles", [])
                return [{"title": a.get("title", "Untitled"), 
                        "description": a.get("description", ""),
                        "source": a.get("source", {}).get("name", "Unknown"),
                        "url": a.get("url", ""), 
                        "published": a.get("publishedAt", ""),
                        "image": a.get("urlToImage", ""),
                        "category": category}
                        for a in arts if a.get("title")][:count]
            else:
                if st.session_state.debug_mode:
                    st.warning(f"NewsAPI returned status {r.status_code}. Using category-specific mock data.")
        except Exception as e:
            if st.session_state.debug_mode:
                st.warning(f"NewsAPI error: {e}. Using category-specific mock data.")

    # Return category-specific mock data
    mock_data = MOCK_NEWS_BY_CATEGORY.get(category, MOCK_NEWS_BY_CATEGORY["general"])
    
    # Add category to each article
    articles = []
    for article in mock_data[:count]:
        article_copy = article.copy()
        article_copy["category"] = category
        articles.append(article_copy)
    
    # Shuffle to make it feel more dynamic
    random.shuffle(articles)
    
    return articles


def generate_script(api_key: str, article: dict, duration: int) -> dict:
    """Generate a structured video script using OpenAI GPT-4o-mini."""
    DEMO = {
        "hook": f"🔥 {article['category'].title()} Alert: {article['title'][:60]}...",
        "body": (article.get("description") or f"Latest updates from the {article['category']} world."),
        "cta": f"Follow for more {article['category']} news! 🔔",
        "hashtags": [f"#{article['category']}", "#trending", "#news", "#breaking", "#update"],
        "title": article['title'][:50],
        "duration": duration,
        "category": article['category']
    }

    if not api_key or not api_key.startswith("sk-") or not st.session_state.api_key_valid:
        return DEMO

    try:
        client = OpenAI(api_key=api_key)
        prompt = f"""You are a professional short-form video scriptwriter for social media specializing in {article['category']} news.

Create a {duration}-second video script for this {article['category']} news article:
Title: {article['title']}
Description: {article.get('description', '')}
Source: {article.get('source', '')}
Category: {article['category']}

Return ONLY valid JSON with these exact keys:
{{
  "hook": "Opening 1-2 sentences to grab attention (max 15 words) - must be relevant to {article['category']}",
  "body": "Core story in 3-4 punchy sentences (max 60 words) - focus on {article['category']} details",
  "cta": "Call-to-action closing line (max 10 words) - encourage following for more {article['category']} news",
  "hashtags": ["list", "of", "5", "relevant", "hashtags", "including", f"#{article['category']}"],
  "title": "Short title for the video overlay (max 8 words)"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=512,
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": f"You are a {article['category']} news video scriptwriter. Always return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        )
        result = json.loads(response.choices[0].message.content.strip())
        result["duration"] = duration
        result["category"] = article['category']
        return result

    except Exception as e:
        if st.session_state.debug_mode:
            st.warning(f"⚠️ Script generation error: {e}. Using demo script.")
        return DEMO


def generate_dalle_image(api_key: str, prompt: str, style: str, category: str, size="1024x1024") -> Image.Image:
    """Generate an image using DALL-E 3 with category-specific context"""
    try:
        client = OpenAI(api_key=api_key)
        
        # Enhance prompt with style and category
        style_prompts = {
            "photorealistic": "photorealistic, highly detailed, 4k quality, sharp focus",
            "cinematic": "cinematic lighting, dramatic composition, movie poster style, high contrast",
            "anime": "anime style, vibrant colors, cel-shaded, manga aesthetic",
            "digital art": "digital art, trending on artstation, creative, artistic",
            "comic book": "comic book style, bold lines, vibrant colors, pop art aesthetic",
            "vibrant": "vibrant colors, high saturation, dynamic lighting, eye-catching"
        }
        
        # Category-specific visual cues
        category_cues = {
            "technology": "futuristic, tech, digital, circuit boards, innovation",
            "business": "professional, corporate, financial, charts, graphs, suits",
            "science": "laboratory, scientific, research, microscope, DNA helix, atoms",
            "health": "medical, healthcare, wellness, hospital, doctor, patient care",
            "entertainment": "glamorous, red carpet, stage, performance, celebrity",
            "sports": "action shot, stadium, athlete in motion, competitive spirit",
            "general": "news studio, journalistic, professional broadcast"
        }
        
        category_cue = category_cues.get(category, "news, journalistic")
        style_prompt = style_prompts.get(style, "high quality, detailed")
        
        enhanced_prompt = f"{prompt}. {category_cue}. {style_prompt}"
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=size,
            quality="standard",
            n=1,
        )
        
        # Download the image
        image_url = response.data[0].url
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        
        return img
        
    except RateLimitError:
        if st.session_state.debug_mode:
            st.warning("⚠️ DALL-E rate limit reached. Using fallback image.")
        return None
    except Exception as e:
        if st.session_state.debug_mode:
            st.warning(f"⚠️ DALL-E generation failed: {e}. Using fallback image.")
        return None


def create_fallback_image(width: int, height: int, text: str, category: str = "general", accent_color=(58, 134, 255)) -> Image.Image:
    """Create a category-specific fallback image with gradient background"""
    try:
        # Category-specific colors
        category_colors = {
            "technology": (58, 134, 255),  # Blue
            "business": (0, 176, 155),      # Green
            "science": (156, 39, 176),      # Purple
            "health": (244, 67, 54),        # Red
            "entertainment": (255, 152, 0),  # Orange
            "sports": (33, 150, 243),        # Light Blue
            "general": (58, 134, 255)        # Default Blue
        }
        
        accent_color = category_colors.get(category, (58, 134, 255))
        
        # Create gradient background
        img = Image.new("RGB", (width, height), (15, 15, 26))
        draw = ImageDraw.Draw(img)
        
        # Draw category-specific accent bars
        draw.rectangle([0, 0, width, 8], fill=accent_color)
        draw.rectangle([0, height-8, width, height], fill=accent_color)
        
        # Draw category label
        font_size = min(60, width // 15)
        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "C:\\Windows\\Fonts\\Arial.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # Draw category header
        category_text = f"#{category.upper()} NEWS"
        try:
            bbox = draw.textbbox((0, 0), category_text, font=font)
            text_width = bbox[2] - bbox[0]
        except:
            text_width = len(category_text) * font_size // 2
        
        x = (width - text_width) // 2
        y = 30
        draw.text((x, y), category_text, font=font, fill=accent_color)
        
        # Draw main text
        text_lines = textwrap.wrap(text, width=30)
        line_height = font_size + 10
        total_height = len(text_lines) * line_height
        start_y = (height - total_height) // 2 + 30
        
        for i, line in enumerate(text_lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * font_size // 2
            
            x = (width - text_width) // 2
            y = start_y + i * line_height
            
            # Draw shadow
            draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 180))
            # Draw main text
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
        
        return img
        
    except Exception as e:
        # Ultra simple fallback
        img = Image.new("RGB", (width, height), accent_color)
        return img


def create_text_overlay(image: Image.Image, text: str, category: str = "general") -> Image.Image:
    """Add category-styled text overlay to an image"""
    try:
        # Category-specific colors
        category_colors = {
            "technology": (58, 134, 255),  # Blue
            "business": (0, 176, 155),      # Green
            "science": (156, 39, 176),      # Purple
            "health": (244, 67, 54),        # Red
            "entertainment": (255, 152, 0),  # Orange
            "sports": (33, 150, 243),        # Light Blue
            "general": (58, 134, 255)        # Default Blue
        }
        
        accent_color = category_colors.get(category, (58, 134, 255))
        
        # Create a copy of the image
        img = image.copy()
        
        # Create a semi-transparent overlay for text background
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load a font
        font_size = min(60, img.size[0] // 20)
        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "C:\\Windows\\Fonts\\Arial.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # Wrap text
        max_width = img.size[0] - 200
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(test_line) * font_size // 2
            
            if text_width > max_width and len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        if not lines:
            lines = [text[:50]]
        
        # Calculate text dimensions
        line_height = font_size + 20
        total_height = len(lines) * line_height
        bg_margin = 30
        
        # Draw semi-transparent background
        bg_width = img.size[0] - 200
        bg_height = total_height + (bg_margin * 2)
        bg_x = (img.size[0] - bg_width) // 2
        bg_y = (img.size[1] - bg_height) // 2
        
        bg_overlay = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 180))
        img.paste(bg_overlay, (bg_x, bg_y), bg_overlay)
        
        # Draw colored accent line
        accent_overlay = Image.new('RGBA', (bg_width, 4), accent_color + (200,))
        img.paste(accent_overlay, (bg_x, bg_y - 2), accent_overlay)
        
        # Draw text
        for i, line in enumerate(lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * font_size // 2
            
            x = (img.size[0] - text_width) // 2
            y = bg_y + bg_margin + i * line_height
            
            # Draw text with outline for better visibility
            for dx, dy in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 180))
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        # Convert overlay to RGB and composite
        overlay_rgb = Image.alpha_composite(img.convert('RGBA'), overlay)
        return overlay_rgb.convert('RGB')
        
    except Exception as e:
        if st.session_state.debug_mode:
            st.error(f"Error adding text overlay: {e}")
        return image


def generate_video_with_images(script: dict, images: dict, out_path: str, fps: int, width: int, height: int, progress_callback=None) -> str:
    """Generate video from images using OpenCV"""
    if not CV2_OK:
        st.error("OpenCV is not installed. Please install it with: pip install opencv-python")
        return None
    
    try:
        # Get category from script
        category = script.get("category", "general")
        
        # Calculate section durations
        total_duration = script.get("duration", 45)
        sections = [
            ("hook", max(5, int(total_duration * 0.2))),
            ("body", max(15, int(total_duration * 0.6))),
            ("cta", max(4, int(total_duration * 0.1))),
            ("hashtags", max(4, int(total_duration * 0.1))),
        ]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            st.error("Failed to create video writer")
            return None
        
        total_frames = sum(duration * fps for _, duration in sections)
        frames_processed = 0
        
        for section_name, duration in sections:
            # Get or create image for this section
            if section_name in images and images[section_name] is not None:
                img = images[section_name]
            else:
                # Create category-specific fallback image
                text = script.get(section_name, "")
                if section_name == "hashtags":
                    text = " ".join(script.get("hashtags", [f"#{category}"]))
                img = create_fallback_image(width, height, text, category)
            
            # Resize image to match video dimensions
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Add category-styled text overlay
            text = script.get(section_name, "")
            if section_name == "hashtags":
                text = " ".join(script.get("hashtags", []))
            
            img_with_text = create_text_overlay(img, text, category)
            
            # Convert PIL to numpy array
            frame = np.array(img_with_text)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Write frames
            section_frames = duration * fps
            for frame_num in range(section_frames):
                out.write(frame)
                frames_processed += 1
                if progress_callback:
                    progress_callback(frames_processed / total_frames, f"Rendering {category} {section_name}...")
        
        out.release()
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return out_path
        else:
            st.error("Video file was not created successfully")
            return None
            
    except Exception as e:
        st.error(f"Video generation error: {str(e)}")
        if st.session_state.debug_mode:
            st.code(traceback.format_exc())
        return None


# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 🎬 AI Video Generation Tool")
st.markdown("*Category-specific trending news → AI script → DALL-E images → Video with overlays*")
st.divider()

# Check dependencies
check_dependencies()

# Show debug info if enabled
if st.session_state.debug_mode:
    with st.expander("🔧 Debug Information", expanded=True):
        st.markdown("### System Status")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**OpenAI:** {'✅' if OPENAI_OK else '❌'}")
            st.markdown(f"**PIL:** {'✅' if PIL_OK else '❌'}")
        with col2:
            st.markdown(f"**OpenCV:** {'✅' if CV2_OK else '❌'}")
            st.markdown(f"**NumPy:** {'✅' if 'numpy' in dir() else '❌'}")
        with col3:
            st.markdown(f"**Python:** {os.sys.version[:20]}")
            st.markdown(f"**API Key Valid:** {'✅' if st.session_state.api_key_valid else '❌'}")
            st.markdown(f"**Selected Category:** {news_category}")
        
        if st.session_state.script:
            st.json(st.session_state.script)

# STEP 1 ── Fetch News
st.markdown("### <span class='step-badge'>1</span> Fetch Trending News", unsafe_allow_html=True)
c1, c2 = st.columns([3, 1])
with c1:
    st.info(f"Category: **{news_category.upper()}** | Articles: **{max_articles}**")
with c2:
    fetch_btn = st.button("🔍 Fetch News", use_container_width=True, type="primary", key="fetch_news_btn")

if fetch_btn:
    with st.spinner(f"Fetching {news_category} news…"):
        st.session_state.articles = fetch_trending_news(news_api_key, news_category, max_articles)
    if st.session_state.articles:
        st.success(f"✅ Fetched {len(st.session_state.articles)} {news_category} articles")
    else:
        st.error("Failed to fetch articles")

if st.session_state.articles:
    st.markdown(f"#### 📰 {news_category.upper()} Trending Articles")
    for i, a in enumerate(st.session_state.articles[:3]):
        pub = a.get("published", "")[:10]
        category_badge = f"<span class='category-badge'>#{a.get('category', 'news')}</span>"
        st.markdown(f"""
        <div class='card'>
            <div class='headline'>{i+1}. {a['title'][:100]}</div>
            <div style='color:#aaa;font-size:0.85rem;margin:4px 0'>{a.get('description', '')[:120]}…</div>
            <div class='meta'>{category_badge} 📡 {a.get('source', '?')} &nbsp;|&nbsp; 📅 {pub}</div>
        </div>""", unsafe_allow_html=True)
    
    if len(st.session_state.articles) > 3:
        st.caption(f"... and {len(st.session_state.articles) - 3} more {news_category} articles")

# STEP 2 ── Generate Script
st.markdown("---")
st.markdown("### <span class='step-badge'>2</span> Generate AI Script", unsafe_allow_html=True)

if not st.session_state.articles:
    st.warning("⬆ Fetch news first.")
else:
    article_options = [f"{i+1}. {a['title'][:80]}... [{a.get('category', 'news')}]" for i, a in enumerate(st.session_state.articles)]
    selected_idx = st.selectbox(
        "Choose an article to script",
        range(len(st.session_state.articles)),
        format_func=lambda i: article_options[i],
        key="article_selector"
    )

    if st.button("✍️ Generate Script", type="primary", key="generate_script_btn"):
        with st.spinner("Generating script with GPT-4o-mini…"):
            article = st.session_state.articles[selected_idx]
            st.session_state.script = generate_script(openai_key, article, vid_duration)
            st.session_state.article = article
            st.session_state.generated_images = {}
            st.rerun()

    if st.session_state.script:
        sc = st.session_state.script
        category = sc.get('category', 'general').upper()
        st.markdown(f"#### 📜 Generated Script [{category}]")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔥 Hook**")
            st.info(sc.get('hook', 'No hook generated'))
            st.markdown("**📢 Call-to-Action**")
            st.info(sc.get('cta', 'No CTA generated'))
        
        with col2:
            st.markdown("**📖 Body**")
            st.info(sc.get('body', 'No body generated'))
            st.markdown("**#️⃣ Hashtags**")
            st.info(" ".join(sc.get("hashtags", [f"#{category.lower()}"])))

# STEP 3 ── Generate Images
if st.session_state.script:
    st.markdown("---")
    st.markdown("### <span class='step-badge'>3</span> Generate Images", unsafe_allow_html=True)
    
    sc = st.session_state.script
    category = sc.get('category', 'general')
    
    if use_dalle and openai_key and st.session_state.api_key_valid:
        if st.button(f"🎨 Generate {category.upper()} Images with DALL-E", type="primary", key="generate_images_btn"):
            sections = ["hook", "body", "cta", "hashtags"]
            st.session_state.generated_images = {}
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            image_previews = st.columns(4)
            
            for i, (section, col) in enumerate(zip(sections, image_previews)):
                status_text.text(f"Generating {category} {section.upper()} image with DALL-E...")
                
                # Create category-specific prompt based on section
                if section == "hook":
                    prompt = f"{category} news headline: {sc.get('hook', 'breaking news')}, professional {category} news photography"
                elif section == "body":
                    prompt = f"{category} news story illustration: {sc.get('body', 'news event')}, journalistic style, {category} context"
                elif section == "cta":
                    prompt = f"Call to action for {category} news: subscribe and follow, social media style"
                else:
                    prompt = f"{category} social media hashtags design: {', '.join(sc.get('hashtags', [f'#{category}']))}"
                
                # Generate image with category context
                img = generate_dalle_image(openai_key, prompt, image_style, category)
                
                if img:
                    # Resize to target resolution
                    vid_w, vid_h = map(int, resolution.split("x"))
                    img = img.resize((vid_w, vid_h), Image.Resampling.LANCZOS)
                    st.session_state.generated_images[section] = img
                    
                    # Show preview in column
                    with col:
                        st.image(img, caption=f"{section.upper()}", use_container_width=True)
                else:
                    with col:
                        st.info(f"⚠️ {section} failed")
                
                progress_bar.progress((i + 1) / len(sections))
            
            progress_bar.empty()
            status_text.empty()
            
            if st.session_state.generated_images:
                st.success(f"✅ {category.upper()} images generated successfully!")
    else:
        if not openai_key:
            st.info("ℹ️ Enter an OpenAI API key to generate images with DALL-E")
        elif not st.session_state.api_key_valid:
            st.info("ℹ️ Verify your OpenAI API key first")

# STEP 4 ── Generate Video
if st.session_state.script:
    st.markdown("---")
    st.markdown("### <span class='step-badge'>4</span> Generate Final Video", unsafe_allow_html=True)
    
    vid_w, vid_h = map(int, resolution.split("x"))
    category = st.session_state.script.get('category', 'general')
    
    # Check if we have images
    has_images = st.session_state.generated_images and len(st.session_state.generated_images) > 0
    
    col1, col2 = st.columns([1, 3])
    with col1:
        generate_video_btn = st.button(
            f"🎬 Generate {category.upper()} Video", 
            type="primary", 
            disabled=not CV2_OK,
            key="generate_video_btn",
            use_container_width=True
        )
    
    with col2:
        if not CV2_OK:
            st.warning("⚠️ OpenCV required for video generation")
    
    if generate_video_btn:
        sc = st.session_state.script
        
        with st.spinner(f"Rendering {category} video..."):
            # Create output directory
            out_dir = Path(tempfile.mkdtemp())
            safe_title = "".join(c if c.isalnum() else "_" for c in sc.get("title", "video")[:30])
            out_path = str(out_dir / f"{category}_{safe_title}.mp4")
            
            # Prepare images dictionary
            images = {}
            for section in ["hook", "body", "cta", "hashtags"]:
                if section in st.session_state.generated_images:
                    images[section] = st.session_state.generated_images[section]
            
            # Progress callback
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress, status):
                progress_bar.progress(progress)
                status_text.text(status)
            
            # Generate video
            result = generate_video_with_images(
                sc, images, out_path, fps, vid_w, vid_h, 
                progress_callback=update_progress
            )
            
            progress_bar.empty()
            status_text.empty()
            
            if result and os.path.exists(result):
                st.markdown("<div class='success-banner'>✅ Video Generated Successfully!</div>",
                            unsafe_allow_html=True)
                
                # Show video preview
                st.video(result)
                
                # Download button
                with open(result, "rb") as f:
                    st.download_button(
                        "⬇️ Download Video",
                        data=f,
                        file_name=f"{category}_{safe_title}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
            else:
                st.markdown("<div class='error-banner'>❌ Video generation failed</div>",
                            unsafe_allow_html=True)
    
    # Show storyboard preview if we have images
    if st.session_state.generated_images:
        st.markdown(f"#### 📽️ {category.upper()} Storyboard Preview")
        cols = st.columns(4)
        sections = ["hook", "body", "cta", "hashtags"]
        
        for section, col in zip(sections, cols):
            with col:
                st.markdown(f"**{section.upper()}**")
                if section in st.session_state.generated_images:
                    st.image(st.session_state.generated_images[section], use_container_width=True)
                else:
                    st.info(f"No image")

st.divider()
st.markdown("<div style='text-align:center;color:#555;font-size:0.8rem'>"
            "Task 1 · AI Video Generation Tool &nbsp;|&nbsp; "
            "Category-specific news + AI + DALL-E 3 + OpenCV</div>",
            unsafe_allow_html=True)
