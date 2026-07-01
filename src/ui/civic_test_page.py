"""Page Streamlit — Préparation au Test Civique."""

from __future__ import annotations

import random

import streamlit as st

from src.civic_test.content import (
    get_exam_questions,
    get_module,
    get_modules,
    get_question,
    get_questions_for_module,
    localized,
    questions_count_by_module,
)
from src.civic_test.progress import (
    get_progress,
    mark_course_read,
    overall_stats,
    record_answer,
    record_exam_attempt,
    record_quiz_score,
    reset_progress,
)
from src.ui.i18n import t
from src.ui.theme import hero_section, inject_civic_styles, section_title


def _lang() -> str:
    return st.session_state.get("lang", "fr")


def _L(obj: dict, key: str) -> str:
    return localized(obj, key, _lang())


def _init_civic_state() -> None:
    if "civic_tab_radio" not in st.session_state:
        st.session_state.civic_tab_radio = "overview"
    if "civic_quiz_module" not in st.session_state:
        st.session_state.civic_quiz_module = None
    if "civic_exam_active" not in st.session_state:
        st.session_state.civic_exam_active = False
    if "civic_exam_questions" not in st.session_state:
        st.session_state.civic_exam_questions = []
    if "civic_exam_answers" not in st.session_state:
        st.session_state.civic_exam_answers = {}


def _request_civic_tab(tab: str) -> None:
    """Navigation programmatique (boutons) — compatible avec le widget radio."""
    st.session_state.civic_nav_request = tab
    st.rerun()


def _progress_bar_html(pct: int, color: str = "#2563eb") -> str:
    pct = max(0, min(100, pct))
    return f"""
<div class="civic-progress-wrap">
  <div class="civic-progress-bar" style="width:{pct}%;background:{color};"></div>
</div>
<span class="civic-progress-label">{pct}%</span>
"""


def _module_card(module: dict, progress: dict) -> None:
    mid = module["id"]
    read = mid in progress["courses_read"]
    quiz = progress["quiz_scores"].get(mid)
    badge = "✅" if read and quiz else ("📖" if read else "○")
    st.markdown(
        f"""
<div class="civic-module-card" style="border-top:4px solid {module['color']};">
  <div class="civic-module-header">
    <span class="civic-module-icon">{module['icon']}</span>
    <span class="civic-module-badge">{badge}</span>
  </div>
  <h4>{_L(module, 'title')}</h4>
  <p>{_L(module, 'summary')}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_question(
    q: dict,
    key_prefix: str,
    show_result: bool = False,
    disabled: bool = False,
) -> int | None:
    """Affiche une question ; retourne l'index choisi si soumis."""
    lang = _lang()
    choices = q["choices"][lang] if isinstance(q["choices"], dict) else q["choices"]
    st.markdown(f"**{_L(q, 'question')}**")
    selected = st.radio(
        t("civic_choose"),
        options=range(len(choices)),
        format_func=lambda i: choices[i],
        key=f"{key_prefix}_{q['id']}",
        disabled=disabled and show_result,
        label_visibility="collapsed",
    )
    if show_result:
        correct = q["correct"]
        if selected == correct:
            st.success(f"✓ {t('civic_correct')}")
        else:
            st.error(f"✗ {t('civic_wrong')} — {choices[correct]}")
        st.caption(f"💡 {_L(q, 'explanation')}")
    return selected


def _tab_overview() -> None:
    modules = get_modules()
    counts = questions_count_by_module()
    stats = overall_stats(len(modules), counts)
    progress = get_progress()

    cols = st.columns(4)
    metrics = [
        (t("civic_stat_courses"), f"{stats['courses_done']}/{stats['courses_total']}", f"{stats['course_pct']}%"),
        (t("civic_stat_quiz"), f"{stats['quiz_correct']}/{stats['quiz_total']}", f"{stats['quiz_pct']}%"),
        (t("civic_stat_exam"), str(stats["exam_attempts"]), f"{stats['best_exam_pct']}%"),
        (t("civic_stat_review"), str(stats["to_review"]), "📝"),
    ]
    for col, (label, value, sub) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="civic-stat"><div class="civic-stat-label">{label}</div>'
                f'<div class="civic-stat-value">{value}</div>'
                f'<div class="civic-stat-sub">{sub}</div></div>',
                unsafe_allow_html=True,
            )

    section_title(t("civic_modules_title"))
    mod_cols = st.columns(2)
    for i, mod in enumerate(modules):
        with mod_cols[i % 2]:
            _module_card(mod, progress)
            if st.button(t("civic_open_course"), key=f"goto_course_{mod['id']}", use_container_width=True):
                st.session_state.civic_selected_module = mod["id"]
                _request_civic_tab("courses")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(t("civic_btn_quiz"), type="primary", use_container_width=True):
            _request_civic_tab("quiz")
    with c2:
        if st.button(t("civic_btn_exam"), use_container_width=True):
            _request_civic_tab("exam")
    with c3:
        if st.button(t("civic_btn_review"), use_container_width=True):
            _request_civic_tab("review")


def _tab_courses() -> None:
    modules = get_modules()
    progress = get_progress()
    selected = st.session_state.get("civic_selected_module") or modules[0]["id"]

    labels = {m["id"]: f"{m['icon']} {_L(m, 'title')}" for m in modules}
    picked = st.selectbox(
        t("civic_select_module"),
        options=[m["id"] for m in modules],
        format_func=lambda x: labels[x],
        index=[m["id"] for m in modules].index(selected),
        key="civic_course_select",
    )
    st.session_state.civic_selected_module = picked
    mod = get_module(picked)
    if not mod:
        return

    st.markdown(
        f'<div class="civic-course-hero" style="border-left:5px solid {mod["color"]};">'
        f'<h3>{mod["icon"]} {_L(mod, "title")}</h3>'
        f'<p>{_L(mod, "summary")}</p></div>',
        unsafe_allow_html=True,
    )

    for i, lesson in enumerate(mod["lessons"]):
        with st.expander(_L(lesson, "title"), expanded=i == 0):
            st.markdown(_L(lesson, "body"))

    if st.button(t("civic_mark_read"), type="primary", key=f"read_{picked}"):
        mark_course_read(picked)
        st.toast(t("civic_course_done"))
        st.rerun()

    if picked in progress["courses_read"]:
        st.success(t("civic_already_read"))

    st.markdown("---")
    if st.button(t("civic_quiz_this_module"), key=f"quiz_from_{picked}"):
        st.session_state.civic_quiz_module = picked
        _request_civic_tab("quiz")


def _tab_quiz() -> None:
    modules = get_modules()
    default_mod = st.session_state.civic_quiz_module or modules[0]["id"]
    mod_id = st.selectbox(
        t("civic_quiz_module"),
        [m["id"] for m in modules],
        format_func=lambda x: _L(get_module(x) or {}, "title"),
        index=[m["id"] for m in modules].index(default_mod),
        key="civic_quiz_select",
    )
    questions = get_questions_for_module(mod_id)
    if not questions:
        st.info(t("civic_no_questions"))
        return

    nonce = st.session_state.get("civic_quiz_nonce", 0)
    st.caption(t("civic_quiz_hint").format(n=len(questions)))

    if st.button(t("civic_submit_quiz"), type="primary", key="submit_quiz"):
        st.session_state.civic_quiz_submitted = mod_id
        st.rerun()

    submitted = st.session_state.get("civic_quiz_submitted") == mod_id
    correct_count = 0
    for q in questions:
        with st.container():
            sel = _render_question(q, f"quiz_{nonce}", show_result=submitted, disabled=submitted)
            if submitted and sel is not None:
                ok = sel == q["correct"]
                record_answer(q["id"], ok)
                if ok:
                    correct_count += 1
            st.markdown("")

    if submitted:
        record_quiz_score(mod_id, correct_count, len(questions))
        pct = int(100 * correct_count / len(questions))
        st.balloons() if pct >= 80 else None
        st.markdown(
            f"### {t('civic_score')}: **{correct_count}/{len(questions)}** ({pct}%)"
        )
        if st.button(t("civic_retry_quiz"), key="retry_quiz"):
            st.session_state.civic_quiz_submitted = None
            st.session_state.civic_quiz_nonce = nonce + 1
            st.rerun()


def _tab_exam() -> None:
    if not st.session_state.civic_exam_active:
        st.markdown(f"### {t('civic_exam_intro_title')}")
        st.markdown(t("civic_exam_intro"))
        n = len(get_exam_questions())
        st.info(t("civic_exam_format").format(n=n, pass_pct=80))
        if st.button(t("civic_start_exam"), type="primary"):
            qs = get_exam_questions()
            random.shuffle(qs)
            st.session_state.civic_exam_questions = qs
            st.session_state.civic_exam_answers = {}
            st.session_state.civic_exam_active = True
            st.session_state.civic_exam_submitted = False
            st.rerun()
        return

    questions: list = st.session_state.civic_exam_questions
    submitted = st.session_state.get("civic_exam_submitted", False)

    if not submitted:
        st.progress(0, text=t("civic_exam_progress").format(cur=0, total=len(questions)))

    correct_count = 0
    for idx, q in enumerate(questions):
        st.markdown(f"**{t('civic_question_n').format(n=idx + 1)}**")
        sel = _render_question(q, "exam", show_result=submitted, disabled=submitted)
        if submitted and sel is not None:
            ok = sel == q["correct"]
            record_answer(q["id"], ok)
            if ok:
                correct_count += 1

    if not submitted:
        if st.button(t("civic_finish_exam"), type="primary"):
            st.session_state.civic_exam_submitted = True
            st.rerun()
    else:
        total = len(questions)
        record_exam_attempt(correct_count, total)
        pct = int(100 * correct_count / total) if total else 0
        passed = pct >= 80
        if passed:
            st.success(t("civic_exam_pass").format(score=correct_count, total=total, pct=pct))
            st.balloons()
        else:
            st.warning(t("civic_exam_fail").format(score=correct_count, total=total, pct=pct))
        if st.button(t("civic_new_exam")):
            st.session_state.civic_exam_active = False
            st.session_state.civic_exam_submitted = False
            st.session_state.civic_exam_questions = []
            st.rerun()
        if st.button(t("civic_go_review")):
            _request_civic_tab("review")


def _tab_review() -> None:
    progress = get_progress()
    wrong_ids = progress["wrong_question_ids"]
    if not wrong_ids:
        st.success(t("civic_no_review"))
        return

    st.markdown(t("civic_review_intro").format(n=len(wrong_ids)))
    if st.button(t("civic_clear_review")):
        for qid in wrong_ids:
            record_answer(qid, True)
        st.rerun()

    for qid in wrong_ids:
        q = get_question(qid)
        if not q:
            continue
        mod = get_module(q["module_id"])
        mod_title = _L(mod, "title") if mod else ""
        st.markdown(f"*{mod_title}*")
        _render_question(q, "review", show_result=True, disabled=True)
        st.markdown("---")


def _tab_progress() -> None:
    modules = get_modules()
    counts = questions_count_by_module()
    stats = overall_stats(len(modules), counts)
    progress = get_progress()

    section_title(t("civic_progress_detail"))
    rows = [
        (t("civic_prog_courses"), stats["course_pct"], "#2563eb"),
        (t("civic_prog_quiz"), stats["quiz_pct"], "#00A651"),
        (t("civic_prog_exam"), stats["best_exam_pct"], "#ea580c"),
    ]
    for label, pct, color in rows:
        st.markdown(f"**{label}**")
        st.markdown(_progress_bar_html(pct, color), unsafe_allow_html=True)

    section_title(t("civic_by_module"))
    for mod in modules:
        mid = mod["id"]
        read = "✅" if mid in progress["courses_read"] else "—"
        qs = progress["quiz_scores"].get(mid)
        quiz_str = f"{qs['last_correct']}/{qs['total']}" if qs else "—"
        st.markdown(
            f"- **{mod['icon']} {_L(mod, 'title')}** — "
            f"{t('civic_col_course')}: {read} · {t('civic_col_quiz')}: {quiz_str}"
        )

    if progress["exam_attempts"]:
        section_title(t("civic_exam_history"))
        for i, att in enumerate(reversed(progress["exam_attempts"][-5:]), 1):
            pct = int(100 * att["correct"] / att["total"]) if att["total"] else 0
            st.markdown(f"- {t('civic_attempt_n').format(n=i)}: **{att['correct']}/{att['total']}** ({pct}%)")

    st.markdown("---")
    if st.button(t("civic_reset"), type="secondary"):
        reset_progress()
        st.session_state.civic_quiz_submitted = None
        st.session_state.civic_exam_active = False
        st.toast(t("civic_reset_done"))
        st.rerun()


_TAB_OPTIONS = [
    ("overview", "civic_tab_overview"),
    ("courses", "civic_tab_courses"),
    ("quiz", "civic_tab_quiz"),
    ("exam", "civic_tab_exam"),
    ("review", "civic_tab_review"),
    ("progress", "civic_tab_progress"),
]
_TAB_LABELS = dict(_TAB_OPTIONS)

_TAB_RENDERERS = {
    "overview": _tab_overview,
    "courses": _tab_courses,
    "quiz": _tab_quiz,
    "exam": _tab_exam,
    "review": _tab_review,
    "progress": _tab_progress,
}


def render_civic_test_page() -> None:
    inject_civic_styles()
    _init_civic_state()

    hero_section(
        t("civic_badge"),
        t("civic_title"),
        t("civic_text"),
    )

    tab_keys = list(_TAB_LABELS.keys())
    nav_request = st.session_state.pop("civic_nav_request", None)
    if nav_request in tab_keys:
        st.session_state.civic_tab_radio = nav_request
    elif st.session_state.get("civic_tab_radio") not in tab_keys:
        st.session_state.civic_tab_radio = "overview"

    st.radio(
        "civic_nav",
        options=tab_keys,
        format_func=lambda k: t(_TAB_LABELS[k]),
        horizontal=True,
        key="civic_tab_radio",
        label_visibility="collapsed",
    )
    selected = st.session_state.civic_tab_radio
    st.markdown('<div class="civic-nav-spacer"></div>', unsafe_allow_html=True)

    _TAB_RENDERERS[selected]()
