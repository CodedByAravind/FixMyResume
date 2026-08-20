from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register(email: str) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": email, "password": "strongpass123"},
    )
    assert resp.status_code == 201
    return resp.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_resume(headers: dict, title: str = "My Resume") -> dict:
    resp = client.post("/api/v1/resumes", json={"title": title}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# ---------- Resume CRUD ----------

def test_create_resume_authenticated():
    headers = _headers(_register("a@example.com"))
    resp = client.post("/api/v1/resumes", json={"title": "My Resume"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Resume"
    assert data["education"] == []
    assert data["experience"] == []
    assert data["projects"] == []
    assert data["skills"] == []
    assert data["certifications"] == []


def test_create_resume_unauthenticated():
    resp = client.post("/api/v1/resumes", json={"title": "x"})
    assert resp.status_code == 401


def test_list_only_own_resumes():
    headers_a = _headers(_register("a@example.com"))
    headers_b = _headers(_register("b@example.com"))
    _create_resume(headers_a)
    _create_resume(headers_a)
    _create_resume(headers_b)

    resp_a = client.get("/api/v1/resumes", headers=headers_a)
    assert resp_a.status_code == 200
    assert len(resp_a.json()) == 2

    resp_b = client.get("/api/v1/resumes", headers=headers_b)
    assert len(resp_b.json()) == 1


def test_get_own_resume():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    resp = client.get(f"/api/v1/resumes/{rid}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == rid


def test_get_nonexistent_resume_404():
    headers = _headers(_register("a@example.com"))
    resp = client.get("/api/v1/resumes/999999", headers=headers)
    assert resp.status_code == 404


def test_update_own_resume():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    resp = client.put(
        f"/api/v1/resumes/{rid}",
        json={"title": "Updated", "full_name": "Alice", "phone": "123"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated"
    assert data["full_name"] == "Alice"


def test_delete_own_resume():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    resp = client.delete(f"/api/v1/resumes/{rid}", headers=headers)
    assert resp.status_code == 204
    assert client.get(f"/api/v1/resumes/{rid}", headers=headers).status_code == 404


# ---------- Ownership / isolation ----------

def test_cannot_access_other_users_resume():
    headers_a = _headers(_register("a@example.com"))
    headers_b = _headers(_register("b@example.com"))
    rid = _create_resume(headers_a)["id"]
    resp = client.get(f"/api/v1/resumes/{rid}", headers=headers_b)
    assert resp.status_code == 404


def test_cannot_update_other_users_resume():
    headers_a = _headers(_register("a@example.com"))
    headers_b = _headers(_register("b@example.com"))
    rid = _create_resume(headers_a)["id"]
    resp = client.put(f"/api/v1/resumes/{rid}", json={"title": "hacked"}, headers=headers_b)
    assert resp.status_code == 404


def test_cannot_delete_other_users_resume():
    headers_a = _headers(_register("a@example.com"))
    headers_b = _headers(_register("b@example.com"))
    rid = _create_resume(headers_a)["id"]
    resp = client.delete(f"/api/v1/resumes/{rid}", headers=headers_b)
    assert resp.status_code == 404


def test_cannot_manage_sections_on_other_users_resume():
    headers_a = _headers(_register("a@example.com"))
    headers_b = _headers(_register("b@example.com"))
    rid = _create_resume(headers_a)["id"]
    resp = client.post(
        f"/api/v1/resumes/{rid}/education",
        json={"institution": "MIT"},
        headers=headers_b,
    )
    assert resp.status_code == 404


# ---------- Sections ----------

def test_education_crud():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]

    resp = client.post(
        f"/api/v1/resumes/{rid}/education",
        json={"institution": "MIT", "degree": "BS"},
        headers=headers,
    )
    assert resp.status_code == 201
    eid = resp.json()["id"]
    assert resp.json()["position"] == 0

    resp2 = client.post(
        f"/api/v1/resumes/{rid}/education",
        json={"institution": "Stanford"},
        headers=headers,
    )
    assert resp2.status_code == 201
    assert resp2.json()["position"] == 1

    resp3 = client.put(
        f"/api/v1/resumes/{rid}/education/{eid}",
        json={"degree": "MS"},
        headers=headers,
    )
    assert resp3.status_code == 200
    assert resp3.json()["degree"] == "MS"

    resp4 = client.delete(f"/api/v1/resumes/{rid}/education/{eid}", headers=headers)
    assert resp4.status_code == 204
    detail = client.get(f"/api/v1/resumes/{rid}", headers=headers).json()
    assert len(detail["education"]) == 1


def test_all_section_types_create():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    base = f"/api/v1/resumes/{rid}"

    cases = [
        (f"{base}/education", {"institution": "MIT"}),
        (f"{base}/experience", {"company": "Acme", "title": "Engineer"}),
        (f"{base}/projects", {"name": "Project X"}),
        (f"{base}/skills", {"name": "Python"}),
        (f"{base}/certifications", {"name": "AWS Certified"}),
    ]
    for url, payload in cases:
        resp = client.post(url, json=payload, headers=headers)
        assert resp.status_code == 201, f"{url} -> {resp.status_code} {resp.text}"

    detail = client.get(base, headers=headers).json()
    assert len(detail["education"]) == 1
    assert len(detail["experience"]) == 1
    assert len(detail["projects"]) == 1
    assert len(detail["skills"]) == 1
    assert len(detail["certifications"]) == 1


# ---------- Validation ----------

def test_section_requires_required_field():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    resp = client.post(f"/api/v1/resumes/{rid}/education", json={}, headers=headers)
    assert resp.status_code == 422


def test_invalid_date_format_422():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    resp = client.post(
        f"/api/v1/resumes/{rid}/education",
        json={"institution": "MIT", "start_date": "June 2020"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_end_before_start_date_422():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    resp = client.post(
        f"/api/v1/resumes/{rid}/education",
        json={"institution": "MIT", "start_date": "2022-01", "end_date": "2020-01"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_invalid_url_422():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    resp = client.post(
        f"/api/v1/resumes/{rid}/projects",
        json={"name": "P", "url": "not-a-url"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_invalid_resume_url_422():
    headers = _headers(_register("a@example.com"))
    resp = client.post(
        "/api/v1/resumes",
        json={"title": "R", "website": "ftp://bad"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_duplicate_skill_409():
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    payload = {"name": "Python", "category": "Language"}
    assert (
        client.post(f"/api/v1/resumes/{rid}/skills", json=payload, headers=headers).status_code
        == 201
    )
    resp = client.post(f"/api/v1/resumes/{rid}/skills", json=payload, headers=headers)
    assert resp.status_code == 409


# ---------- Cascade behavior ----------

def test_delete_resume_cascades_sections(db_session):
    headers = _headers(_register("a@example.com"))
    rid = _create_resume(headers)["id"]
    client.post(
        f"/api/v1/resumes/{rid}/education",
        json={"institution": "MIT"},
        headers=headers,
    )
    client.post(
        f"/api/v1/resumes/{rid}/skills",
        json={"name": "Python"},
        headers=headers,
    )

    from app.models.education import EducationEntry
    from app.models.skill import Skill

    assert db_session.query(EducationEntry).count() == 1
    assert db_session.query(Skill).count() == 1

    client.delete(f"/api/v1/resumes/{rid}", headers=headers)

    assert db_session.query(EducationEntry).count() == 0
    assert db_session.query(Skill).count() == 0
