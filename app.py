import streamlit as st
from main import analyze_pipeline

st.set_page_config(
    page_title="AO3 Analyzer",
    page_icon="📖",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Mono:wght@300;400&family=DM+Sans:wght@300;400&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f0d0d;
    color: #e8e0d5;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 20% 10%, rgba(120,30,30,0.18) 0%, transparent 55%),
        radial-gradient(ellipse at 80% 80%, rgba(80,20,20,0.12) 0%, transparent 50%),
        #0f0d0d;
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
footer { display: none; }

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
}

p, div, span, label, input {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Title block ── */
.title-block {
    text-align: center;
    padding: 3rem 0 2rem 0;
    border-bottom: 1px solid rgba(180,60,60,0.3);
    margin-bottom: 2.5rem;
}

.title-block h1 {
    font-size: 3.2rem;
    font-weight: 700;
    color: #f0e6d3;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.1;
}

.title-block .subtitle {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem;
    color: #8a6a5a;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.6rem;
}

/* ── Input ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(180,60,60,0.35) !important;
    border-radius: 2px !important;
    color: #e8e0d5 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease;
}

[data-testid="stTextInput"] input:focus {
    border-color: rgba(180,60,60,0.8) !important;
    box-shadow: 0 0 0 2px rgba(180,60,60,0.12) !important;
}

[data-testid="stTextInput"] label {
    color: #8a6a5a !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

/* ── Button ── */
[data-testid="stButton"] button {
    background: #7a1e1e !important;
    color: #f5ede3 !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 2.5rem !important;
    transition: background 0.2s ease, transform 0.1s ease !important;
    width: 100%;
}

[data-testid="stButton"] button:hover {
    background: #9a2828 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stButton"] button:active {
    transform: translateY(0px) !important;
}

/* ── Result card ── */
.result-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(180,60,60,0.2);
    border-radius: 3px;
    padding: 1.8rem 2rem;
    margin: 1.5rem 0;
}

.result-card .label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #7a4a3a;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.result-card .value {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: #f0e6d3;
    font-weight: 700;
}

.result-card .value.italic {
    font-style: italic;
    font-weight: 400;
}

/* ── CP display ── */
.cp-display {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(180,60,60,0.15);
    margin-bottom: 1.5rem;
}

.cp-name {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f0e6d3;
}

.cp-name.sub-char {
    color: #a07060;
    font-style: italic;
    font-weight: 400;
}

.cp-slash {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #7a1e1e;
}

/* ── Score bar ── */
.score-section {
    margin: 1.2rem 0;
}

.score-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #7a4a3a;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

.score-bar-wrap {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.5rem;
}

.score-char {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #a09080;
    width: 80px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.score-bar-bg {
    flex: 1;
    background: rgba(255,255,255,0.06);
    border-radius: 1px;
    height: 6px;
    overflow: hidden;
}

.score-bar-fill {
    height: 100%;
    border-radius: 1px;
    transition: width 0.6s ease;
}

.score-bar-fill.dom { background: #9a2828; }
.score-bar-fill.sub { background: #4a3030; }

.score-val {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #6a5a50;
    width: 40px;
    text-align: right;
}

/* ── Final verdict ── */
.verdict {
    text-align: center;
    padding: 2rem;
    margin-top: 1.5rem;
    border: 1px solid rgba(180,60,60,0.3);
    background: rgba(120,30,30,0.08);
    border-radius: 2px;
}

.verdict .verdict-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #7a4a3a;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.verdict .verdict-text {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f0e6d3;
}

.verdict .verdict-text.switch-text {
    font-style: italic;
    color: #c09060;
    font-size: 1.8rem;
}

.verdict .verdict-text.uncertain-text {
    font-style: italic;
    color: #808080;
    font-size: 1.8rem;
}

/* ── Meta row ── */
.meta-row {
    display: flex;
    gap: 1.5rem;
    margin: 1.2rem 0;
}

.meta-item {
    flex: 1;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 2px;
    padding: 1rem 1.2rem;
}

.meta-item .label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #7a4a3a;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.meta-item .value {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    color: #d0c0b0;
}

/* ── Explicit warning ── */
.explicit-tag {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 1px;
    margin-top: 1rem;
}

.explicit-tag.yes {
    background: rgba(180,60,30,0.15);
    border: 1px solid rgba(180,60,30,0.4);
    color: #c07060;
}

.explicit-tag.no {
    background: rgba(60,80,60,0.15);
    border: 1px solid rgba(60,80,60,0.4);
    color: #708070;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    font-family: 'DM Mono', monospace !important;
    color: #8a6a5a !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0f0d0d; }
::-webkit-scrollbar-thumb { background: #3a2020; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Title ──
st.markdown("""
<div class="title-block">
    <h1>AO3 Analyzer</h1>
    <div class="subtitle">fanfiction · relationship dynamics · analysis</div>
</div>
""", unsafe_allow_html=True)

# ── Input ──
url = st.text_input("AO3 Work URL", placeholder="https://archiveofourown.org/works/...")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_btn = st.button("Analyze", use_container_width=True)

# ── Analysis ──
if analyze_btn:
    if not url:
        st.warning("Please enter an AO3 URL.")
    else:
        with st.spinner("Reading the work..."):
            try:
                result = analyze_pipeline(url)

                if result is None:
                    st.error("Analysis failed. Please check the URL or try another work.")
                else:
                    charA = result["charA"]
                    charB = result["charB"]
                    score = result["score"]
                    delta = result["delta"]
                    switch = result["switch"]
                    verdict = result["result"]
                    has_explicit = result.get("has_explicit", False)

                    # Determine who has higher score
                    top_char = charA if score[charA] >= score[charB] else charB
                    sub_char = charB if top_char == charA else charA

                    # ── CP display ──
                    st.markdown(f"""
                    <div class="cp-display">
                        <span class="cp-name">{top_char}</span>
                        <span class="cp-slash">/</span>
                        <span class="cp-name sub-char">{sub_char}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Score bars ──
                    scoreA_pct = round(abs(score[charA]) * 100, 1)
                    scoreB_pct = round(abs(score[charB]) * 100, 1)
                    max_score = max(scoreA_pct, scoreB_pct, 1)

                    barA_w = round(scoreA_pct / max_score * 100)
                    barB_w = round(scoreB_pct / max_score * 100)
                    fillA = "dom" if score[charA] >= score[charB] else "sub"
                    fillB = "dom" if score[charB] > score[charA] else "sub"

                    st.markdown(f"""
                    <div class="score-section">
                        <div class="score-label">Score Distribution</div>
                        <div class="score-bar-wrap">
                            <span class="score-char">{charA}</span>
                            <div class="score-bar-bg">
                                <div class="score-bar-fill {fillA}" style="width:{barA_w}%"></div>
                            </div>
                            <span class="score-val">{scoreA_pct}</span>
                        </div>
                        <div class="score-bar-wrap">
                            <span class="score-char">{charB}</span>
                            <div class="score-bar-bg">
                                <div class="score-bar-fill {fillB}" style="width:{barB_w}%"></div>
                            </div>
                            <span class="score-val">{scoreB_pct}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Meta row ──
                    st.markdown(f"""
                    <div class="meta-row">
                        <div class="meta-item">
                            <div class="label">Confidence</div>
                            <div class="value">{round(delta * 100, 1)}%</div>
                        </div>
                        <div class="meta-item">
                            <div class="label">Switch Signals</div>
                            <div class="value">{switch}</div>
                        </div>
                        <div class="meta-item">
                            <div class="label">Explicit Content</div>
                            <div class="value">{"Yes" if has_explicit else "No"}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Verdict ──
                    if "SWITCH" in verdict:
                        verdict_class = "switch-text"
                        verdict_display = "Switch"
                    elif "Uncertain" in verdict:
                        verdict_class = "uncertain-text"
                        verdict_display = "Uncertain"
                    else:
                        verdict_class = ""
                        verdict_display = verdict

                    st.markdown(f"""
                    <div class="verdict">
                        <div class="verdict-label">Verdict</div>
                        <div class="verdict-text {verdict_class}">{verdict_display}</div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
