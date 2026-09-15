
"""
CareerLens AI V2 Result Assembler

Purpose
-------
Combine the frozen recommendation and explanation layers into
a single stable user-facing backend payload.

This module does NOT:
- calculate new scores
- alter ranking
- create a universal final score
- modify recommender output
- modify explanation output
"""

from typing import Any, Dict, List

from src.models.recommender_v2 import recommend_careers_v2
from src.utils.explanations_v2 import explain_recommendations_v2


LANE_ORDER = [
    "full_readiness",
    "limited_readiness",
    "routing_only",
    "safe_shell",
]


def _build_career_payload(
    row: Dict[str, Any],
    explanation: Dict[str, Any]
) -> Dict[str, Any]:

    return {

        "career_name":
            row.get(
                "career_name"
            ),

        "primary_domain":
            row.get(
                "primary_domain"
            ),

        "matched_domain":
            row.get(
                "matched_domain"
            ),

        "lane":
            row.get(
                "lane"
            ),

        "presentation_role":
            row.get(
                "presentation_role"
            ),

        "lane_rank":
            row.get(
                "lane_rank"
            ),

        "readiness":
            explanation.get(
                "readiness"
            ),

        "skill_gap":
            explanation.get(
                "skill_gap"
            ),

        "routing":
            explanation.get(
                "routing"
            ),

        "market":
            explanation.get(
                "market"
            ),

        "growth":
            explanation.get(
                "growth"
            ),

        "ordering":
            explanation.get(
                "ordering"
            ),

        "explanation_disclaimer":
            explanation.get(
                "disclaimer"
            ),
    }


def assemble_careerlens_result_v2(
    user_skills
) -> Dict[str, Any]:
    """
    Build complete CareerLens V2 result payload.
    """

    recommendation_result = recommend_careers_v2(
        user_skills
    )


    recommendations = recommendation_result[
        "recommendations"
    ]


    explanations = explain_recommendations_v2(
        recommendations
    )


    careers = []


    if len(
        recommendations
    ) > 0:

        records = recommendations.to_dict(
            orient="records"
        )


        for row, explanation in zip(
            records,
            explanations
        ):

            careers.append(
                _build_career_payload(
                    row,
                    explanation
                )
            )


    career_groups = {

        lane:
            []

        for lane
        in LANE_ORDER
    }


    for career in careers:

        lane = career.get(
            "lane"
        )


        if lane in career_groups:

            career_groups[
                lane
            ].append(
                career
            )


    full_count = len(
        career_groups[
            "full_readiness"
        ]
    )

    limited_count = len(
        career_groups[
            "limited_readiness"
        ]
    )

    routing_count = len(
        career_groups[
            "routing_only"
        ]
    )

    safe_count = len(
        career_groups[
            "safe_shell"
        ]
    )


    market_supported_count = sum(

        1

        for career
        in careers

        if bool(
            career[
                "market"
            ].get(
                "available",
                False
            )
        )
    )


    growth_supported_count = sum(

        1

        for career
        in careers

        if bool(
            career[
                "growth"
            ].get(
                "available",
                False
            )
        )
    )


    summary = {

        "total_candidates":
            len(
                careers
            ),

        "full_readiness_count":
            full_count,

        "limited_readiness_count":
            limited_count,

        "routing_only_count":
            routing_count,

        "safe_shell_count":
            safe_count,

        "readiness_scored_count":
            full_count
            +
            limited_count,

        "market_supported_count":
            market_supported_count,

        "growth_supported_count":
            growth_supported_count,
    }


    if len(
        careers
    ) == 0:

        status = (
            recommendation_result.get(
                "routing_state",
                "no_routing_evidence"
            )
        )

    else:

        status = (
            "recommendations_available"
        )


    return {

        "status":
            status,

        "routing_state":
            recommendation_result.get(
                "routing_state"
            ),

        "known_skills":
            recommendation_result.get(
                "known_skills",
                []
            ),

        "unknown_skills":
            recommendation_result.get(
                "unknown_skills",
                []
            ),

        "retained_domains":
            recommendation_result.get(
                "retained_domains",
                []
            ),

        "candidate_count":
            recommendation_result.get(
                "candidate_count",
                0
            ),

        "summary":
            summary,

        "career_groups":
            career_groups,

        "careers":
            careers,

        "disclaimer":
            (
                "CareerLens uses validated career-profile evidence and "
                "supported descriptive market signals. Readiness percentages "
                "measure weighted requirement coverage, not hiring probability. "
                "Market and growth evidence do not affect career ranking."
            ),
    }
