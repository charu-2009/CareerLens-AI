# ============================================================
# CAREERLENS AI — SKILL UTILITIES
# ============================================================


SKILL_ALIASES = {
    "ml": "machine learning",
    "machine learning": "machine learning",

    "nlp": "natural language processing",
    "natural language processing": "natural language processing",

    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",

    "k8s": "kubernetes",

    "scikit learn": "scikit-learn",
    "scikit learn python": "scikit-learn",
    "sklearn": "scikit-learn",

    "powerbi": "power bi",

    "ms excel": "excel",
    "microsoft excel": "excel",

    "tf": "tensorflow",
    "torch": "pytorch",

    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",

    "data viz": "data visualization"
}


def normalize_skill(skill):
    """
    Normalize a skill name into the canonical CareerLens format.
    """

    if skill is None:
        return ""

    normalized_skill = (
        str(skill)
        .strip()
        .lower()
    )

    return SKILL_ALIASES.get(
        normalized_skill,
        normalized_skill
    )


def normalize_skill_set(skills):
    """
    Normalize a collection of skills and return a unique set.
    """

    if skills is None:
        return set()

    return {
        normalize_skill(skill)
        for skill in skills
        if normalize_skill(skill)
    }