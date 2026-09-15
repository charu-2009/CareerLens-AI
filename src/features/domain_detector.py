# ============================================================
# CAREERLENS AI
# Career Domain Detection Engine
# ============================================================

import json
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOMAIN_SKILL_MAP_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "domain_skill_map.json"
)


# ============================================================
# LOAD DOMAIN SKILL KNOWLEDGE BASE
# ============================================================

def load_domain_skill_map(path=None):

    if path is None:
        path = DOMAIN_SKILL_MAP_PATH

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Domain skill map not found: {path}"
        )

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    required_keys = {
        "schema_version",
        "aliases",
        "skills"
    }

    missing_keys = required_keys - set(data.keys())

    if missing_keys:
        raise ValueError(
            f"Invalid domain skill map. "
            f"Missing keys: {sorted(missing_keys)}"
        )

    return data


# Load once when module is imported
_DOMAIN_DATA = load_domain_skill_map()

SKILL_DOMAIN_MAP = _DOMAIN_DATA["skills"]
DOMAIN_SKILL_ALIASES = _DOMAIN_DATA["aliases"]


# ============================================================
# NORMALIZE DOMAIN SKILL
# ============================================================

def normalize_domain_skill(skill):

    if skill is None:
        return ""

    normalized = str(skill).strip().lower()

    normalized = DOMAIN_SKILL_ALIASES.get(
        normalized,
        normalized
    )

    return normalized


# ============================================================
# NORMALIZE USER SKILLS
# ============================================================

def normalize_user_skills(user_skills):

    normalized_skills = []

    seen = set()

    for skill in user_skills:

        normalized = normalize_domain_skill(skill)

        if not normalized:
            continue

        if normalized not in seen:

            seen.add(normalized)

            normalized_skills.append(normalized)

    return normalized_skills


# ============================================================
# DETECT CAREER DOMAINS
# ============================================================

def detect_career_domains(
    user_skills,
    top_n=5,
    minimum_raw_score=0.0
):

    """
    Detect likely career domains from a user's skills.

    Important:
    domain_score is a relative compatibility score.
    It is NOT a probability.

    The strongest detected domain receives 100.
    Other domains are scaled relative to it.
    """

    if user_skills is None:
        user_skills = []

    normalized_skills = normalize_user_skills(
        user_skills
    )

    domain_scores = {}

    matched_skills = {}

    recognized_skills = []

    unknown_skills = []


    # --------------------------------------------------------
    # SCORE EACH SKILL
    # --------------------------------------------------------

    for skill in normalized_skills:

        domain_weights = SKILL_DOMAIN_MAP.get(skill)

        if not domain_weights:

            unknown_skills.append(skill)

            continue


        recognized_skills.append(skill)


        for domain, weight in domain_weights.items():

            domain_scores[domain] = (
                domain_scores.get(domain, 0.0)
                + float(weight)
            )

            matched_skills.setdefault(
                domain,
                []
            )

            matched_skills[domain].append(
                {
                    "skill": skill,
                    "weight": float(weight)
                }
            )


    # --------------------------------------------------------
    # NO DOMAIN SIGNAL
    # --------------------------------------------------------

    if not domain_scores:

        return {

            "input_skills":
                list(user_skills),

            "normalized_skills":
                normalized_skills,

            "recognized_skills":
                recognized_skills,

            "unknown_skills":
                unknown_skills,

            "skill_coverage_percent":
                0.0,

            "top_domains":
                [],

            "primary_domain":
                None,

            "primary_domain_score":
                0.0
        }


    # --------------------------------------------------------
    # RELATIVE DOMAIN SCORING
    # --------------------------------------------------------

    max_raw_score = max(
        domain_scores.values()
    )

    results = []


    for domain, raw_score in domain_scores.items():

        if raw_score < minimum_raw_score:
            continue


        relative_score = (
            raw_score / max_raw_score
        ) * 100


        domain_matches = matched_skills.get(
            domain,
            []
        )


        results.append(
            {

                "domain":
                    domain,

                "raw_score":
                    round(raw_score, 2),

                "domain_score":
                    round(relative_score, 2),

                "matched_skill_count":
                    len(domain_matches),

                "matched_skills":
                    domain_matches
            }
        )


    # --------------------------------------------------------
    # SORT DOMAINS
    # --------------------------------------------------------

    results = sorted(
        results,
        key=lambda item: (
            item["raw_score"],
            item["matched_skill_count"]
        ),
        reverse=True
    )


    if top_n is not None:
        results = results[:top_n]


    # --------------------------------------------------------
    # SKILL COVERAGE
    # --------------------------------------------------------

    total_skill_count = len(
        normalized_skills
    )

    recognized_count = len(
        recognized_skills
    )


    if total_skill_count > 0:

        skill_coverage = (
            recognized_count
            / total_skill_count
        ) * 100

    else:

        skill_coverage = 0.0


    # --------------------------------------------------------
    # PRIMARY DOMAIN
    # --------------------------------------------------------

    if results:

        primary_domain = results[0]["domain"]

        primary_domain_score = (
            results[0]["domain_score"]
        )

    else:

        primary_domain = None
        primary_domain_score = 0.0


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "input_skills":
            list(user_skills),

        "normalized_skills":
            normalized_skills,

        "recognized_skills":
            recognized_skills,

        "unknown_skills":
            unknown_skills,

        "skill_coverage_percent":
            round(skill_coverage, 2),

        "top_domains":
            results,

        "primary_domain":
            primary_domain,

        "primary_domain_score":
            primary_domain_score
    }


# ============================================================
# GET RELEVANT DOMAIN NAMES
# ============================================================

def get_relevant_domains(
    user_skills,
    top_n=3,
    minimum_domain_score=25.0
):

    result = detect_career_domains(
        user_skills=user_skills,
        top_n=None
    )

    relevant_domains = []

    for domain in result["top_domains"]:

        if (
            domain["domain_score"]
            >= minimum_domain_score
        ):

            relevant_domains.append(
                domain["domain"]
            )


    return relevant_domains[:top_n]