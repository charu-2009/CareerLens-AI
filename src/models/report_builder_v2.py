
"""
CareerLens AI V2 User-Facing Report Builder

Purpose
-------
Convert the stable V2 result-assembler payload into a
presentation-friendly report/view model.

This module does NOT:
- calculate new ranking scores
- re-rank careers
- remove backend careers
- convert routing evidence to fit scores
- promote market or growth signals into ranking
"""

from typing import Any, Dict, List

from src.models.result_assembler_v2 import (
    assemble_careerlens_result_v2
)


SECTION_ORDER = [
    "readiness_matches",
    "limited_readiness_matches",
    "validated_no_current_match",
    "related_careers",
    "discovery_only",
]


def _score_value(career: Dict[str, Any]):

    readiness = career.get(
        "readiness"
    ) or {}

    return readiness.get(
        "score"
    )


def _presentation_state(
    career: Dict[str, Any]
) -> str:

    lane = career.get(
        "lane"
    )

    score = _score_value(
        career
    )


    if lane == "full_readiness":

        if (
            score is not None
            and
            float(score) > 0
        ):

            return (
                "readiness_match"
            )

        return (
            "validated_no_current_match"
        )


    if lane == "limited_readiness":

        if (
            score is not None
            and
            float(score) > 0
        ):

            return (
                "limited_readiness_match"
            )

        return (
            "validated_no_current_match"
        )


    if lane == "routing_only":

        return (
            "related_career"
        )


    if lane == "safe_shell":

        return (
            "discovery_only"
        )


    return (
        "discovery_only"
    )


def _display_rank(
    career: Dict[str, Any],
    presentation_state: str
):

    if presentation_state in {
        "readiness_match",
        "limited_readiness_match",
    }:

        return career.get(
            "lane_rank"
        )


    return None


def _display_badge(
    presentation_state: str
) -> str:

    mapping = {

        "readiness_match":
            "Readiness Match",

        "limited_readiness_match":
            "Limited Evidence",

        "validated_no_current_match":
            "No Current Skill Match",

        "related_career":
            "Related Career",

        "discovery_only":
            "Explore",
    }

    return mapping.get(
        presentation_state,
        "Explore"
    )


def _display_note(
    career: Dict[str, Any],
    presentation_state: str
) -> str:

    readiness = (
        career.get(
            "readiness"
        )
        or
        {}
    )


    score = readiness.get(
        "score"
    )


    if presentation_state == "readiness_match":

        return (
            f"Readiness coverage: {score:.2f}%. "
            f"This reflects weighted matched requirements, "
            f"not hiring probability."
        )


    if presentation_state == "limited_readiness_match":

        return (
            f"Readiness coverage: {score:.2f}%, based on a "
            f"limited-evidence career profile."
        )


    if presentation_state == "validated_no_current_match":

        return (
            "CareerLens has validated readiness requirements for "
            "this career, but none of your entered skills currently "
            "match those requirements."
        )


    if presentation_state == "related_career":

        return (
            "Your skills connect with this career's domain, but "
            "CareerLens does not currently have enough validated "
            "career-specific evidence to calculate readiness."
        )


    return (
        "This career is available for exploration, but CareerLens "
        "does not currently have enough validated career-specific "
        "evidence for readiness scoring."
    )


def _build_card(
    career: Dict[str, Any]
) -> Dict[str, Any]:

    state = _presentation_state(
        career
    )


    return {

        "career_name":
            career.get(
                "career_name"
            ),

        "primary_domain":
            career.get(
                "primary_domain"
            ),

        "matched_domain":
            career.get(
                "matched_domain"
            ),

        "backend_lane":
            career.get(
                "lane"
            ),

        "presentation_state":
            state,

        "badge":
            _display_badge(
                state
            ),

        "display_rank":
            _display_rank(
                career,
                state
            ),

        "display_note":
            _display_note(
                career,
                state
            ),

        "readiness":
            career.get(
                "readiness"
            ),

        "skill_gap":
            career.get(
                "skill_gap"
            ),

        "routing":
            career.get(
                "routing"
            ),

        "market":
            career.get(
                "market"
            ),

        "growth":
            career.get(
                "growth"
            ),

        "ordering":
            career.get(
                "ordering"
            ),

        "explanation_disclaimer":
            career.get(
                "explanation_disclaimer"
            ),
    }


def build_careerlens_report_v2(
    user_skills
) -> Dict[str, Any]:
    """
    Build user-facing CareerLens V2 report/view model.

    Backend career order is preserved exactly.
    Presentation sections are classifications only.
    """

    result = assemble_careerlens_result_v2(
        user_skills
    )


    cards = [

        _build_card(
            career
        )

        for career
        in result[
            "careers"
        ]
    ]


    sections = {

        "readiness_matches": [],

        "limited_readiness_matches": [],

        "validated_no_current_match": [],

        "related_careers": [],

        "discovery_only": [],
    }


    for card in cards:

        state = card[
            "presentation_state"
        ]


        if state == "readiness_match":

            sections[
                "readiness_matches"
            ].append(
                card
            )


        elif state == "limited_readiness_match":

            sections[
                "limited_readiness_matches"
            ].append(
                card
            )


        elif state == "validated_no_current_match":

            sections[
                "validated_no_current_match"
            ].append(
                card
            )


        elif state == "related_career":

            sections[
                "related_careers"
            ].append(
                card
            )


        elif state == "discovery_only":

            sections[
                "discovery_only"
            ].append(
                card
            )


    section_metadata = {

        "readiness_matches":
            {
                "title":
                    "Readiness Matches",

                "description":
                    (
                        "Careers with fuller validated readiness "
                        "evidence and at least one matched requirement."
                    ),

                "count":
                    len(
                        sections[
                            "readiness_matches"
                        ]
                    ),
            },

        "limited_readiness_matches":
            {
                "title":
                    "Limited-Evidence Readiness Matches",

                "description":
                    (
                        "Careers with limited validated readiness "
                        "evidence and at least one matched requirement."
                    ),

                "count":
                    len(
                        sections[
                            "limited_readiness_matches"
                        ]
                    ),
            },

        "validated_no_current_match":
            {
                "title":
                    "Validated Profiles With No Current Skill Match",

                "description":
                    (
                        "CareerLens has readiness evidence for these "
                        "careers, but none of the entered skills match "
                        "their currently validated readiness requirements."
                    ),

                "count":
                    len(
                        sections[
                            "validated_no_current_match"
                        ]
                    ),
            },

        "related_careers":
            {
                "title":
                    "Related Careers",

                "description":
                    (
                        "Your skills connect with these career domains, "
                        "but career-specific readiness evidence is "
                        "currently insufficient."
                    ),

                "count":
                    len(
                        sections[
                            "related_careers"
                        ]
                    ),
            },

        "discovery_only":
            {
                "title":
                    "Explore More Careers",

                "description":
                    (
                        "Careers available for exploration where "
                        "validated career-specific readiness evidence "
                        "is currently unavailable."
                    ),

                "count":
                    len(
                        sections[
                            "discovery_only"
                        ]
                    ),
            },
    }


    presentation_summary = {

        "positive_readiness_matches":
            len(
                sections[
                    "readiness_matches"
                ]
            ),

        "limited_positive_matches":
            len(
                sections[
                    "limited_readiness_matches"
                ]
            ),

        "validated_zero_matches":
            len(
                sections[
                    "validated_no_current_match"
                ]
            ),

        "related_careers":
            len(
                sections[
                    "related_careers"
                ]
            ),

        "discovery_only":
            len(
                sections[
                    "discovery_only"
                ]
            ),

        "total_presented":
            len(
                cards
            ),
    }


    return {

        "status":
            result[
                "status"
            ],

        "routing_state":
            result[
                "routing_state"
            ],

        "known_skills":
            result[
                "known_skills"
            ],

        "unknown_skills":
            result[
                "unknown_skills"
            ],

        "retained_domains":
            result[
                "retained_domains"
            ],

        "candidate_count":
            result[
                "candidate_count"
            ],

        "backend_summary":
            result[
                "summary"
            ],

        "presentation_summary":
            presentation_summary,

        "section_metadata":
            section_metadata,

        "sections":
            sections,

        "cards":
            cards,

        "disclaimer":
            result[
                "disclaimer"
            ],
    }
