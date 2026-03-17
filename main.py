"""
Unified launcher — runs all 3 tools as a single Streamlit multi-page app.
Place this file at the project root and run: streamlit run main.py
"""

import streamlit as st

st.set_page_config(
    page_title="AI Internship Tools",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 100%); }
    .hero { text-align:center; padding: 3rem 0 2rem; }
    .hero h1 { font-size: 2.8rem; font-weight: 900; color: #f0f0f0; }
    .hero p  { color: #6b7280; font-size: 1.1rem; margin-top: 0.5rem; }
    .tool-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.2s;
        height: 100%;
    }
    .tool-card:hover {
        border-color: rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.07);
    }
    .tool-icon { font-size: 3rem; margin-bottom: 0.8rem; }
    .tool-title { font-size: 1.2rem; font-weight: 700; color: #f3f4f6; margin-bottom: 0.5rem; }
    .tool-desc  { color: #6b7280; font-size: 0.88rem; line-height: 1.6; margin-bottom: 1rem; }
    .chip {
        display: inline-block;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
        color: #9ca3af;
        margin: 2px;
    }
    .divider { border-color: rgba(255,255,255,0.06); margin: 2rem 0; }
    .stack-row { text-align:center; color:#4b5563; font-size:0.85rem; margin-top:2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='hero'>
    <h1>🤖 AI Internship Tools</h1>
    <p>Three AI-powered automation tools built with Python + Streamlit + Claude</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🎬</div>
        <div class='tool-title'>AI Video Generator</div>
        <div class='tool-desc'>
            Scrapes trending news articles, generates AI-powered scripts,
            and produces 30–60s videos with text overlays and frames.
        </div>
        <div>
            <span class='chip'>NewsAPI</span>
            <span class='chip'>Claude AI</span>
            <span class='chip'>MoviePy</span>
            <span class='chip'>PIL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_🎬_Video_Generator.py", label="Open Video Generator →",
                 use_container_width=True)

with c2:
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>✍️</div>
        <div class='tool-title'>SEO Blog Creator</div>
        <div class='tool-desc'>
            Scrapes best-selling products, researches SEO keywords,
            generates 150–200 word optimised blog posts, and exports
            for WordPress/Medium publishing.
        </div>
        <div>
            <span class='chip'>BeautifulSoup</span>
            <span class='chip'>Claude AI</span>
            <span class='chip'>SEO Scoring</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_✍️_SEO_Blog_Creator.py", label="Open SEO Blog Creator →",
                 use_container_width=True)

with c3:
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🏗️</div>
        <div class='tool-title'>Architecture Pipeline</div>
        <div class='tool-desc'>
            Converts high-level business requirements into full technical
            specs: modules, DB schemas, API contracts, pseudocode, and
            ER diagrams.
        </div>
        <div>
            <span class='chip'>Claude AI</span>
            <span class='chip'>JSON Spec</span>
            <span class='chip'>Mermaid</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_🏗️_Architecture_Pipeline.py", label="Open Architecture Pipeline →",
                 use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

st.markdown("""
<div class='stack-row'>
    Built with &nbsp; Python 3.12 &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp;
    Anthropic Claude &nbsp;·&nbsp; MoviePy &nbsp;·&nbsp; BeautifulSoup
</div>
""", unsafe_allow_html=True)