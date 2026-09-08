from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_JD = (
    "Fintech software engineer, backend. Strong communication. "
    "Python, React, PostgreSQL, AWS, Docker, real-time systems."
)


def _register(email: str) -> str:
    r = client.post(
        "/api/v1/auth/register",
        json={"name": "U", "email": email, "password": "strongpass123"},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": "Bearer " + token}


def _resume(headers: dict, title: str = "R") -> dict:
    r = client.post("/api/v1/resumes", json={"title": title}, headers=headers)
    assert r.status_code == 201
    return r.json()


def _version(headers: dict, rid: int, jd: str = VALID_JD) -> dict:
    r = client.post("/api/v1/resumes/{}/tailor".format(rid), json={"job_description": jd}, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def _app(headers: dict, rid: int, **over) -> dict:
    payload = {"resume_id": rid, "company": "Acme", "job_title": "Engineer"}
    payload.update(over)
    return client.post("/api/v1/applications", json=payload, headers=headers)


# ---------- auth ----------

def test_list_requires_auth():
    assert client.get("/api/v1/applications").status_code == 401

def test_create_requires_auth():
    assert client.post("/api/v1/applications", json={"resume_id": 1, "company": "A", "job_title": "B"}).status_code == 401

def test_detail_requires_auth():
    assert client.get("/api/v1/applications/1").status_code == 401

def test_update_requires_auth():
    assert client.put("/api/v1/applications/1", json={"status": "interview"}).status_code == 401

def test_delete_requires_auth():
    assert client.delete("/api/v1/applications/1").status_code == 401


# ---------- create ----------

def test_create_live_resume_application():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    r = _app(h, rid, company="Acme", job_title="Engineer", notes="hello")
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["company"] == "Acme"
    assert data["resume_version_id"] is None
    assert data["status"] == "applied"
    assert data["created_at"]
    assert data["updated_at"]


def test_create_with_tailored_version():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    vid = _version(h, rid)["id"]
    r = _app(h, rid, resume_version_id=vid)
    assert r.status_code == 201
    assert r.json()["resume_version_id"] == vid


def test_create_requires_resume():
    h = _headers(_register("a@x.com"))
    r = client.post("/api/v1/applications", json={"company": "A", "job_title": "B"}, headers=h)
    assert r.status_code == 422


def test_create_requires_company_and_title():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    assert _app(h, rid, company="").status_code == 422
    assert _app(h, rid, job_title="").status_code == 422


def test_create_invalid_status():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    assert _app(h, rid, status="nonsense").status_code == 422


def test_create_invalid_url():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    assert _app(h, rid, job_url="notaurl").status_code == 422


def test_create_backdated_application_date():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    r = _app(h, rid, application_date="2022-01-15T00:00:00")
    assert r.status_code == 201
    assert r.json()["application_date"].startswith("2022-01-15")


def test_create_default_application_date():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    r = _app(h, rid)
    assert r.status_code == 201
    assert r.json()["application_date"]


def test_interview_date_requires_interview_status():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    r = _app(h, rid, interview_date="2025-01-01T10:00:00")
    assert r.status_code == 422


def test_interview_date_with_interview_status():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    r = _app(h, rid, status="interview", interview_date="2025-01-01T10:00:00")
    assert r.status_code == 201
    assert r.json()["interview_date"]


# ---------- ownership ----------

def test_own_application_succeeds():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    aid = _app(h, rid).json()["id"]
    assert client.get("/api/v1/applications/{}".format(aid), headers=h).status_code == 200


def test_another_users_application_404():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid = _resume(ha)["id"]
    aid = _app(ha, rid).json()["id"]
    assert client.get("/api/v1/applications/{}".format(aid), headers=hb).status_code == 404
    assert client.put("/api/v1/applications/{}".format(aid), json={"notes": "x"}, headers=hb).status_code == 404
    assert client.delete("/api/v1/applications/{}".format(aid), headers=hb).status_code == 404


def test_another_users_resume_404():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid = _resume(ha)["id"]
    assert _app(hb, rid).status_code == 404


def test_another_users_version_404():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid = _resume(ha)["id"]
    vid = _version(ha, rid)["id"]
    ridb = _resume(hb)["id"]
    assert _app(hb, ridb, resume_version_id=vid).status_code == 404


def test_version_belongs_to_another_resume_404():
    h = _headers(_register("a@x.com"))
    rid1 = _resume(h)["id"]
    rid2 = _resume(h)["id"]
    vid2 = _version(h, rid2)["id"]
    assert _app(h, rid1, resume_version_id=vid2).status_code == 404


# ---------- CRUD ----------

def test_list_get_update_delete():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    aid = _app(h, rid).json()["id"]
    # list
    lst = client.get("/api/v1/applications", headers=h)
    assert lst.status_code == 200 and len(lst.json()) == 1
    # get
    assert client.get("/api/v1/applications/{}".format(aid), headers=h).status_code == 200
    # update
    up = client.put("/api/v1/applications/{}".format(aid), json={"notes": "new"}, headers=h)
    assert up.status_code == 200 and up.json()["notes"] == "new"
    # updated_at changes
    assert up.json()["updated_at"] >= lst.json()[0]["updated_at"]
    # delete 204 empty
    d = client.delete("/api/v1/applications/{}".format(aid), headers=h)
    assert d.status_code == 204
    assert d.content == b"" or d.content is None
    assert client.get("/api/v1/applications/{}".format(aid), headers=h).status_code == 404


# ---------- filtering ----------

def _mk_two(h):
    rid = _resume(h)["id"]
    _app(h, rid, company="Alpha", job_title="Backend Eng", status="applied")
    _app(h, rid, company="Beta Corp", job_title="Data Scientist", status="interview")


def test_filter_by_status():
    h = _headers(_register("a@x.com"))
    _mk_two(h)
    lst = client.get("/api/v1/applications?status=interview", headers=h).json()
    assert len(lst) == 1 and lst[0]["company"] == "Beta Corp"


def test_search_q():
    h = _headers(_register("a@x.com"))
    _mk_two(h)
    assert len(client.get("/api/v1/applications?q=alpha", headers=h).json()) == 1
    assert len(client.get("/api/v1/applications?q=data", headers=h).json()) == 1


def test_sort_company_asc():
    h = _headers(_register("a@x.com"))
    _mk_two(h)
    lst = client.get("/api/v1/applications?sort_by=company&order=asc", headers=h).json()
    assert lst[0]["company"] == "Alpha"
    lst2 = client.get("/api/v1/applications?sort_by=company&order=desc", headers=h).json()
    assert lst2[0]["company"] == "Beta Corp"


def test_invalid_filter_values_422():
    h = _headers(_register("a@x.com"))
    assert client.get("/api/v1/applications?status=bogus", headers=h).status_code == 422
    assert client.get("/api/v1/applications?sort_by=bogus", headers=h).status_code == 422
    assert client.get("/api/v1/applications?order=bogus", headers=h).status_code == 422


# ---------- timestamps / updates ----------

def test_updated_at_changes_and_partial_update():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    aid = _app(h, rid, notes="first").json()["id"]
    before = client.get("/api/v1/applications/{}".format(aid), headers=h).json()
    # partial update: change status, keep notes; exclude_unset means company/title unchanged
    r = client.put("/api/v1/applications/{}".format(aid), json={"status": "offer"}, headers=h)
    assert r.status_code == 200
    after = r.json()
    # notes preserved (not overwritten), status changed
    assert after["notes"] == "first"
    assert after["status"] == "offer"
    # application_date unchanged
    assert after["application_date"] == before["application_date"]


def test_interview_date_persisted():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    aid = _app(h, rid, status="interview", interview_date="2025-06-01T09:00:00").json()["id"]
    data = client.get("/api/v1/applications/{}".format(aid), headers=h).json()
    assert data["interview_date"]


# ---------- version deletion preserves app ----------

def test_delete_version_preserves_application():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    vid = _version(h, rid)["id"]
    aid = _app(h, rid, resume_version_id=vid).json()["id"]
    assert client.delete("/api/v1/resumes/{}/versions/{}".format(rid, vid), headers=h).status_code == 204
    data = client.get("/api/v1/applications/{}".format(aid), headers=h).json()
    assert data["resume_version_id"] is None


def test_resume_with_apps_cannot_be_deleted():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    _app(h, rid)
    r = client.delete("/api/v1/resumes/{}".format(rid), headers=h)
    # RESTRICT -> application preserved; server returns a clean 409
    assert r.status_code == 409
    # application still intact
    assert len(client.get("/api/v1/applications", headers=h).json()) == 1


# ---------- multiple apps ----------

def test_multiple_apps_and_isolation():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid_a = _resume(ha)["id"]
    rid_b = _resume(hb)["id"]
    _app(ha, rid_a)
    _app(ha, rid_a)
    _app(hb, rid_b)
    assert len(client.get("/api/v1/applications", headers=ha).json()) == 2
    assert len(client.get("/api/v1/applications", headers=hb).json()) == 1
