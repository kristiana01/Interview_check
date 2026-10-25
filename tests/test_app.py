import pytest

from app import create_app
from questions import QUESTIONS


@pytest.fixture()
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def form(role="CTO", **over):
    data = {"respondent": "R1", "company": "Acme", "held_on": "2026-10-01", "notes": "n"}
    for i in range(len(QUESTIONS[role])):
        data["answer_%d" % i] = "answer %d" % i
    data["tags"] = ["no_cases", "no_automation"]
    data.update(over)
    return data


def create(client, role="CTO", **over):
    r = client.post("/new?role=" + role, data=dict(form(role, **over), role=role))
    assert r.status_code == 302
    return int(r.headers["Location"].rsplit("/", 1)[1])


def test_index_empty(client):
    r = client.get("/")
    assert r.status_code == 200 and b"No interviews found" in r.data


def test_create_and_view(client):
    i = create(client)
    r = client.get("/interview/%d" % i)
    assert b"answer 3" in r.data and b"No automated tests" in r.data


def test_validation(client):
    r = client.post("/new?role=CEO", data=form("CEO", respondent="", held_on="bad"))
    assert r.status_code == 400
    assert b"Respondent name" in r.data and b"YYYY-MM-DD" in r.data


def test_edit(client):
    i = create(client)
    d = form(respondent="Changed", tags=["no_owner"], answer_0="new text")
    assert client.post("/interview/%d/edit" % i, data=d).status_code == 302
    page = client.get("/interview/%d" % i).data
    assert b"Changed" in page and b"new text" in page
    assert b"No person responsible" in page and b"No automated tests" not in page


def test_delete_confirm_and_delete(client):
    i = create(client)
    page = client.get("/interview/%d/delete" % i)
    assert page.status_code == 200 and b"cannot be undone" in page.data
    assert client.get("/interview/%d" % i).status_code == 200  # GET does not delete
    assert client.post("/interview/%d/delete" % i).status_code == 302
    assert client.get("/interview/%d" % i).status_code == 404
    assert b"No interviews found" in client.get("/").data


def test_delete_removes_answers_and_tags(client):
    import db
    i = create(client)
    client.post("/interview/%d/delete" % i)
    con = db.connect(client.application.config["DB_PATH"])
    assert con.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM tags").fetchone()[0] == 0


def test_list_order(client):
    create(client, "CTO", respondent="Anna", held_on="2026-01-01")
    create(client, "CEO", respondent="Bob", held_on="2026-02-01")
    page = client.get("/").data
    assert b"Anna" in page and b"Bob" in page
    assert page.index(b"Bob") < page.index(b"Anna")


def test_summary(client):
    create(client, tags=["no_cases"])
    create(client, "CEO", tags=["no_cases", "no_owner"])
    page = client.get("/summary").data
    assert b"2 interviews" in page and b"2 / 2" in page


def test_exports(client):
    i = create(client)
    csv_data = client.get("/export.csv").data.decode()
    assert csv_data.startswith("id,respondent") and "answer 0" in csv_data
    txt = client.get("/interview/%d/export.txt" % i)
    assert b"Interview with the CTO" in txt.data


def test_404(client):
    assert client.get("/interview/999").status_code == 404
