# ============================================================
# CAREERLENS AI — PERSONALIZED SKILL GAP & LEARNING ENGINE
# ============================================================

import pandas as pd

from src.features.skill_utils import normalize_skill


# ============================================================
# 1. SKILL PRIORITY CLASSIFICATION
# ============================================================

def classify_skill_priority(
    role_profile_category,
    role_skill_score
):
    """
    Classify a missing skill using:
    1. Curated CareerLens role relevance
    2. Observed role-specific demand in the market dataset.
    """

    if role_profile_category == "core_skills":
        return "High Priority"

    if (
        role_profile_category == "tools_technologies"
        and role_skill_score is not None
        and role_skill_score >= 50
    ):
        return "High Priority"

    if role_profile_category == "tools_technologies":
        return "Medium Priority"

    if (
        role_profile_category == "advanced_skills"
        and role_skill_score is not None
        and role_skill_score >= 60
    ):
        return "Medium Priority"

    if role_profile_category == "market_observed":

        if (
            role_skill_score is not None
            and role_skill_score >= 70
        ):
            return "Specialized / Market Observed"

        return "Optional / Market Observed"

    return "Optional"


# ============================================================
# 2. ROLE PROFILE SKILL CATEGORIES
# ============================================================

def get_role_profile_skill_categories(
    job_role,
    role_skill_profiles
):
    """
    Return normalized curated skills and their category
    for a CareerLens role.
    """

    if job_role not in role_skill_profiles:
        return {}

    profile = role_skill_profiles[job_role]

    skill_categories = {}

    for category in [
        "core_skills",
        "tools_technologies",
        "advanced_skills"
    ]:

        for skill in profile.get(category, []):

            normalized_skill = normalize_skill(skill)

            skill_categories[
                normalized_skill
            ] = category

    return skill_categories


# ============================================================
# 3. PERSONALIZED SKILL GAP
# ============================================================

def build_personalized_skill_gap(
    user_skills,
    job_role,
    role_skill_profiles,
    role_skill_demand_30k
):
    """
    Build a personalized skill-gap profile using curated
    role requirements plus observed market skills.
    """

    normalized_user_skills = {
        normalize_skill(skill)
        for skill in user_skills
    }

    curated_skill_categories = (
        get_role_profile_skill_categories(
            job_role=job_role,
            role_skill_profiles=role_skill_profiles
        )
    )

    market_role_skills = (
        role_skill_demand_30k[
            role_skill_demand_30k["job_title"]
            == job_role
        ]
        .copy()
    )

    market_lookup = (
        market_role_skills
        .set_index("skill")
        .to_dict("index")
    )

    combined_skills = set(
        curated_skill_categories.keys()
    ).union(
        market_lookup.keys()
    )

    skill_gap_records = []

    for skill in combined_skills:

        matched = (
            skill in normalized_user_skills
        )

        role_profile_category = (
            curated_skill_categories.get(
                skill,
                "market_observed"
            )
        )

        market_data = market_lookup.get(
            skill,
            {}
        )

        role_skill_rank = market_data.get(
            "role_skill_rank"
        )

        job_mentions = market_data.get(
            "job_mentions"
        )

        role_skill_percentage = market_data.get(
            "role_skill_percentage"
        )

        role_skill_score = market_data.get(
            "role_skill_score"
        )

        priority = classify_skill_priority(
            role_profile_category,
            role_skill_score
        )

        skill_gap_records.append(
            {
                "job_role": job_role,
                "skill": skill,

                "status": (
                    "Matched"
                    if matched
                    else "Missing"
                ),

                "role_profile_category":
                    role_profile_category,

                "role_skill_rank":
                    role_skill_rank,

                "job_mentions":
                    job_mentions,

                "role_skill_percentage":
                    role_skill_percentage,

                "role_skill_score":
                    role_skill_score,

                "learning_priority":
                    priority,

                "market_data_available":
                    bool(market_data)
            }
        )

    result = pd.DataFrame(
        skill_gap_records
    )

    priority_order = {
        "High Priority": 1,
        "Medium Priority": 2,
        "Specialized / Market Observed": 3,
        "Optional": 4,
        "Optional / Market Observed": 5
    }

    result["_priority_order"] = (
        result["learning_priority"]
        .map(priority_order)
        .fillna(99)
    )

    result["_market_score_sort"] = (
        result["role_skill_score"]
        .fillna(-1)
    )

    result = (
        result
        .sort_values(
            [
                "status",
                "_priority_order",
                "_market_score_sort"
            ],
            ascending=[
                False,
                True,
                False
            ]
        )
        .drop(
            columns=[
                "_priority_order",
                "_market_score_sort"
            ]
        )
        .reset_index(drop=True)
    )

    return result


# ============================================================
# 4. LEARNING PRIORITY SCORE
# ============================================================

def calculate_learning_priority_score(
    skill_gap_df
):
    """
    Calculate learning priorities for missing skills.

    Curated role relevance is the primary signal.
    Market demand acts as supporting evidence.
    """

    missing = skill_gap_df[
        skill_gap_df["status"] == "Missing"
    ].copy()

    relevance_scores = {
        "core_skills": 100,
        "tools_technologies": 80,
        "advanced_skills": 60,
        "market_observed": 30
    }

    missing["role_relevance_score"] = (
        missing["role_profile_category"]
        .map(relevance_scores)
        .fillna(20)
    )

    missing["market_demand_score"] = (
        missing["role_skill_score"]
        .fillna(0)
    )

    missing["market_evidence_score"] = (
        missing.apply(
            lambda row:
                row["market_demand_score"]
                if row["market_data_available"]
                else 50,
            axis=1
        )
    )

    missing["learning_priority_score"] = (
        missing["role_relevance_score"] * 0.75
        +
        missing["market_evidence_score"] * 0.25
    ).round(2)

    def assign_learning_tier(score):

        if score >= 85:
            return "Learn First"

        elif score >= 70:
            return "High Priority"

        elif score >= 55:
            return "Medium Priority"

        elif score >= 40:
            return "Low Priority"

        return "Specialized / Optional"

    missing["learning_tier"] = (
        missing["learning_priority_score"]
        .apply(assign_learning_tier)
    )

    missing = (
        missing
        .sort_values(
            [
                "learning_priority_score",
                "role_skill_score"
            ],
            ascending=[
                False,
                False
            ]
        )
        .reset_index(drop=True)
    )

    missing["learning_rank"] = range(
        1,
        len(missing) + 1
    )

    return missing


# ============================================================
# 5. ALL-CAREER PERSONALIZED LEARNING
# ============================================================

def enrich_with_personalized_learning(
    recommendation_df,
    user_skills,
    role_skill_profiles,
    role_skill_demand_30k
):
    """
    Attach personalized skill gaps and learning priorities
    to every recommended CareerLens role.
    """

    enriched = recommendation_df.copy()

    skill_gap_profiles = []
    learning_profiles = []

    matched_skill_counts = []
    missing_skill_counts = []
    high_priority_gap_counts = []

    for _, row in enriched.iterrows():

        job_role = row["job_role"]

        skill_gap = (
            build_personalized_skill_gap(
                user_skills=user_skills,
                job_role=job_role,
                role_skill_profiles=role_skill_profiles,
                role_skill_demand_30k=role_skill_demand_30k
            )
        )

        learning_priority = (
            calculate_learning_priority_score(
                skill_gap
            )
        )

        matched_count = (
            skill_gap["status"]
            .eq("Matched")
            .sum()
        )

        missing_count = (
            skill_gap["status"]
            .eq("Missing")
            .sum()
        )

        high_priority_count = (
            learning_priority[
                "learning_tier"
            ]
            .isin(
                [
                    "Learn First",
                    "High Priority"
                ]
            )
            .sum()
        )

        skill_gap_profiles.append(
            skill_gap.to_dict(
                orient="records"
            )
        )

        learning_profiles.append(
            learning_priority.to_dict(
                orient="records"
            )
        )

        matched_skill_counts.append(
            int(matched_count)
        )

        missing_skill_counts.append(
            int(missing_count)
        )

        high_priority_gap_counts.append(
            int(high_priority_count)
        )

    enriched[
        "personalized_skill_gap"
    ] = skill_gap_profiles

    enriched[
        "learning_priorities"
    ] = learning_profiles

    enriched[
        "matched_market_skill_count"
    ] = matched_skill_counts

    enriched[
        "missing_market_skill_count"
    ] = missing_skill_counts

    enriched[
        "high_priority_gap_count"
    ] = high_priority_gap_counts

    return enriched