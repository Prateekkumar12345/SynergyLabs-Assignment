"""
Task 3: High-Level to Low-Level Architecture Pipeline
Pipeline: Parse business requirements → Break into modules → Generate schemas + pseudocode
AI: OpenAI GPT-4o-mini
"""

import streamlit as st
import json
from datetime import datetime

try:
    from openai import OpenAI, AuthenticationError, RateLimitError
    OPENAI_OK = True
except ImportError:
    OPENAI_OK = False


# ─────────────────────────────────────────────────────────────────────────────
# API KEY VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────
def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Returns (is_valid, error_message). Makes a cheap 1-token test call."""
    if not api_key or not api_key.strip():
        return False, "No API key — demo mode active."
    if not api_key.startswith("sk-"):
        return False, "Key format invalid (must start with `sk-`). Demo mode active."
    try:
        client = OpenAI(api_key=api_key)
        client.chat.completions.create(
            model="gpt-4o-mini", max_tokens=1,
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
st.set_page_config(page_title="Architecture Pipeline", page_icon="🏗️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: linear-gradient(160deg, #0d0d0d 0%, #0d1117 100%); }
    .module-card {
        background:#161b22;border:1px solid #30363d;
        border-left:4px solid #f78166;border-radius:0 10px 10px 0;
        padding:1rem;margin-bottom:0.8rem;
    }
    .module-name { font-size:1rem;font-weight:700;color:#f78166;margin-bottom:0.4rem; }
    .schema-box {
        background:#0d1117;border:1px solid #388bfd55;border-radius:8px;
        padding:1rem;font-family:'Courier New',monospace;font-size:0.85rem;
        color:#79c0ff;overflow-x:auto;white-space:pre;
    }
    .pseudo-box {
        background:#0d1117;border:1px solid #56d36455;border-radius:8px;
        padding:1rem;font-family:'Courier New',monospace;font-size:0.85rem;
        color:#7ee787;overflow-x:auto;white-space:pre-wrap;
    }
    .badge { display:inline-block;padding:2px 10px;border-radius:20px;
             font-size:0.72rem;font-weight:600;margin:2px; }
    .badge-blue   { background:#388bfd22;color:#388bfd;border:1px solid #388bfd44; }
    .badge-green  { background:#56d36422;color:#56d364;border:1px solid #56d36444; }
    .badge-orange { background:#ffa65722;color:#ffa657;border:1px solid #ffa65744; }
    .badge-red    { background:#f7816622;color:#f78166;border:1px solid #f7816644; }
    h1  { color:#f78166 !important; }
    h2,h3 { color:#c9d1d9 !important; }
    .step-dot {
        background:#f78166;color:#000;border-radius:50%;width:26px;height:26px;
        display:inline-flex;align-items:center;justify-content:center;
        font-weight:800;font-size:0.85rem;margin-right:8px;
    }
    .summary-grid {
        display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
        gap:0.8rem;margin:1rem 0;
    }
    .summary-cell {
        background:#161b22;border:1px solid #30363d;border-radius:8px;
        padding:0.8rem;text-align:center;
    }
    .summary-num   { font-size:1.8rem;font-weight:800;color:#f78166; }
    .summary-label { font-size:0.72rem;color:#6e7681;text-transform:uppercase; }
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
    st.markdown("### 🏗️ Pipeline Settings")
    detail_level = st.select_slider(
        "Detail Level",
        options=["Minimal", "Standard", "Detailed", "Comprehensive"],
        value="Detailed",
    )
    output_format = st.multiselect(
        "Output Artifacts",
        ["Module Breakdown", "Database Schemas", "Pseudocode",
         "API Endpoints", "Tech Stack", "Mermaid Diagram"],
        default=["Module Breakdown", "Database Schemas", "Pseudocode", "API Endpoints"],
    )
    tech_preference = st.selectbox(
        "Tech Stack Preference",
        ["Auto-detect", "Python/Django", "Node.js/Express",
         "Java/Spring", "Go", "FastAPI"],
    )
    st.divider()
    st.markdown("### 📋 Example Requirements")
    examples = {
        "E-Commerce Platform": (
            "Build an online marketplace where sellers can list products, "
            "buyers can search and purchase items, process payments securely, "
            "track order status, and leave reviews. Admins can manage users and "
            "resolve disputes. The system must handle 10,000 concurrent users."
        ),
        "Hospital Management": (
            "Create a hospital management system for patient registration, "
            "doctor appointment scheduling, medical records management, "
            "pharmacy inventory, billing, and lab test results. Must comply "
            "with HIPAA regulations and support multi-branch hospitals."
        ),
        "EdTech Platform": (
            "Build an online learning platform with course creation tools for "
            "instructors, video streaming, quizzes, progress tracking, "
            "certificates, discussion forums, subscription payments, "
            "and analytics dashboards."
        ),
        "Food Delivery App": (
            "Develop a food delivery app where restaurants upload menus, "
            "customers order food, delivery agents are assigned automatically, "
            "real-time GPS tracking is shown, payments processed, and ratings "
            "collected after delivery."
        ),
    }
    selected_example = st.selectbox("Load Example", ["— select —"] + list(examples.keys()))
    st.divider()
    st.caption("💡 OpenAI key → platform.openai.com")


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_prompt(requirement: str, detail: str, formats: list, tech_pref: str) -> str:
    artifacts_str = ", ".join(formats) if formats else "all"
    return f"""You are a senior software architect. Convert the following high-level business
requirement into a detailed low-level technical specification.

BUSINESS REQUIREMENT:
{requirement}

DETAIL LEVEL: {detail}
TECH PREFERENCE: {tech_pref}
ARTIFACTS TO INCLUDE: {artifacts_str}

Return ONLY valid JSON — no markdown fences, no preamble — with exactly this structure:
{{
  "project_name": "string",
  "summary": "2-3 sentence technical summary",
  "tech_stack": {{
    "frontend": ["tech1","tech2"],
    "backend":  ["tech1","tech2"],
    "database": ["tech1","tech2"],
    "infrastructure": ["tech1","tech2"],
    "devops": ["tech1","tech2"]
  }},
  "modules": [
    {{
      "name": "Module Name",
      "description": "What this module does",
      "responsibilities": ["r1","r2","r3"],
      "dependencies": ["other_module_name"],
      "priority": "High|Medium|Low",
      "complexity": "High|Medium|Low",
      "estimated_effort_days": 5
    }}
  ],
  "schemas": [
    {{
      "model": "ModelName",
      "table": "table_name",
      "fields": [
        {{"name":"id","type":"UUID","constraints":"PK, auto-generated"}}
      ],
      "indexes": ["idx_table_field"],
      "relationships": ["ModelName has_many OtherModel"]
    }}
  ],
  "api_endpoints": [
    {{
      "method": "GET|POST|PUT|DELETE|PATCH",
      "path": "/api/v1/resource",
      "description": "What it does",
      "auth_required": true,
      "request_body": "JSON schema or null",
      "response": "JSON schema"
    }}
  ],
  "pseudocode": [
    {{
      "function": "functionName",
      "module":   "ModuleName",
      "pseudocode": "multi-line pseudocode string"
    }}
  ],
  "mermaid_diagram": "erDiagram or flowchart LR code string",
  "non_functional": {{
    "scalability": "description",
    "security":    "description",
    "performance": "description"
  }},
  "risks": [
    {{"risk":"description","mitigation":"description","severity":"High|Medium|Low"}}
  ]
}}"""


# ─────────────────────────────────────────────────────────────────────────────
# DEMO SPEC
# ─────────────────────────────────────────────────────────────────────────────
def _demo_spec() -> dict:
    return {
        "project_name": "E-Commerce Platform",
        "summary": (
            "A scalable multi-vendor marketplace supporting 10k concurrent users. "
            "Microservices architecture with event-driven communication. "
            "React frontend, Python FastAPI backend, PostgreSQL + Redis."
        ),
        "tech_stack": {
            "frontend":      ["React 18","TypeScript","TailwindCSS","Redux Toolkit"],
            "backend":       ["Python 3.12","FastAPI","Celery","Pydantic v2"],
            "database":      ["PostgreSQL 16","Redis 7","Elasticsearch"],
            "infrastructure":["Docker","Kubernetes","AWS S3","CloudFront"],
            "devops":        ["GitHub Actions","Terraform","Prometheus","Grafana"],
        },
        "modules": [
            {"name":"User Management","description":"Auth, profiles, roles",
             "responsibilities":["Registration/login","JWT auth","Role-based access"],
             "dependencies":[],"priority":"High","complexity":"Medium","estimated_effort_days":5},
            {"name":"Product Catalog","description":"Product CRUD, search, categories",
             "responsibilities":["Product listing","Search (Elasticsearch)","Image upload"],
             "dependencies":["User Management"],"priority":"High","complexity":"High","estimated_effort_days":10},
            {"name":"Order Management","description":"Cart, checkout, order tracking",
             "responsibilities":["Cart management","Order creation","Status tracking"],
             "dependencies":["Product Catalog","Payment Gateway"],"priority":"High","complexity":"High","estimated_effort_days":12},
            {"name":"Payment Gateway","description":"Secure payment processing",
             "responsibilities":["Stripe integration","Refunds","Invoice generation"],
             "dependencies":["User Management"],"priority":"High","complexity":"Medium","estimated_effort_days":6},
            {"name":"Review System","description":"Ratings and reviews",
             "responsibilities":["Submit review","Aggregate ratings","Moderation"],
             "dependencies":["Order Management","User Management"],"priority":"Medium","complexity":"Low","estimated_effort_days":3},
        ],
        "schemas": [
            {"model":"User","table":"users",
             "fields":[
                 {"name":"id","type":"UUID","constraints":"PK"},
                 {"name":"email","type":"VARCHAR(255)","constraints":"UNIQUE, NOT NULL"},
                 {"name":"password_hash","type":"TEXT","constraints":"NOT NULL"},
                 {"name":"role","type":"ENUM","constraints":"buyer|seller|admin"},
                 {"name":"created_at","type":"TIMESTAMP","constraints":"DEFAULT NOW()"},
             ],
             "indexes":["idx_users_email"],
             "relationships":["User has_many Products (as seller)","User has_many Orders"]},
            {"model":"Product","table":"products",
             "fields":[
                 {"name":"id","type":"UUID","constraints":"PK"},
                 {"name":"seller_id","type":"UUID","constraints":"FK → users.id"},
                 {"name":"name","type":"VARCHAR(500)","constraints":"NOT NULL"},
                 {"name":"price","type":"DECIMAL(10,2)","constraints":"NOT NULL"},
                 {"name":"stock_qty","type":"INTEGER","constraints":"DEFAULT 0"},
                 {"name":"category_id","type":"UUID","constraints":"FK → categories.id"},
             ],
             "indexes":["idx_products_seller_id","idx_products_category_id"],
             "relationships":["Product belongs_to User","Product has_many OrderItems"]},
        ],
        "api_endpoints": [
            {"method":"POST","path":"/api/v1/auth/register","description":"Register new user",
             "auth_required":False,"request_body":'{"email":"str","password":"str","role":"buyer|seller"}',
             "response":'{"user_id":"uuid","token":"jwt"}'},
            {"method":"GET","path":"/api/v1/products","description":"List products with filters",
             "auth_required":False,"request_body":"null",
             "response":'{"products":[...],"total":int,"page":int}'},
            {"method":"POST","path":"/api/v1/orders","description":"Create order from cart",
             "auth_required":True,
             "request_body":'{"items":[{"product_id":"uuid","qty":int}],"payment_method":"str"}',
             "response":'{"order_id":"uuid","status":"pending","total":float}'},
            {"method":"PATCH","path":"/api/v1/orders/{order_id}/status","description":"Update order status",
             "auth_required":True,
             "request_body":'{"status":"processing|shipped|delivered|cancelled"}',
             "response":'{"order_id":"uuid","status":"str","updated_at":"timestamp"}'},
        ],
        "pseudocode": [
            {"function":"create_order","module":"Order Management",
             "pseudocode":(
                 "FUNCTION create_order(user_id, items[], payment_method):\n"
                 "  VALIDATE user is authenticated\n"
                 "  FOR EACH item IN items:\n"
                 "    product = fetch_product(item.product_id)\n"
                 "    IF product.stock_qty < item.qty THEN\n"
                 "      RAISE InsufficientStockError\n"
                 "  total = SUM(product.price * item.qty FOR item IN items)\n"
                 "  BEGIN TRANSACTION:\n"
                 "    charge_result = payment_gateway.charge(user_id, total)\n"
                 "    IF charge_result.success:\n"
                 "      order = create_order_record(user_id, items, total)\n"
                 "      deduct_stock(items)\n"
                 "      COMMIT\n"
                 "      EMIT order_created_event(order.id)\n"
                 "    ELSE:\n"
                 "      ROLLBACK\n"
                 "      RAISE PaymentFailedError\n"
                 "  RETURN order"
             )},
            {"function":"search_products","module":"Product Catalog",
             "pseudocode":(
                 "FUNCTION search_products(query, filters, page, page_size):\n"
                 "  cache_key = hash(query + filters + page)\n"
                 "  IF cache.exists(cache_key) THEN\n"
                 "    RETURN cache.get(cache_key)\n"
                 "  es_query = build_elasticsearch_query(query, filters)\n"
                 "  results  = elasticsearch.search(es_query,\n"
                 "               from=page*page_size, size=page_size)\n"
                 "  formatted = [format_product(hit) FOR hit IN results.hits]\n"
                 "  cache.set(cache_key, formatted, ttl=300)\n"
                 "  RETURN {products: formatted, total: results.total}"
             )},
        ],
        "mermaid_diagram": (
            "erDiagram\n"
            "    User ||--o{ Product : sells\n"
            "    User ||--o{ Order : places\n"
            "    Order ||--|{ OrderItem : contains\n"
            "    Product ||--o{ OrderItem : included_in\n"
            "    Order ||--|| Payment : has\n"
            "    Product }|--|| Category : belongs_to"
        ),
        "non_functional": {
            "scalability":  "Horizontal scaling via Kubernetes; read replicas for DB",
            "security":     "JWT auth, bcrypt passwords, rate limiting, OWASP Top 10 compliance",
            "performance":  "Redis caching, CDN for assets, DB query optimisation, <200ms p99",
        },
        "risks": [
            {"risk":"Payment processing failures","severity":"High",
             "mitigation":"Idempotent payments, retry logic, dead-letter queues"},
            {"risk":"Database bottleneck at scale","severity":"Medium",
             "mitigation":"Read replicas, connection pooling, query optimisation"},
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# OPENAI CALL
# ─────────────────────────────────────────────────────────────────────────────
def analyse_requirements(api_key: str, requirement: str,
                         detail: str, formats: list, tech_pref: str) -> dict:
    """Convert requirements → architecture spec using GPT-4o-mini."""
    valid, err = validate_api_key(api_key)
    if not valid:
        if err and "demo" not in err.lower():
            st.warning(err)
        return _demo_spec()

    try:
        client   = OpenAI(api_key=api_key)
        prompt   = build_prompt(requirement, detail, formats, tech_pref)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=4096,
            temperature=0.3,
            response_format={"type": "json_object"},   # native JSON mode → no fences
            messages=[
                {"role": "system",
                 "content": "You are a senior software architect. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.choices[0].message.content.strip())

    except AuthenticationError:
        st.error("❌ Invalid OpenAI API key. Please check your key in the sidebar.")
        return _demo_spec()
    except RateLimitError:
        st.warning("⚠️ OpenAI rate limit hit — showing demo architecture.")
        return _demo_spec()
    except json.JSONDecodeError as e:
        st.warning(f"⚠️ Couldn't parse AI response ({e}) — showing demo architecture.")
        return _demo_spec()
    except Exception as e:
        st.warning(f"⚠️ Unexpected error: {e} — showing demo architecture.")
        return _demo_spec()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 🏗️ High-Level → Low-Level Architecture Pipeline")
st.markdown("*Business requirements → Modules, Schemas, Pseudocode & API Contracts · GPT-4o-mini*")
st.divider()

# ── Step 1: Input ─────────────────────────────────────────────────────────────
st.markdown("### <span class='step-dot'>1</span> Enter Business Requirement",
            unsafe_allow_html=True)

default_text = examples.get(selected_example, "") if selected_example != "— select —" else ""
requirement  = st.text_area(
    "Business Requirement", value=default_text, height=140,
    placeholder="Describe your business requirement in plain English…",
    label_visibility="collapsed",
)

c1, c2 = st.columns([4, 1])
with c1:
    words  = len(requirement.split()) if requirement.strip() else 0
    colour = "#10b981" if 20 <= words <= 300 else "#f59e0b"
    st.markdown(f"<small style='color:{colour}'>Word count: {words} "
                f"(recommended: 20–300)</small>", unsafe_allow_html=True)
with c2:
    analyse_btn = st.button("🔍 Analyse & Convert", type="primary",
                            use_container_width=True,
                            disabled=len(requirement.strip().split()) < 5)

# ── Step 2: Run pipeline ──────────────────────────────────────────────────────
if "arch" not in st.session_state:
    st.session_state.arch = None

if analyse_btn and requirement.strip():
    with st.spinner("Running architecture pipeline with GPT-4o-mini… (15–30s)"):
        st.session_state.arch = analyse_requirements(
            openai_key, requirement, detail_level, output_format, tech_preference
        )

if st.session_state.arch:
    arch       = st.session_state.arch
    modules    = arch.get("modules", [])
    schemas    = arch.get("schemas", [])
    endpoints  = arch.get("api_endpoints", [])
    total_days = sum(m.get("estimated_effort_days", 0) for m in modules)

    st.markdown("---")
    st.markdown(f"## 🏛️ {arch.get('project_name', 'Architecture')}")
    st.markdown(f"> {arch.get('summary', '')}")

    st.markdown(f"""
    <div class='summary-grid'>
        <div class='summary-cell'>
            <div class='summary-num'>{len(modules)}</div>
            <div class='summary-label'>Modules</div>
        </div>
        <div class='summary-cell'>
            <div class='summary-num'>{len(schemas)}</div>
            <div class='summary-label'>DB Schemas</div>
        </div>
        <div class='summary-cell'>
            <div class='summary-num'>{len(endpoints)}</div>
            <div class='summary-label'>API Endpoints</div>
        </div>
        <div class='summary-cell'>
            <div class='summary-num'>{total_days}</div>
            <div class='summary-label'>Est. Dev Days</div>
        </div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📦 Modules", "🗄️ Schemas", "🔌 API",
                    "💻 Pseudocode", "⚙️ Tech Stack", "📊 Diagram", "⚠️ Risks"])

    # Modules
    with tabs[0]:
        st.markdown("#### Module Breakdown")
        pc = {"High": "#f78166", "Medium": "#ffa657", "Low": "#56d364"}
        for m in modules:
            pri_c = pc.get(m.get("priority",""), "#888")
            cx_c  = pc.get(m.get("complexity",""), "#888")
            deps  = " ".join(f"<span class='badge badge-blue'>→ {d}</span>"
                             for d in m.get("dependencies", [])
                             ) or "<span style='color:#555'>none</span>"
            resps = "".join(f"<li style='color:#8b949e;font-size:0.85rem'>{r}</li>"
                            for r in m.get("responsibilities", []))
            st.markdown(f"""
            <div class='module-card'>
                <div class='module-name'>{m['name']}</div>
                <div style='color:#8b949e;font-size:0.87rem;margin-bottom:6px'>
                    {m.get('description','')}</div>
                <ul style='margin:4px 0 6px 1rem;padding:0'>{resps}</ul>
                <div style='display:flex;gap:8px;flex-wrap:wrap;align-items:center'>
                    <span class='badge' style='background:{pri_c}22;color:{pri_c};
                          border:1px solid {pri_c}44'>Priority: {m.get('priority','?')}</span>
                    <span class='badge' style='background:{cx_c}22;color:{cx_c};
                          border:1px solid {cx_c}44'>Complexity: {m.get('complexity','?')}</span>
                    <span class='badge badge-orange'>~{m.get('estimated_effort_days','?')} days</span>
                    {deps}
                </div>
            </div>""", unsafe_allow_html=True)

    # Schemas
    with tabs[1]:
        st.markdown("#### Database Schemas")
        for schema in schemas:
            with st.expander(f"📋 {schema['model']}  (table: `{schema['table']}`)", expanded=True):
                lines = [f"CREATE TABLE {schema['table']} ("]
                for f in schema.get("fields", []):
                    lines.append(f"    {f['name']:<20} {f['type']:<20} -- {f['constraints']}")
                lines.append(");")
                for idx in schema.get("indexes", []):
                    lines.append(f"CREATE INDEX {idx} ON {schema['table']};")
                st.markdown("<div class='schema-box'>" + "\n".join(lines) + "</div>",
                            unsafe_allow_html=True)
                for rel in schema.get("relationships", []):
                    st.markdown(f"<span class='badge badge-green'>{rel}</span>",
                                unsafe_allow_html=True)

    # API Endpoints
    with tabs[2]:
        st.markdown("#### API Endpoints")
        mc_map = {"GET":"#56d364","POST":"#388bfd","PUT":"#ffa657",
                  "PATCH":"#ffa657","DELETE":"#f78166"}
        for ep in endpoints:
            mc   = mc_map.get(ep.get("method","GET"), "#888")
            auth = "🔒 Auth required" if ep.get("auth_required") else "🔓 Public"
            st.markdown(f"""
            <div style='background:#161b22;border:1px solid #30363d;
                        border-radius:8px;padding:0.9rem;margin-bottom:0.6rem'>
                <span class='badge' style='background:{mc}22;color:{mc};
                      border:1px solid {mc}44'>{ep.get('method','')}</span>
                <code style='color:#c9d1d9;font-size:0.9rem;margin-left:6px'>
                    {ep.get('path','')}</code>
                <span style='color:#6e7681;font-size:0.8rem;margin-left:10px'>{auth}</span>
                <div style='color:#8b949e;font-size:0.85rem;margin-top:6px'>
                    {ep.get('description','')}</div>
                <div style='font-size:0.8rem;margin-top:4px'>
                    <span style='color:#6e7681'>Body: </span>
                    <code style='color:#79c0ff'>{ep.get('request_body','null')}</code>
                </div>
                <div style='font-size:0.8rem'>
                    <span style='color:#6e7681'>Response: </span>
                    <code style='color:#7ee787'>{ep.get('response','')}</code>
                </div>
            </div>""", unsafe_allow_html=True)

    # Pseudocode
    with tabs[3]:
        st.markdown("#### Core Algorithm Pseudocode")
        for pc in arch.get("pseudocode", []):
            with st.expander(f"⚙️ `{pc.get('function','fn')}` — {pc.get('module','')}",
                             expanded=True):
                st.markdown(f"<div class='pseudo-box'>{pc.get('pseudocode','')}</div>",
                            unsafe_allow_html=True)

    # Tech Stack
    with tabs[4]:
        st.markdown("#### Recommended Tech Stack")
        icons = {"frontend":"🌐","backend":"⚙️","database":"🗄️",
                 "infrastructure":"☁️","devops":"🔧"}
        for layer, items in arch.get("tech_stack", {}).items():
            pills = " ".join(f"<span class='badge badge-blue'>{t}</span>" for t in items)
            st.markdown(
                f"<div style='margin:0.6rem 0'>"
                f"<strong style='color:#c9d1d9'>{icons.get(layer,'📦')} {layer.title()}"
                f"</strong> &nbsp; {pills}</div>",
                unsafe_allow_html=True,
            )
        nf = arch.get("non_functional", {})
        if nf:
            st.markdown("---")
            st.markdown("#### Non-Functional Requirements")
            for key, val in nf.items():
                st.markdown(f"**{key.title()}:** {val}")

    # Diagram
    with tabs[5]:
        diagram_code = arch.get("mermaid_diagram", "")
        if diagram_code:
            st.markdown("#### ER / Flow Diagram")
            st.markdown("```mermaid\n" + diagram_code + "\n```")
            st.caption("💡 Paste the code below into mermaid.live to render it")
            st.code(diagram_code, language="text")
        else:
            st.info("No diagram generated. Add 'Mermaid Diagram' to Output Artifacts.")

    # Risks
    with tabs[6]:
        st.markdown("#### Risk Register")
        sc = {"High":"#f78166","Medium":"#ffa657","Low":"#56d364"}
        for risk in arch.get("risks", []):
            sev_c = sc.get(risk.get("severity","Medium"), "#888")
            st.markdown(f"""
            <div style='background:#161b22;border:1px solid #30363d;
                        border-left:4px solid {sev_c};border-radius:0 8px 8px 0;
                        padding:0.9rem;margin-bottom:0.6rem'>
                <span class='badge' style='background:{sev_c}22;color:{sev_c};
                      border:1px solid {sev_c}44'>{risk.get('severity','')} Risk</span>
                <div style='color:#c9d1d9;font-weight:600;margin-top:6px'>
                    {risk.get('risk','')}</div>
                <div style='color:#6e7681;font-size:0.85rem;margin-top:4px'>
                    🛡️ {risk.get('mitigation','')}</div>
            </div>""", unsafe_allow_html=True)

    # Export
    st.markdown("---")
    st.markdown("### 📥 Export Full Specification")
    spec_md = (
        f"# {arch.get('project_name','Architecture Spec')}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"## Summary\n{arch.get('summary','')}\n\n## Modules\n"
        + "".join(f"### {m['name']}\n{m.get('description','')}\n" for m in modules)
        + "\n## API Endpoints\n"
        + "".join(f"- {e['method']} {e['path']} — {e.get('description','')}\n"
                  for e in endpoints)
        + "\n## Risks\n"
        + "".join(f"- [{r.get('severity','')}] {r.get('risk','')} → "
                  f"{r.get('mitigation','')}\n"
                  for r in arch.get("risks", []))
    )
    ec1, ec2 = st.columns(2)
    with ec1:
        st.download_button("⬇️ Download Spec (.md)", data=spec_md,
                           file_name="architecture_spec.md", mime="text/markdown",
                           use_container_width=True)
    with ec2:
        st.download_button("⬇️ Download Full JSON", data=json.dumps(arch, indent=2),
                           file_name="architecture_spec.json", mime="application/json",
                           use_container_width=True)

st.divider()
st.markdown(
    "<div style='text-align:center;color:#21262d;font-size:0.8rem'>"
    "Task 3 · High-Level → Low-Level Architecture Pipeline &nbsp;|&nbsp; "
    "Python + Streamlit + OpenAI GPT-4o-mini</div>",
    unsafe_allow_html=True,
)