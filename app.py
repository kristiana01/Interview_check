"""Interview Check - a small web app for recording and analysing interviews
about manual software testing practices.

Author: Kristiana Baranovska (Turiba University qualification paper).
"""
import csv
import io
import os
from datetime import date

from flask import (Flask, Response, abort, flash, g, redirect, render_template,
                   request, url_for)

import db
from questions import PROBLEM_TAGS, QUESTIONS, ROLES, TAG_LABELS


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["DB_PATH"] = db_path or os.environ.get(
        "INTERVIEW_DB", os.path.join(app.root_path, "interviews.db"))
    db.init(app.config["DB_PATH"])

    def get_db():
        if "db" not in g:
            g.db = db.connect(app.config["DB_PATH"])
        return g.db

    @app.teardown_appcontext
    def close_db(_):
        con = g.pop("db", None)
        if con is not None:
            con.close()

    app.jinja_env.globals.update(TAG_LABELS=TAG_LABELS, ROLES=ROLES,
                                 PROBLEM_TAGS=PROBLEM_TAGS)

    # ---------- helpers ----------
    def load(interview_id):
        con = get_db()
        row = con.execute("SELECT * FROM interviews WHERE id=?", (interview_id,)).fetchone()
        if row is None:
            abort(404)
        answers = con.execute(
            "SELECT * FROM answers WHERE interview_id=? ORDER BY position", (interview_id,)).fetchall()
        tags = [r["tag"] for r in con.execute(
            "SELECT tag FROM tags WHERE interview_id=?", (interview_id,))]
        return row, answers, tags

    def read_form(role):
        """Validate the form; return (data, errors)."""
        f = request.form
        data = {
            "respondent": f.get("respondent", "").strip(),
            "company": f.get("company", "").strip(),
            "held_on": f.get("held_on", "").strip(),
            "notes": f.get("notes", "").strip(),
            "tags": [t for t in f.getlist("tags") if t in TAG_LABELS],
            "answers": [f.get("answer_%d" % i, "").strip()
                        for i in range(len(QUESTIONS[role]))],
        }
        errors = []
        if not data["respondent"]:
            errors.append("Respondent name or code is required.")
        try:
            date.fromisoformat(data["held_on"])
        except ValueError:
            errors.append("Date must be in the format YYYY-MM-DD.")
        return data, errors

    def save_children(con, interview_id, role, data, questions=None):
        con.execute("DELETE FROM answers WHERE interview_id=?", (interview_id,))
        con.execute("DELETE FROM tags WHERE interview_id=?", (interview_id,))
        qs = questions or QUESTIONS[role]
        for pos, (q, a) in enumerate(zip(qs, data["answers"]), 1):
            con.execute("INSERT INTO answers(interview_id, position, question, answer) VALUES (?,?,?,?)",
                        (interview_id, pos, q, a))
        for t in data["tags"]:
            con.execute("INSERT INTO tags(interview_id, tag) VALUES (?,?)", (interview_id, t))

    # ---------- pages ----------
    @app.route("/")
    def index():
        rows = get_db().execute(
            "SELECT * FROM interviews ORDER BY held_on DESC, id DESC").fetchall()
        counts = {r["interview_id"]: r["n"] for r in get_db().execute(
            "SELECT interview_id, COUNT(*) n FROM tags GROUP BY interview_id")}
        return render_template("index.html", rows=rows, counts=counts)

    @app.route("/new", methods=["GET", "POST"])
    def new():
        role = request.values.get("role", "CEO")
        if role not in ROLES:
            role = "CEO"
        if request.method == "POST":
            data, errors = read_form(role)
            if not errors:
                con = get_db()
                cur = con.execute(
                    "INSERT INTO interviews(respondent, role, company, held_on, notes) VALUES (?,?,?,?,?)",
                    (data["respondent"], role, data["company"], data["held_on"], data["notes"]))
                save_children(con, cur.lastrowid, role, data)
                con.commit()
                flash("Interview saved.")
                return redirect(url_for("view", interview_id=cur.lastrowid))
            for e in errors:
                flash(e, "error")
            return render_template("form.html", mode="new", role=role, questions=QUESTIONS[role],
                                   data=data, today=date.today().isoformat()), 400
        data = {"respondent": "", "company": "", "held_on": date.today().isoformat(),
                "notes": "", "tags": [], "answers": [""] * len(QUESTIONS[role])}
        return render_template("form.html", mode="new", role=role, questions=QUESTIONS[role], data=data)

    @app.route("/interview/<int:interview_id>")
    def view(interview_id):
        row, answers, tags = load(interview_id)
        return render_template("view.html", i=row, answers=answers, tags=tags)

    @app.route("/interview/<int:interview_id>/edit", methods=["GET", "POST"])
    def edit(interview_id):
        row, answers, tags = load(interview_id)
        role = row["role"]
        questions = [a["question"] for a in answers]
        if request.method == "POST":
            data, errors = read_form(role)
            data["answers"] = [request.form.get("answer_%d" % i, "").strip() for i in range(len(questions))]
            if not errors:
                con = get_db()
                con.execute("UPDATE interviews SET respondent=?, company=?, held_on=?, notes=? WHERE id=?",
                            (data["respondent"], data["company"], data["held_on"], data["notes"], interview_id))
                save_children(con, interview_id, role, data, questions)
                con.commit()
                flash("Changes saved.")
                return redirect(url_for("view", interview_id=interview_id))
            for e in errors:
                flash(e, "error")
            return render_template("form.html", mode="edit", role=role, questions=questions,
                                   data=data, i=row), 400
        data = {"respondent": row["respondent"], "company": row["company"], "held_on": row["held_on"],
                "notes": row["notes"], "tags": tags, "answers": [a["answer"] for a in answers]}
        return render_template("form.html", mode="edit", role=role, questions=questions, data=data, i=row)

    @app.route("/interview/<int:interview_id>/delete", methods=["GET", "POST"])
    def delete(interview_id):
        row, _, _ = load(interview_id)
        if request.method == "POST":
            con = get_db()
            con.execute("DELETE FROM interviews WHERE id=?", (interview_id,))
            con.commit()
            flash("Interview '%s' was deleted." % row["respondent"])
            return redirect(url_for("index"))
        return render_template("delete.html", i=row)

    @app.route("/summary")
    def summary():
        con = get_db()
        total = con.execute("SELECT COUNT(*) FROM interviews").fetchone()[0]
        by_role = con.execute("SELECT role, COUNT(*) n FROM interviews GROUP BY role ORDER BY n DESC").fetchall()
        counts = {r["tag"]: r["n"] for r in con.execute("SELECT tag, COUNT(*) n FROM tags GROUP BY tag")}
        rows = sorted(((label, counts.get(key, 0)) for key, label in PROBLEM_TAGS),
                      key=lambda x: -x[1])
        return render_template("summary.html", total=total, by_role=by_role, rows=rows)

    # ---------- export ----------
    @app.route("/export.csv")
    def export_csv():
        con = get_db()
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["id", "respondent", "role", "company", "date", "tags", "question_no", "question", "answer"])
        for i in con.execute("SELECT * FROM interviews ORDER BY id"):
            tags = ";".join(r["tag"] for r in con.execute("SELECT tag FROM tags WHERE interview_id=?", (i["id"],)))
            for a in con.execute("SELECT * FROM answers WHERE interview_id=? ORDER BY position", (i["id"],)):
                w.writerow([i["id"], i["respondent"], i["role"], i["company"], i["held_on"],
                            tags, a["position"], a["question"], a["answer"]])
        return Response(buf.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=interviews.csv"})

    @app.route("/interview/<int:interview_id>/export.txt")
    def export_txt(interview_id):
        row, answers, tags = load(interview_id)
        lines = ["Interview with the %s (%s)" % (row["role"], row["respondent"]),
                 "Company: %s" % (row["company"] or "-"), "Date: %s" % row["held_on"],
                 "Problems: %s" % (", ".join(TAG_LABELS[t] for t in tags) or "-"), ""]
        for a in answers:
            lines += ["%d. %s" % (a["position"], a["question"]), a["answer"] or "-", ""]
        if row["notes"]:
            lines += ["Notes: " + row["notes"]]
        return Response("\n".join(lines), mimetype="text/plain; charset=utf-8",
                        headers={"Content-Disposition": "attachment; filename=interview_%d.txt" % interview_id})

    return app


if __name__ == "__main__":
    create_app().run(debug=os.environ.get("FLASK_DEBUG") == "1")
