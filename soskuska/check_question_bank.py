"""Native authoring workflow check; uses only a disposable database."""
import tempfile
import traceback
from pathlib import Path

import customtkinter as ctk
from app import Dashboard
from storage import Store

ctk.set_appearance_mode("dark")
temp = tempfile.TemporaryDirectory()
path = Path(temp.name) / "questions.sqlite3"
app = Dashboard(path)
errors = []
subject = app.store.create_subject("Mathematics – skúška")
other = app.store.create_subject("Русский язык")
other_question = app.store.create_question(other, "Other subject?", ["A", "B", "C", "D"], 0)
app.store.add_session(60, subject, "Mathematics – skúška")
page = app.question_bank


def guarded(callback):
    def run():
        try:
            callback()
        except Exception as exc:
            errors.append(str(exc))
            traceback.print_exc()
            app.destroy()
    return run


def later(callback):
    app.after(250, guarded(callback))


def start():
    app.geometry("1024x700")
    app.open_question_bank(subject)
    page.add_topic_button.invoke()
    page.topic_entry.insert(0, "Derivatives")
    page.save_topic_button.invoke()
    topic = app.store.topics(subject)[0]["id"]
    page.topic_filter.set("Topic: Derivatives")
    page.filter_changed()
    page.edit_topic_button.invoke()
    page.topic_entry.delete(0, "end")
    page.topic_entry.insert(0, "Calculus")
    page.save_topic_button.invoke()
    assert app.store.topic(topic)["name"] == "Calculus"
    page.add_topic_button.invoke()
    page.topic_entry.insert(0, "calculus")
    page.save_topic_button.invoke()
    assert page.topic_error.cget("text")
    assert len(app.store.topics(subject)) == 1
    page.add_question_button.invoke()
    page.save_question_button.invoke()
    assert page.question_error.cget("text")
    assert not app.store.questions(subject)
    page.prompt_entry.insert("1.0", "Derivative of x²?")
    for entry, answer in zip(page.option_entries, ["x", "2x", "x²", "2"]):
        entry.insert(0, answer)
    page.correct.set("B")
    page.difficulty.set("Hard")
    page.question_topic.set("Topic: Calculus")
    page.explanation_entry.insert("1.0", "Use the power rule.")
    later(check_editor)


def check_editor():
    assert page.question_form.winfo_ismapped()
    assert page.save_question_button.winfo_width() >= 100
    canvas = app.scroll._parent_canvas
    canvas.yview_moveto(1)
    assert canvas.yview()[0] > 0
    page.save_question_button.invoke()
    question = app.store.questions(subject)[0]
    assert question["correct_option"] == 1
    assert question["explanation"] == "Use the power rule."
    page.show_question_form(question["id"])
    page.prompt_entry.delete("1.0", "end")
    page.prompt_entry.insert("1.0", "Find derivative of x²")
    page.save_question_button.invoke()
    assert app.store.questions(subject)[0]["id"] == question["id"]
    page.difficulty_filter.set("Easy")
    page.filter_changed()
    assert "0 of 1 questions" in page.count_label.cget("text")
    page.difficulty_filter.set("Hard")
    page.query.set("DERIVATIVE")
    page.filter_changed()
    assert "1 of 1 questions" in page.count_label.cget("text")
    page.query.set("no match")
    assert "0 of 1 questions" in page.count_label.cget("text")
    page.query.set("")
    page.delete_topic_button.invoke()
    assert "kept without a topic" in page.delete_text.cget("text")
    page.delete_button.invoke()
    assert app.store.question(question["id"])["topic_id"] is None
    page.ask_delete("question", question["id"])
    page.cancel_delete()
    assert app.store.question(question["id"])
    page.ask_delete("question", question["id"])
    page.delete_button.invoke()
    assert app.store.question(question["id"]) is None
    app.open_question_bank(other)
    assert "1 of 1 questions" in page.count_label.cget("text")
    app.open_question_bank(subject)
    assert "0 of 0 questions" in page.count_label.cget("text")
    topic = app.store.create_topic(subject, "Delete with subject")
    app.store.create_question(subject, "Remove me?", ["a", "b", "c", "d"], 0, topic_id=topic)
    app.refresh_data()
    app.navigate("My Subjects")
    app.subject_page.ask_delete(subject)
    later(check_subject_delete)


def check_subject_delete():
    assert app.subject_page.delete_panel.winfo_ismapped()
    assert "1 topics and 1 questions" in app.subject_page.delete_label.cget("text")
    app.subject_page.delete_button.invoke()
    assert app.store.subject(subject) is None
    assert not app.store.questions(subject) and not app.store.topics(subject)
    assert app.store.question(other_question)
    assert app.store.seconds() == 60
    app.close()


def timeout():
    errors.append("Question bank UI check timed out")
    app.destroy()


def callback_error(kind, value, tb):
    errors.append(str(value))
    traceback.print_exception(kind, value, tb)
    app.destroy()


app.report_callback_exception = callback_error
app.after(900, guarded(start))
app.after(12000, timeout)
try:
    app.mainloop()
finally:
    app.store.close()
if not errors:
    reopened = Store(path)
    try:
        assert reopened.question(other_question)
        assert reopened.seconds() == 60
    finally:
        reopened.close()
    print("PASS: topic/question CRUD, validation, filters, compact editor scrolling, subject isolation, deletion and reopen", flush=True)
temp.cleanup()
raise SystemExit(1 if errors else 0)
