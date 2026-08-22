from fastapi.testclient import TestClient

from app.analysis.providers import (
    AnalysisProvider,
    ResumeContext,
    RuleBasedAnalysisProvider,
    SkillEntry,
)
from app.main import app
from app.schemas.analysis import AnalysisResult, ScoreDetails

client = TestClient(app)

VALID_JD = (
    "We need a software engineer with Python, React, Docker, and PostgreSQL. "
    "Strong communication and problem solving. AWS experience is a plus. "
    "Fintech domain preferred."
)


def _register(email: str) -> str:
    r = client.post(
        "/api/v1/auth/register",
        json={"name": "U", "email": email, "password": "strongpass123"},
    )
    assert r.status_code == 201
    return r.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _mk_resume(headers: dict, payload: dict) -> dict:
    r = client.post("/api/v1/resumes", json=payload, headers=headers)
    assert r.status_code == 201
    return r.json()


def _add_skill(headers: dict, rid: int, name: str):
    assert (
        client.post(
            f"/api/v1/resumes/{rid}/skills", json={"name": name}, headers=headers
        ).status_code
        == 201
    )


# ---------- ownership / auth ----------

def test_analyze_requires_auth():
    r = client.post("/api/v1/resumes/1/analyze", json={"job_description": "x"})
    assert r.status_code == 401


def test_analyze_other_users_resume_404():
    ha = _headers(_register("a@x.com"))
    hb = _headers(_register("b@x.com"))
    rid = _mk_resume(ha, {"title": "A"})["id"]
    r = client.post(
        f"/api/v1/resumes/{rid}/analyze",
        json={"job_description": VALID_JD},
        headers=hb,
    )
    assert r.status_code == 404


def test_analyze_nonexistent_resume_404():
    h = _headers(_register("a@x.com"))
    r = client.post(
        "/api/v1/resumes/99999/analyze",
        json={"job_description": VALID_JD},
        headers=h,
    )
    assert r.status_code == 404


# ---------- validation ----------

def test_analyze_empty_jd_422():
    h = _headers(_register("a@x.com"))
    rid = _mk_resume(h, {"title": "A"})["id"]
    r = client.post(f"/api/v1/resumes/{rid}/analyze", json={"job_description": ""}, headers=h)
    assert r.status_code == 422


def test_analyze_oversized_jd_422():
    h = _headers(_register("a@x.com"))
    rid = _mk_resume(h, {"title": "A"})["id"]
    big = "a" * 20001
    r = client.post(f"/api/v1/resumes/{rid}/analyze", json={"job_description": big}, headers=h)
    assert r.status_code == 422


# ---------- successful analysis ----------

def test_analyze_own_resume_returns_contract():
    h = _headers(_register("a@x.com"))
    rid = _mk_resume(h, {"title": "A"})["id"]
    _add_skill(h, rid, "Python")
    _add_skill(h, rid, "Docker")
    r = client.post(
        f"/api/v1/resumes/{rid}/analyze",
        json={"job_description": VALID_JD},
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()
    # Stable contract fields
    assert 0 <= data["score"] <= 100
    assert "score_details" in data
    assert isinstance(data["matched_skills"], list)
    assert isinstance(data["missing_skills"], list)
    assert isinstance(data["job_keywords"], list)
    assert isinstance(data["recommendations"], list)
    assert data["provider"] == "rule_based"


def test_matched_skills_detected():
    h = _headers(_register("a@x.com"))
    rid = _mk_resume(h, {"title": "A"})["id"]
    _add_skill(h, rid, "Python")
    r = client.post(
        f"/api/v1/resumes/{rid}/analyze",
        json={"job_description": VALID_JD},
        headers=h,
    )
    data = r.json()
    matched = {s["name"] for s in data["matched_skills"]}
    assert "python" in matched


def test_missing_skills_detected():
    h = _headers(_register("a@x.com"))
    rid = _mk_resume(h, {"title": "A"})["id"]
    r = client.post(
        f"/api/v1/resumes/{rid}/analyze",
        json={"job_description": VALID_JD},
        headers=h,
    )
    data = r.json()
    missing = {s["name"] for s in data["missing_skills"]}
    assert "react" in missing
    assert "postgresql" in missing


def test_score_higher_with_more_skills():
    h = _headers(_register("a@x.com"))
    rid1 = _mk_resume(h, {"title": "A"})["id"]
    rid2 = _mk_resume(h, {"title": "B"})["id"]
    for name in ["Python", "React", "Docker", "PostgreSQL"]:
        _add_skill(h, rid2, name)
    
    s1 = client.post(
        f"/api/v1/resumes/{rid1}/analyze", json={"job_description": VALID_JD}, headers=h
    ).json()["score"]
    s2 = client.post(
        f"/api/v1/resumes/{rid2}/analyze", json={"job_description": VALID_JD}, headers=h
    ).json()["score"]
    assert s2 > s1


def test_deterministic():
    h = _headers(_register("a@x.com"))
    rid = _mk_resume(h, {"title": "A"})["id"]
    _add_skill(h, rid, "Python")
    r1 = client.post(
        f"/api/v1/resumes/{rid}/analyze", json={"job_description": VALID_JD}, headers=h
    ).json()
    r2 = client.post(
        f"/api/v1/resumes/{rid}/analyze", json={"job_description": VALID_JD}, headers=h
    ).json()
    assert r1 == r2


def test_recommendations_for_missing_skills():
    h = _headers(_register("a@x.com"))
    rid = _mk_resume(h, {"title": "A"})["id"]
    data = client.post(
        f"/api/v1/resumes/{rid}/analyze", json={"job_description": VALID_JD}, headers=h
    ).json()
    assert any("highlight" in rec or "gain" in rec for rec in data["recommendations"])


# ---------- word boundary / alias ----------

def test_word_boundary_avoids_substring_matches():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(skills=[SkillEntry(name="go")])
    jd = "We are going forward with the plan."
    result: AnalysisResult = provider.analyze(ctx, jd)
    # "go" should not match inside "going"
    matched = {s.name for s in result.matched_skills}
    assert "go" not in matched


def test_alias_normalization():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(skills=[SkillEntry(name="Node.js")])
    result = provider.analyze(ctx, "We use nodejs extensively.")
    matched = {s.name for s in result.matched_skills}
    assert "node.js" in matched


# ---------- provider interface ----------

class FakeProvider(AnalysisProvider):
    name = "fake"

    def analyze(self, resume_context, job_description):
        return AnalysisResult(
            score=42,
            score_details=ScoreDetails(skill_score=0.0, keyword_score=0.0, role_domain_score=0.0, overall=42),
            matched_skills=[],
            missing_skills=[],
            job_keywords=[],
            matched_keywords=[],
            missing_keywords=[],
            recommendations=["rec"],
            summary="s",
            provider=self.name,
        )


def test_rule_based_provider_is_a_provider():
    from app.api.v1.analysis import get_provider

    provider = get_provider()
    assert isinstance(provider, AnalysisProvider)
    assert provider.name == "rule_based"


# FakeProvider test requires injecting a provider; the service accepts any
# AnalysisProvider argument, so we test the interface at the unit level.
def test_provider_interface_contract():
    fake = FakeProvider()
    result = fake.analyze(ResumeContext(), "jd")
    assert result.provider == "fake"
    assert result.score == 42


# ---------- edge cases ----------

def test_word_boundary_c_and_r():
    provider = RuleBasedAnalysisProvider()
    # C and R must only match standalone words, not letters inside other words.
    ctx = ResumeContext(skills=[SkillEntry(name="c"), SkillEntry(name="r")])
    jd = "We value creativity, real-time processing, and rock solid teamwork."
    result = provider.analyze(ctx, jd)
    matched = {s.name for s in result.matched_skills}
    assert "c" not in matched
    assert "r" not in matched
    # Standalone C and R should match.
    ctx2 = ResumeContext(skills=[SkillEntry(name="c"), SkillEntry(name="r")])
    result2 = provider.analyze(ctx2, "We use C and R daily.")
    matched2 = {s.name for s in result2.matched_skills}
    assert "c" in matched2
    assert "r" in matched2


def test_generic_node_does_not_match_nodejs():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(skills=[SkillEntry(name="node.js")])
    result = provider.analyze(ctx, "Each node in the cluster handles requests.")
    matched = {s.name for s in result.matched_skills}
    assert "node.js" not in matched


def test_nodejs_and_node_dot_js_match():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(skills=[SkillEntry(name="node.js")])
    for jd in ["We use node.js for the backend.", "We use nodejs for the backend."]:
        result = provider.analyze(ctx, jd)
        matched = {s.name for s in result.matched_skills}
        assert "node.js" in matched


def test_jd_with_no_recognized_terms_scores_zero():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(
        skills=[SkillEntry(name="python"), SkillEntry(name="react")],
        summary="Builds web apps.",
    )
    jd = "The sky is blue and the sun is warm today."
    result = provider.analyze(ctx, jd)
    assert 0 <= result.score <= 100
    # Nothing recognizable in the JD, so no positive contribution.
    assert result.score == 0


def test_resume_with_no_skills():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(summary="I am a product manager.")
    jd = "We need Python, React, and Django skills plus strong communication."
    result = provider.analyze(ctx, jd)
    assert 0 <= result.score <= 100
    assert len(result.matched_skills) == 0
    assert "python" in {s.name for s in result.missing_skills}


def test_resume_matching_nothing_scores_low():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(skills=[SkillEntry(name="c++")], summary="Low-level systems.")
    jd = "Need a React frontend engineer with Python, PostgreSQL, AWS, communication, and fintech."
    result = provider.analyze(ctx, jd)
    assert 0 <= result.score <= 100
    # A very weak match should be below 50.
    assert result.score < 50


def test_resume_matching_everything_scores_high():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(
        skills=[
            SkillEntry(name="python"),
            SkillEntry(name="react"),
            SkillEntry(name="postgresql"),
            SkillEntry(name="aws"),
        ],
        experience_descriptions=["Built fintech apps with strong communication."],
    )
    jd = "Fintech software engineer. Strong communication. Python, React, PostgreSQL, AWS."
    result = provider.analyze(ctx, jd)
    assert 0 <= result.score <= 100
    assert result.score >= 75


def test_score_bounded_zero_to_one_hundred():
    provider = RuleBasedAnalysisProvider()
    for jd in ["Nothing here matches anything at all.", VALID_JD]:
        for ctx in [ResumeContext(), ResumeContext(skills=[SkillEntry(name="python")])]:
            result = provider.analyze(ctx, jd)
            assert 0 <= result.score <= 100


def test_score_reaches_100_when_everything_matches():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(
        skills=[
            SkillEntry(name="python"),
            SkillEntry(name="aws"),
            SkillEntry(name="docker"),
            SkillEntry(name="fintech"),
        ],
        experience_descriptions=["Fintech software engineer with strong communication."],
        summary="Full stack fintech engineer. Strong communication. Backend, real-time systems.",
    )
    jd = (
        "Fintech software engineer, backend. Strong communication."
        "Python, AWS, Docker, real-time systems."
    )
    result = provider.analyze(ctx, jd)
    assert 0 <= result.score <= 100
    # Full coverage of every bucket's recognized terms.
    assert result.score == 100


def test_deterministic_identical_runs():
    provider = RuleBasedAnalysisProvider()
    ctx = ResumeContext(skills=[SkillEntry(name="python")], summary="Backend engineer.")
    r1 = provider.analyze(ctx, VALID_JD)
    r2 = provider.analyze(ctx, VALID_JD)
    assert r1 == r2
