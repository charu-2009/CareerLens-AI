
"""
CareerLens AI — V2 Career Domain Router

Responsibilities
----------------
1. Normalize user skills conservatively.
2. Resolve only trusted explicit domain aliases.
3. Calculate domain routing evidence.
4. Assign routing confidence states.
5. Retain domains according to the frozen V2 routing policy.
6. Generate candidate careers from taxonomy domain membership.

This module DOES NOT:
- calculate readiness
- calculate skill gaps
- calculate market demand
- calculate growth
- calculate final recommendation scores

Domain routing is candidate-generation infrastructure only.
"""

from pathlib import Path
import json

from src.features.v2_skill_matcher import normalize_skill


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

REFERENCE = (
    PROJECT_ROOT
    / "data"
    / "reference"
)

DOMAIN_MAP_PATH = (
    REFERENCE
    / "domain_skill_map.json"
)

TAXONOMY_PATH = (
    REFERENCE
    / "career_taxonomy.json"
)

ROUTING_POLICY_PATH = (
    REFERENCE
    / "routing_policy_v2.json"
)


# ============================================================
# LOAD STATIC ARTIFACTS
# ============================================================

def _load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


_DOMAIN_MAP = _load_json(
    DOMAIN_MAP_PATH
)

_TAXONOMY = _load_json(
    TAXONOMY_PATH
)

_ROUTING_POLICY = _load_json(
    ROUTING_POLICY_PATH
)


# ============================================================
# TRUSTED EXPLICIT ALIASES
# ============================================================

_RAW_ALIASES = _DOMAIN_MAP.get(
    "aliases",
    {}
)

_ALIASES = {

    normalize_skill(alias):
        normalize_skill(canonical)

    for alias, canonical
    in _RAW_ALIASES.items()
}


def resolve_routing_skill(skill):
    """
    Conservative normalization + trusted explicit routing alias.
    """

    normalized = normalize_skill(
        skill
    )

    return _ALIASES.get(
        normalized,
        normalized
    )


# ============================================================
# DOMAIN INDEX
# ============================================================

def _parse_domain_links(value):

    links = []


    if isinstance(
        value,
        dict
    ):

        for domain, weight in value.items():

            try:

                links.append(
                    (
                        str(domain),
                        float(weight)
                    )
                )

            except Exception:

                pass


    elif isinstance(
        value,
        list
    ):

        for item in value:

            if not isinstance(
                item,
                dict
            ):

                continue


            domain = (
                item.get("domain")
                or
                item.get("name")
            )

            weight = (
                item.get("weight")
                or
                item.get("score")
            )


            if (
                domain is None
                or
                weight is None
            ):

                continue


            try:

                links.append(
                    (
                        str(domain),
                        float(weight)
                    )
                )

            except Exception:

                pass


    return links


def _build_domain_index():

    index = {}


    for raw_skill, mapping in (
        _DOMAIN_MAP.get(
            "skills",
            {}
        ).items()
    ):

        skill = resolve_routing_skill(
            raw_skill
        )

        links = _parse_domain_links(
            mapping
        )


        if not links:

            continue


        index.setdefault(
            skill,
            {}
        )


        for domain, weight in links:

            previous = (
                index[
                    skill
                ].get(
                    domain
                )
            )


            if (
                previous is None
                or
                weight > previous
            ):

                index[
                    skill
                ][
                    domain
                ] = weight


    return index


_DOMAIN_INDEX = _build_domain_index()


# ============================================================
# TAXONOMY NORMALIZATION
# ============================================================

def _build_taxonomy_records():

    records = []


    for record in _TAXONOMY.get(
        "careers",
        []
    ):

        career_name = (
            record.get(
                "career_name"
            )
            or
            record.get(
                "career"
            )
            or
            record.get(
                "name"
            )
            or
            record.get(
                "title"
            )
        )


        primary_domain = (
            record.get(
                "primary_domain"
            )
            or
            record.get(
                "domain"
            )
        )


        secondary_domains = (
            record.get(
                "secondary_domains"
            )
            or
            []
        )


        if isinstance(
            secondary_domains,
            str
        ):

            secondary_domains = [
                secondary_domains
            ]


        records.append(
            {
                "career_name":
                    career_name,

                "primary_domain":
                    primary_domain,

                "secondary_domains":
                    list(
                        secondary_domains
                    ),
            }
        )


    return records


_TAXONOMY_RECORDS = (
    _build_taxonomy_records()
)


# ============================================================
# CONFIDENCE STATE
# ============================================================

def routing_confidence_state(
    matched_skill_count
):

    if matched_skill_count <= 0:

        return "no_evidence"


    if matched_skill_count == 1:

        return "tentative"


    if matched_skill_count == 2:

        return "supported"


    return "strong"


# ============================================================
# DOMAIN EVIDENCE
# ============================================================

def detect_domain_evidence(
    user_skills
):
    """
    Return all domain evidence generated by the user's skills.

    routing_score is compatibility evidence only.
    """

    normalized_skills = []


    for raw_skill in (
        user_skills
        or
        []
    ):

        skill = resolve_routing_skill(
            raw_skill
        )


        if skill:

            normalized_skills.append(
                skill
            )


    normalized_skills = list(
        dict.fromkeys(
            normalized_skills
        )
    )


    known_skills = []
    unknown_skills = []

    scores = {}
    matched = {}
    weights = {}


    for skill in normalized_skills:

        mappings = (
            _DOMAIN_INDEX.get(
                skill
            )
        )


        if not mappings:

            unknown_skills.append(
                skill
            )

            continue


        known_skills.append(
            skill
        )


        for domain, weight in mappings.items():

            scores[
                domain
            ] = (
                scores.get(
                    domain,
                    0.0
                )
                +
                weight
            )


            matched.setdefault(
                domain,
                []
            )

            weights.setdefault(
                domain,
                []
            )


            matched[
                domain
            ].append(
                skill
            )

            weights[
                domain
            ].append(
                weight
            )


    domain_rows = []


    for domain, score in scores.items():

        matched_skills = list(
            dict.fromkeys(
                matched.get(
                    domain,
                    []
                )
            )
        )


        domain_weights = weights.get(
            domain,
            []
        )


        match_count = len(
            matched_skills
        )


        domain_rows.append(
            {
                "domain":
                    domain,

                "routing_score":
                    round(
                        float(score),
                        6
                    ),

                "matched_skill_count":
                    match_count,

                "matched_skills":
                    matched_skills,

                "strong_match_count":
                    sum(
                        weight >= 0.7
                        for weight
                        in domain_weights
                    ),

                "core_match_count":
                    sum(
                        weight >= 1.0
                        for weight
                        in domain_weights
                    ),

                "confidence_state":
                    routing_confidence_state(
                        match_count
                    ),
            }
        )


    domain_rows.sort(
        key=lambda row: (
            -row[
                "matched_skill_count"
            ],
            -row[
                "routing_score"
            ],
            -row[
                "core_match_count"
            ],
            -row[
                "strong_match_count"
            ],
            row[
                "domain"
            ].lower(),
        )
    )


    top_score = (
        max(
            (
                row[
                    "routing_score"
                ]
                for row
                in domain_rows
            ),
            default=0.0
        )
    )


    for row in domain_rows:

        row[
            "relative_to_top_score"
        ] = (
            round(
                row[
                    "routing_score"
                ]
                /
                top_score,
                6
            )
            if top_score > 0
            else
            0.0
        )


    return {
        "input_skill_count":
            len(
                normalized_skills
            ),

        "known_skill_count":
            len(
                known_skills
            ),

        "unknown_skill_count":
            len(
                unknown_skills
            ),

        "known_skills":
            known_skills,

        "unknown_skills":
            unknown_skills,

        "domains":
            domain_rows,
    }


# ============================================================
# FROZEN DOMAIN RETENTION POLICY
# ============================================================

def retain_candidate_domains(
    domain_rows
):
    """
    Frozen V2 routing retention policy.

    Strong:
        retain every strong domain.

    Supported-only:
        retain supported domain(s) sharing the highest
        routing score.

    Tentative:
        never generate careers.
    """

    strong = [
        row
        for row in domain_rows
        if row[
            "confidence_state"
        ]
        ==
        "strong"
    ]


    if strong:

        return list(
            strong
        )


    supported = [
        row
        for row in domain_rows
        if row[
            "confidence_state"
        ]
        ==
        "supported"
    ]


    if not supported:

        return []


    top_score = max(
        row[
            "routing_score"
        ]
        for row
        in supported
    )


    # Scores are generated from the frozen discrete
    # domain weights, but use a tiny numerical tolerance
    # rather than unsafe direct float equality.
    tolerance = 1e-12


    retained = [
        row
        for row in supported
        if abs(
            row[
                "routing_score"
            ]
            -
            top_score
        )
        <=
        tolerance
    ]


    return retained


# ============================================================
# CANDIDATE GENERATION
# ============================================================

def generate_candidate_careers(
    retained_domains
):
    """
    Generate candidate careers from retained domain membership.

    No career ranking is performed here.
    """

    if not retained_domains:

        return []


    domain_names = [
        row[
            "domain"
        ]
        for row
        in retained_domains
    ]


    domain_rank = {
        row[
            "domain"
        ]:
            index

        for index, row
        in enumerate(
            retained_domains
        )
    }


    domain_lookup = {
        row[
            "domain"
        ]:
            row

        for row
        in retained_domains
    }


    candidates = []


    for career in _TAXONOMY_RECORDS:

        primary_domain = career[
            "primary_domain"
        ]

        secondary_domains = career[
            "secondary_domains"
        ]


        matched_primary = (
            primary_domain
            in
            domain_names
        )


        matched_secondary = [
            domain
            for domain
            in secondary_domains
            if domain in domain_names
        ]


        if not (
            matched_primary
            or
            matched_secondary
        ):

            continue


        if matched_primary:

            matched_domain = (
                primary_domain
            )

            relation = (
                "primary_domain"
            )


        else:

            matched_domain = min(
                matched_secondary,
                key=lambda domain:
                    domain_rank[
                        domain
                    ]
            )

            relation = (
                "secondary_domain"
            )


        evidence = domain_lookup[
            matched_domain
        ]


        candidates.append(
            {
                "career_name":
                    career[
                        "career_name"
                    ],

                "primary_domain":
                    primary_domain,

                "matched_domain":
                    matched_domain,

                "routing_relation":
                    relation,

                "domain_confidence_state":
                    evidence[
                        "confidence_state"
                    ],

                "domain_matched_skill_count":
                    evidence[
                        "matched_skill_count"
                    ],

                "domain_routing_score":
                    evidence[
                        "routing_score"
                    ],

                "readiness_score":
                    None,

                "final_recommendation_score":
                    None,
            }
        )


    candidates.sort(
        key=lambda row: (
            -row[
                "domain_matched_skill_count"
            ],
            -row[
                "domain_routing_score"
            ],
            0
            if row[
                "routing_relation"
            ]
            ==
            "primary_domain"
            else
            1,
            row[
                "career_name"
            ].lower(),
        )
    )


    return candidates


# ============================================================
# PUBLIC ROUTER
# ============================================================

def route_careers_v2(
    user_skills
):
    """
    Main V2 routing entry point.

    Returns routing evidence + candidate career pool.

    This function does NOT perform final career ranking.
    """

    evidence = detect_domain_evidence(
        user_skills
    )


    retained_domains = (
        retain_candidate_domains(
            evidence[
                "domains"
            ]
        )
    )


    candidates = (
        generate_candidate_careers(
            retained_domains
        )
    )


    tentative_domains = [
        row
        for row in evidence[
            "domains"
        ]
        if row[
            "confidence_state"
        ]
        ==
        "tentative"
    ]


    if retained_domains:

        if any(
            row[
                "confidence_state"
            ]
            ==
            "strong"
            for row
            in retained_domains
        ):

            routing_state = (
                "strong_route"
            )

        else:

            routing_state = (
                "supported_route"
            )


    elif tentative_domains:

        routing_state = (
            "tentative_insufficient_for_careers"
        )


    else:

        routing_state = (
            "no_routing_evidence"
        )


    return {
        "routing_state":
            routing_state,

        "routing_only":
            True,

        "final_ranking_applied":
            False,

        "known_skills":
            evidence[
                "known_skills"
            ],

        "unknown_skills":
            evidence[
                "unknown_skills"
            ],

        "domain_evidence":
            evidence[
                "domains"
            ],

        "retained_domains":
            retained_domains,

        "tentative_domains":
            tentative_domains,

        "candidate_careers":
            candidates,

        "candidate_count":
            len(
                candidates
            ),
    }


def routing_policy():
    """
    Return a defensive copy of the frozen routing policy.
    """

    return json.loads(
        json.dumps(
            _ROUTING_POLICY
        )
    )


def taxonomy_career_count():

    return len(
        _TAXONOMY_RECORDS
    )


def routing_skill_count():

    return len(
        _DOMAIN_INDEX
    )
