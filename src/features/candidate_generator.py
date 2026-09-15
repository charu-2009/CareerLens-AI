# ============================================================
# CAREERLENS AI
# Career Candidate Generation Engine
# ============================================================

import json
from pathlib import Path

from src.features.domain_detector import (
    detect_career_domains
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CAREER_TAXONOMY_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "career_taxonomy.json"
)


# ============================================================
# LOAD CAREER TAXONOMY
# ============================================================

def load_career_taxonomy(path=None):

    if path is None:
        path = CAREER_TAXONOMY_PATH

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Career taxonomy not found: {path}"
        )

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "careers" not in data:
        raise ValueError(
            "Invalid career taxonomy: 'careers' missing."
        )

    return data


_TAXONOMY_DATA = load_career_taxonomy()

CAREERS = _TAXONOMY_DATA["careers"]


# ============================================================
# GENERATE CAREER CANDIDATES
# ============================================================

def generate_career_candidates(
    user_skills,
    top_domains=3,
    minimum_domain_score=25.0,
    include_secondary_domains=True,
    max_candidates=40
):

    """
    Generate career candidates using detected career domains.

    IMPORTANT:
    This function performs candidate generation only.

    It does NOT determine the final CareerLens ranking.
    """

    domain_result = detect_career_domains(
        user_skills=user_skills,
        top_n=None
    )

    detected_domains = []

    domain_score_lookup = {}


    # --------------------------------------------------------
    # SELECT RELEVANT DOMAINS
    # --------------------------------------------------------

    for item in domain_result["top_domains"]:

        if item["domain_score"] < minimum_domain_score:
            continue

        detected_domains.append(
            item["domain"]
        )

        domain_score_lookup[
            item["domain"]
        ] = item["domain_score"]

        if len(detected_domains) >= top_domains:
            break


    # --------------------------------------------------------
    # NO DOMAIN FOUND
    # --------------------------------------------------------

    if not detected_domains:

        return {

            "domain_detection":
                domain_result,

            "selected_domains":
                [],

            "candidate_count":
                0,

            "candidates":
                []
        }


    # --------------------------------------------------------
    # GENERATE CANDIDATES
    # --------------------------------------------------------

    candidates = []


    for career in CAREERS:

        primary_domain = career[
            "primary_domain"
        ]

        secondary_domains = career.get(
            "secondary_domains",
            []
        )


        matched_as_primary = (
            primary_domain
            in detected_domains
        )


        matched_secondary = [

            domain

            for domain in secondary_domains

            if domain in detected_domains
        ]


        if not matched_as_primary:

            if (
                not include_secondary_domains
                or not matched_secondary
            ):
                continue


        # ----------------------------------------------------
        # CANDIDATE DOMAIN SCORE
        # ----------------------------------------------------

        if matched_as_primary:

            candidate_domain_score = (
                domain_score_lookup[
                    primary_domain
                ]
            )

            match_type = "primary"

            matched_domain = primary_domain


        else:

            best_secondary_domain = max(
                matched_secondary,
                key=lambda domain:
                    domain_score_lookup[domain]
            )

            # Secondary-domain careers receive a small
            # candidate-generation penalty.
            candidate_domain_score = (
                domain_score_lookup[
                    best_secondary_domain
                ]
                * 0.75
            )

            match_type = "secondary"

            matched_domain = (
                best_secondary_domain
            )


        candidates.append(
            {

                "career_id":
                    career["career_id"],

                "career_name":
                    career["career_name"],

                "primary_domain":
                    primary_domain,

                "secondary_domains":
                    secondary_domains,

                "aliases":
                    career.get(
                        "aliases",
                        []
                    ),

                "legacy_careerlens_role":
                    career.get(
                        "legacy_careerlens_role",
                        False
                    ),

                "matched_domain":
                    matched_domain,

                "domain_match_type":
                    match_type,

                "candidate_domain_score":
                    round(
                        candidate_domain_score,
                        2
                    )
            }
        )


    # --------------------------------------------------------
    # SORT CANDIDATES
    # --------------------------------------------------------

    candidates = sorted(
        candidates,
        key=lambda item: (
            item[
                "candidate_domain_score"
            ],
            item[
                "domain_match_type"
            ] == "primary",
            item[
                "career_name"
            ]
        ),
        reverse=True
    )


    if max_candidates is not None:

        candidates = candidates[
            :max_candidates
        ]


    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    return {

        "domain_detection":
            domain_result,

        "selected_domains":
            detected_domains,

        "candidate_count":
            len(candidates),

        "candidates":
            candidates
    }