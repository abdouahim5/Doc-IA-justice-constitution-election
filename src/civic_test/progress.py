"""Suivi de progression — session Streamlit."""

from __future__ import annotations

import streamlit as st

_PROGRESS_KEY = "civic_progress"


def _empty_progress() -> dict:
    return {
        "courses_read": [],
        "quiz_scores": {},
        "exam_attempts": [],
        "wrong_question_ids": [],
        "last_module": None,
    }


def init_progress() -> None:
    if _PROGRESS_KEY not in st.session_state:
        st.session_state[_PROGRESS_KEY] = _empty_progress()


def get_progress() -> dict:
    init_progress()
    return st.session_state[_PROGRESS_KEY]


def mark_course_read(module_id: str) -> None:
    p = get_progress()
    if module_id not in p["courses_read"]:
        p["courses_read"] = [*p["courses_read"], module_id]
    p["last_module"] = module_id


def record_quiz_score(module_id: str, correct: int, total: int) -> None:
    p = get_progress()
    prev = p["quiz_scores"].get(module_id, {})
    best = max(prev.get("correct", 0), correct)
    p["quiz_scores"][module_id] = {"correct": best, "total": total, "last_correct": correct}


def record_answer(question_id: str, correct: bool) -> None:
    p = get_progress()
    if correct:
        wrong = p["wrong_question_ids"]
        if question_id in wrong:
            p["wrong_question_ids"] = [q for q in wrong if q != question_id]
    elif question_id not in p["wrong_question_ids"]:
        p["wrong_question_ids"] = [*p["wrong_question_ids"], question_id]


def record_exam_attempt(correct: int, total: int) -> None:
    p = get_progress()
    attempts = p["exam_attempts"]
    attempts.append({"correct": correct, "total": total})
    p["exam_attempts"] = attempts[-10:]


def reset_progress() -> None:
    st.session_state[_PROGRESS_KEY] = _empty_progress()


def overall_stats(modules_count: int, questions_by_module: dict[str, int]) -> dict:
    p = get_progress()
    courses_done = len(p["courses_read"])
    quiz_done = len(p["quiz_scores"])
    quiz_correct = sum(v.get("last_correct", 0) for v in p["quiz_scores"].values())
    quiz_total = sum(questions_by_module.get(mid, 0) for mid in p["quiz_scores"])
    best_exam = 0
    if p["exam_attempts"]:
        best_exam = max(
            int(100 * a["correct"] / a["total"]) if a["total"] else 0
            for a in p["exam_attempts"]
        )
    course_pct = int(100 * courses_done / modules_count) if modules_count else 0
    quiz_pct = int(100 * quiz_correct / quiz_total) if quiz_total else 0
    return {
        "courses_done": courses_done,
        "courses_total": modules_count,
        "course_pct": course_pct,
        "quiz_done": quiz_done,
        "quiz_correct": quiz_correct,
        "quiz_total": quiz_total,
        "quiz_pct": quiz_pct,
        "exam_attempts": len(p["exam_attempts"]),
        "best_exam_pct": best_exam,
        "to_review": len(p["wrong_question_ids"]),
    }
