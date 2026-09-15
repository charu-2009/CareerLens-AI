# ============================================================
# CAREERLENS AI — UNIFIED PRODUCTION PIPELINE
# ============================================================

import pandas as pd

from src.features.skill_utils import normalize_skill
from src.models.recommender import recommend_roles
from src.models.growth_model import predict_career_growth

from src.utils.market_intelligence import (
    enrich_career_recommendations
)

from src.utils.explanations import (
    generate_career_explanation
)

from src.utils.report_engine import (
    build_final_career_report
)


# ============================================================
# FINAL PRODUCTION WEIGHTS
# ============================================================

FINAL_CAREERLENS_WEIGHTS = {
    "readiness": 0.50,
    "market_demand": 0.25,
    "experience": 0.20,
    "growth": 0.05
}


# ============================================================
# FINAL SCORE
# ============================================================

def calculate_final_score(
    readiness_score,
    market_demand_score,
    experience_score,
    growth_score
):
    """
    Calculate final CareerLens score.

    Growth intentionally receives only 5% weight because
    the growth model is experimental / low reliability.
    """

    score = (
        float(readiness_score)
        * FINAL_CAREERLENS_WEIGHTS["readiness"]

        + float(market_demand_score)
        * FINAL_CAREERLENS_WEIGHTS["market_demand"]

        + float(experience_score)
        * FINAL_CAREERLENS_WEIGHTS["experience"]

        + float(growth_score)
        * FINAL_CAREERLENS_WEIGHTS["growth"]
    )

    return round(score, 2)


# ============================================================
# RECOMMENDATION CATEGORY
# ============================================================

def get_recommendation_category(score):

    score = float(score)

    if score >= 80:
        return "Excellent Match"

    if score >= 70:
        return "Strong Match"

    if score >= 60:
        return "Moderate Match"

    if score >= 50:
        return "Potential Match"

    return "Low Match"


# ============================================================
# UNIFIED CAREERLENS PIPELINE
# ============================================================

def run_career_lens(
    user_skills,
    user_experience,
    role_skill_profiles,
    role_market_lookup,
    growth_model,
    df_market,
    salary_lookup,
    experience_lookup,
    education_lookup,
    remote_lookup,
    role_skill_demand_30k,
    top_company_locations,
    personalized_learning_function,
    top_n=10
):
    """
    Run the complete production CareerLens backend.

    Pipeline:
        user profile
        -> base recommendation
        -> market demand
        -> experimental growth
        -> final score/ranking
        -> personalized learning
        -> market intelligence
        -> explanations
        -> final reports
    """

    # ========================================================
    # 1. NORMALIZE USER SKILLS
    # ========================================================

    normalized_skills = sorted({
        normalize_skill(skill)
        for skill in user_skills
        if str(skill).strip()
    })

    if not normalized_skills:
        raise ValueError(
            "At least one valid user skill is required."
        )

    user_experience = float(
        user_experience
    )


    # ========================================================
    # 2. BASE CAREER RECOMMENDATIONS
    # ========================================================

    recommendations = recommend_roles(
        user_skills=normalized_skills,
        user_years_experience=user_experience,
        profiles=role_skill_profiles,
        top_n=top_n
    ).copy()


    # ========================================================
    # 3. MARKET DEMAND
    # ========================================================

    recommendations[
        "market_demand_score"
    ] = (
        recommendations[
            "job_role"
        ]
        .map(role_market_lookup)
        .fillna(0)
        .astype(float)
    )


    # ========================================================
    # 4. EXPERIMENTAL GROWTH SIGNAL
    # ========================================================

    growth_records = []

    for _, row in recommendations.iterrows():

        result = predict_career_growth(
            model=growth_model,
            df_market=df_market,
            career_role=row["job_role"]
        )

        growth_records.append({

            "predicted_growth":
                result["predicted_growth"],

            "growth_confidence":
                result["confidence"],

            "growth_confidence_level":
                result["confidence_level"],

            "growth_score":
                result["growth_score"],

            "growth_class_probabilities":
                result["class_probabilities"],

            "growth_market_title":
                result["market_title"]
        })

    growth_df = pd.DataFrame(
        growth_records
    )

    recommendations = pd.concat(
        [
            recommendations.reset_index(
                drop=True
            ),
            growth_df.reset_index(
                drop=True
            )
        ],
        axis=1
    )


    # ========================================================
    # 5. FINAL CAREERLENS SCORE
    # ========================================================

    recommendations[
        "final_careerlens_score"
    ] = recommendations.apply(

        lambda row:
            calculate_final_score(

                readiness_score=
                    row["readiness_score"],

                market_demand_score=
                    row["market_demand_score"],

                experience_score=
                    row["experience_score"],

                growth_score=
                    row["growth_score"]
            ),

        axis=1
    )


    # ========================================================
    # 6. RECOMMENDATION CATEGORY
    # ========================================================

    recommendations[
        "recommendation_category"
    ] = recommendations[
        "final_careerlens_score"
    ].apply(
        get_recommendation_category
    )


    # ========================================================
    # 7. FINAL RANKING
    # ========================================================

    recommendations = (
        recommendations
        .sort_values(
            [
                "final_careerlens_score",
                "readiness_score",
                "market_demand_score"
            ],
            ascending=[
                False,
                False,
                False
            ]
        )
        .reset_index(
            drop=True
        )
    )

    recommendations[
        "career_rank"
    ] = (
        recommendations.index + 1
    )


    # ========================================================
    # 8. PERSONALIZED SKILL GAP + LEARNING
    # ========================================================

    recommendations = (
        personalized_learning_function(
            recommendation_df=
                recommendations,

            user_skills=
                normalized_skills
        )
    )


    # ========================================================
    # 9. MARKET INTELLIGENCE
    # ========================================================

    recommendations = (
        enrich_career_recommendations(

            recommendation_df=
                recommendations,

            salary_lookup=
                salary_lookup,

            experience_lookup=
                experience_lookup,

            education_lookup=
                education_lookup,

            remote_lookup=
                remote_lookup,

            role_skill_demand_30k=
                role_skill_demand_30k,

            top_company_locations=
                top_company_locations
        )
    )


    # ========================================================
    # 10. CAREER EXPLANATIONS
    # ========================================================

    recommendations[
        "career_explanation"
    ] = recommendations.apply(
        generate_career_explanation,
        axis=1
    )


    # ========================================================
    # 11. FINAL USER REPORTS
    # ========================================================

    reports = [

        build_final_career_report(
            row
        )

        for _, row
        in recommendations.iterrows()
    ]


    # ========================================================
    # 12. RETURN COMPLETE BACKEND RESULT
    # ========================================================

    return {

        "user_profile": {
            "skills":
                normalized_skills,

            "experience_years":
                user_experience
        },

        "top_role":
            recommendations.iloc[
                0
            ]["job_role"],

        "recommendations":
            recommendations,

        "reports":
            reports,

        "metadata": {

            "career_count":
                len(recommendations),

            "growth_model_experimental":
                True,

            "growth_model_weight":
                FINAL_CAREERLENS_WEIGHTS[
                    "growth"
                ],

            "scoring_weights":
                FINAL_CAREERLENS_WEIGHTS.copy()
        }
    }