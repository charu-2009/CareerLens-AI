# ============================================================
# CAREERLENS AI — BASE CAREER RECOMMENDER
# ============================================================

import pandas as pd

from src.features.skill_utils import normalize_skill


# ============================================================
# ROLE SENIORITY CONFIGURATION
# ============================================================

ROLE_SENIORITY = {
    "Data Analyst": {
        "tier": "Entry",
        "min_years": 0
    },

    "Data Scientist": {
        "tier": "Mid",
        "min_years": 2
    },

    "Data Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "Machine Learning Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "ML Ops Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "AI Specialist": {
        "tier": "Entry",
        "min_years": 0
    },

    "AI Consultant": {
        "tier": "Mid",
        "min_years": 2
    },

    "AI Software Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "Computer Vision Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "NLP Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "Deep Learning Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "Autonomous Systems Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "Robotics Engineer": {
        "tier": "Mid",
        "min_years": 2
    },

    "Machine Learning Researcher": {
        "tier": "Mid",
        "min_years": 2
    },

    "Research Scientist": {
        "tier": "Mid",
        "min_years": 2
    },

    "AI Research Scientist": {
        "tier": "Senior",
        "min_years": 5
    },

    "Principal Data Scientist": {
        "tier": "Senior",
        "min_years": 6
    },

    "AI Architect": {
        "tier": "Senior",
        "min_years": 6
    },

    "AI Product Manager": {
        "tier": "Senior",
        "min_years": 5
    },

    "Head of AI": {
        "tier": "Leadership",
        "min_years": 8
    }
}


# ============================================================
# SKILL-GAP ANALYSIS
# ============================================================

def analyze_skill_gap(
    target_role,
    user_skills,
    profiles
):
    """
    Compare user skills against a curated CareerLens
    role profile and calculate weighted readiness.
    """

    if target_role not in profiles:
        raise ValueError(
            f"Role '{target_role}' is not available."
        )

    profile = profiles[target_role]

    user_skills_normalized = {
        normalize_skill(skill)
        for skill in user_skills
    }

    category_weights = {
        "core_skills": 3,
        "tools_technologies": 2,
        "advanced_skills": 1
    }

    matched_skills = []
    missing_skills = []

    total_weight = 0
    matched_weight = 0

    for category, skills in profile.items():

        weight = category_weights[category]

        for skill in skills:

            normalized_skill = normalize_skill(
                skill
            )

            total_weight += weight

            skill_info = {
                "skill": skill,
                "category": category,
                "weight": weight
            }

            if (
                normalized_skill
                in user_skills_normalized
            ):
                matched_skills.append(
                    skill_info
                )

                matched_weight += weight

            else:
                missing_skills.append(
                    skill_info
                )

    readiness_score = (
        matched_weight
        / total_weight
        * 100
        if total_weight > 0
        else 0
    )

    skill_gap_percentage = (
        100 - readiness_score
    )

    return {
        "target_role":
            target_role,

        "user_skills":
            sorted(
                user_skills_normalized
            ),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "readiness_score":
            round(
                readiness_score,
                2
            ),

        "skill_gap_percentage":
            round(
                skill_gap_percentage,
                2
            )
    }


# ============================================================
# EXPERIENCE SUITABILITY
# ============================================================

def calculate_experience_suitability(
    user_years_experience,
    role_min_years
):
    """
    Calculate compatibility between the user's years of
    experience and the role's minimum experience level.
    """

    if (
        user_years_experience
        >= role_min_years
    ):
        return 100.0

    experience_gap = (
        role_min_years
        - user_years_experience
    )

    suitability = (
        100
        - experience_gap * 15
    )

    return max(
        0,
        suitability
    )


# ============================================================
# BASE ROLE RECOMMENDER
# ============================================================

def recommend_roles(
    user_skills,
    user_years_experience,
    profiles,
    seniority_mapping=None,
    top_n=10
):
    """
    Generate base CareerLens recommendations using
    weighted skill readiness and experience suitability.
    """

    if seniority_mapping is None:
        seniority_mapping = ROLE_SENIORITY

    role_recommendations = []

    for role in profiles.keys():

        analysis = analyze_skill_gap(
            target_role=role,
            user_skills=user_skills,
            profiles=profiles
        )

        readiness_score = (
            analysis["readiness_score"]
        )

        role_min_years = (
            seniority_mapping[
                role
            ]["min_years"]
        )

        role_tier = (
            seniority_mapping[
                role
            ]["tier"]
        )

        experience_score = (
            calculate_experience_suitability(
                user_years_experience=
                    user_years_experience,

                role_min_years=
                    role_min_years
            )
        )

        final_score = (
            0.80 * readiness_score
            + 0.20 * experience_score
        )

        experience_gap = max(
            0,
            role_min_years
            - user_years_experience
        )

        role_recommendations.append(
            {
                "job_role":
                    role,

                "role_tier":
                    role_tier,

                "readiness_score":
                    round(
                        readiness_score,
                        2
                    ),

                "experience_score":
                    round(
                        experience_score,
                        2
                    ),

                "experience_gap_years":
                    experience_gap,

                "final_recommendation_score":
                    round(
                        final_score,
                        2
                    ),

                "matched_skills":
                    len(
                        analysis[
                            "matched_skills"
                        ]
                    ),

                "missing_skills":
                    len(
                        analysis[
                            "missing_skills"
                        ]
                    )
            }
        )

    recommendations_df = pd.DataFrame(
        role_recommendations
    )

    recommendations_df = (
        recommendations_df
        .sort_values(
            by=[
                "final_recommendation_score",
                "readiness_score"
            ],
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    return recommendations_df.head(
        top_n
    )