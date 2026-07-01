"""Navigation latérale — sidebar Streamlit native."""

from __future__ import annotations

import html
from collections.abc import Callable

import streamlit as st

from src.ui.i18n import get_lang, get_nav_items, t
from src.ui.theme import GREEN, LANG_FLAGS, sidebar_brand_mid, sidebar_divider

_NAV_ROOT = '[data-testid="stSidebar"]'


def _nav_selector(suffix: str) -> str:
    return f"{_NAV_ROOT} {suffix}"


def inject_nav_styles(active_page: str, lang: str) -> None:
    """CSS des boutons de navigation dans la sidebar."""
    nav_keys = [key for key, _, _ in get_nav_items()]
    nav_rules = []
    for key in nav_keys:
        if key == active_page:
            nav_rules.append(f"""
          {_nav_selector(f".st-key-nav_{key} button")},
          {_nav_selector(f'[data-testid="stButton-nav_{key}"] button')} {{
              background: rgba(255,255,255,0.12) !important;
              border: none !important;
              border-radius: 12px !important;
              color: #ffffff !important;
              font-weight: 600 !important;
          }}""")
        else:
            nav_rules.append(f"""
          {_nav_selector(f".st-key-nav_{key} button")},
          {_nav_selector(f'[data-testid="stButton-nav_{key}"] button')} {{
              background: transparent !important;
              border: none !important;
              color: #c8cdd5 !important;
              font-weight: 500 !important;
          }}""")

    lang_fr_active = lang == "fr"
    lang_en_active = lang == "en"

    css = f"""
    <style>
    {_nav_selector('[class*="st-key-nav_"] button')},
    {_nav_selector('[data-testid^="stButton-nav_"] button')} {{
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.6rem 0.85rem !important;
        margin: 0.1rem 0 !important;
        font-size: 0.93rem !important;
        box-shadow: none !important;
        background: transparent !important;
        border: none !important;
        color: #c8cdd5 !important;
    }}
    {_nav_selector('[class*="st-key-nav_"] button:hover')},
    {_nav_selector('[data-testid^="stButton-nav_"] button:hover')} {{
        background: rgba(255,255,255,0.06) !important;
        color: #ffffff !important;
    }}
    {''.join(nav_rules)}
    {_nav_selector(".st-key-lang_fr button")},
    {_nav_selector('[data-testid="stButton-lang_fr"] button')} {{
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        background: {GREEN if lang_fr_active else "rgba(255,255,255,0.04)"} !important;
        border: 1px solid {GREEN if lang_fr_active else "#3a3f4d"} !important;
        color: #fff !important;
        padding: 0.5rem 0.4rem !important;
    }}
    {_nav_selector(".st-key-lang_en button")},
    {_nav_selector('[data-testid="stButton-lang_en"] button')} {{
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        background: {GREEN if lang_en_active else "rgba(255,255,255,0.04)"} !important;
        border: 1px solid {GREEN if lang_en_active else "#3a3f4d"} !important;
        color: #fff !important;
        padding: 0.5rem 0.4rem !important;
    }}
    {_nav_selector(".st-key-new_chat button")},
    {_nav_selector('[data-testid="stButton-new_chat"] button')} {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid #3a3f4d !important;
        color: #e8eaed !important;
        border-radius: 999px !important;
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
        margin: 0.15rem 0 !important;
        box-shadow: none !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_lang_buttons(lang: str) -> None:
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button(
            f"{LANG_FLAGS['fr']}  FR",
            key="lang_fr",
            use_container_width=True,
            type="secondary",
        ):
            if lang != "fr":
                st.session_state.lang = "fr"
                st.rerun()
    with c2:
        if st.button(
            f"{LANG_FLAGS['en']}  EN",
            key="lang_en",
            use_container_width=True,
            type="secondary",
        ):
            if lang != "en":
                st.session_state.lang = "en"
                st.rerun()


def render_nav_panel(
    *,
    active_page: str,
    on_nav: Callable[[str], None],
    on_new_chat: Callable[[], None],
    llm_ready: bool,
    llm_message: str,
) -> None:
    """Contenu de la sidebar."""
    lang = get_lang()
    inject_nav_styles(active_page, lang)

    for key, icon, label in get_nav_items():
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
            type="secondary",
        ):
            on_nav(key)

        if key == "test_civique":
            sidebar_divider()
            sidebar_brand_mid()
            render_lang_buttons(lang)
            sidebar_divider()
            if st.button(
                f"✏️  {t('new_conversation')}",
                key="new_chat",
                use_container_width=True,
                type="secondary",
            ):
                on_new_chat()
            sidebar_divider()

    dot = "🟢" if llm_ready else "🔴"
    st.markdown(
        f'<p class="sidebar-status-line">{dot} {html.escape(llm_message)}</p>',
        unsafe_allow_html=True,
    )
