"""Maintainable skill taxonomy used by the rule-based analysis provider.

Each entry maps a canonical skill label to a set of aliases. Aliases are
matched case-insensitively at word boundaries so short terms like "c" or
"go" only match as standalone words. Organised by category for readability
and future maintenance.
"""

# label -> (category, {aliases})
SKILL_TAXONOMY: dict[str, tuple[str, set[str]]] = {
    # Programming languages
    "python": ("language", {"python", "python3"}),
    "javascript": ("language", {"javascript", "js", "ecmascript"}),
    "typescript": ("language", {"typescript", "ts"}),
    "java": ("language", {"java"}),
    "c": ("language", {"c"}),
    "c++": ("language", {"c++", "cpp", "c plus plus"}),
    "c#": ("language", {"c#", "csharp", "c sharp"}),
    "go": ("language", {"go", "golang"}),
    "rust": ("language", {"rust"}),
    "ruby": ("language", {"ruby"}),
    "swift": ("language", {"swift"}),
    "kotlin": ("language", {"kotlin"}),
    "php": ("language", {"php"}),
    "shell": ("language", {"shell", "bash"}),
    "sql": ("language", {"sql"}),
    "r": ("language", {"r"}),

    # Frameworks / libraries
    "react": ("framework", {"react", "reactjs", "react.js"}),
    "node.js": ("framework", {"node.js", "nodejs"}),
    "express": ("framework", {"express", "express.js"}),
    "django": ("framework", {"django"}),
    "flask": ("framework", {"flask"}),
    "fastapi": ("framework", {"fastapi"}),
    "angular": ("framework", {"angular", "angular.js", "angularjs"}),
    "vue": ("framework", {"vue", "vue.js", "vuejs"}),
    "next.js": ("framework", {"next.js", "nextjs"}),
    "spring": ("framework", {"spring", "spring boot", "springboot"}),
    "laravel": ("framework", {"laravel"}),
    "tensorflow": ("library", {"tensorflow", "tf"}),
    "pytorch": ("library", {"pytorch", "torch"}),
    "pandas": ("library", {"pandas"}),
    "numpy": ("library", {"numpy"}),
    "jquery": ("library", {"jquery"}),

    # Databases
    "postgresql": ("database", {"postgresql", "postgres"}),
    "mysql": ("database", {"mysql"}),
    "mongodb": ("database", {"mongodb", "mongo"}),
    "redis": ("database", {"redis"}),
    "sqlite": ("database", {"sqlite"}),
    "elasticsearch": ("database", {"elasticsearch", "elastic"}),
    "dynamodb": ("database", {"dynamodb"}),
    "oracle": ("database", {"oracle"}),

    # Cloud
    "aws": ("cloud", {"aws", "amazon web services"}),
    "azure": ("cloud", {"azure", "microsoft azure"}),
    "gcp": ("cloud", {"gcp", "google cloud", "google cloud platform"}),

    # DevOps / tools
    "docker": ("devops", {"docker"}),
    "kubernetes": ("devops", {"kubernetes", "k8s"}),
    "terraform": ("devops", {"terraform"}),
    "jenkins": ("devops", {"jenkins"}),
    "github actions": ("devops", {"github actions", "gh actions"}),
    "ci/cd": ("devops", {"ci/cd", "cicd", "continuous integration", "continuous deployment"}),
    "git": ("tools", {"git"}),
    "linux": ("tools", {"linux"}),
    "nginx": ("tools", {"nginx"}),

    # Testing
    "pytest": ("testing", {"pytest"}),
    "jest": ("testing", {"jest"}),
    "selenium": ("testing", {"selenium"}),
    "junit": ("testing", {"junit"}),
    "testing": ("testing", {"unit testing", "testing", "tldd", "test driven development", "tdd"}),

    # AI / ML / Data
    "machine learning": ("ai_ml", {"machine learning", "ml"}),
    "deep learning": ("ai_ml", {"deep learning", "dl"}),
    "nlp": ("ai_ml", {"nlp", "natural language processing"}),
    "computer vision": ("ai_ml", {"computer vision", "cv"}),
    "data analysis": ("data", {"data analysis", "data analytics"}),
    "data science": ("data", {"data science"}),
    "etl": ("data", {"etl"}),
    "dbt": ("data", {"dbt"}),
    "airflow": ("data", {"airflow"}),

    # Security
    "security": ("security", {"security", "cybersecurity"}),
    "oauth": ("security", {"oauth", "oauth2"}),
    "encryption": ("security", {"encryption"}),
    "pki": ("security", {"pki", "public key infrastructure"}),

    # Other technical / domain
    "rest": ("other", {"rest", "rest api", "restful"}),
    "graphql": ("other", {"graphql"}),
    "microservices": ("other", {"microservices", "microservices architecture"}),
    "agile": ("other", {"agile", "scrum"}),
    "fintech": ("other", {"fintech", "fintech industry"}),
    "e-commerce": ("other", {"e-commerce", "ecommerce", "e commerce"}),
}


def aliases_by_category() -> dict[str, set[str]]:
    """Return alias lookup organised by category for extraction."""
    result: dict[str, set[str]] = {}
    for label, (category, aliases) in SKILL_TAXONOMY.items():
        for alias in aliases:
            result.setdefault(category, set()).add(alias)
    return result


def all_aliases() -> set[str]:
    """Flatten every alias across the taxonomy."""
    out: set[str] = set()
    for _, (_, aliases) in SKILL_TAXONOMY.items():
        out.update(aliases)
    return out


def canonical_for_alias(alias: str) -> str | None:
    """Return the canonical label for a matched alias."""
    for label, (category, aliases) in SKILL_TAXONOMY.items():
        if alias in aliases:
            return label
    return None
