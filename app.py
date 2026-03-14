import streamlit as st
import json
import os
import anthropic
import streamlit.components.v1 as components
from datetime import datetime
import io

def generate_cv_pdf(data):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle

    buffer = io.BytesIO()
    PAGE_W, PAGE_H = A4
    MARGIN = 18 * mm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=14*mm, bottomMargin=14*mm
    )

    PURPLE     = colors.HexColor("#5B4FCF")
    DARK       = colors.HexColor("#111111")
    GRAY       = colors.HexColor("#555555")
    LIGHT_GRAY = colors.HexColor("#888888")
    DIVIDER    = colors.HexColor("#DDDDDD")

    name_style = ParagraphStyle("name", fontName="Helvetica-Bold",
        fontSize=22, textColor=DARK, spaceAfter=2, leading=26)
    contact_style = ParagraphStyle("contact", fontName="Helvetica",
        fontSize=8, textColor=GRAY, spaceAfter=6, leading=12)
    section_style = ParagraphStyle("section", fontName="Helvetica-Bold",
        fontSize=7.5, textColor=PURPLE, spaceBefore=10, spaceAfter=3,
        leading=10, letterSpacing=2)
    summary_style = ParagraphStyle("summary", fontName="Helvetica",
        fontSize=9, textColor=DARK, leading=14, spaceAfter=4)
    job_title_style = ParagraphStyle("jobtitle", fontName="Helvetica-Bold",
        fontSize=9.5, textColor=DARK, leading=13)
    company_style = ParagraphStyle("company", fontName="Helvetica",
        fontSize=8.5, textColor=PURPLE, leading=12, spaceAfter=2)
    bullet_style = ParagraphStyle("bullet", fontName="Helvetica",
        fontSize=8.5, textColor=DARK, leading=13, leftIndent=10,
        bulletIndent=2, spaceAfter=1)
    edu_style = ParagraphStyle("edu", fontName="Helvetica-Bold",
        fontSize=9, textColor=DARK, leading=13)
    edu_sub_style = ParagraphStyle("edusub", fontName="Helvetica",
        fontSize=8.5, textColor=GRAY, leading=12, spaceAfter=4)

    pi = data.get("personal_info", {})
    story = []

    # NAME
    story.append(Paragraph(pi.get("name", "Your Name"), name_style))

    # CONTACT
    contact_parts = [x for x in [
        pi.get("email",""), pi.get("phone",""), pi.get("location",""),
        pi.get("linkedin",""), pi.get("github",""), pi.get("portfolio","")
    ] if x.strip()]
    story.append(Paragraph("  ·  ".join(contact_parts), contact_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PURPLE, spaceAfter=6))

    # SUMMARY
    if data.get("summary"):
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
        story.append(Paragraph(data["summary"], summary_style))
        story.append(HRFlowable(width="100%", thickness=0.4, color=DIVIDER, spaceAfter=4))

    # SKILLS
    if data.get("skills"):
        story.append(Paragraph("TECHNICAL SKILLS", section_style))
        for cat, skills_val in data["skills"].items():
            skill_list = skills_val if isinstance(skills_val, list) else [s.strip() for s in skills_val.split(",")]
            story.append(Paragraph(f"<b>{cat}:</b>  {' · '.join(skill_list)}", ParagraphStyle(
                "skillrow", fontName="Helvetica", fontSize=8.5,
                textColor=DARK, leading=13, spaceAfter=2
            )))
        story.append(HRFlowable(width="100%", thickness=0.4, color=DIVIDER, spaceAfter=4))

    # EXPERIENCE
    if data.get("experience"):
        story.append(Paragraph("EXPERIENCE", section_style))
        for exp in data["experience"]:
            title_para = Paragraph(exp.get("role",""), job_title_style)
            dates_para = Paragraph(exp.get("dates",""), ParagraphStyle(
                "dates", fontName="Helvetica", fontSize=8, textColor=LIGHT_GRAY,
                leading=13, alignment=2
            ))
            t = Table([[title_para, dates_para]], colWidths=[PAGE_W - 2*MARGIN - 55*mm, 55*mm])
            t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
            story.append(t)
            story.append(Paragraph(f"{exp.get('company','')}  ·  {exp.get('location','')}", company_style))
            for bullet in exp.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=0.4, color=DIVIDER, spaceAfter=4))

    # PROJECTS
    if data.get("projects"):
        story.append(Paragraph("PROJECTS", section_style))
        for proj in data["projects"]:
            techs = proj.get("technologies", [])
            if isinstance(techs, str): techs = [t.strip() for t in techs.split(",")]
            title_para = Paragraph(f"<b>{proj.get('name','')}</b>", job_title_style)
            link_para  = Paragraph(proj.get("link",""), ParagraphStyle(
                "link", fontName="Helvetica", fontSize=7.5, textColor=PURPLE,
                leading=13, alignment=2
            ))
            t = Table([[title_para, link_para]], colWidths=[PAGE_W - 2*MARGIN - 60*mm, 60*mm])
            t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
            story.append(t)
            if techs:
                story.append(Paragraph(" · ".join(techs), ParagraphStyle(
                    "tech", fontName="Helvetica-Oblique", fontSize=8,
                    textColor=GRAY, leading=12, spaceAfter=2
                )))
            for bullet in proj.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=0.4, color=DIVIDER, spaceAfter=4))

    # EDUCATION
    if data.get("education"):
        story.append(Paragraph("EDUCATION", section_style))
        for edu in data["education"]:
            degree_para = Paragraph(edu.get("degree",""), edu_style)
            dates_para  = Paragraph(edu.get("dates",""), ParagraphStyle(
                "edudates", fontName="Helvetica", fontSize=8, textColor=LIGHT_GRAY,
                leading=13, alignment=2
            ))
            t = Table([[degree_para, dates_para]], colWidths=[PAGE_W - 2*MARGIN - 50*mm, 50*mm])
            t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
            story.append(t)
            story.append(Paragraph(edu.get("institution",""), edu_sub_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# ─────────────────────────────────────────────
# PAGE CONFIG & GLOBAL STYLES
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CV.Studio",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── RESET & BASE ── */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0a0a0f; color: #e8e6f0; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1400px; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── HERO HEADER ── */
.hero {
    display: flex; align-items: center; justify-content: space-between;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(135deg, #c8b8ff 0%, #7b61ff 50%, #4de8c2 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -1px; line-height: 1;
}
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem; color: #555570; letter-spacing: 2px;
    text-transform: uppercase; margin-top: 0.4rem;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: #0f0f1a;
    border: 1px solid #1e1e2e; border-radius: 12px;
    padding: 4px; margin-bottom: 2rem;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace; font-size: 0.78rem;
    letter-spacing: 1px; text-transform: uppercase;
    color: #555570; border-radius: 8px; padding: 0.6rem 1.4rem;
    border: none !important; background: transparent;
}
.stTabs [aria-selected="true"] {
    background: #1e1e35 !important; color: #c8b8ff !important;
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'DM Mono', monospace; font-size: 0.65rem;
    letter-spacing: 3px; text-transform: uppercase; color: #7b61ff;
    margin-bottom: 0.5rem;
}

/* ── CARDS ── */
.card {
    background: #0f0f1a; border: 1px solid #1e1e2e;
    border-radius: 16px; padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: #7b61ff44; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #0f0f1a !important; border: 1px solid #1e1e2e !important;
    border-radius: 10px !important; color: #e8e6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #7b61ff !important;
    box-shadow: 0 0 0 2px #7b61ff22 !important;
}
label { color: #888 !important; font-size: 0.78rem !important; letter-spacing: 0.5px; }

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important; letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border-radius: 10px !important;
    border: 1px solid #1e1e2e !important;
    background: #0f0f1a !important; color: #888 !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #7b61ff !important; color: #c8b8ff !important;
    background: #1e1e35 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7b61ff, #4de8c2) !important;
    border: none !important; color: #0a0a0f !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px #7b61ff44 !important;
}

/* ── SKILL PILLS ── */
.skill-pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: #1e1e35; border: 1px solid #7b61ff44;
    border-radius: 999px; padding: 0.3rem 0.85rem;
    font-family: 'DM Mono', monospace; font-size: 0.72rem;
    color: #c8b8ff; margin: 0.2rem;
    transition: all 0.2s; cursor: default;
}
.skill-pill:hover { background: #2a2a50; border-color: #7b61ff; }
.skill-category-badge {
    font-family: 'DM Mono', monospace; font-size: 0.6rem;
    letter-spacing: 2px; text-transform: uppercase;
    color: #4de8c2; background: #0d2e28;
    border: 1px solid #4de8c244;
    border-radius: 4px; padding: 0.15rem 0.5rem;
    margin-bottom: 0.6rem; display: inline-block;
}

/* ── EXPANDERS ── */
.streamlit-expanderHeader {
    font-family: 'Syne', sans-serif !important; font-size: 0.9rem !important;
    color: #c8b8ff !important; background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important; border-radius: 12px !important;
}
.streamlit-expanderContent {
    background: #0d0d18 !important;
    border: 1px solid #1e1e2e !important; border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}

/* ── CV PREVIEW ── */
.cv-preview {
    background: #ffffff; color: #111;
    border-radius: 16px; padding: 2.5rem 2.8rem;
    font-family: 'DM Sans', sans-serif;
    box-shadow: 0 32px 80px #00000088;
    line-height: 1.6;
}
.cv-name {
    font-family: 'Syne', sans-serif; font-size: 2rem;
    font-weight: 800; letter-spacing: -1px; color: #111;
    margin-bottom: 0.2rem;
}
.cv-contact {
    font-size: 0.78rem; color: #555; margin-bottom: 1.2rem;
    font-family: 'DM Mono', monospace;
}
.cv-section-title {
    font-family: 'Syne', sans-serif; font-size: 0.7rem;
    letter-spacing: 3px; text-transform: uppercase;
    color: #7b61ff; border-bottom: 2px solid #7b61ff;
    padding-bottom: 0.3rem; margin: 1.2rem 0 0.6rem;
}
.cv-skill-tag {
    display: inline-block; background: #f0eeff;
    border-radius: 4px; padding: 0.15rem 0.5rem;
    font-size: 0.72rem; color: #5040aa;
    margin: 0.15rem; font-family: 'DM Mono', monospace;
}
.cv-job-header {
    display: flex; justify-content: space-between;
    align-items: baseline; margin-bottom: 0.2rem;
}
.cv-job-title { font-weight: 700; font-size: 0.92rem; color: #111; }
.cv-job-meta { font-size: 0.75rem; color: #888; font-family: 'DM Mono', monospace; }
.cv-bullet { font-size: 0.82rem; color: #333; margin: 0.2rem 0 0.2rem 1rem; }

/* ── AI STREAM ── */
.ai-stream-box {
    background: #0d0d18; border: 1px solid #7b61ff33;
    border-radius: 12px; padding: 1rem 1.2rem;
    font-family: 'DM Mono', monospace; font-size: 0.78rem;
    color: #c8b8ff; min-height: 80px;
    white-space: pre-wrap; line-height: 1.7;
}

/* ── DIVIDER ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #7b61ff44, transparent);
    margin: 1.5rem 0;
}

/* ── METRIC CHIPS ── */
.metric-chip {
    background: #1e1e35; border: 1px solid #2e2e50;
    border-radius: 10px; padding: 0.8rem 1rem;
    text-align: center;
}
.metric-chip-value {
    font-family: 'Syne', sans-serif; font-size: 1.6rem;
    font-weight: 800; color: #c8b8ff;
}
.metric-chip-label {
    font-family: 'DM Mono', monospace; font-size: 0.6rem;
    letter-spacing: 2px; text-transform: uppercase; color: #555;
}

/* ── TOAST / SUCCESS ── */
.stSuccess { background: #0d2e28 !important; border: 1px solid #4de8c244 !important; color: #4de8c2 !important; }
.stInfo { background: #1e1e35 !important; border: 1px solid #7b61ff44 !important; color: #c8b8ff !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] { background: #0f0f1a !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────
DATA_FILE = "master_cv.json"
DEFAULT_DATA = {
    "personal_info": {
        "name": "Your Name", "email": "you@email.com",
        "phone": "+1 234 567 8900", "location": "City, Country",
        "linkedin": "linkedin.com/in/yourprofile",
        "github": "github.com/yourusername", "portfolio": "yourwebsite.com"
    },
    "summary": "Software Engineer with 3+ years of experience building scalable web applications...",
    "skills": {
        "Languages": ["Python", "JavaScript", "C++", "SQL"],
        "Frameworks": ["React", "Streamlit", "FastAPI", "Django"],
        "Tools": ["Git", "Docker", "AWS", "Linux"]
    },
    "experience": [
        {
            "company": "Tech Corp", "role": "Software Engineer",
            "dates": "Jan 2022 – Present", "location": "Remote",
            "bullets": [
                "Developed a smart CV generator using Python and Streamlit, increasing user engagement by 40%.",
                "Optimized database queries resulting in a 30% reduction in API response times."
            ]
        }
    ],
    "education": [
        {
            "institution": "University of Technology",
            "degree": "B.S. in Computer Science",
            "dates": "Sep 2017 – May 2021", "gpa": "3.8/4.0"
        }
    ],
    "projects": [
        {
            "name": "Smart CV Builder",
            "technologies": ["Python", "Streamlit", "JSON"],
            "link": "github.com/yourusername/smart-cv",
            "bullets": [
                "Architected an open-source tool to dynamically generate ATS-friendly CVs.",
                "Implemented session state management for live UI editing."
            ]
        }
    ],
    "certifications": [],
    "languages": []
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        # Migrate flat skill strings → lists
        for cat, val in data.get("skills", {}).items():
            if isinstance(val, str):
                data["skills"][cat] = [s.strip() for s in val.split(",") if s.strip()]
        return data
    return json.loads(json.dumps(DEFAULT_DATA))

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    st.toast("✅ CV data saved!", icon="💾")

def count_skills(data):
    return sum(len(v) if isinstance(v, list) else len(v.split(",")) for v in data.get("skills", {}).values())

# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
if "cv_data" not in st.session_state:
    st.session_state.cv_data = load_data()
if "ai_output" not in st.session_state:
    st.session_state.ai_output = ""
if "tailored_cv" not in st.session_state:
    st.session_state.tailored_cv = None

data = st.session_state.cv_data

# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div>
    <div class="hero-title">⬡ CV.Studio</div>
    <div class="hero-sub">AI-Powered Career Intelligence Platform</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Quick stats row
skill_count = count_skills(data)
exp_count = len(data.get("experience", []))
proj_count = len(data.get("projects", []))

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class="metric-chip">
        <div class="metric-chip-value">{skill_count}</div>
        <div class="metric-chip-label">Skills</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="metric-chip">
        <div class="metric-chip-value">{exp_count}</div>
        <div class="metric-chip-label">Roles</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class="metric-chip">
        <div class="metric-chip-value">{proj_count}</div>
        <div class="metric-chip-label">Projects</div>
    </div>""", unsafe_allow_html=True)
with m4:
    total_bullets = sum(len(e.get("bullets", [])) for e in data.get("experience", []))
    st.markdown(f"""<div class="metric-chip">
        <div class="metric-chip-value">{total_bullets}</div>
        <div class="metric-chip-label">Achievements</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_gen, tab_skills, tab_editor, tab_export = st.tabs([
    "✦ AI Tailor", "⬡ Skills Vault", "✎ Edit CV", "↗ Export"
])

# ══════════════════════════════════════════════
# TAB 1 — AI TAILOR + LIVE PREVIEW
# ══════════════════════════════════════════════
with tab_gen:
    left, right = st.columns([1, 1.3], gap="large")

    with left:
        st.markdown('<div class="section-label">Target Position</div>', unsafe_allow_html=True)
        job_title = st.text_input("Job Title", "Senior Software Engineer", label_visibility="collapsed")
        
        st.markdown('<div class="section-label" style="margin-top:1rem">Job Description</div>', unsafe_allow_html=True)
        job_desc = st.text_area("Paste the full job description here…", height=220, label_visibility="collapsed")
        
        col_a, col_b = st.columns(2)
        with col_a:
            tone = st.selectbox("Tone", ["Professional", "Startup-friendly", "Academic", "Executive"])
        with col_b:
            focus = st.selectbox("Emphasize", ["Impact & Metrics", "Technical Depth", "Leadership", "Breadth"])

        if st.button("✦ Tailor My CV with AI", type="primary", use_container_width=True):
            if not job_desc.strip():
                st.warning("Please paste a job description first.")
            else:
                with st.spinner(""):
                    client = anthropic.Anthropic()
                    
                    cv_snapshot = json.dumps({
                        "summary": data.get("summary"),
                        "skills": data.get("skills"),
                        "experience": data.get("experience"),
                        "projects": data.get("projects"),
                    }, indent=2)

                    prompt = f"""You are an elite career coach and CV writer. 
                    
The candidate's current CV data:
{cv_snapshot}

Target job title: {job_title}
Tone: {tone}
Focus: {focus}
Job Description:
{job_desc}

Your task:
1. Write a tailored Professional Summary (3-4 lines) that mirrors the job's language.
2. Rewrite the top 3 most relevant experience bullet points to emphasize {focus} and match keywords from the JD.
3. List the top 8 skills from the candidate's profile that best match this role (as comma-separated).
4. Give 2 specific suggestions to strengthen the CV for this role.

Format your response with clear sections:
## TAILORED SUMMARY
## KEY BULLETS (label each with company name)
## TOP SKILLS MATCH
## STRATEGIC SUGGESTIONS
"""
                    full_response = ""
                    stream_box = st.empty()
                    
                    with client.messages.stream(
                        model="claude-opus-4-5",
                        max_tokens=1200,
                        messages=[{"role": "user", "content": prompt}]
                    ) as stream:
                        for text in stream.text_stream:
                            full_response += text
                            stream_box.markdown(
                                f'<div class="ai-stream-box">{full_response}▌</div>',
                                unsafe_allow_html=True
                            )
                    
                    stream_box.markdown(
                        f'<div class="ai-stream-box">{full_response}</div>',
                        unsafe_allow_html=True
                    )
                    st.session_state.ai_output = full_response

        if st.session_state.ai_output:
            st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
            
            if st.button("⬇ Apply AI Summary to My CV"):
                lines = st.session_state.ai_output.split("\n")
                in_summary = False
                summary_lines = []
                for line in lines:
                    if "TAILORED SUMMARY" in line:
                        in_summary = True; continue
                    if line.startswith("## ") and in_summary:
                        break
                    if in_summary and line.strip():
                        summary_lines.append(line.strip())
                if summary_lines:
                    st.session_state.cv_data["summary"] = " ".join(summary_lines)
                    save_data(st.session_state.cv_data)
                    st.success("Summary updated!")

    with right:
        st.markdown('<div class="section-label">Live CV Preview</div>', unsafe_allow_html=True)
        
        d = st.session_state.cv_data
        pi = d.get("personal_info", {})
        
        # Build skill tags HTML
        all_skill_tags = ""
        for cat, skills in d.get("skills", {}).items():
            skill_list = skills if isinstance(skills, list) else [s.strip() for s in skills.split(",")]
            for s in skill_list:
                all_skill_tags += f'<span class="cv-skill-tag">{s}</span>'
        
        # Build experience HTML
        exp_html = ""
        for exp in d.get("experience", []):
            bullets_html = "".join(f'<div class="cv-bullet">• {b}</div>' for b in exp.get("bullets", []))
            exp_html += f"""
            <div style="margin-bottom:0.8rem">
                <div class="cv-job-header">
                    <span class="cv-job-title">{exp.get('role','')}</span>
                    <span class="cv-job-meta">{exp.get('dates','')}</span>
                </div>
                <div style="font-size:0.78rem;color:#7b61ff;margin-bottom:0.3rem;font-family:'DM Mono',monospace">{exp.get('company','')} · {exp.get('location','')}</div>
                {bullets_html}
            </div>"""
        
        # Build education HTML
        edu_html = ""
        for edu in d.get("education", []):
            edu_html += f"""
            <div style="margin-bottom:0.5rem">
                <div class="cv-job-header">
                    <span class="cv-job-title">{edu.get('degree','')}</span>
                    <span class="cv-job-meta">{edu.get('dates','')}</span>
                </div>
                <div style="font-size:0.78rem;color:#555;font-family:'DM Mono',monospace">{edu.get('institution','')}</div>
            </div>"""

        # Build projects HTML
        proj_html = ""
        for proj in d.get("projects", []):
            techs = proj.get("technologies", [])
            if isinstance(techs, str): techs = [t.strip() for t in techs.split(",")]
            tech_tags = "".join(f'<span class="cv-skill-tag">{t}</span>' for t in techs)
            bullets_html = "".join(f'<div class="cv-bullet">• {b}</div>' for b in proj.get("bullets", []))
            proj_html += f"""
            <div style="margin-bottom:0.8rem">
                <div class="cv-job-header">
                    <span class="cv-job-title">{proj.get('name','')}</span>
                    <span class="cv-job-meta" style="font-size:0.68rem">{proj.get('link','')}</span>
                </div>
                <div style="margin-bottom:0.3rem">{tech_tags}</div>
                {bullets_html}
            </div>"""

        preview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; padding: 0; }}
            .cv-preview {{
                background: #ffffff; color: #111;
                border-radius: 16px; padding: 2.2rem 2.5rem;
                font-family: 'DM Sans', sans-serif;
                box-shadow: 0 32px 80px rgba(0,0,0,0.5);
                line-height: 1.6;
            }}
            .cv-name {{
                font-family: 'Syne', sans-serif; font-size: 2rem;
                font-weight: 800; letter-spacing: -1px; color: #111;
                margin-bottom: 0.25rem;
            }}
            .cv-contact {{
                font-size: 0.75rem; color: #555; margin-bottom: 1.2rem;
                font-family: 'DM Mono', monospace;
            }}
            .cv-section-title {{
                font-family: 'Syne', sans-serif; font-size: 0.65rem;
                letter-spacing: 3px; text-transform: uppercase;
                color: #7b61ff; border-bottom: 2px solid #7b61ff;
                padding-bottom: 0.25rem; margin: 1.1rem 0 0.55rem;
            }}
            .cv-skill-tag {{
                display: inline-block; background: #f0eeff;
                border-radius: 4px; padding: 0.12rem 0.45rem;
                font-size: 0.7rem; color: #5040aa;
                margin: 0.12rem; font-family: 'DM Mono', monospace;
            }}
            .cv-job-header {{
                display: flex; justify-content: space-between;
                align-items: baseline; margin-bottom: 0.15rem;
            }}
            .cv-job-title {{ font-weight: 700; font-size: 0.88rem; color: #111; }}
            .cv-job-meta {{ font-size: 0.72rem; color: #888; font-family: 'DM Mono', monospace; }}
            .cv-company {{ font-size: 0.75rem; color: #7b61ff; margin-bottom: 0.25rem; font-family: 'DM Mono', monospace; }}
            .cv-bullet {{ font-size: 0.8rem; color: #333; margin: 0.18rem 0 0.18rem 1rem; }}
            .cv-exp-block {{ margin-bottom: 0.9rem; }}
        </style>
        </head>
        <body>
        <div class="cv-preview">
            <div class="cv-name">{pi.get('name', 'Your Name')}</div>
            <div class="cv-contact">
                {pi.get('email','')} &nbsp;·&nbsp; {pi.get('phone','')} &nbsp;·&nbsp; {pi.get('location','')} &nbsp;·&nbsp;
                {pi.get('linkedin','')} &nbsp;·&nbsp; {pi.get('github','')}
            </div>

            <div class="cv-section-title">Professional Summary</div>
            <div style="font-size:0.8rem;color:#333;line-height:1.6">{d.get('summary','')}</div>

            <div class="cv-section-title">Technical Skills</div>
            <div>{all_skill_tags}</div>

            <div class="cv-section-title">Experience</div>
            {exp_html}

            <div class="cv-section-title">Projects</div>
            {proj_html}

            <div class="cv-section-title">Education</div>
            {edu_html}
        </div>
        </body>
        </html>
        """
        components.html(preview_html, height=900, scrolling=True)


# ══════════════════════════════════════════════
# TAB 2 — SKILLS VAULT (the killer feature)
# ══════════════════════════════════════════════
with tab_skills:
    st.markdown('<div class="section-label">Your Skills Vault</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#555;font-size:0.83rem;margin-bottom:1.5rem'>Add, organize, and grow your skills. Every skill you add is immediately reflected in your CV.</p>", unsafe_allow_html=True)

    skills = st.session_state.cv_data.setdefault("skills", {})

    # ── Existing Skills Display ──
    if skills:
        for cat, skill_list in list(skills.items()):
            if isinstance(skill_list, str):
                skill_list = [s.strip() for s in skill_list.split(",") if s.strip()]
                skills[cat] = skill_list

            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f'<div class="skill-category-badge">{cat}</div>', unsafe_allow_html=True)
                pills_html = "".join(
                    f'<span class="skill-pill">⬡ {s}</span>' for s in skill_list
                )
                st.markdown(f'<div style="margin-bottom:0.3rem">{pills_html}</div>', unsafe_allow_html=True)
            with cols[1]:
                if st.button("✎ Edit", key=f"edit_cat_{cat}"):
                    st.session_state[f"editing_{cat}"] = True

            if st.session_state.get(f"editing_{cat}"):
                with st.container():
                    st.markdown(f"<div style='background:#0f0f1a;border:1px solid #1e1e2e;border-radius:12px;padding:1rem;margin:0.5rem 0'>", unsafe_allow_html=True)
                    new_val = st.text_input(
                        f"Edit {cat} skills (comma-separated)",
                        value=", ".join(skill_list),
                        key=f"edit_val_{cat}"
                    )
                    c1, c2, c3 = st.columns([1,1,2])
                    with c1:
                        if st.button("Save", key=f"save_{cat}"):
                            skills[cat] = [s.strip() for s in new_val.split(",") if s.strip()]
                            st.session_state[f"editing_{cat}"] = False
                            save_data(st.session_state.cv_data)
                            st.rerun()
                    with c2:
                        if st.button("Delete Cat", key=f"del_{cat}"):
                            del skills[cat]
                            st.session_state[f"editing_{cat}"] = False
                            save_data(st.session_state.cv_data)
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

    # ── Add New Skill ──
    st.markdown('<div class="section-label" style="margin-top:1.5rem">⊕ Add a New Skill</div>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            existing_cats = list(skills.keys())
            add_mode = st.radio("Category", ["Existing category", "New category"], horizontal=True)
        
        with col2:
            if add_mode == "Existing category" and existing_cats:
                selected_cat = st.selectbox("Pick category", existing_cats, label_visibility="collapsed")
            else:
                selected_cat = st.text_input("New category name", placeholder="e.g. Cloud, AI/ML, Soft Skills", label_visibility="collapsed")
        
        with col3:
            new_skill = st.text_input("Skill name", placeholder="e.g. Rust", label_visibility="collapsed")

        if st.button("⊕ Add Skill", type="primary", use_container_width=False):
            if selected_cat and new_skill.strip():
                if selected_cat not in skills:
                    skills[selected_cat] = []
                if isinstance(skills[selected_cat], str):
                    skills[selected_cat] = [s.strip() for s in skills[selected_cat].split(",") if s.strip()]
                if new_skill.strip() not in skills[selected_cat]:
                    skills[selected_cat].append(new_skill.strip())
                    save_data(st.session_state.cv_data)
                    st.toast(f"✅ '{new_skill}' added to {selected_cat}!", icon="⬡")
                    st.rerun()
                else:
                    st.warning(f"'{new_skill}' already exists in {selected_cat}.")
            else:
                st.warning("Please fill in both category and skill name.")

    # ── AI Skill Suggester ──
    st.markdown('<div class="fancy-divider" style="margin-top:2rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">✦ AI Skill Gap Analyzer</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#555;font-size:0.83rem'>Paste a job description and get AI suggestions for skills you might be missing.</p>", unsafe_allow_html=True)

    jd_for_skills = st.text_area("Job Description for Skill Analysis", height=120, key="jd_skills", label_visibility="collapsed", placeholder="Paste job description here…")
    
    if st.button("✦ Analyze Skill Gaps", use_container_width=False):
        if jd_for_skills.strip():
            with st.spinner("Analyzing…"):
                client = anthropic.Anthropic()
                current_skills_flat = []
                for v in skills.values():
                    if isinstance(v, list): current_skills_flat.extend(v)
                    else: current_skills_flat.extend([s.strip() for s in v.split(",")])
                
                prompt = f"""The candidate already has these skills: {', '.join(current_skills_flat)}

Job Description:
{jd_for_skills}

Identify up to 8 specific skills/technologies mentioned in the JD that the candidate likely lacks.
For each, give: skill name | category | why it matters for this role (1 sentence).
Format as a simple list, one per line:
SKILL | CATEGORY | REASON"""

                resp = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=600,
                    messages=[{"role": "user", "content": prompt}]
                )
                suggestions_raw = resp.content[0].text
                st.session_state["skill_suggestions"] = suggestions_raw

    if "skill_suggestions" in st.session_state:
        st.markdown('<div class="section-label" style="margin-top:1rem">Suggested Skills to Learn</div>', unsafe_allow_html=True)
        lines = [l.strip() for l in st.session_state["skill_suggestions"].split("\n") if "|" in l]
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                skill_name = parts[0].lstrip("-• ").strip()
                category = parts[1] if len(parts) > 1 else "Other"
                reason = parts[2] if len(parts) > 2 else ""
                
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.markdown(f'<span class="skill-pill" style="background:#1a1a10;border-color:#4de8c244;color:#4de8c2">⊕ {skill_name}</span>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='color:#555;font-size:0.75rem'>{reason}</span>", unsafe_allow_html=True)
                with c3:
                    if st.button("Add to CV", key=f"add_suggest_{i}"):
                        if category not in skills:
                            skills[category] = []
                        if isinstance(skills[category], str):
                            skills[category] = [s.strip() for s in skills[category].split(",")]
                        if skill_name not in skills[category]:
                            skills[category].append(skill_name)
                            save_data(st.session_state.cv_data)
                            st.toast(f"Added {skill_name}!", icon="✅")
                            st.rerun()


# ══════════════════════════════════════════════
# TAB 3 — EDITOR
# ══════════════════════════════════════════════
with tab_editor:
    st.markdown('<div class="section-label">Edit Your CV Data</div>', unsafe_allow_html=True)

    # Personal Info
    with st.expander("👤 Personal Information", expanded=False):
        pi = st.session_state.cv_data["personal_info"]
        c1, c2 = st.columns(2)
        pi["name"]     = c1.text_input("Full Name", pi.get("name",""))
        pi["email"]    = c2.text_input("Email", pi.get("email",""))
        pi["phone"]    = c1.text_input("Phone", pi.get("phone",""))
        pi["location"] = c2.text_input("Location", pi.get("location",""))
        pi["linkedin"] = c1.text_input("LinkedIn", pi.get("linkedin",""))
        pi["github"]   = c2.text_input("GitHub", pi.get("github",""))
        pi["portfolio"]= c1.text_input("Portfolio / Website", pi.get("portfolio",""))

        st.session_state.cv_data["summary"] = st.text_area(
            "Professional Summary", st.session_state.cv_data.get("summary",""), height=100
        )

    # Experience
    with st.expander("💼 Experience"):
        for i, exp in enumerate(st.session_state.cv_data.get("experience", [])):
            st.markdown(f"<div class='section-label'>Role {i+1}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            exp["company"]  = c1.text_input("Company",  exp.get("company",""),  key=f"co_{i}")
            exp["role"]     = c2.text_input("Job Title", exp.get("role",""),     key=f"ro_{i}")
            exp["dates"]    = c1.text_input("Dates",     exp.get("dates",""),    key=f"dt_{i}")
            exp["location"] = c2.text_input("Location",  exp.get("location",""), key=f"lo_{i}")
            bullets_text = "\n".join(exp.get("bullets", []))
            new_b = st.text_area("Achievements (one per line)", bullets_text, key=f"bu_{i}", height=100)
            exp["bullets"] = [b.strip() for b in new_b.split("\n") if b.strip()]
            
            if st.button("🗑 Remove this role", key=f"del_exp_{i}"):
                st.session_state.cv_data["experience"].pop(i)
                save_data(st.session_state.cv_data)
                st.rerun()
            st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

        if st.button("➕ Add New Role"):
            st.session_state.cv_data["experience"].append({
                "company": "", "role": "", "dates": "", "location": "", "bullets": []
            })
            save_data(st.session_state.cv_data)
            st.rerun()

    # Education
    with st.expander("🎓 Education"):
        for i, edu in enumerate(st.session_state.cv_data.get("education", [])):
            c1, c2 = st.columns(2)
            edu["institution"] = c1.text_input("Institution", edu.get("institution",""), key=f"inst_{i}")
            edu["degree"]      = c2.text_input("Degree",      edu.get("degree",""),      key=f"deg_{i}")
            edu["dates"]       = c1.text_input("Dates",       edu.get("dates",""),        key=f"eddt_{i}")
            st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

        if st.button("➕ Add Education"):
            st.session_state.cv_data["education"].append({"institution":"","degree":"","dates":"","gpa":""})
            save_data(st.session_state.cv_data)
            st.rerun()

    # Projects
    with st.expander("🚀 Projects"):
        for i, proj in enumerate(st.session_state.cv_data.get("projects", [])):
            st.markdown(f"<div class='section-label'>Project {i+1}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            proj["name"] = c1.text_input("Project Name", proj.get("name",""), key=f"pn_{i}")
            proj["link"] = c2.text_input("Link",         proj.get("link",""), key=f"pl_{i}")
            
            techs = proj.get("technologies", [])
            if isinstance(techs, list): techs_str = ", ".join(techs)
            else: techs_str = techs
            new_techs = st.text_input("Technologies (comma-separated)", techs_str, key=f"pt_{i}")
            proj["technologies"] = [t.strip() for t in new_techs.split(",") if t.strip()]
            
            bullets_text = "\n".join(proj.get("bullets", []))
            new_b = st.text_area("Description bullets (one per line)", bullets_text, key=f"pb_{i}", height=80)
            proj["bullets"] = [b.strip() for b in new_b.split("\n") if b.strip()]

            if st.button("🗑 Remove project", key=f"del_proj_{i}"):
                st.session_state.cv_data["projects"].pop(i)
                save_data(st.session_state.cv_data)
                st.rerun()
            st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

        if st.button("➕ Add New Project"):
            st.session_state.cv_data["projects"].append({"name":"","link":"","technologies":[],"bullets":[]})
            save_data(st.session_state.cv_data)
            st.rerun()

    # Save all
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    if st.button("💾 Save All Changes", type="primary", use_container_width=True):
        save_data(st.session_state.cv_data)
        st.rerun()


# ══════════════════════════════════════════════
# TAB 4 — EXPORT
# ══════════════════════════════════════════════
with tab_export:
    st.markdown('<div class="section-label">Export Your CV</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#c8b8ff;margin-bottom:0.5rem">📄 JSON Export</div>
            <p style="color:#555;font-size:0.8rem">Export your raw CV data as JSON for backup or migration.</p>
        </div>
        """, unsafe_allow_html=True)
        
        json_str = json.dumps(st.session_state.cv_data, indent=4)
        st.download_button(
            label="⬇ Download master_cv.json",
            data=json_str,
            file_name="master_cv.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        st.markdown("""
        <div class="card">
            <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#c8b8ff;margin-bottom:0.5rem">📝 Plain Text Export</div>
            <p style="color:#555;font-size:0.8rem">ATS-safe plain text version, perfect for online application forms.</p>
        </div>
        """, unsafe_allow_html=True)
        
        d = st.session_state.cv_data
        pi = d.get("personal_info", {})
        lines = [
            pi.get("name",""), 
            f"{pi.get('email','')} | {pi.get('phone','')} | {pi.get('location','')}",
            f"{pi.get('linkedin','')} | {pi.get('github','')}",
            "", "PROFESSIONAL SUMMARY", "-"*40,
            d.get("summary",""), "",
            "SKILLS", "-"*40,
        ]
        for cat, skills_val in d.get("skills",{}).items():
            sl = skills_val if isinstance(skills_val, list) else [s.strip() for s in skills_val.split(",")]
            lines.append(f"{cat}: {', '.join(sl)}")
        lines += ["", "EXPERIENCE", "-"*40]
        for exp in d.get("experience",[]):
            lines.append(f"{exp.get('role','')} | {exp.get('company','')} | {exp.get('dates','')}")
            for b in exp.get("bullets",[]): lines.append(f"  • {b}")
            lines.append("")
        lines += ["EDUCATION", "-"*40]
        for edu in d.get("education",[]):
            lines.append(f"{edu.get('degree','')} | {edu.get('institution','')} | {edu.get('dates','')}")
        
        plain_text = "\n".join(lines)
        st.download_button(
            label="⬇ Download CV as .txt",
            data=plain_text,
            file_name="cv_plain.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col3:
        st.markdown("""
        <div class="card">
            <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#c8b8ff;margin-bottom:0.5rem">🖨 PDF Export</div>
            <p style="color:#555;font-size:0.8rem">Print-ready PDF with clean typography. Send directly to recruiters.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⬇ Generate & Download PDF", use_container_width=True):
            try:
                pdf_bytes = generate_cv_pdf(st.session_state.cv_data)
                name_slug = st.session_state.cv_data.get("personal_info",{}).get("name","cv").replace(" ","_").lower()
                st.download_button(
                    label="📥 Click to Save PDF",
                    data=pdf_bytes,
                    file_name=f"{name_slug}_cv.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}. Make sure reportlab is installed: pip install reportlab")

    st.markdown('<div class="fancy-divider" style="margin:2rem 0"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">✦ AI Cover Letter Generator</div>', unsafe_allow_html=True)
    
    cl_job = st.text_input("Job Title for Cover Letter", "Software Engineer")
    cl_company = st.text_input("Company Name", "Acme Corp")
    cl_jd = st.text_area("Job Description (optional but recommended)", height=120, key="cl_jd")
    
    if st.button("✦ Generate Cover Letter", type="primary"):
        with st.spinner("Writing your cover letter…"):
            client = anthropic.Anthropic()
            d = st.session_state.cv_data
            pi = d.get("personal_info", {})
            
            prompt = f"""Write a compelling, personalized cover letter for:
Candidate: {pi.get('name','')}
Applying for: {cl_job} at {cl_company}

Their background:
- Summary: {d.get('summary','')}
- Top experience: {json.dumps(d.get('experience',[])[0] if d.get('experience') else {}, indent=2)}
- Key skills: {', '.join([s for v in d.get('skills',{}).values() for s in (v if isinstance(v,list) else v.split(','))][:12])}

Job Description: {cl_jd if cl_jd else 'Not provided'}

Write a 3-paragraph cover letter that:
1. Opens with a compelling hook (NOT "I am writing to apply")
2. Connects their specific experience to the role's needs
3. Closes with confidence and a clear call to action

Tone: Professional yet personable. Avoid clichés."""

            cover_letter = ""
            cl_box = st.empty()
            with client.messages.stream(
                model="claude-opus-4-5",
                max_tokens=800,
                messages=[{"role":"user","content":prompt}]
            ) as stream:
                for text in stream.text_stream:
                    cover_letter += text
                    cl_box.markdown(f'<div class="ai-stream-box">{cover_letter}▌</div>', unsafe_allow_html=True)
            
            cl_box.markdown(f'<div class="ai-stream-box">{cover_letter}</div>', unsafe_allow_html=True)
            
            st.download_button(
                "⬇ Download Cover Letter",
                data=cover_letter,
                file_name=f"cover_letter_{cl_company.lower().replace(' ','_')}.txt",
                mime="text/plain"
            )