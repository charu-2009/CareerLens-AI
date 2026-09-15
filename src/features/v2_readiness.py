
from pathlib import Path
import json

from src.features.v2_skill_matcher import (
    match_readiness_requirements,
    matched_skill_names,
    missing_skill_names,
)

from src.utils.profile_adapter import (
    get_runtime_profile,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

POLICY_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "readiness_policy_v2.json"
)


def _load_policy():

    with open(
        POLICY_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


READINESS_POLICY = _load_policy()

CORE_WEIGHT = float(
    READINESS_POLICY[
        "weights"
    ][
        "core"
    ]
)

IMPORTANT_WEIGHT = float(
    READINESS_POLICY[
        "weights"
    ][
        "important"
    ]
)


def _confidence_for_mode(
    readiness_mode
):

    confidence_policy = (
        READINESS_POLICY.get(
            "confidence_policy",
            {}
        )
    )

    entry = confidence_policy.get(
        readiness_mode,
        {}
    )

    return {
        "label":
            entry.get(
                "label",
                "unavailable"
            ),

        "message":
            entry.get(
                "message",
                ""
            ),
    }


def _empty_result(
    career_name,
    *,
    career_found,
    readiness_mode,
    reason,
):

    confidence = _confidence_for_mode(
        readiness_mode
    )

    return {

        "career_name":
            career_name,

        "career_found":
            bool(
                career_found
            ),

        "readiness_available":
            False,

        "readiness_mode":
            readiness_mode,

        "readiness_score":
            None,

        "matched_core_count":
            0,

        "total_core_count":
            0,

        "matched_important_count":
            0,

        "total_important_count":
            0,

        "matched_total":
            0,

        "requirement_total":
            0,

        "matched_core_skills":
            [],

        "missing_core_skills":
            [],

        "matched_important_skills":
            [],

        "missing_important_skills":
            [],

        "matched_skills":
            [],

        "missing_skills":
            [],

        "core_weight":
            CORE_WEIGHT,

        "important_weight":
            IMPORTANT_WEIGHT,

        "weighted_matched_points":
            0.0,

        "weighted_total_points":
            0.0,

        "confidence_label":
            confidence[
                "label"
            ],

        "confidence_message":
            confidence[
                "message"
            ],

        "limited_evidence":
            readiness_mode
            ==
            "limited_readiness_candidate",

        "reason":
            reason,
    }


def calculate_readiness(
    career_name,
    user_skills
):

    profile = get_runtime_profile(
        career_name
    )


    if not profile:

        return _empty_result(
            career_name,
            career_found=False,
            readiness_mode="unknown",
            reason="career_not_found",
        )


    readiness_mode = profile.get(
        "readiness_mode"
    )


    if readiness_mode not in {
        "full_readiness_candidate",
        "limited_readiness_candidate",
    }:

        return _empty_result(
            career_name,
            career_found=True,
            readiness_mode=readiness_mode,
            reason="readiness_not_available_for_mode",
        )


    match_result = (
        match_readiness_requirements(
            career_name,
            user_skills
        )
    )


    if not match_result.get(
        "readiness_available",
        False
    ):

        return _empty_result(
            career_name,
            career_found=True,
            readiness_mode=readiness_mode,
            reason="matcher_readiness_unavailable",
        )


    matched_core = (
        match_result.get(
            "matched_core",
            []
        )
    )

    missing_core = (
        match_result.get(
            "missing_core",
            []
        )
    )

    matched_important = (
        match_result.get(
            "matched_important",
            []
        )
    )

    missing_important = (
        match_result.get(
            "missing_important",
            []
        )
    )


    total_core = (
        len(
            matched_core
        )
        +
        len(
            missing_core
        )
    )

    total_important = (
        len(
            matched_important
        )
        +
        len(
            missing_important
        )
    )


    matched_core_count = len(
        matched_core
    )

    matched_important_count = len(
        matched_important
    )


    weighted_matched = (
        matched_core_count
        *
        CORE_WEIGHT
        +
        matched_important_count
        *
        IMPORTANT_WEIGHT
    )


    weighted_total = (
        total_core
        *
        CORE_WEIGHT
        +
        total_important
        *
        IMPORTANT_WEIGHT
    )


    if weighted_total <= 0:

        return _empty_result(
            career_name,
            career_found=True,
            readiness_mode=readiness_mode,
            reason="zero_readiness_requirements",
        )


    readiness_score = (
        weighted_matched
        /
        weighted_total
        *
        100.0
    )


    decimals = int(
        READINESS_POLICY[
            "rules"
        ].get(
            "score_rounding_decimals",
            2
        )
    )


    readiness_score = round(
        readiness_score,
        decimals
    )


    matched_core_names = [
        item.get(
            "concept"
        )
        for item in matched_core
        if item.get(
            "concept"
        )
    ]

    missing_core_names = [
        item.get(
            "concept"
        )
        for item in missing_core
        if item.get(
            "concept"
        )
    ]

    matched_important_names = [
        item.get(
            "concept"
        )
        for item in matched_important
        if item.get(
            "concept"
        )
    ]

    missing_important_names = [
        item.get(
            "concept"
        )
        for item in missing_important
        if item.get(
            "concept"
        )
    ]


    confidence = _confidence_for_mode(
        readiness_mode
    )


    return {

        "career_name":
            career_name,

        "career_found":
            True,

        "readiness_available":
            True,

        "readiness_mode":
            readiness_mode,

        "readiness_score":
            readiness_score,

        "matched_core_count":
            matched_core_count,

        "total_core_count":
            total_core,

        "matched_important_count":
            matched_important_count,

        "total_important_count":
            total_important,

        "matched_total":
            (
                matched_core_count
                +
                matched_important_count
            ),

        "requirement_total":
            (
                total_core
                +
                total_important
            ),

        "matched_core_skills":
            matched_core_names,

        "missing_core_skills":
            missing_core_names,

        "matched_important_skills":
            matched_important_names,

        "missing_important_skills":
            missing_important_names,

        "matched_skills":
            (
                matched_core_names
                +
                matched_important_names
            ),

        "missing_skills":
            (
                missing_core_names
                +
                missing_important_names
            ),

        "core_weight":
            CORE_WEIGHT,

        "important_weight":
            IMPORTANT_WEIGHT,

        "weighted_matched_points":
            round(
                weighted_matched,
                6
            ),

        "weighted_total_points":
            round(
                weighted_total,
                6
            ),

        "confidence_label":
            confidence[
                "label"
            ],

        "confidence_message":
            confidence[
                "message"
            ],

        "limited_evidence":
            readiness_mode
            ==
            "limited_readiness_candidate",

        "reason":
            "ok",
    }


def readiness_score(
    career_name,
    user_skills
):

    result = calculate_readiness(
        career_name,
        user_skills
    )

    return result[
        "readiness_score"
    ]
