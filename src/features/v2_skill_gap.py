
from src.features.v2_readiness import (
    calculate_readiness,
    CORE_WEIGHT,
    IMPORTANT_WEIGHT,
)


def _priority_group(
    tier
):

    if tier == "core":
        return "core_priority"

    if tier == "important":
        return "important_priority"

    return "unavailable"


def _priority_level(
    tier
):

    if tier == "core":
        return "high"

    if tier == "important":
        return "standard"

    return "unavailable"


def calculate_skill_gap(
    career_name,
    user_skills
):

    readiness = calculate_readiness(
        career_name,
        user_skills
    )


    base_result = {

        "career_name":
            career_name,

        "career_found":
            readiness[
                "career_found"
            ],

        "readiness_available":
            readiness[
                "readiness_available"
            ],

        "readiness_mode":
            readiness[
                "readiness_mode"
            ],

        "readiness_score":
            readiness[
                "readiness_score"
            ],

        "confidence_label":
            readiness[
                "confidence_label"
            ],

        "confidence_message":
            readiness[
                "confidence_message"
            ],

        "limited_evidence":
            readiness[
                "limited_evidence"
            ],
    }


    if not readiness[
        "readiness_available"
    ]:

        return {

            **base_result,

            "gap_available":
                False,

            "missing_core_count":
                0,

            "missing_important_count":
                0,

            "missing_total":
                0,

            "learning_priorities":
                [],

            "within_tier_order_is_evidence_based":
                False,

            "ordering_policy":
                (
                    "Tier-level priority only; "
                    "no evidence-backed ordering within a tier."
                ),

            "reason":
                readiness[
                    "reason"
                ],
        }


    missing_core = list(
        readiness[
            "missing_core_skills"
        ]
    )

    missing_important = list(
        readiness[
            "missing_important_skills"
        ]
    )


    priorities = []


    # --------------------------------------------------------
    # Deterministic alphabetical ordering is retained ONLY
    # for stable output. It must not be interpreted as
    # pedagogical or evidence-backed ranking.
    # --------------------------------------------------------

    for skill in sorted(
        missing_core,
        key=lambda value: value.lower()
    ):

        priorities.append(
            {
                "skill":
                    skill,

                "requirement_tier":
                    "core",

                "priority_group":
                    "core_priority",

                "priority_level":
                    "high",

                "priority_weight":
                    CORE_WEIGHT,

                "within_tier_rank":
                    None,

                "within_tier_order_evidence":
                    "not_available",
            }
        )


    for skill in sorted(
        missing_important,
        key=lambda value: value.lower()
    ):

        priorities.append(
            {
                "skill":
                    skill,

                "requirement_tier":
                    "important",

                "priority_group":
                    "important_priority",

                "priority_level":
                    "standard",

                "priority_weight":
                    IMPORTANT_WEIGHT,

                "within_tier_rank":
                    None,

                "within_tier_order_evidence":
                    "not_available",
            }
        )


    return {

        **base_result,

        "gap_available":
            True,

        "missing_core_count":
            len(
                missing_core
            ),

        "missing_important_count":
            len(
                missing_important
            ),

        "missing_total":
            len(
                priorities
            ),

        "learning_priorities":
            priorities,

        "within_tier_order_is_evidence_based":
            False,

        "ordering_policy":
            (
                "Core requirements have higher priority than "
                "important requirements. Requirements within "
                "the same tier are not evidence-ranked."
            ),

        "reason":
            "ok",
    }


def top_learning_priorities(
    career_name,
    user_skills,
    limit=5
):

    result = calculate_skill_gap(
        career_name,
        user_skills
    )


    if not result[
        "gap_available"
    ]:

        return []


    if limit is None:

        return list(
            result[
                "learning_priorities"
            ]
        )


    limit = max(
        0,
        int(
            limit
        )
    )


    return result[
        "learning_priorities"
    ][
        :limit
    ]
