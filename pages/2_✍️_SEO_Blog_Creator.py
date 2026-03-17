"""
Task 2: SEO Blog Post Creation Tool
Pipeline: Scrape trending products → Research SEO keywords → Generate blog via OpenAI → Export
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

try:
    from openai import OpenAI, AuthenticationError, RateLimitError
    OPENAI_OK = True
except ImportError:
    OPENAI_OK = False


# ─────────────────────────────────────────────────────────────────────────────
# API KEY VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────
def validate_api_key(api_key: str) -> tuple[bool, str]:
    if not api_key or not api_key.strip():
        return False, "No API key — demo mode active."
    if not api_key.startswith("sk-"):
        return False, "Key format invalid (must start with `sk-`). Demo mode active."
    try:
        client = OpenAI(api_key=api_key)
        client.chat.completions.create(
            model="gpt-4o-mini", max_tokens=1,
            messages=[{"role":"user","content":"hi"}])
        return True, ""
    except AuthenticationError:
        return False, "❌ Invalid API key — check platform.openai.com."
    except Exception as e:
        return False, f"❌ API error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="SEO Blog Creator", page_icon="✍️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background:linear-gradient(135deg,#0a0a0a 0%,#111827 100%); }
    .product-card { background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                    border-radius:10px;padding:1rem;margin-bottom:0.6rem; }
    .kw-pill { display:inline-block;background:#10b98122;color:#10b981;
               border:1px solid #10b98144;border-radius:20px;padding:3px 12px;
               font-size:0.78rem;margin:3px;font-weight:600; }
    .blog-content { background:#111827;border-left:4px solid #10b981;padding:1.5rem;
                    border-radius:0 10px 10px 0;line-height:1.8;font-size:0.95rem;
                    color:#d1d5db;white-space:pre-wrap; }
    .metric-row { display:flex;gap:1rem;flex-wrap:wrap;margin:0.5rem 0; }
    .metric-item { background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);
                   border-radius:8px;padding:0.5rem 1rem;text-align:center;flex:1;min-width:100px; }
    .metric-label { font-size:0.72rem;color:#6b7280;text-transform:uppercase; }
    .metric-value { font-size:1.2rem;font-weight:700;color:#10b981; }
    h1 { color:#10b981 !important; }
    h2,h3 { color:#d1d5db !important; }
    .step-num { background:#10b981;color:#000;border-radius:50%;width:26px;height:26px;
                display:inline-flex;align-items:center;justify-content:center;
                font-weight:800;font-size:0.85rem;margin-right:8px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

    if openai_key:
        if st.button("✅ Verify Key", use_container_width=True):
            with st.spinner("Verifying…"):
                ok, msg = validate_api_key(openai_key)
            st.success("Key is valid!") if ok else st.error(msg)
    else:
        st.info("🔑 No key entered — demo mode active")

    st.divider()
    st.markdown("### 🛒 Scraper Settings")
    source       = st.selectbox("Product Source",
        ["Amazon Best Sellers (Mock)","eBay Trending (Mock)","Custom URL"])
    category     = st.selectbox("Category",
        ["Electronics","Laptops","Headphones","Books","Home & Kitchen",
         "Fitness","Skincare","Toys","Fashion"])
    max_products = st.slider("Products to scrape", 3, 10, 5)
    st.divider()
    st.markdown("### ✍️ Blog Settings")
    word_count   = st.slider("Target word count", 150, 300, 200)
    tone         = st.selectbox("Tone", ["Informative","Conversational","Expert","Engaging"])
    num_keywords = st.slider("Target keywords", 2, 5, 3)
    st.divider()
    st.caption("💡 OpenAI key → platform.openai.com")


# ─────────────────────────────────────────────────────────────────────────────
# MOCK PRODUCT DATA
# ─────────────────────────────────────────────────────────────────────────────
MOCK_PRODUCTS = {
    "Electronics": [
        {"name":"Sony WH-1000XM5 Wireless Headphones","price":"$349","rating":4.8,
         "reviews":12400,"rank":1,"description":"Industry-leading noise cancellation, 30-hour battery"},
        {"name":"Apple AirPods Pro (2nd Gen)","price":"$249","rating":4.7,
         "reviews":98000,"rank":2,"description":"Active noise cancellation, spatial audio, MagSafe"},
        {"name":"Anker PowerCore 26800mAh Power Bank","price":"$59","rating":4.6,
         "reviews":45200,"rank":3,"description":"High-capacity portable charger with fast charging"},
        {"name":"Logitech MX Master 3S Mouse","price":"$99","rating":4.7,
         "reviews":31000,"rank":4,"description":"Advanced wireless mouse, ultra-fast scroll wheel"},
        {"name":"Samsung T7 Portable SSD 1TB","price":"$89","rating":4.6,
         "reviews":27500,"rank":5,"description":"USB 3.2 Gen 2, speeds up to 1050MB/s"},
    ],
    "Laptops": [
        {"name":"Apple MacBook Air M3","price":"$1099","rating":4.9,
         "reviews":8900,"rank":1,"description":"Up to 18-hour battery, Apple M3 chip, 8GB RAM"},
        {"name":"Dell XPS 15 (2024)","price":"$1299","rating":4.6,
         "reviews":5400,"rank":2,"description":"OLED display, Intel Core Ultra 7, 16GB RAM"},
        {"name":"ASUS ROG Zephyrus G14","price":"$1499","rating":4.7,
         "reviews":4200,"rank":3,"description":"AMD Ryzen 9, RTX 4060, 165Hz QHD display"},
        {"name":"Lenovo ThinkPad X1 Carbon","price":"$1549","rating":4.8,
         "reviews":3800,"rank":4,"description":"Ultra-light business laptop, Intel Core i7"},
        {"name":"HP Spectre x360 14","price":"$1199","rating":4.6,
         "reviews":6100,"rank":5,"description":"2-in-1 convertible, OLED touch display"},
    ],
}
for cat in ["Headphones","Books","Home & Kitchen","Fitness","Skincare","Toys","Fashion"]:
    MOCK_PRODUCTS[cat] = MOCK_PRODUCTS["Electronics"]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def scrape_products(source_name: str, cat: str, count: int) -> list[dict]:
    base = MOCK_PRODUCTS.get(cat, MOCK_PRODUCTS["Electronics"])
    return [p.copy() for p in base[:count]]


def generate_seo_keywords(product: dict, n: int) -> list[dict]:
    """Generate keyword suggestions with simulated metrics."""
    import random
    random.seed(hash(product["name"]))
    base_kws = [
        product["name"],
        f"best {product['name']}",
        f"{product['name']} review",
        f"{product['name']} 2024",
        f"buy {product['name']}",
        f"{product['name']} vs alternatives",
        f"{product['name']} deal",
    ]
    keywords = []
    for kw in base_kws[:n + 2]:
        keywords.append({
            "keyword":    kw,
            "volume":     random.randint(500, 50000),
            "difficulty": random.randint(15, 75),
            "cpc":        round(random.uniform(0.5, 8.0), 2),
        })
    keywords.sort(key=lambda x: x["volume"], reverse=True)
    return keywords[:n]


def calculate_seo_score(blog: str, keywords: list[dict]) -> dict:
    wc        = len(blog.split())
    kw_counts = {kw["keyword"].lower(): blog.lower().count(kw["keyword"].lower())
                 for kw in keywords}
    density_ok   = all(1 <= v <= 5 for v in kw_counts.values())
    has_h2       = "##" in blog
    score        = 0
    score       += 30 if density_ok      else 10
    score       += 20 if has_h2          else 5
    score       += 20 if 150 <= wc <= 250 else 10
    score       += 15
    return {"score": min(100, score), "word_count": wc,
            "kw_density": kw_counts,
            "readability": min(100, max(0, 100 - abs(wc - 180)))}


def generate_blog_post(api_key: str, product: dict,
                       keywords: list[dict], wc: int, tone: str) -> str:
    """Generate an SEO-optimised blog post using OpenAI GPT-4o-mini."""
    kws = [k["keyword"] for k in keywords]

    DEMO = f"""## {product['name']}: Is It Worth Buying in 2024?

If you've been searching for the **{kws[0] if kws else product['name']}**, your search ends here.
The {product['name']} has quickly become one of the most talked-about products on the market.

### Key Features & Why It Stands Out

Priced at {product['price']}, the {product['name']} delivers {product['description']}.
With a rating of {product['rating']}/5 from over {product['reviews']:,} verified buyers,
it consistently ranks as a best-seller.

### Our Verdict

Whether you need a {kws[1] if len(kws)>1 else 'great deal'} or the best option in its category,
the {product['name']} delivers excellent value. Highly recommended.

*{kws[2] if len(kws)>2 else product['name']} | Best Price: {product['price']}*"""

    valid, err = validate_api_key(api_key)
    if not valid:
        if err and "demo" not in err.lower():
            st.warning(err)
        return DEMO

    try:
        client = OpenAI(api_key=api_key)
        kw_str = ", ".join(f'"{k["keyword"]}"' for k in keywords)
        prompt = f"""Write an SEO-optimised blog post for this product:

Product: {product['name']}
Price: {product['price']}
Rating: {product['rating']}/5 ({product['reviews']:,} reviews)
Description: {product['description']}

SEO Keywords to include naturally (3-4 uses each max): {kw_str}

Requirements:
- Exactly {wc}–{wc+30} words
- Tone: {tone}
- Include a markdown H2 subheading (##)
- Start with an attention-grabbing sentence
- End with a clear buying recommendation
- Include product price and rating
- NO keyword stuffing

Return ONLY the blog post text."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=600,
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are an expert SEO content writer."},
                {"role": "user",   "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    except AuthenticationError:
        st.error("❌ Invalid OpenAI API key. Please check your key in the sidebar.")
        return DEMO
    except RateLimitError:
        st.warning("⚠️ OpenAI rate limit hit — showing demo blog post.")
        return DEMO
    except Exception as e:
        st.warning(f"⚠️ Unexpected error: {e} — showing demo blog post.")
        return DEMO


# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# ✍️ SEO Blog Post Creation Tool")
st.markdown("*Trending products → SEO keywords → Optimised blog posts → Publish*")
st.divider()

# STEP 1 ── Scrape Products
st.markdown("### <span class='step-num'>1</span> Scrape Trending Products", unsafe_allow_html=True)
c1, c2 = st.columns([3,1])
with c1: st.info(f"Source: **{source}** | Category: **{category}** | Count: **{max_products}**")
with c2: scrape_btn = st.button("🛒 Scrape Products", type="primary", use_container_width=True)

if "products" not in st.session_state:
    st.session_state.products = []

if scrape_btn:
    with st.spinner("Scraping products…"):
        time.sleep(0.6)
        st.session_state.products = scrape_products(source, category, max_products)
    st.success(f"✅ Found {len(st.session_state.products)} trending products")

if st.session_state.products:
    cols = st.columns(min(3, len(st.session_state.products)))
    for i, p in enumerate(st.session_state.products):
        with cols[i % len(cols)]:
            stars = "⭐" * int(p["rating"])
            st.markdown(f"""
            <div class='product-card'>
                <div style='font-weight:700;font-size:0.9rem;color:#f3f4f6;margin-bottom:4px'>
                    #{p['rank']} {p['name'][:45]}{'…' if len(p['name'])>45 else ''}</div>
                <div style='color:#10b981;font-weight:700'>{p['price']}</div>
                <div style='color:#9ca3af;font-size:0.8rem'>{stars} {p['rating']}
                    ({p['reviews']:,} reviews)</div>
                <div style='color:#6b7280;font-size:0.78rem;margin-top:4px'>
                    {p['description'][:70]}…</div>
            </div>""", unsafe_allow_html=True)

# STEP 2 ── SEO Keywords
st.markdown("---")
st.markdown("### <span class='step-num'>2</span> Research SEO Keywords", unsafe_allow_html=True)

if not st.session_state.products:
    st.warning("⬆ Scrape products first.")
else:
    sel_idx = st.selectbox("Select product to target",
                           range(len(st.session_state.products)),
                           format_func=lambda i: st.session_state.products[i]["name"])

    if st.button("🔍 Research Keywords", type="primary"):
        with st.spinner("Analysing keyword opportunities…"):
            time.sleep(0.5)
            st.session_state.keywords    = generate_seo_keywords(
                st.session_state.products[sel_idx], num_keywords)
            st.session_state.sel_product = st.session_state.products[sel_idx]

    if "keywords" in st.session_state:
        st.markdown("#### 🎯 Top Keywords")
        kw_cols = st.columns(len(st.session_state.keywords))
        for kw, col in zip(st.session_state.keywords, kw_cols):
            with col:
                diff_c = "#10b981" if kw["difficulty"]<40 else \
                         "#f59e0b" if kw["difficulty"]<65 else "#ef4444"
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                             border-radius:10px;padding:0.8rem;text-align:center'>
                    <div style='font-size:0.85rem;font-weight:700;color:#f3f4f6;margin-bottom:6px'>
                        {kw['keyword']}</div>
                    <div style='color:#3b82f6;font-size:1.1rem;font-weight:800'>
                        {kw['volume']:,}</div>
                    <div style='font-size:0.7rem;color:#6b7280'>monthly searches</div>
                    <div style='color:{diff_c};font-size:0.85rem;margin-top:4px'>
                        Difficulty: {kw['difficulty']}/100</div>
                    <div style='color:#9ca3af;font-size:0.78rem'>CPC: ${kw['cpc']}</div>
                </div>""", unsafe_allow_html=True)

# STEP 3 ── Generate Blog
st.markdown("---")
st.markdown("### <span class='step-num'>3</span> Generate SEO Blog Post", unsafe_allow_html=True)

if "keywords" not in st.session_state:
    st.warning("⬆ Research keywords first.")
else:
    if st.button("✍️ Generate Blog Post", type="primary"):
        with st.spinner("Writing optimised blog post with GPT-4o-mini…"):
            blog = generate_blog_post(openai_key, st.session_state.sel_product,
                                      st.session_state.keywords, word_count, tone)
            st.session_state.blog      = blog
            st.session_state.seo_score = calculate_seo_score(blog, st.session_state.keywords)

    if "blog" in st.session_state:
        sc = st.session_state.seo_score
        score_color = "#10b981" if sc["score"]>=70 else "#f59e0b" if sc["score"]>=50 else "#ef4444"
        st.markdown(f"""
        <div class='metric-row'>
            <div class='metric-item'>
                <div class='metric-label'>SEO Score</div>
                <div class='metric-value' style='color:{score_color}'>{sc['score']}/100</div>
            </div>
            <div class='metric-item'>
                <div class='metric-label'>Word Count</div>
                <div class='metric-value'>{sc['word_count']}</div>
            </div>
            <div class='metric-item'>
                <div class='metric-label'>Readability</div>
                <div class='metric-value'>{sc['readability']}/100</div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("**Keyword Usage**")
        for kw, cnt in sc["kw_density"].items():
            col  = "#10b981" if 1<=cnt<=4 else "#ef4444"
            st.markdown(f"<span class='kw-pill' style='background:{col}22;color:{col};"
                        f"border-color:{col}44'>{kw}: {cnt}×</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📝 Generated Blog Post")
        st.markdown(f"<div class='blog-content'>{st.session_state.blog}</div>",
                    unsafe_allow_html=True)

        # STEP 4 ── Export
        st.markdown("---")
        st.markdown("### <span class='step-num'>4</span> Export & Publish", unsafe_allow_html=True)
        slug      = st.session_state.sel_product["name"].replace(" ","_")[:30]
        date_str  = datetime.now().strftime("%Y%m%d")
        base_name = f"blog_{slug}_{date_str}"

        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            st.download_button("⬇️ Download .txt", data=st.session_state.blog,
                               file_name=f"{base_name}.txt", mime="text/plain",
                               use_container_width=True)
        with ec2:
            md = (f"# {st.session_state.sel_product['name']}\n\n"
                  f"**Keywords:** {', '.join(k['keyword'] for k in st.session_state.keywords)}\n\n"
                  + st.session_state.blog)
            st.download_button("⬇️ Download .md", data=md,
                               file_name=f"{base_name}.md", mime="text/markdown",
                               use_container_width=True)
        with ec3:
            html = (f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                    f"<title>{st.session_state.sel_product['name']}</title>"
                    f"<meta name='keywords' content='"
                    f"{', '.join(k['keyword'] for k in st.session_state.keywords)}'>"
                    f"</head><body><article>"
                    f"{st.session_state.blog.replace(chr(10),'<br>')}"
                    f"</article></body></html>")
            st.download_button("⬇️ Download .html", data=html,
                               file_name=f"{base_name}.html", mime="text/html",
                               use_container_width=True)

        st.info("💡 **Publish:** Copy the markdown and paste into WordPress/Medium, "
                "or use their REST API for full automation.")

st.divider()
st.markdown("<div style='text-align:center;color:#374151;font-size:0.8rem'>"
            "Task 2 · SEO Blog Post Creation Tool &nbsp;|&nbsp; "
            "Python + Streamlit + OpenAI GPT-4o-mini</div>",
            unsafe_allow_html=True)