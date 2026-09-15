# ============================================================
# CAREERLENS AI — FINAL REPORT ENGINE
# ============================================================


def build_final_career_report(
    row,
    top_learning_n=5
):
    """
    Build one complete user-facing CareerLens report
    for a recommended career.
    """

    market_profile = row["market_profile"]
    explanation = row["career_explanation"]

    salary = market_profile.get("salary", {})
    experience = market_profile.get("experience", {})
    education = market_profile.get("education", {})
    remote = market_profile.get("remote", {})

    top_market_skills = market_profile.get(
        "top_market_skills",
        []
    )

    top_locations = market_profile.get(
        "top_company_locations",
        []
    )

    learning_priorities = row[
        "learning_priorities"
    ][:top_learning_n]


    report = {

        "career_rank":
            int(row["career_rank"]),

        "job_role":
            row["job_role"],

        "role_tier":
            row["role_tier"],

        "career_lens_score":
            round(
                float(row["final_careerlens_score"]),
                2
            ),

        "recommendation_category":
            row["recommendation_category"],


        "fit_scores": {

            "readiness_score":
                round(
                    float(row["readiness_score"]),
                    2
                ),

            "market_demand_score":
                round(
                    float(row["market_demand_score"]),
                    2
                ),

            "experience_score":
                round(
                    float(row["experience_score"]),
                    2
                ),

            "growth_score":
                round(
                    float(row["growth_score"]),
                    2
                )
        },


        "skill_summary": {

            "matched_profile_skills":
                row["matched_skills"],

            "missing_profile_skills":
                row["missing_skills"],

            "matched_market_skill_count":
                int(
                    row[
                        "matched_market_skill_count"
                    ]
                ),

            "missing_market_skill_count":
                int(
                    row[
                        "missing_market_skill_count"
                    ]
                ),

            "high_priority_gap_count":
                int(
                    row[
                        "high_priority_gap_count"
                    ]
                )
        },


        "learning_priorities": [

            {
                "rank":
                    int(item["learning_rank"]),

                "skill":
                    item["skill"],

                "priority_score":
                    round(
                        float(
                            item[
                                "learning_priority_score"
                            ]
                        ),
                        2
                    ),

                "learning_tier":
                    item["learning_tier"],

                "role_profile_category":
                    item[
                        "role_profile_category"
                    ]
            }

            for item in learning_priorities
        ],


        "growth_outlook": {

            "predicted_growth":
                row["predicted_growth"],

            "confidence_percent":
                round(
                    float(
                        row["growth_confidence"]
                    ),
                    2
                ),

            "confidence_level":
                row[
                    "growth_confidence_level"
                ],

            "experimental_model":
                True,

            "model_reliability_note":
                (
                    "Experimental signal only. "
                    "The growth model has low predictive "
                    "reliability and should not be interpreted "
                    "as a definitive future-market forecast."
                )
        },


        "salary_intelligence": {

            "median_salary_usd":
                salary.get(
                    "median_salary_usd"
                ),

            "average_salary_usd":
                salary.get(
                    "average_salary_usd"
                ),

            "salary_p25_usd":
                salary.get(
                    "salary_p25_usd"
                ),

            "salary_p75_usd":
                salary.get(
                    "salary_p75_usd"
                ),

            "salary_p90_usd":
                salary.get(
                    "salary_p90_usd"
                ),

            "salary_category":
                salary.get(
                    "salary_category"
                )
        },


        "experience_intelligence": {

            "median_experience_years":
                experience.get(
                    "median_experience_years"
                ),

            "average_experience_years":
                experience.get(
                    "average_experience_years"
                ),

            "entry_level_opportunity_percent":
                experience.get(
                    "entry_level_opportunity_percent"
                ),

            "zero_experience_opportunity_percent":
                experience.get(
                    "zero_experience_opportunity_percent"
                ),

            "experience_accessibility_score":
                experience.get(
                    "experience_accessibility_score"
                ),

            "experience_category":
                experience.get(
                    "experience_category"
                )
        },


        "education_intelligence": {

            "dominant_education":
                education.get(
                    "dominant_education"
                ),

            "bachelor_percent":
                education.get(
                    "bachelor_percent"
                ),

            "master_percent":
                education.get(
                    "master_percent"
                ),

            "phd_percent":
                education.get(
                    "phd_percent"
                ),

            "advanced_degree_percent":
                education.get(
                    "advanced_degree_percent"
                ),

            "education_category":
                education.get(
                    "education_category"
                )
        },


        "remote_intelligence": remote,

        "top_market_skills":
            top_market_skills,

        "top_company_locations":
            top_locations,

        "explanation":
            explanation
    }

    return report


def build_all_career_reports(
    career_df,
    top_learning_n=5
):
    """
    Build final user-facing reports for all CareerLens
    recommendations.
    """

    return [
        build_final_career_report(
            row,
            top_learning_n=top_learning_n
        )
        for _, row in career_df.iterrows()
    ]