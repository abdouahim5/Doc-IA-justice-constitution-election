"""Styles et composants visuels Streamlit (theme SenStat-like)."""

import html

import streamlit as st

# Couleurs
NAVY = "#0B1F3A"
GREEN = "#00A651"
CORAL = "#FF5A5F"
CORAL_DARK = "#E84E53"
SIDEBAR_BG = "#12141C"
PAGE_BG = "#F4F6F9"
CARD_WHITE = "#FFFFFF"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}
.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stMainBlockContainer"] .block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 100% !important;
    width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}}
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stAppViewContainer"] {{
    width: 100% !important;
    max-width: 100% !important;
}}
[data-testid="stAppViewContainer"] {{
    background-color: {PAGE_BG};
}}
section[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG} !important;
    border-right: 1px solid #1e2230;
}}
section[data-testid="stSidebar"] > div {{
    background-color: {SIDEBAR_BG} !important;
}}
section[data-testid="stSidebar"] * {{
    color: #e8eaed !important;
}}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {{
    color: #ffffff !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.7;
}}
section[data-testid="stSidebar"] .sidebar-status-line {{
    font-size: 0.72rem !important;
    opacity: 0.45 !important;
    margin-top: 0.25rem !important;
    color: #c8cdd5 !important;
}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button,
section[data-testid="stSidebar"] [data-testid^="stButton-nav_"] button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #c8cdd5 !important;
}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button p,
section[data-testid="stSidebar"] [data-testid^="stButton-nav_"] button p,
section[data-testid="stSidebar"] [class*="st-key-nav_"] button span,
section[data-testid="stSidebar"] [data-testid^="stButton-nav_"] button span {{
    color: inherit !important;
}}
.nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    margin: 4px 0;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 500;
    color: #c8cdd5;
    cursor: default;
}}
.nav-item.active {{
    background: rgba(255,255,255,0.12);
    color: #ffffff;
    font-weight: 600;
}}
.hero-card {{
    background: linear-gradient(135deg, {NAVY} 0%, #132d52 55%, #0d2240 100%);
    border-radius: 20px;
    padding: 2.75rem 3rem;
    margin-bottom: 0.85rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(11,31,58,0.25);
    width: 100%;
    box-sizing: border-box;
}}
.hero-card .hero-badge,
.hero-card .hero-title,
.hero-card .hero-text {{
    position: relative;
    z-index: 2;
}}
.hero-card::after {{
    content: '';
    position: absolute;
    right: -40px;
    top: -40px;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}}
.hero-card::before {{
    content: '';
    position: absolute;
    right: 60px;
    bottom: -60px;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: rgba(0,166,81,0.08);
}}
.hero-badge {{
    color: {GREEN} !important;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}}
.hero-title {{
    color: #ffffff !important;
    font-size: clamp(1.65rem, 3vw, 2.35rem);
    font-weight: 800;
    line-height: 1.22;
    margin: 0 0 1rem 0;
    max-width: none;
}}
.hero-text {{
    color: rgba(255,255,255,0.92) !important;
    font-size: 1.02rem;
    line-height: 1.65;
    max-width: 52rem;
    margin: 0;
}}
.st-key-home_page .st-key-home_btn_chat button,
.st-key-home_page [data-testid="stButton-home_btn_chat"] button {{
    background: linear-gradient(135deg, {CORAL} 0%, {CORAL_DARK} 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.9rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: 0 6px 20px rgba(255, 90, 95, 0.35) !important;
    min-height: 3.25rem !important;
}}
.st-key-home_page .st-key-home_btn_chat button:hover,
.st-key-home_page [data-testid="stButton-home_btn_chat"] button:hover {{
    background: linear-gradient(135deg, #ff7075 0%, {CORAL} 100%) !important;
    box-shadow: 0 8px 24px rgba(255, 90, 95, 0.45) !important;
}}
.st-key-home_page .st-key-home_btn_themes button,
.st-key-home_page [data-testid="stButton-home_btn_themes"] button {{
    background: #ffffff !important;
    color: #1f2937 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
    padding: 0.9rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    min-height: 3.25rem !important;
}}
.st-key-home_page .st-key-home_btn_themes button:hover,
.st-key-home_page [data-testid="stButton-home_btn_themes"] button:hover {{
    background: #f9fafb !important;
    border-color: #d1d5db !important;
}}
.st-key-home_page .home-cta-row {{
    margin-bottom: 0.25rem;
}}
.st-key-home_page .section-title {{
    margin-top: 2rem;
}}
.main .hero-card .hero-title {{
    color: #ffffff !important;
}}
.main .hero-card .hero-text {{
    color: rgba(255,255,255,0.92) !important;
}}
.main .hero-card .hero-badge {{
    color: {GREEN} !important;
}}
.stat-card {{
    background: {CARD_WHITE};
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e8ecf1;
    height: 100%;
}}
.stat-label {{
    color: {GREEN};
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}}
.stat-value {{
    color: #111827;
    font-size: 1.75rem;
    font-weight: 800;
    line-height: 1.1;
}}
.section-title {{
    color: #6b7280;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.8rem 0 1rem 0;
}}
.theme-card {{
    background: white;
    border: 1px solid #e5e9ef;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
    transition: box-shadow 0.2s;
}}
.theme-card:hover {{
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}}
.theme-card h4 {{
    margin: 0 0 0.4rem 0;
    color: #111827;
    font-size: 1rem;
}}
.theme-card p {{
    margin: 0;
    color: #6b7280;
    font-size: 0.88rem;
}}
.explore-theme-wrap {{
    margin-bottom: 1.25rem;
}}
.explore-theme-card {{
    background: #fff;
    border: 1px solid #e8ecf1;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    min-height: 220px;
    display: flex;
    flex-direction: column;
}}
.explore-theme-accent {{
    height: 5px;
    width: 100%;
}}
.explore-theme-body {{
    padding: 1.35rem 1.25rem 1rem 1.25rem;
    text-align: center;
    flex: 1;
}}
.explore-theme-icon {{
    font-size: 2.2rem;
    line-height: 1;
    margin-bottom: 0.65rem;
}}
.explore-theme-name {{
    color: #111827 !important;
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
}}
.explore-theme-desc {{
    color: #6b7280 !important;
    font-size: 0.82rem;
    line-height: 1.45;
    margin: 0 0 0.75rem 0;
}}
.explore-theme-source {{
    color: {GREEN} !important;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 0;
}}
.explore-theme-wrap [data-testid="stButton"] button,
.explore-theme-card + div [data-testid="stButton"] button {{
    background: #ecfdf3 !important;
    border: none !important;
    border-top: 1px solid #d1fae5 !important;
    border-radius: 0 0 14px 14px !important;
    color: {GREEN} !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.7rem 1rem !important;
    margin-top: -0.35rem !important;
    box-shadow: none !important;
}}
.explore-theme-card + div [data-testid="stButton"] button:hover,
.explore-theme-wrap [data-testid="stButton"] button:hover {{
    background: #d1fae5 !important;
    color: #047857 !important;
}}
.brand-box {{
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #2a2f3d;
}}
.brand-name {{
    font-size: 1.15rem;
    font-weight: 800;
    color: #fff !important;
    margin: 0.5rem 0 0 0;
}}
.sidebar-status {{
    font-size: 0.78rem;
    opacity: 0.65;
    margin-top: 0.25rem;
}}
.sidebar-divider {{
    border-top: 1px solid #2a2f3d;
    margin: 1.1rem 0;
}}
.sidebar-brand-mid {{
    padding: 0.15rem 0 0.85rem 0;
}}
.sidebar-brand-mid .brand-title {{
    font-size: 1.2rem;
    font-weight: 800;
    color: #fff !important;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}}
[data-testid="stSidebar"] .sidebar-status-line {{
    font-size: 0.72rem !important;
    opacity: 0.45 !important;
    margin-top: 0.25rem !important;
    color: #c8cdd5 !important;
}}
div[data-testid="stChatMessage"] {{
    background: white;
    border-radius: 12px;
    border: 1px solid #e8ecf1;
}}
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,166,81,0.12);
    border: 1px solid rgba(0,166,81,0.35);
    color: #065f36;
    padding: 0.45rem 0.9rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 1rem;
}}
.status-pill.warn {{
    background: rgba(245,158,11,0.12);
    border-color: rgba(245,158,11,0.35);
    color: #92400e;
}}
.info-card {{
    background: white;
    border: 1px solid #e5e9ef;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}}
.info-card code {{
    background: #f3f4f6;
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
    font-size: 0.85rem;
}}
#MainMenu, footer {{
    visibility: hidden;
    height: 0;
}}
/* Masquer uniquement le bouton Deploy */
[data-testid="stToolbar"] [data-testid="stBaseButton-header"] {{
    display: none !important;
}}
</style>
"""


def inject_styles() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


CIVIC_CSS = """
<style>
.civic-stat {
    background: white;
    border: 1px solid #e5e9ef;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    text-align: center;
    margin-bottom: 0.5rem;
}
.civic-stat-label {
    color: #6b7280;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.civic-stat-value {
    color: #111827;
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0.25rem 0;
}
.civic-stat-sub {
    color: #00A651;
    font-size: 0.85rem;
    font-weight: 600;
}
.civic-module-card {
    background: white;
    border: 1px solid #e8ecf1;
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.civic-module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.35rem;
}
.civic-module-icon { font-size: 1.75rem; }
.civic-module-badge { font-size: 1rem; opacity: 0.7; }
.civic-module-card h4 {
    margin: 0 0 0.35rem 0;
    color: #111827;
    font-size: 1rem;
}
.civic-module-card p {
    margin: 0;
    color: #6b7280;
    font-size: 0.85rem;
}
.civic-course-hero {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.civic-course-hero h3 { margin: 0 0 0.35rem 0; color: #111827; }
.civic-course-hero p { margin: 0; color: #6b7280; }
.civic-progress-wrap {
    background: #e5e7eb;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    margin: 0.35rem 0 0.15rem 0;
}
.civic-progress-bar {
    height: 100%;
    border-radius: 999px;
    transition: width 0.3s;
}
.civic-progress-label {
    font-size: 0.82rem;
    color: #6b7280;
    font-weight: 600;
}
.civic-nav-spacer { margin-bottom: 0.5rem; }
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0.35rem;
    flex-wrap: wrap;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: white !important;
    border: 1px solid #e5e9ef !important;
    border-radius: 999px !important;
    padding: 0.35rem 0.9rem !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: #ecfdf3 !important;
    border-color: #00A651 !important;
    color: #047857 !important;
}
</style>
"""


def inject_civic_styles() -> None:
    st.markdown(CIVIC_CSS, unsafe_allow_html=True)


def render_home_actions(chat_label: str, themes_label: str, on_chat, on_themes) -> None:
    """Boutons d'action page d'accueil — style maquette SenStat."""
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        if st.button(chat_label, key="home_btn_chat", use_container_width=True, type="primary"):
            on_chat()
    with c2:
        if st.button(themes_label, key="home_btn_themes", use_container_width=True, type="secondary"):
            on_themes()


def hero_section(badge: str, title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-badge">{html.escape(badge)}</div>
            <div class="hero-title">{html.escape(title)}</div>
            <p class="hero-text">{html.escape(text)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_cards(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-label">{html.escape(label)}</div>
                    <div class="stat-value">{html.escape(value)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def section_title(text: str) -> None:
    st.markdown(f'<p class="section-title">{html.escape(text)}</p>', unsafe_allow_html=True)


def render_theme_card(card: dict) -> None:
    """Carte thème style SenStat (corps HTML)."""
    st.markdown(
        f"""
        <div class="explore-theme-card">
            <div class="explore-theme-accent" style="background:{html.escape(card['color'])};"></div>
            <div class="explore-theme-body">
                <div class="explore-theme-icon">{card['icon']}</div>
                <p class="explore-theme-name">{html.escape(card['title'])}</p>
                <p class="explore-theme-desc">{html.escape(card['desc'])}</p>
                <p class="explore-theme-source">📄 {html.escape(card['source'])}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_theme_grid(cards: list[dict], explore_label: str, on_explore: callable) -> None:
    """Grille 3 colonnes de cartes thèmes + bouton Explorer."""
    for row_start in range(0, len(cards), 3):
        row = cards[row_start : row_start + 3]
        cols = st.columns(3)
        for col, card in zip(cols, row):
            with col:
                render_theme_card(card)
                if st.button(explore_label, key=f"theme_card_{card['id']}", use_container_width=True):
                    on_explore(card["question"], card["id"], card["title"])


def status_pill(text: str, ok: bool = True) -> None:
    cls = "status-pill" if ok else "status-pill warn"
    st.markdown(f'<div class="{cls}">{html.escape(text)}</div>', unsafe_allow_html=True)


LANG_FLAGS = {"fr": "🇫🇷", "en": "🇬🇧"}


def sidebar_divider() -> None:
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)


def sidebar_brand_mid() -> None:
    """Marque au centre de la sidebar (style SenStat)."""
    from src.ui.i18n import t

    st.markdown(
        f"""
        <div class="sidebar-brand-mid">
            <p class="brand-title"><span>🇫🇷</span> {html.escape(t("app_name"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_item(icon: str, label: str, active: bool) -> str:
    cls = "nav-item active" if active else "nav-item"
    return f'<div class="{cls}">{icon} {html.escape(label)}</div>'


NAV_ITEMS = [
    ("accueil", "🏠", "Accueil"),
    ("chat", "💬", "Poser une question"),
    ("france", "🇫🇷", "France Civique"),
    ("themes", "📋", "Thèmes"),
    ("faq", "❓", "FAQ"),
    ("admin", "⚙️", "Configuration"),
]

# Legacy — préférer src.ui.i18n.get_france_suggestions()
FRANCE_SUGGESTIONS = [
    ("Calendrier", "Quelles sont les dates des derniers scrutins en France ?", "Présidentielle, législatives, européennes"),
    ("Constitution", "Que dit l'article 2 de la Constitution ?", "Symboles de la République"),
    ("Élections", "Comment se déroule une élection présidentielle ?", "Scrutin et tours de vote"),
    ("Chiffres", "Quel est le taux de participation aux élections ?", "Données chiffrées indexées"),
]

THEME_SUGGESTIONS = [
    ("Constitution", "article 2", "Langue, drapeau, hymne et devise de la République"),
    ("Institutions", "Quels sont les droits du president", "Pouvoirs du Président de la République"),
    ("Recherche", "Marseillaise", "Trouver le mot dans tous les documents"),
    ("Technique", "Qu'est-ce que le RAG ?", "Comprendre le fonctionnement de l'agent"),
]
