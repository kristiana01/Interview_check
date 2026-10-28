# Interview Check

A small web application for recording and analysing interviews about manual software testing practices. It was developed by Kristiana Baranovska as the practical part of a qualification paper at Turiba University ("Analysis and Improvement of Manual Software Testing Practices in a Startup Company").

## Features

- Ready question sets for three roles (CEO, CTO, Developer) and a short general set
- Create, view, **edit and delete** interviews (delete asks for confirmation)
- Mark the testing problems that the respondent mentioned
- Summary page that shows how often each problem was mentioned
- Export all interviews to CSV (on the Summary page), or one interview to TXT
- Light and dark theme, works on phones

## Run it

Requires Python 3.9 or newer.

```bash
git clone https://github.com/kristiana01/Interview_check.git
cd Interview_check
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in a browser. The data is stored in a local SQLite file (`interviews.db`), created on first start. Set the `INTERVIEW_DB` environment variable to use another file, and `SECRET_KEY` for any public use.

## Test it

```bash
python -m pytest
```

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Flask routes and application logic |
| `db.py` | SQLite schema and connection |
| `questions.py` | Question sets and problem tags |
| `templates/`, `static/` | Pages and styles |
| `tests/test_app.py` | Automated tests |

## Licence

MIT, see `LICENSE`.
