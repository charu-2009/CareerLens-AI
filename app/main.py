# ============================================================
# CAREERLENS AI — STREAMLIT APPLICATION
# ============================================================

import sys
from pathlib import Path
from textwrap import dedent

import altair as alt
import pandas as pd
import streamlit as st


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# CAREERLENS IMPORTS
# ============================================================

from src.models.report_builder_v2 import build_careerlens_report_v2


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareerLens AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HTML HELPER
# IMPORTANT:
# dedent() prevents Streamlit Markdown from interpreting
# indented HTML as a literal code block.
# ============================================================

def render_html(markup: str):
    """
    Render raw HTML/CSS without passing it through Markdown.

    st.markdown(..., unsafe_allow_html=True) can still interpret
    indented nested HTML as Markdown code blocks. st.html()
    avoids that parser entirely.
    """
    st.html(
        dedent(markup).strip()
    )


# ============================================================
# THEME CONFIGURATION
# ============================================================

THEME_OPTIONS = {
    "🌙 Dark Modern": "dark_modern",
    "☀️ Light Professional": "light_professional",
    "🌿 Gradient Fresh": "gradient_fresh",
    "💜 Minimal Purple": "minimal_purple",
    "🍂 Warm Earth": "warm_earth",
    "🌌 Dark Glass": "dark_glass",
}


THEME_DESCRIPTIONS = {
    "dark_modern":
        "Dark navy navigation with purple and blue AI accents.",
    "light_professional":
        "Bright, clean and professional analytics dashboard.",
    "gradient_fresh":
        "Fresh teal and green data-intelligence style.",
    "minimal_purple":
        "Minimal white interface with soft purple accents.",
    "warm_earth":
        "Warm amber and orange visual style.",
    "dark_glass":
        "Futuristic dark interface with glass-like surfaces.",
}


THEMES = {

    "light_professional": {

        "label": "Light Professional",
        "mode": "light",

        "page_bg": "#F6F8FC",
        "sidebar_bg": "#EEF4FB",
        "sidebar_bg_2": "#E7EFF9",

        "primary": "#1769E0",
        "button_text": "#FFFFFF",
        "secondary": "#3485F7",

        "text": "#111827",
        "muted": "#53657D",

        "card": "#FFFFFF",
        "border": "#D6DFEB",

        "hero_1": "#EAF3FF",
        "hero_2": "#F8FBFF",
        "hero_text": "#10213A",
        "hero_muted": "#445B78",

        "sidebar_text": "#14213D",
        "sidebar_muted": "#536B89",

        "input_bg": "#FFFFFF",
        "input_border": "#C8D4E3",
        "input_text": "#111827",

        "accent_soft": "#E8F2FF",
        "focus": "#1769E0",
    },


    "dark_modern": {

        "label": "Dark Modern",
        "mode": "dark",

        "page_bg": "#071426",
        "sidebar_bg": "#071A2E",
        "sidebar_bg_2": "#091D33",

        "primary": "#22B8CF",
        "button_text": "#07111F",
        "secondary": "#20C997",

        "text": "#F5F8FC",
        "muted": "#B4C1D3",

        "card": "#0D1C2F",
        "border": "#29415D",

        "hero_1": "#0B1930",
        "hero_2": "#102A3D",
        "hero_text": "#FFFFFF",
        "hero_muted": "#C9D5E5",

        "sidebar_text": "#F5F8FC",
        "sidebar_muted": "#B6C4D7",

        "input_bg": "#0D2136",
        "input_border": "#3B5674",
        "input_text": "#FFFFFF",

        "accent_soft": "#0D3440",
        "focus": "#39D6E8",
    },


    "midnight_blue": {

        "label": "Midnight Blue",
        "mode": "dark",

        "page_bg": "#06101E",
        "sidebar_bg": "#07192F",
        "sidebar_bg_2": "#0A2140",

        "primary": "#2588FF",
        "button_text": "#FFFFFF",
        "secondary": "#8158FF",

        "text": "#F7FAFF",
        "muted": "#B8C8DD",

        "card": "#0D2145",
        "border": "#294A73",

        "hero_1": "#071A3B",
        "hero_2": "#21164F",
        "hero_text": "#FFFFFF",
        "hero_muted": "#D9E1F5",

        "sidebar_text": "#F7FAFF",
        "sidebar_muted": "#B5C7DF",

        "input_bg": "#0B2341",
        "input_border": "#365A82",
        "input_text": "#FFFFFF",

        "accent_soft": "#102F5A",
        "focus": "#58A6FF",
    },


    "soft_lavender": {

        "label": "Soft Lavender",
        "mode": "light",

        "page_bg": "#FBFAFF",
        "sidebar_bg": "#F1EDFF",
        "sidebar_bg_2": "#EAE4FF",

        "primary": "#6242D8",
        "button_text": "#FFFFFF",
        "secondary": "#8A63E8",

        "text": "#29213F",
        "muted": "#625A75",

        "card": "#FFFFFF",
        "border": "#DCD5F0",

        "hero_1": "#F3EFFF",
        "hero_2": "#FBF9FF",
        "hero_text": "#29213F",
        "hero_muted": "#5C5274",

        "sidebar_text": "#30264A",
        "sidebar_muted": "#675D80",

        "input_bg": "#FFFFFF",
        "input_border": "#CFC6E8",
        "input_text": "#29213F",

        "accent_soft": "#EFE9FF",
        "focus": "#6242D8",
    },


    "high_contrast": {

        "label": "High Contrast",
        "mode": "dark",

        "page_bg": "#000000",
        "sidebar_bg": "#050505",
        "sidebar_bg_2": "#000000",

        "primary": "#FFF200",
        "button_text": "#000000",
        "secondary": "#FFD400",

        "text": "#FFFFFF",
        "muted": "#E6E6E6",

        "card": "#0A0A0A",
        "border": "#BDBDBD",

        "hero_1": "#000000",
        "hero_2": "#101010",
        "hero_text": "#FFFFFF",
        "hero_muted": "#F2F2F2",

        "sidebar_text": "#FFFFFF",
        "sidebar_muted": "#E8E8E8",

        "input_bg": "#000000",
        "input_border": "#FFFFFF",
        "input_text": "#FFFFFF",

        "accent_soft": "#282600",
        "focus": "#FFF200",
    },
}


THEME_OPTIONS = {

    "Light Professional":
        "light_professional",

    "Dark Modern":
        "dark_modern",

    "Midnight Blue":
        "midnight_blue",

    "Soft Lavender":
        "soft_lavender",

    "High Contrast":
        "high_contrast",
}


THEME_DESCRIPTIONS = {

    "light_professional":
        "Clean, bright and professional for everyday use.",

    "dark_modern":
        "A focused dark interface designed for comfortable viewing.",

    "midnight_blue":
        "A premium navy workspace with modern blue accents.",

    "soft_lavender":
        "A friendly light interface with restrained lavender accents.",

    "high_contrast":
        "Maximum visual separation for strong readability.",
}


if "app_theme" not in st.session_state:
    st.session_state.app_theme = "dark_modern"


def get_theme():
    return THEMES.get(
        st.session_state.app_theme,
        THEMES["dark_modern"],
    )


def apply_theme(theme_name: str):

    theme = THEMES.get(
        theme_name,
        THEMES["dark_modern"],
    )

    render_html(
        f"""
        <style>

        :root {{
            --page-bg: {theme["page_bg"]};
            --sidebar-bg: {theme["sidebar_bg"]};
            --sidebar-bg-2: {theme["sidebar_bg_2"]};

            --primary: {theme["primary"]};
            --button-text: {theme["button_text"]};
            --secondary: {theme["secondary"]};

            --text: {theme["text"]};
            --muted: {theme["muted"]};

            --card: {theme["card"]};
            --border: {theme["border"]};

            --hero-1: {theme["hero_1"]};
            --hero-2: {theme["hero_2"]};
            --hero-text: {theme["hero_text"]};
            --hero-muted: {theme["hero_muted"]};

            --sidebar-text: {theme["sidebar_text"]};
            --sidebar-muted: {theme["sidebar_muted"]};

            --input-bg: {theme["input_bg"]};
            --input-border: {theme["input_border"]};
            --input-text: {theme["input_text"]};

            --accent-soft: {theme["accent_soft"]};
            --focus: {theme["focus"]};
        }}


        /* ---------------- Global ---------------- */

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {{
            background:
                var(--page-bg) !important;

            color:
                var(--text) !important;
        }}


        .block-container {{
            max-width:
                1380px;

            padding-top:
                1.1rem;

            padding-bottom:
                3rem;

            padding-left:
                2rem;

            padding-right:
                2rem;
        }}


        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6 {{
            color:
                var(--text) !important;

            letter-spacing:
                -0.02em;
        }}


        .stApp p,
        .stApp label,
        .stApp li {{
            color:
                var(--text);
        }}


        .stApp a {{
            color:
                var(--primary) !important;
        }}


        hr {{
            border-color:
                var(--border) !important;
        }}


        /* ---------------- Captions ---------------- */

        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p,
        .stApp small {{
            color:
                var(--muted) !important;
        }}


        /* ---------------- Sidebar ---------------- */

        section[data-testid="stSidebar"] {{
            background:
                linear-gradient(
                    180deg,
                    var(--sidebar-bg),
                    var(--sidebar-bg-2)
                ) !important;

            border-right:
                1px solid var(--border);
        }}


        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {{
            color:
                var(--sidebar-text) !important;
        }}


        section[data-testid="stSidebar"]
        [data-testid="stCaptionContainer"],
        section[data-testid="stSidebar"]
        [data-testid="stCaptionContainer"] p {{
            color:
                var(--sidebar-muted) !important;
        }}


        /* ---------------- Inputs ---------------- */

        div[data-baseweb="select"] > div,
        input,
        textarea {{
            background:
                var(--input-bg) !important;

            border-color:
                var(--input-border) !important;

            color:
                var(--input-text) !important;
        }}


        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div > div {{
            background:
                var(--input-bg) !important;

            color:
                var(--input-text) !important;

            border-color:
                var(--input-border) !important;
        }}


        div[data-baseweb="select"] span {{
            color:
                var(--input-text) !important;
        }}


        div[data-baseweb="select"] svg {{
            color:
                var(--input-text) !important;

            fill:
                currentColor !important;
        }}


        input::placeholder,
        textarea::placeholder {{
            color:
                var(--muted) !important;

            opacity:
                1 !important;
        }}


        input:focus,
        textarea:focus,
        div[data-baseweb="select"] > div:focus-within {{
            outline:
                2px solid var(--focus) !important;

            outline-offset:
                1px;
        }}


        /* ---------------- Hero ---------------- */

        .career-hero {{
            position:
                relative;

            overflow:
                hidden;

            padding:
                38px 40px;

            border-radius:
                20px;

            background:
                radial-gradient(
                    circle at 86% 28%,
                    color-mix(
                        in srgb,
                        var(--secondary) 25%,
                        transparent
                    ),
                    transparent 28%
                ),
                linear-gradient(
                    120deg,
                    var(--hero-1),
                    var(--hero-2)
                );

            border:
                1px solid var(--border);

            margin-bottom:
                24px;
        }}


        .career-hero h1 {{
            color:
                var(--hero-text) !important;

            font-size:
                clamp(
                    2.1rem,
                    4vw,
                    3.2rem
                );

            font-weight:
                850;

            line-height:
                1.08;

            margin:
                0;
        }}


        .career-hero .accent {{
            background:
                linear-gradient(
                    90deg,
                    var(--primary),
                    var(--secondary)
                );

            -webkit-background-clip:
                text;

            -webkit-text-fill-color:
                transparent;

            background-clip:
                text;
        }}


        .career-hero p {{
            color:
                var(--hero-muted) !important;

            max-width:
                760px;

            line-height:
                1.7;
        }}


        /* ---------------- Cards ---------------- */

        .career-card {{
            background:
                var(--card);

            border:
                1px solid var(--border);

            border-radius:
                16px;

            padding:
                20px 22px;
        }}


        .career-card-label,
        .career-card-caption {{
            color:
                var(--muted) !important;
        }}


        .career-card-value {{
            color:
                var(--text) !important;
        }}


        .career-badge {{
            background:
                var(--accent-soft);

            color:
                var(--primary) !important;
        }}


        /* ---------------- Streamlit containers ---------------- */

        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background:
                var(--card) !important;

            border-color:
                var(--border) !important;

            border-radius:
                14px !important;
        }}


        /* ---------------- Metrics ---------------- */

        div[data-testid="stMetric"] {{
            background:
                var(--card) !important;

            border:
                1px solid var(--border);

            border-radius:
                15px;

            padding:
                17px 18px;
        }}


        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] p {{
            color:
                var(--muted) !important;
        }}


        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {{
            color:
                var(--text) !important;
        }}


        /* ---------------- Buttons ---------------- */

        div.stButton > button[kind="primary"] {{
            border:
                none !important;

            border-radius:
                10px !important;

            font-weight:
                750 !important;

            min-height:
                45px;

            background:
                linear-gradient(
                    90deg,
                    var(--primary),
                    var(--secondary)
                ) !important;

            color:
                var(--button-text) !important;
        }}


        div.stButton > button:not([kind="primary"]) {{
            background:
                var(--card) !important;

            color:
                var(--text) !important;

            border:
                1px solid var(--border) !important;
        }}


        div.stButton > button:focus-visible {{
            outline:
                3px solid var(--focus) !important;

            outline-offset:
                2px;
        }}


        /* ---------------- Tabs ---------------- */

        button[data-baseweb="tab"] {{
            color:
                var(--muted) !important;

            font-weight:
                650;
        }}


        button[data-baseweb="tab"][aria-selected="true"] {{
            color:
                var(--text) !important;
        }}


        [data-baseweb="tab-highlight"] {{
            background-color:
                var(--primary) !important;
        }}


        /* ---------------- Expanders ---------------- */

        [data-testid="stExpander"],
        details {{
            background:
                var(--card) !important;

            border:
                1px solid var(--border) !important;

            border-radius:
                12px !important;
        }}


        [data-testid="stExpander"] summary,
        details summary {{
            background:
                var(--card) !important;

            color:
                var(--text) !important;

            border-radius:
                11px !important;
        }}


        [data-testid="stExpander"] summary *,
        details summary * {{
            color:
                var(--text) !important;

            fill:
                var(--text) !important;
        }}


        [data-testid="stExpander"] summary:hover,
        details summary:hover {{
            background:
                var(--accent-soft) !important;
        }}


        [data-testid="stExpander"] svg,
        details summary svg {{
            color:
                var(--text) !important;

            fill:
                currentColor !important;
        }}


        /* ---------------- Progress ---------------- */

        [data-testid="stProgress"] > div > div {{
            background-color:
                var(--border) !important;
        }}


        [data-testid="stProgress"] > div > div > div {{
            background:
                linear-gradient(
                    90deg,
                    var(--primary),
                    var(--secondary)
                ) !important;
        }}


        /* ---------------- Alerts ---------------- */

        div[data-testid="stAlert"] {{
            border-radius:
                12px !important;

            border:
                1px solid var(--border) !important;
        }}


        /* ---------------- Dataframes ---------------- */

        div[data-testid="stDataFrame"] {{
            border:
                1px solid var(--border);

            border-radius:
                14px;

            overflow:
                hidden;

            background:
                var(--card);
        }}


        /* ---------------- Skill chips ---------------- */

        .skill-chip {{
            background:
                var(--accent-soft) !important;

            color:
                var(--text) !important;

            border:
                1px solid var(--border) !important;
        }}


        /* ---------------- Popovers ---------------- */

        [data-baseweb="popover"],
        [data-baseweb="popover"] > div,
        [role="listbox"],
        [role="listbox"] > div {{
            background:
                var(--card) !important;

            color:
                var(--text) !important;
        }}


        [role="option"],
        [role="option"] * {{
            background:
                var(--card) !important;

            color:
                var(--text) !important;
        }}


        [role="option"]:hover,
        [role="option"][aria-selected="true"] {{
            background:
                var(--accent-soft) !important;

            color:
                var(--text) !important;
        }}


        /* ---------------- Responsive ---------------- */

        @media (max-width: 800px) {{

            .block-container {{
                padding-left:
                    1rem;

                padding-right:
                    1rem;
            }}

            .career-hero {{
                padding:
                    28px 24px;
            }}
        }}


        #MainMenu {{
            visibility:
                hidden;
        }}


        footer {{
            visibility:
                hidden;
        }}

        </style>
        """
    )




apply_theme(st.session_state.app_theme)


# ============================================================
# ALTAIR THEME HELPER
# ============================================================

def style_chart(chart):
    theme = get_theme()

    return (
        chart
        .configure_view(
            strokeOpacity=0
        )
        .configure_axis(
            labelColor=theme["muted"],
            titleColor=theme["muted"],
            gridColor=theme["border"],
            domainColor=theme["border"],
            tickColor=theme["border"],
        )
        .configure_title(
            color=theme["text"]
        )
        .configure(
            background="transparent"
        )
    )


# ============================================================
# LOAD CAREERLENS V2 BACKEND
# ============================================================

@st.cache_resource
def load_careerlens_backend():
    """
    Validate availability of the frozen CareerLens V2 report API.

    The V2 report builder resolves recommendation, explanation,
    market, and growth evidence internally through frozen modules.
    """
    return build_careerlens_report_v2


try:
    careeerlens_v2_runner = load_careerlens_backend()

except Exception as error:

    st.error("CareerLens V2 backend could not be loaded.")

    st.exception(error)

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div style="padding:8px 2px 16px 2px;">
            <div style="
                font-size:27px;
                font-weight:850;
                color:var(--sidebar-text);
                letter-spacing:-0.02em;
            ">
                🎯 CareerLens <span style="color:var(--secondary);">AI</span>
            </div>

            <div style="
                color:var(--sidebar-muted);
                font-size:13px;
                line-height:1.6;
                margin-top:6px;
            ">
                AI-Powered Job Market &amp;<br>
                Skill Gap Analytics Platform
            </div>
        </div>
        """
    )

    st.divider()

    render_html(
        """
        <div style="
            color:var(--primary);
            font-size:12px;
            font-weight:800;
            letter-spacing:.08em;
            margin-bottom:8px;
        ">
            👤 YOUR PROFILE
        </div>
        """
    )

    skills_input = st.text_area(
        "Enter your current skills",
        placeholder=(
            "Python, SQL, Excel,\n"
            "Power BI, Machine Learning"
        ),
        height=125,
    )

    experience = st.number_input(
        "Years of experience",
        min_value=0.0,
        max_value=40.0,
        value=0.0,
        step=0.5,
    )

    analyze_button = st.button(
        "🚀 Analyze My Career",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    render_html(
        """
        <div style="
            color:var(--primary);
            font-size:12px;
            font-weight:800;
            letter-spacing:.08em;
            margin-bottom:8px;
        ">
            🎨 APPEARANCE
        </div>
        """
    )

    theme_labels = list(THEME_OPTIONS.keys())

    current_theme = st.session_state.app_theme

    current_label = next(
        label
        for label, value in THEME_OPTIONS.items()
        if value == current_theme
    )

    selected_theme_label = st.selectbox(
        "Choose theme",
        options=theme_labels,
        index=theme_labels.index(current_label),
        help="Switch the visual appearance of CareerLens.",
    )

    selected_theme = THEME_OPTIONS[
        selected_theme_label
    ]

    st.caption(
        THEME_DESCRIPTIONS.get(
            selected_theme,
            ""
        )
    )

    if selected_theme != st.session_state.app_theme:
        st.session_state.app_theme = selected_theme
        st.rerun()

    st.divider()

    with st.expander("About CareerLens"):
        st.write(
            """
            CareerLens uses your recognized skills and career-domain
            evidence to identify relevant career paths and assess readiness
            where validated profiles are available. Supported market,
            experience, education, remote-work, location, and experimental
            growth information is shown separately as descriptive context
            and does not determine career ranking.
            """
        )


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="career-hero">
        <h1>
            Find Your
            <span class="accent">Best Career Path</span>
        </h1>

        <p>
            Understand your strengths, identify skill gaps,
            and explore market intelligence to make more
            confident career decisions.
        </p>
    </div>
    """
)


# ============================================================
# RUN CAREERLENS V2
# ============================================================

if analyze_button:

    if not skills_input.strip():

        st.warning(
            "Please enter at least one skill."
        )

    else:

        user_skills = [

            skill.strip()

            for skill
            in skills_input.split(",")

            if skill.strip()
        ]


        try:

            with st.spinner(
                "Analyzing your skills across CareerLens V2..."
            ):

                report = careeerlens_v2_runner(
                    user_skills
                )


            st.session_state[
                "careerlens_v2_report"
            ] = report


            st.session_state[
                "careerlens_v2_input_skills"
            ] = user_skills


            # Retire stale V1 payload from the active UI path.
            if (
                "career_lens_result"
                in
                st.session_state
            ):

                del st.session_state[
                    "career_lens_result"
                ]


        except Exception as error:

            st.error(
                "Career analysis failed."
            )

            st.exception(
                error
            )


# ============================================================
# EMPTY STATE
# ============================================================

if "careerlens_v2_report" not in st.session_state:

    render_html(
        """
        <div class="career-card" style="margin-top:4px;">
            <div class="career-card-label">
                Ready when you are
            </div>

            <div class="career-card-value"
                 style="font-size:1.3rem;">
                Add your skills in the sidebar
            </div>

            <div class="career-card-caption"
                 style="font-size:0.92rem; line-height:1.6;">
                CareerLens will rank suitable careers,
                identify skill gaps, and generate a
                personalized learning roadmap.
            </div>
        </div>
        """
    )

    st.stop()


# ============================================================
# RESULT VARIABLES
# ============================================================

report_v2 = st.session_state["careerlens_v2_report"]


# ============================================================
# CAREERLENS V2 RESULTS INTERFACE
# ============================================================


# ------------------------------------------------------------
# RESULT HELPERS
# ------------------------------------------------------------

def format_percent_v2(value):

    if value is None:
        return "Unavailable"

    try:
        return f"{float(value):.2f}%"

    except Exception:
        return str(value)


def format_number_v2(value):

    if value is None:
        return "Unavailable"

    try:

        number = float(value)

        if number.is_integer():
            return f"{int(number):,}"

        return f"{number:,.2f}"

    except Exception:
        return str(value)


def format_currency_usd_v2(value):

    if value is None:
        return "Unavailable"

    try:

        return f"${float(value):,.0f}"

    except Exception:

        return str(value)


def format_percent_plain_v2(value):

    if value is None:
        return "Unavailable"

    try:

        return f"{float(value):.2f}%"

    except Exception:

        return str(value)


def render_skill_chips_v2(skills):

    if not skills:
        return

    chip_html = "".join(
        f"""
        <span style="
            display:inline-block;
            padding:6px 10px;
            margin:3px 4px 3px 0;
            border-radius:999px;
            border:1px solid rgba(148,163,184,.28);
            font-size:.84rem;
        ">
            {skill}
        </span>
        """
        for skill in skills
    )

    st.markdown(
        chip_html,
        unsafe_allow_html=True
    )


def render_career_card_v2(card):

    career_name = card.get(
        "career_name",
        "Career"
    )

    badge = card.get(
        "badge",
        ""
    )

    display_rank = card.get(
        "display_rank"
    )

    presentation_state = card.get(
        "presentation_state"
    )

    primary_domain = card.get(
        "primary_domain"
    )

    matched_domain = card.get(
        "matched_domain"
    )

    readiness = (
        card.get(
            "readiness"
        )
        or
        {}
    )

    readiness_available = readiness.get(
        "available",
        False
    )

    score = readiness.get(
        "score"
    )

    display_note = card.get(
        "display_note"
    )


    # --------------------------------------------------------
    # Presentation-state labels
    # --------------------------------------------------------

    state_labels = {

        "readiness_match":
            "Readiness Match",

        "limited_readiness_match":
            "Limited-Evidence Match",

        "validated_no_current_match":
            "No Current Skill Match",

        "related_career":
            "Related Career",

        "discovery_only":
            "Explore",
    }


    state_label = state_labels.get(
        presentation_state,
        badge
        or
        "Career"
    )


    with st.container(
        border=True
    ):

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        title_col, status_col = st.columns(
            [4, 1.25]
        )


        with title_col:

            if display_rank is not None:

                st.markdown(
                    f"### #{display_rank} · {career_name}"
                )

            else:

                st.markdown(
                    f"### {career_name}"
                )


        with status_col:

            st.markdown(
                f"**{state_label}**"
            )


        # ----------------------------------------------------
        # Domain context
        # ----------------------------------------------------

        domain_parts = []


        if primary_domain:

            domain_parts.append(
                f"Primary domain: **{primary_domain}**"
            )


        if (
            matched_domain
            and
            matched_domain
            !=
            primary_domain
        ):

            domain_parts.append(
                f"Reached through: **{matched_domain}**"
            )


        if domain_parts:

            st.caption(
                " · ".join(
                    domain_parts
                )
            )


        # ----------------------------------------------------
        # Readiness visualization
        # ----------------------------------------------------

        if (
            readiness_available
            and
            score is not None
        ):

            try:

                numeric_score = float(
                    score
                )

            except Exception:

                numeric_score = None


            score_col1, score_col2 = st.columns(
                [1.2, 3]
            )


            with score_col1:

                st.metric(
                    "Readiness",
                    format_percent_v2(
                        score
                    )
                )


            with score_col2:

                if numeric_score is not None:

                    safe_progress = max(
                        0.0,
                        min(
                            numeric_score
                            /
                            100.0,
                            1.0
                        )
                    )


                    st.progress(
                        safe_progress
                    )


                    if presentation_state == "validated_no_current_match":

                        st.caption(
                            "Validated profile available, but your current "
                            "skills do not match its readiness requirements."
                        )

                    else:

                        st.caption(
                            "Weighted coverage of validated readiness "
                            "requirements."
                        )


        else:

            if presentation_state == "related_career":

                st.info(
                    "This career is related through routing evidence. "
                    "A readiness score is not currently available."
                )

            elif presentation_state == "discovery_only":

                st.info(
                    "This career is available for exploration, but "
                    "CareerLens does not currently have enough validated "
                    "evidence to calculate readiness."
                )

            else:

                st.caption(
                    "Readiness evidence is unavailable."
                )


        # ----------------------------------------------------
        # Evidence / confidence
        # ----------------------------------------------------

        if readiness_available:

            evidence_level = readiness.get(
                "evidence_level"
            )

            confidence = readiness.get(
                "confidence"
            )


            evidence_col1, evidence_col2 = st.columns(
                2
            )


            with evidence_col1:

                st.caption(
                    "Evidence level: "
                    +
                    (
                        str(
                            evidence_level
                        ).replace(
                            "_",
                            " "
                        ).title()
                        if evidence_level is not None
                        else
                        "Unavailable"
                    )
                )


            with evidence_col2:

                st.caption(
                    "Readiness confidence: "
                    +
                    (
                        str(
                            confidence
                        ).replace(
                            "_",
                            " "
                        ).title()
                        if confidence is not None
                        else
                        "Unavailable"
                    )
                )


        # ----------------------------------------------------
        # Presentation note
        # ----------------------------------------------------

        if display_note:

            st.caption(
                display_note
            )


# ------------------------------------------------------------
# RESULT PAYLOAD
# ------------------------------------------------------------

report_v2 = st.session_state[
    "careerlens_v2_report"
]


presentation_summary_v2 = (
    report_v2.get(
        "presentation_summary"
    )
    or
    {}
)


sections_v2 = (
    report_v2.get(
        "sections"
    )
    or
    {}
)


section_metadata_v2 = (
    report_v2.get(
        "section_metadata"
    )
    or
    {}
)


cards_v2 = (
    report_v2.get(
        "cards"
    )
    or
    []
)


# ============================================================
# ANALYSIS SUMMARY
# ============================================================

st.subheader(
    "Your CareerLens Results"
)

st.caption(
    "CareerLens separates readiness matches, validated profiles with "
    "no current skill match, related careers, and discovery-only careers "
    "so different evidence levels are not mixed into one universal ranking."
)


summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(
    4
)


with summary_col1:

    st.metric(
        "Total Candidates",
        report_v2.get(
            "candidate_count",
            0
        )
    )


with summary_col2:

    st.metric(
        "Readiness Matches",
        presentation_summary_v2.get(
            "positive_readiness_matches",
            0
        )
    )


with summary_col3:

    st.metric(
        "Related Careers",
        presentation_summary_v2.get(
            "related_careers",
            0
        )
    )


with summary_col4:

    st.metric(
        "Discovery Careers",
        presentation_summary_v2.get(
            "discovery_only",
            0
        )
    )


secondary_col1, secondary_col2 = st.columns(
    2
)


with secondary_col1:

    st.metric(
        "Validated — No Current Match",
        presentation_summary_v2.get(
            "validated_zero_matches",
            0
        )
    )


with secondary_col2:

    st.metric(
        "Limited-Evidence Matches",
        presentation_summary_v2.get(
            "limited_positive_matches",
            0
        )
    )


# ============================================================
# ROUTING + SKILL INPUT SUMMARY
# ============================================================

st.divider()

st.markdown(
    "### Analysis Context"
)

st.caption(
    "These signals explain how CareerLens interpreted your submitted skills "
    "and which domains contributed to candidate generation."
)


context_col1, context_col2 = st.columns(
    2
)


with context_col1:

    st.markdown(
        "**Recognized skills**"
    )

    known_skills_v2 = report_v2.get(
        "known_skills",
        []
    )


    if known_skills_v2:

        render_skill_chips_v2(
            known_skills_v2
        )

    else:

        st.caption(
            "No recognized skills."
        )


with context_col2:

    st.markdown(
        "**Unrecognized skills**"
    )

    unknown_skills_v2 = report_v2.get(
        "unknown_skills",
        []
    )


    if unknown_skills_v2:

        render_skill_chips_v2(
            unknown_skills_v2
        )

        st.caption(
            "Unrecognized skills are preserved rather than "
            "silently removed from your input."
        )

    else:

        st.caption(
            "All submitted skills were recognized."
        )


retained_domains_v2 = report_v2.get(
    "retained_domains",
    []
)


if retained_domains_v2:

    st.markdown(
        "**Routing domains**"
    )

    for routing_domain_v2 in retained_domains_v2:

        if isinstance(
            routing_domain_v2,
            dict
        ):

            domain_name_v2 = str(
                routing_domain_v2.get(
                    "domain",
                    "Unknown domain"
                )
            )

            confidence_state_v2 = str(
                routing_domain_v2.get(
                    "confidence_state",
                    "available"
                )
            ).replace(
                "_",
                " "
            ).strip().title()

            matched_skills_v2 = (
                routing_domain_v2.get(
                    "matched_skills",
                    []
                )
                or
                []
            )

            matched_skill_count_v2 = (
                routing_domain_v2.get(
                    "matched_skill_count",
                    len(
                        matched_skills_v2
                    )
                )
            )

            try:

                matched_skill_count_v2 = int(
                    matched_skill_count_v2
                )

            except (
                TypeError,
                ValueError
            ):

                matched_skill_count_v2 = len(
                    matched_skills_v2
                )


            st.markdown(
                f"**{domain_name_v2}**"
            )

            st.caption(
                f"{confidence_state_v2} routing evidence · "
                f"{matched_skill_count_v2} matched "
                f"{'skill' if matched_skill_count_v2 == 1 else 'skills'}"
            )

            if matched_skills_v2:

                render_skill_chips_v2(
                    [
                        str(
                            skill
                        )
                        for skill in matched_skills_v2
                    ]
                )


        else:

            st.markdown(
                f"**{str(routing_domain_v2)}**"
            )


    st.caption(
        "Routing domains explain which areas contributed to "
        "candidate generation. They are not probabilities, "
        "readiness scores, or career-fit scores."
    )


# ============================================================
# READINESS MATCHES
# ============================================================

readiness_matches_v2 = sections_v2.get(
    "readiness_matches",
    []
)


if readiness_matches_v2:

    metadata = section_metadata_v2.get(
        "readiness_matches",
        {}
    )


    st.divider()

    st.header(
        metadata.get(
            "title",
            "Readiness Matches"
        )
    )


    st.caption(
        metadata.get(
            "description",
            ""
        )
    )


    for card in readiness_matches_v2:

        render_career_card_v2(
            card
        )


# ============================================================
# LIMITED-EVIDENCE READINESS MATCHES
# ============================================================

limited_matches_v2 = sections_v2.get(
    "limited_readiness_matches",
    []
)


if limited_matches_v2:

    metadata = section_metadata_v2.get(
        "limited_readiness_matches",
        {}
    )


    st.divider()

    st.header(
        metadata.get(
            "title",
            "Limited-Evidence Readiness Matches"
        )
    )


    st.caption(
        metadata.get(
            "description",
            ""
        )
    )


    st.info(
        "These careers have readiness estimates based on a "
        "more limited validated evidence profile. Their percentages "
        "should not be ranked directly against full-readiness careers."
    )


    for card in limited_matches_v2:

        render_career_card_v2(
            card
        )


# ============================================================
# VALIDATED PROFILES WITH NO CURRENT MATCH
# ============================================================

zero_match_v2 = sections_v2.get(
    "validated_no_current_match",
    []
)


if zero_match_v2:

    metadata = section_metadata_v2.get(
        "validated_no_current_match",
        {}
    )


    st.divider()

    st.header(
        metadata.get(
            "title",
            "Validated Profiles With No Current Skill Match"
        )
    )


    st.caption(
        metadata.get(
            "description",
            ""
        )
    )


    with st.expander(
        f"View {len(zero_match_v2)} careers",
        expanded=False
    ):

        for card in zero_match_v2:

            render_career_card_v2(
                card
            )


# ============================================================
# RELATED CAREERS
# ============================================================

related_v2 = sections_v2.get(
    "related_careers",
    []
)


if related_v2:

    metadata = section_metadata_v2.get(
        "related_careers",
        {}
    )


    st.divider()

    st.header(
        metadata.get(
            "title",
            "Related Careers"
        )
    )


    st.caption(
        metadata.get(
            "description",
            ""
        )
    )


    with st.expander(
        f"View {len(related_v2)} related careers",
        expanded=False
    ):

        for card in related_v2:

            render_career_card_v2(
                card
            )


# ============================================================
# DISCOVERY-ONLY CAREERS
# ============================================================

discovery_v2 = sections_v2.get(
    "discovery_only",
    []
)


if discovery_v2:

    metadata = section_metadata_v2.get(
        "discovery_only",
        {}
    )


    st.divider()

    st.header(
        metadata.get(
            "title",
            "Explore More Careers"
        )
    )


    st.caption(
        metadata.get(
            "description",
            ""
        )
    )


    with st.expander(
        f"View {len(discovery_v2)} careers",
        expanded=False
    ):

        for card in discovery_v2:

            render_career_card_v2(
                card
            )


# ============================================================
# NO-CANDIDATE STATE
# ============================================================

if not cards_v2:

    routing_state_v2 = report_v2.get(
        "routing_state"
    )


    if routing_state_v2 == "tentative_insufficient_for_careers":

        st.info(
            "CareerLens recognized part of your skill profile, "
            "but there is not yet enough routing evidence to generate "
            "career candidates. Try adding more relevant skills."
        )


    elif routing_state_v2 == "no_routing_evidence":

        st.info(
            "CareerLens could not find enough routing evidence from "
            "the submitted skills. Try entering additional technical, "
            "business, analytical, or domain-specific skills."
        )


    else:

        st.info(
            "No career candidates are currently available for this input."
        )


# ============================================================
# CAREER DETAIL
# ============================================================

if cards_v2:

    st.divider()

    st.header(
        "Career Detail"
    )

    st.caption(
        "Select any candidate to inspect its readiness evidence, skill gap, "
        "market context, routing explanation, and experimental growth evidence."
    )


    career_names_v2 = [

        card.get(
            "career_name",
            "Career"
        )

        for card in cards_v2
    ]


    selected_career_v2 = st.selectbox(
        "Select a career to explore",
        career_names_v2,
        key="careerlens_v2_selected_career"
    )


    selected_card_v2 = next(
        (
            card
            for card
            in cards_v2
            if card.get(
                "career_name"
            )
            ==
            selected_career_v2
        ),
        cards_v2[
            0
        ]
    )


    st.markdown(
        f"## {selected_card_v2.get('career_name', 'Career')}"
    )


    selected_state_v2 = selected_card_v2.get(
        "presentation_state",
        ""
    )


    selected_badge_v2 = selected_card_v2.get(
        "badge",
        ""
    )


    selected_domain_v2 = selected_card_v2.get(
        "primary_domain"
    )


    selected_context_parts_v2 = []


    if selected_badge_v2:

        selected_context_parts_v2.append(
            selected_badge_v2
        )


    if selected_domain_v2:

        selected_context_parts_v2.append(
            selected_domain_v2
        )


    if selected_context_parts_v2:

        st.caption(
            " · ".join(
                selected_context_parts_v2
            )
        )


    st.caption(
        selected_card_v2.get(
            "display_note",
            ""
        )
    )


    detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs(
        [
            "Readiness",
            "Skill Gap",
            "Market Context",
            "Growth & Evidence",
        ]
    )


    # --------------------------------------------------------
    # READINESS TAB
    # --------------------------------------------------------

    with detail_tab1:

        readiness_v2 = (
            selected_card_v2.get(
                "readiness"
            )
            or
            {}
        )


        if readiness_v2.get(
            "available",
            False
        ):

            metric_col1, metric_col2, metric_col3 = st.columns(
                3
            )


            with metric_col1:

                st.metric(
                    "Readiness Coverage",
                    format_percent_v2(
                        readiness_v2.get(
                            "score"
                        )
                    )
                )


            with metric_col2:

                st.metric(
                    "Evidence Level",
                    str(
                        readiness_v2.get(
                            "evidence_level",
                            "Unavailable"
                        )
                    ).replace(
                        "_",
                        " "
                    ).title()
                )


            with metric_col3:

                confidence_v2 = readiness_v2.get(
                    "confidence"
                )

                st.metric(
                    "Readiness Confidence",
                    (
                        str(
                            confidence_v2
                        ).replace(
                            "_",
                            " "
                        ).title()
                        if confidence_v2 is not None
                        else "Unavailable"
                    )
                )


            st.write(
                readiness_v2.get(
                    "summary",
                    ""
                )
            )


            st.info(
                readiness_v2.get(
                    "interpretation",
                    ""
                )
            )


        else:

            st.info(
                readiness_v2.get(
                    "summary",
                    "Readiness evidence is unavailable."
                )
            )


        routing_v2 = (
            selected_card_v2.get(
                "routing"
            )
            or
            {}
        )


        st.markdown(
            "### Why this career appeared"
        )


        st.write(
            routing_v2.get(
                "summary",
                ""
            )
        )


        st.caption(
            routing_v2.get(
                "warning",
                ""
            )
        )


    # --------------------------------------------------------
    # SKILL GAP TAB
    # --------------------------------------------------------

    with detail_tab2:

        gap_v2 = (
            selected_card_v2.get(
                "skill_gap"
            )
            or
            {}
        )


        if gap_v2.get(
            "available",
            False
        ):

            gap_col1, gap_col2, gap_col3 = st.columns(
                3
            )


            with gap_col1:

                st.metric(
                    "Missing Requirements",
                    (
                        gap_v2.get(
                            "missing_total"
                        )
                        if
                        gap_v2.get(
                            "missing_total"
                        )
                        is not None
                        else
                        "Unavailable"
                    )
                )


            with gap_col2:

                core_count_v2 = gap_v2.get(
                    "missing_core_count"
                )

                st.metric(
                    "Missing Core",
                    (
                        core_count_v2
                        if core_count_v2 is not None
                        else "Unavailable"
                    )
                )


            with gap_col3:

                important_count_v2 = gap_v2.get(
                    "missing_important_count"
                )

                st.metric(
                    "Missing Important",
                    (
                        important_count_v2
                        if important_count_v2 is not None
                        else "Unavailable"
                    )
                )


            st.write(
                gap_v2.get(
                    "summary",
                    ""
                )
            )


            st.caption(
                gap_v2.get(
                    "ordering_note",
                    ""
                )
            )


            if (
                not gap_v2.get(
                    "missing_core_skills"
                )
                and
                not gap_v2.get(
                    "missing_important_skills"
                )
                and
                (
                    gap_v2.get(
                        "missing_total"
                    )
                    or
                    0
                )
                >
                0
            ):

                st.info(
                    "CareerLens currently has an authoritative count "
                    "of missing readiness requirements for this career, "
                    "but the production result does not expose individual "
                    "missing skill names. No names are invented."
                )


        else:

            st.info(
                gap_v2.get(
                    "summary",
                    "Skill-gap evidence is unavailable."
                )
            )


    # --------------------------------------------------------
    # MARKET CONTEXT TAB
    # --------------------------------------------------------

    with detail_tab3:

        market_v2 = (
            selected_card_v2.get(
                "market"
            )
            or
            {}
        )


        if market_v2.get(
            "available",
            False
        ):

            demand_v2 = (
                market_v2.get(
                    "demand"
                )
                or
                {}
            )


            market_col1, market_col2, market_col3 = st.columns(
                3
            )


            with market_col1:

                st.metric(
                    "Observed Job Records",
                    format_number_v2(
                        demand_v2.get(
                            "job_count"
                        )
                    )
                )


            with market_col2:

                market_share_v2 = demand_v2.get(
                    "market_share"
                )


                if market_share_v2 is not None:

                    try:

                        market_share_display_v2 = (
                            f"{float(market_share_v2) * 100:.2f}%"
                        )

                    except Exception:

                        market_share_display_v2 = str(
                            market_share_v2
                        )

                else:

                    market_share_display_v2 = "Unavailable"


                st.metric(
                    "Dataset Share",
                    market_share_display_v2
                )


            with market_col3:

                st.metric(
                    "Relative Representation",
                    (
                        format_number_v2(
                            demand_v2.get(
                                "relative_demand_score"
                            )
                        )
                        +
                        " / 100"
                        if
                        demand_v2.get(
                            "relative_demand_score"
                        )
                        is not None
                        else
                        "Unavailable"
                    )
                )


            st.write(
                market_v2.get(
                    "summary",
                    ""
                )
            )


            st.caption(
                market_v2.get(
                    "warning",
                    ""
                )
            )


            top_market_skills_v2 = market_v2.get(
                "top_market_skills",
                []
            )


            if top_market_skills_v2:

                st.markdown(
                    "### Common Market Skills"
                )


                market_skill_rows_v2 = []


                for item in top_market_skills_v2[:10]:

                    if isinstance(
                        item,
                        dict
                    ):

                        market_skill_rows_v2.append(
                            item
                        )


                if market_skill_rows_v2:

                    st.dataframe(
                        pd.DataFrame(
                            market_skill_rows_v2
                        ),
                        use_container_width=True,
                        hide_index=True
                    )


            salary_v2 = market_v2.get(
                "salary"
            )


            if isinstance(
                salary_v2,
                dict
            ) and salary_v2:

                with st.expander(
                    "Salary context",
                    expanded=False
                ):

                    salary_col1, salary_col2, salary_col3 = st.columns(
                        3
                    )


                    with salary_col1:

                        st.metric(
                            "Median Salary",
                            format_currency_usd_v2(
                                salary_v2.get(
                                    "median_salary_usd"
                                )
                            )
                        )


                    with salary_col2:

                        st.metric(
                            "Average Salary",
                            format_currency_usd_v2(
                                salary_v2.get(
                                    "average_salary_usd"
                                )
                            )
                        )


                    with salary_col3:

                        st.metric(
                            "Salary Category",
                            salary_v2.get(
                                "salary_category",
                                "Unavailable"
                            )
                        )


                    salary_range_col1, salary_range_col2, salary_range_col3 = st.columns(
                        3
                    )


                    with salary_range_col1:

                        st.metric(
                            "25th Percentile",
                            format_currency_usd_v2(
                                salary_v2.get(
                                    "salary_p25_usd"
                                )
                            )
                        )


                    with salary_range_col2:

                        st.metric(
                            "75th Percentile",
                            format_currency_usd_v2(
                                salary_v2.get(
                                    "salary_p75_usd"
                                )
                            )
                        )


                    with salary_range_col3:

                        st.metric(
                            "90th Percentile",
                            format_currency_usd_v2(
                                salary_v2.get(
                                    "salary_p90_usd"
                                )
                            )
                        )


                    st.caption(
                        "Salary data is descriptive market context, "
                        "not a personal earnings estimate."
                    )


            experience_v2 = market_v2.get(
                "experience"
            )


            if isinstance(
                experience_v2,
                dict
            ) and experience_v2:

                with st.expander(
                    "Experience context",
                    expanded=False
                ):

                    exp_col1, exp_col2, exp_col3 = st.columns(
                        3
                    )


                    with exp_col1:

                        st.metric(
                            "Median Experience",
                            (
                                f"{experience_v2.get('median_experience_years'):.1f} years"
                                if experience_v2.get(
                                    "median_experience_years"
                                ) is not None
                                else "Unavailable"
                            )
                        )


                    with exp_col2:

                        st.metric(
                            "Average Experience",
                            (
                                f"{experience_v2.get('average_experience_years'):.1f} years"
                                if experience_v2.get(
                                    "average_experience_years"
                                ) is not None
                                else "Unavailable"
                            )
                        )


                    with exp_col3:

                        st.metric(
                            "Experience Category",
                            experience_v2.get(
                                "experience_category",
                                "Unavailable"
                            )
                        )


                    exp_col4, exp_col5 = st.columns(
                        2
                    )


                    with exp_col4:

                        st.metric(
                            "Entry-Level Opportunities",
                            format_percent_plain_v2(
                                experience_v2.get(
                                    "entry_level_opportunity_percent"
                                )
                            )
                        )


                    with exp_col5:

                        st.metric(
                            "Zero-Experience Opportunities",
                            format_percent_plain_v2(
                                experience_v2.get(
                                    "zero_experience_opportunity_percent"
                                )
                            )
                        )


                    st.caption(
                        "Experience evidence is descriptive and is "
                        "not used as an eligibility or ranking score."
                    )


            education_v2 = market_v2.get(
                "education"
            )


            if isinstance(
                education_v2,
                dict
            ) and education_v2:

                with st.expander(
                    "Education context",
                    expanded=False
                ):

                    edu_col1, edu_col2 = st.columns(
                        2
                    )


                    with edu_col1:

                        st.metric(
                            "Most Common Education",
                            education_v2.get(
                                "dominant_education",
                                "Unavailable"
                            )
                        )


                    with edu_col2:

                        st.metric(
                            "Education Pattern",
                            education_v2.get(
                                "education_category",
                                "Unavailable"
                            )
                        )


                    edu_col3, edu_col4, edu_col5 = st.columns(
                        3
                    )


                    with edu_col3:

                        st.metric(
                            "Bachelor",
                            format_percent_plain_v2(
                                education_v2.get(
                                    "bachelor_percent"
                                )
                            )
                        )


                    with edu_col4:

                        st.metric(
                            "Master",
                            format_percent_plain_v2(
                                education_v2.get(
                                    "master_percent"
                                )
                            )
                        )


                    with edu_col5:

                        st.metric(
                            "PhD",
                            format_percent_plain_v2(
                                education_v2.get(
                                    "phd_percent"
                                )
                            )
                        )


                    edu_col6, edu_col7 = st.columns(
                        2
                    )


                    with edu_col6:

                        st.metric(
                            "Bachelor or Below",
                            format_percent_plain_v2(
                                education_v2.get(
                                    "bachelor_or_below_percent"
                                )
                            )
                        )


                    with edu_col7:

                        st.metric(
                            "Advanced Degree",
                            format_percent_plain_v2(
                                education_v2.get(
                                    "advanced_degree_percent"
                                )
                            )
                        )


                    st.caption(
                        "Education distributions describe the supported "
                        "dataset and do not define mandatory eligibility."
                    )


            remote_v2 = market_v2.get(
                "remote"
            )


            if isinstance(
                remote_v2,
                dict
            ) and remote_v2:

                with st.expander(
                    "Remote-work context",
                    expanded=False
                ):

                    remote_col1, remote_col2 = st.columns(
                        2
                    )


                    with remote_col1:

                        st.metric(
                            "Flexibility Category",
                            remote_v2.get(
                                "remote_flexibility_category",
                                "Unavailable"
                            )
                        )


                    with remote_col2:

                        st.metric(
                            "Average Remote Ratio",
                            format_percent_plain_v2(
                                remote_v2.get(
                                    "average_remote_ratio"
                                )
                            )
                        )


                    remote_col3, remote_col4, remote_col5 = st.columns(
                        3
                    )


                    with remote_col3:

                        st.metric(
                            "On-site",
                            format_percent_plain_v2(
                                remote_v2.get(
                                    "on_site_percent"
                                )
                            )
                        )


                    with remote_col4:

                        st.metric(
                            "Hybrid",
                            format_percent_plain_v2(
                                remote_v2.get(
                                    "hybrid_percent"
                                )
                            )
                        )


                    with remote_col5:

                        st.metric(
                            "Remote",
                            format_percent_plain_v2(
                                remote_v2.get(
                                    "remote_percent"
                                )
                            )
                        )


                    st.caption(
                        "Remote-work evidence is descriptive context "
                        "and does not affect career ranking."
                    )


            location_v2 = market_v2.get(
                "location"
            )


            if isinstance(
                location_v2,
                list
            ) and location_v2:

                with st.expander(
                    "Observed company locations",
                    expanded=False
                ):

                    st.dataframe(
                        pd.DataFrame(
                            location_v2
                        ),
                        use_container_width=True,
                        hide_index=True
                    )


        else:

            st.info(
                market_v2.get(
                    "summary",
                    "Supported market evidence is unavailable."
                )
            )


            st.caption(
                market_v2.get(
                    "warning",
                    ""
                )
            )


    # --------------------------------------------------------
    # GROWTH + EVIDENCE TAB
    # --------------------------------------------------------

    with detail_tab4:

        growth_v2 = (
            selected_card_v2.get(
                "growth"
            )
            or
            {}
        )


        if growth_v2.get(
            "available",
            False
        ):

            growth_col1, growth_col2 = st.columns(
                2
            )


            with growth_col1:

                st.metric(
                    "Experimental Growth Outlook",
                    growth_v2.get(
                        "outlook",
                        "Unavailable"
                    )
                )


            with growth_col2:

                st.metric(
                    "Growth Confidence",
                    growth_v2.get(
                        "confidence",
                        "Unavailable"
                    )
                )


            st.write(
                growth_v2.get(
                    "summary",
                    ""
                )
            )


            st.warning(
                growth_v2.get(
                    "warning",
                    ""
                )
            )


        else:

            st.info(
                growth_v2.get(
                    "summary",
                    "Experimental growth evidence is unavailable."
                )
            )


        ordering_v2 = (
            selected_card_v2.get(
                "ordering"
            )
            or
            {}
        )


        st.markdown(
            "### Recommendation interpretation"
        )


        st.write(
            ordering_v2.get(
                "summary",
                ""
            )
        )


        st.caption(
            ordering_v2.get(
                "warning",
                ""
            )
        )


        explanation_disclaimer_v2 = selected_card_v2.get(
            "explanation_disclaimer"
        )


        if explanation_disclaimer_v2:

            st.info(
                explanation_disclaimer_v2
            )


# ============================================================
# GLOBAL REPORT DISCLAIMER
# ============================================================

st.divider()

st.caption(
    report_v2.get(
        "disclaimer",
        ""
    )
)
