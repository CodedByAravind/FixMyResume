from fastapi.testclient import TestClient

from app.analysis.providers import ResumeContext, SkillEntry
from app.main import app
from app.schemas.analysis import AnalysisResult, ScoreDetails, SkillMatch
from app.tailoring.providers.base import TailoringContext, TailoringProvider, TailoringResult
from app.tailoring.providers.rule_based import RuleBasedTailoringProvider

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


def _full_resume(headers: dict) -> dict:
    r = client.post(
        "/api/v1/resumes",
        json={"title": "Full", "summary": "Backend engineer focused on Python APIs."},
        headers=headers,
    )
    rid = r.json()["id"]
    for sk in ["Python", "Django", "Go"]:
        client.post("/api/v1/resumes/{}/skills".format(rid), json={"name": sk}, headers=headers)
    client.post(
        "/api/v1/resumes/{}/experience".format(rid),
        json={
            "company": "Acme",
            "title": "Backend Engineer",
            "description": "Built Python REST APIs and React dashboards.",
        },
        headers=headers,
    )
    client.post(
        "/api/v1/resumes/{}/projects".format(rid),
        json={"name": "Payments API", "description": "Python + Docker service at scale."},
        headers=headers,
    )
    return r.json()


def _tailor(headers: dict, rid: int, jd: str = VALID_JD):
    return client.post(
        "/api/v1/resumes/{}/tailor".format(rid),
        json={"job_description": jd},
        headers=headers,
    )


def _fake_analysis(matched, missing=None):
    missing = missing or []
    return AnalysisResult(
        score=50,
        score_details=ScoreDetails(skill_score=50.0, keyword_score=0.0, role_domain_score=0.0, overall=50),
        matched_skills=[SkillMatch(name=m) for m in matched],
        missing_skills=[SkillMatch(name=m) for m in missing],
        job_keywords=["fintech"],
        matched_keywords=["communication"] if matched else [],
        missing_keywords=[],
        recommendations=["rec"],
        summary="s",
        provider="rule_based",
    )

# ---------- auth / ownership ----------

def test_tailor_requires_auth():
    r = client.post("/api/v1/resumes/1/tailor", json={"job_description": "x"})
    assert r.status_code == 401


def test_tailor_other_users_resume_404():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid = _resume(ha)["id"]
    r = client.post(
        "/api/v1/resumes/{}/tailor".format(rid),
        json={"job_description": VALID_JD},
        headers=hb,
    )
    assert r.status_code == 404


def test_list_versions_other_user_404():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid = _full_resume(ha)["id"]
    _tailor(ha, rid)
    assert client.get("/api/v1/resumes/{}/versions".format(rid), headers=hb).status_code == 404


def test_version_detail_other_user_404():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid = _full_resume(ha)["id"]
    vid = _tailor(ha, rid).json()["id"]
    assert client.get("/api/v1/resumes/{}/versions/{}".format(rid, vid), headers=hb).status_code == 404


# ---------- validation ----------

def test_tailor_empty_jd_422():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    assert _tailor(h, rid, jd="").status_code == 422


def test_tailor_oversized_jd_422():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]
    assert _tailor(h, rid, jd="a" * 20001).status_code == 422


# ---------- versioning ----------

def test_tailor_creates_version_with_snapshots():
    h = _headers(_register("a@x.com"))
    resume = _full_resume(h)
    rid = resume["id"]
    r = _tailor(h, rid)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["resume_id"] == rid
    assert data["source"]["skills"]
    assert data["tailored"]["skills"]
    assert data["analysis_score"] is not None
    assert {"python", "django", "go"} <= {s["name"].lower() for s in data["source"]["skills"]}


def test_original_resume_unchanged():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    _tailor(h, rid)
    r = client.get("/api/v1/resumes/{}".format(rid), headers=h).json()
    assert {s["name"].lower() for s in r["skills"]} == {"python", "django", "go"}
    assert len(r["experience"]) == 1
    assert len(r["projects"]) == 1


def test_tailored_version_stable_after_original_edit():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    version = _tailor(h, rid).json()
    vid = version["id"]
    snapshot_names = {s["name"] for s in version["tailored"]["skills"]}
    # Mutate the live resume: delete a skill entry
    skills = client.get("/api/v1/resumes/{}".format(rid), headers=h).json()["skills"]
    client.delete(
        "/api/v1/resumes/{}/skills/{}".format(rid, skills[0]["id"]), headers=h
    )
    after = client.get("/api/v1/resumes/{}/versions/{}".format(rid, vid), headers=h).json()
    assert {s["name"] for s in after["tailored"]["skills"]} == snapshot_names


def test_multiple_versions_for_one_resume():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    _tailor(h, rid, jd="Fintech Python AWS good")
    _tailor(h, rid, jd="Backend Go services needed")
    versions = client.get("/api/v1/resumes/{}/versions".format(rid), headers=h).json()
    assert len(versions) >= 2


def test_versions_list_and_detail():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    version = _tailor(h, rid).json()
    vid = version["id"]
    listing = client.get("/api/v1/resumes/{}/versions".format(rid), headers=h).json()
    assert any(v["id"] == vid for v in listing)
    detail = client.get("/api/v1/resumes/{}/versions/{}".format(rid, vid), headers=h)
    assert detail.status_code == 200
    assert detail.json()["source"]
    assert detail.json()["tailored"]


def test_compare_returns_source_vs_tailored():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    version = _tailor(h, rid).json()
    c = client.get("/api/v1/resumes/{}/versions/{}/compare".format(rid, version["id"]), headers=h)
    assert c.status_code == 200
    assert c.json()["source"]
    assert c.json()["tailored"]
    assert isinstance(c.json()["changed_sections"], list)


def test_delete_version():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    vid = _tailor(h, rid).json()["id"]
    assert client.delete("/api/v1/resumes/{}/versions/{}".format(rid, vid), headers=h).status_code == 204
    assert client.get("/api/v1/resumes/{}/versions/{}".format(rid, vid), headers=h).status_code == 404


# ---------- provider behavior ----------

def test_rule_based_no_fabrication():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    version = _tailor(h, rid).json()
    source = {s["name"] for s in version["source"]["skills"]}
    tailored = {s["name"] for s in version["tailored"]["skills"]}
    assert tailored <= source  # no new skills invented


def test_rule_based_prioritizes_relevant_skills():
    provider = RuleBasedTailoringProvider()
    analysis = _fake_analysis(["python"], ["fintech"])
    ctx = TailoringContext(
        skills=[{"name": "Go"}, {"name": "Python"}, {"name": "Django"}],
        experience=[], projects=[], education=[], certifications=[],
    )
    result = provider.tailor(ctx, analysis, VALID_JD)
    names = [s["name"] for s in result.skills]
    assert names[0] == "Python"
    assert set(names) == {"Go", "Python", "Django"}


def test_provider_reorders_experience():
    provider = RuleBasedTailoringProvider()
    analysis = _fake_analysis(["python"])
    ctx = TailoringContext(
        skills=[{"name": "Python"}],
        experience=[
            {"company": "A", "title": "X", "description": "No keywords here."},
            {"company": "B", "title": "Y", "description": "Built Python APIs with AWS."},
        ],
        projects=[], education=[], certifications=[],
    )
    result = provider.tailor(ctx, analysis, VALID_JD)
    assert result.experience[0]["company"] == "B"


def test_summary_transform_is_safe():
    provider = RuleBasedTailoringProvider()
    analysis = _fake_analysis(["python"])
    ctx = TailoringContext(
        summary="I build systems.",
        skills=[{"name": "Python"}],
        experience=[], projects=[], education=[], certifications=[],
    )
    result = provider.tailor(ctx, analysis, VALID_JD)
    assert "Python" in result.summary or "python" in result.summary.lower()


def test_tailoring_provider_interface():
    p = RuleBasedTailoringProvider()
    assert isinstance(p, TailoringProvider)
    assert p.name == "rule_based"


def test_tailored_score_reported():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    data = _tailor(h, rid).json()
    assert data["analysis_score"] is not None


def test_harmless_warning_when_no_changes():
    provider = RuleBasedTailoringProvider()
    analysis = _fake_analysis([])
    ctx = TailoringContext(
        summary="Fintech backend engineer.",
        skills=[{"name": "Python"}],
        experience=[], projects=[], education=[], certifications=[],
    )
    result = provider.tailor(ctx, analysis, "No recognizable terms here.")
    assert isinstance(result.warnings, list)
    assert isinstance(result.recommendations, list)


# ---------- review-fix tests ----------

def test_resume_deletion_cascades_versions():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    v1 = _tailor(h, rid, jd="Fintech Python").json()["id"]
    v2 = _tailor(h, rid, jd="Backend Go").json()["id"]
    # Confirm 2 versions exist
    assert len(client.get("/api/v1/resumes/{}/versions".format(rid), headers=h).json()) == 2
    # Delete the resume
    assert client.delete("/api/v1/resumes/{}".format(rid), headers=h).status_code == 204
    # Versions gone
    assert client.get("/api/v1/resumes/{}/versions".format(rid), headers=h).status_code == 404
    assert client.get("/api/v1/resumes/{}/versions/{}".format(rid, v1), headers=h).status_code == 404
    # Define a helper-based DB check: snapshot rows removed via another user''s clean resume
    # (indirectly verified by 404 on version access + resume gone)


def test_tailored_profile_retains_personal_info():
    h = _headers(_register("a@x.com"))
    r = client.post(
        "/api/v1/resumes",
        json={
            "title": "R", "summary": "I build systems fast.",
            "full_name": "Alice Doe", "email": "alice@x.com", "phone": "123-456",
            "location": "NYC", "website": "https://a.dev", "linkedin": "https://li", "github": "https://gh",
        },
        headers=h,
    )
    rid = r.json()["id"]
    client.post("/api/v1/resumes/{}/skills".format(rid), json={"name": "Python"}, headers=h)
    version = _tailor(h, rid).json()
    src_p = version["source"]["profile"]
    tai_p = version["tailored"]["profile"]
    for field in ["full_name", "email", "phone", "location", "website", "linkedin", "github"]:
        assert src_p[field] == tai_p[field], field
    # summary may differ (tailored)
    assert tai_p["summary"] is not None


def test_empty_sections_tailor_succeeds():
    h = _headers(_register("a@x.com"))
    rid = _resume(h)["id"]  # no skills/experience/projects/education/certifications
    r = _tailor(h, rid)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["source"]["skills"] == []
    assert data["tailored"]["skills"] == []
    assert data["source"]["experience"] == []
    assert data["tailored"]["certifications"] == []


def test_delete_version_returns_204_no_body():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]
    vid = _tailor(h, rid).json()["id"]
    resp = client.delete("/api/v1/resumes/{}/versions/{}".format(rid, vid), headers=h)
    assert resp.status_code == 204
    assert resp.content == b"" or resp.content is None


def test_tailored_score_exposed_and_consistent():
    h = _headers(_register("a@x.com"))
    rid = _full_resume(h)["id"]  # has Python, Django, Go skills + experience
    jd = "Need a Backend engineer with Python, Django. Strong communication. AWS."
    data = _tailor(h, rid, jd=jd).json()
    assert "analysis_score" in data
    assert "tailored_score" in data
    assert data["tailored_score"] is not None
    # tailored snapshot adds matched skills to the summary lead, so tailored >= source
    assert data["tailored_score"] >= data["analysis_score"]
    # detail + compare also expose it
    det = client.get("/api/v1/resumes/{}/versions/{}".format(rid, data["id"]), headers=h).json()
    assert det["tailored_score"] == data["tailored_score"]
