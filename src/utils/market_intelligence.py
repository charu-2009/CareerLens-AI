# ============================================================
# CAREERLENS AI — MARKET INTELLIGENCE UTILITIES
# ============================================================


def get_career_market_profile(
    job_role,
    salary_lookup,
    experience_lookup,
    education_lookup,
    remote_lookup,
    role_skill_demand_30k,
    top_company_locations
):
    """
    Build a unified descriptive market profile for a career.

    All market objects are passed explicitly so this module does
    not depend on notebook globals.
    """

    # --------------------------------------------------------
    # 1. Salary intelligence
    # --------------------------------------------------------

    salary_data = salary_lookup.get(
        job_role,
        {}
    )

    # --------------------------------------------------------
    # 2. Experience intelligence
    # --------------------------------------------------------

    experience_data = experience_lookup.get(
        job_role,
        {}
    )

    # --------------------------------------------------------
    # 3. Education intelligence
    # --------------------------------------------------------

    education_data = education_lookup.get(
        job_role,
        {}
    )

    # --------------------------------------------------------
    # 4. Remote intelligence
    # --------------------------------------------------------

    remote_data = remote_lookup.get(
        job_role,
        {}
    )

    # --------------------------------------------------------
    # 5. Skill intelligence
    # --------------------------------------------------------

    role_skills = (
        role_skill_demand_30k[
            role_skill_demand_30k[
                "job_title"
            ] == job_role
        ]
        .sort_values(
            "role_skill_rank"
        )
        .head(10)
    )

    top_skills = []

    for _, row in role_skills.iterrows():

        top_skills.append({
            "skill":
                row["skill"],

            "rank":
                int(
                    row[
                        "role_skill_rank"
                    ]
                ),

            "job_mentions":
                int(
                    row[
                        "job_mentions"
                    ]
                ),

            "job_percentage":
                float(
                    row[
                        "role_skill_percentage"
                    ]
                ),

            "role_skill_score":
                float(
                    row[
                        "role_skill_score"
                    ]
                )
        })

    # --------------------------------------------------------
    # 6. Top company locations
    # --------------------------------------------------------

    role_locations = (
        top_company_locations[
            top_company_locations[
                "job_title"
            ] == job_role
        ]
        .sort_values(
            [
                "location_rank",
                "job_count"
            ],
            ascending=[
                True,
                False
            ]
        )
        .head(5)
    )

    top_locations = []

    for _, row in role_locations.iterrows():

        top_locations.append({
            "location":
                row[
                    "company_location"
                ],

            "job_count":
                int(
                    row[
                        "job_count"
                    ]
                ),

            "rank":
                int(
                    row[
                        "location_rank"
                    ]
                )
        })

    # --------------------------------------------------------
    # 7. Build unified profile
    # --------------------------------------------------------

    profile = {

        "job_role":
            job_role,

        "salary": {

            "median_salary_usd":
                salary_data.get(
                    "median_salary_usd"
                ),

            "average_salary_usd":
                salary_data.get(
                    "average_salary_usd"
                ),

            "salary_p25_usd":
                salary_data.get(
                    "salary_p25_usd"
                ),

            "salary_p75_usd":
                salary_data.get(
                    "salary_p75_usd"
                ),

            "salary_p90_usd":
                salary_data.get(
                    "salary_p90_usd"
                ),

            "salary_category":
                salary_data.get(
                    "salary_category"
                )
        },

        "experience": {

            "median_experience_years":
                experience_data.get(
                    "median_experience_years"
                ),

            "average_experience_years":
                experience_data.get(
                    "average_experience_years"
                ),

            "entry_level_opportunity_percent":
                experience_data.get(
                    "entry_level_opportunity_percent"
                ),

            "zero_experience_opportunity_percent":
                experience_data.get(
                    "zero_experience_opportunity_percent"
                ),

            "experience_category":
                experience_data.get(
                    "experience_category"
                )
        },

        "education": {

            "dominant_education":
                education_data.get(
                    "dominant_education"
                ),

            "bachelor_percent":
                education_data.get(
                    "bachelor_percent"
                ),

            "master_percent":
                education_data.get(
                    "master_percent"
                ),

            "phd_percent":
                education_data.get(
                    "phd_percent"
                ),

            "bachelor_or_below_percent":
                education_data.get(
                    "bachelor_or_below_percent"
                ),

            "advanced_degree_percent":
                education_data.get(
                    "advanced_degree_percent"
                ),

            "education_category":
                education_data.get(
                    "education_category"
                )
        },

        "remote": {

            "on_site_percent":
                remote_data.get(
                    "on_site_percent"
                ),

            "hybrid_percent":
                remote_data.get(
                    "hybrid_percent"
                ),

            "remote_percent":
                remote_data.get(
                    "remote_percent"
                ),

            "average_remote_ratio":
                remote_data.get(
                    "average_remote_ratio"
                ),

            "remote_flexibility_category":
                remote_data.get(
                    "remote_flexibility_category"
                )
        },

        "top_market_skills":
            top_skills,

        "top_company_locations":
            top_locations
    }

    return profile


def enrich_career_recommendations(
    recommendation_df,
    salary_lookup,
    experience_lookup,
    education_lookup,
    remote_lookup,
    role_skill_demand_30k,
    top_company_locations
):
    """
    Attach the unified market profile to every recommended role.
    """

    enriched_df = recommendation_df.copy()

    enriched_df[
        "market_profile"
    ] = enriched_df[
        "job_role"
    ].apply(
        lambda job_role:
            get_career_market_profile(
                job_role=job_role,
                salary_lookup=salary_lookup,
                experience_lookup=experience_lookup,
                education_lookup=education_lookup,
                remote_lookup=remote_lookup,
                role_skill_demand_30k=role_skill_demand_30k,
                top_company_locations=top_company_locations
            )
    )

    return enriched_df