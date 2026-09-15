from pathlib import Path
import json

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

DATA_DIR = PROJECT_ROOT / "data"

PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
REFERENCE_DIR = DATA_DIR / "reference"


# ============================================================
# LOAD CORE 30K JOB DATA
# ============================================================

def load_core_jobs():

    path = (
        PROCESSED_DIR
        / "core_job_market_data.csv"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Core job dataset not found: {path}"
        )

    return pd.read_csv(path)


# ============================================================
# LOAD 500-ROW GROWTH DATASET
# ============================================================

def load_growth_market_data():

    path = (
        RAW_DIR
        / "ai_job_market_insights.csv"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Growth market dataset not found: {path}"
        )

    return pd.read_csv(path)


# ============================================================
# LOAD CURATED ROLE PROFILES
# ============================================================

def load_role_skill_profiles():

    path = (
        REFERENCE_DIR
        / "role_skill_profiles.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Role profile file not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        profiles = json.load(file)

    return profiles


# ============================================================
# LOAD ALL BASE DATA
# ============================================================

def load_base_data():

    return {
        "core_jobs":
            load_core_jobs(),

        "df_market":
            load_growth_market_data(),

        "role_skill_profiles":
            load_role_skill_profiles()
    }

# ============================================================
# BUILD MARKET DEMAND LOOKUP
# ============================================================

def build_role_market_lookup(core_jobs):
    """
    Build relative role-demand scores from job counts.
    Highest-demand role receives score 100.
    """

    role_counts = (
        core_jobs["job_title"]
        .value_counts()
    )

    max_count = role_counts.max()

    lookup = (
        role_counts
        .div(max_count)
        .mul(100)
        .round(2)
        .to_dict()
    )

    return lookup


# ============================================================
# BUILD SALARY LOOKUP
# ============================================================

def build_salary_lookup(core_jobs):

    salary_stats = (
        core_jobs
        .groupby("job_title")["salary_usd"]
        .agg(
            average_salary_usd="mean",
            median_salary_usd="median"
        )
        .reset_index()
    )

    percentiles = (
        core_jobs
        .groupby("job_title")["salary_usd"]
        .quantile(
            [0.25, 0.75, 0.90]
        )
        .unstack()
        .reset_index()
        .rename(
            columns={
                0.25: "salary_p25_usd",
                0.75: "salary_p75_usd",
                0.90: "salary_p90_usd"
            }
        )
    )

    salary_stats = salary_stats.merge(
        percentiles,
        on="job_title",
        how="left"
    )

    min_salary = (
        salary_stats[
            "median_salary_usd"
        ].min()
    )

    max_salary = (
        salary_stats[
            "median_salary_usd"
        ].max()
    )

    if max_salary == min_salary:

        salary_stats[
            "salary_score"
        ] = 50.0

    else:

        salary_stats[
            "salary_score"
        ] = (
            (
                salary_stats[
                    "median_salary_usd"
                ]
                - min_salary
            )
            /
            (
                max_salary
                - min_salary
            )
            * 100
        ).round(2)

    def salary_category(score):

        if score >= 75:
            return "Higher"

        if score >= 50:
            return "Upper-Middle"

        if score >= 25:
            return "Middle"

        return "Lower"

    salary_stats[
        "salary_category"
    ] = (
        salary_stats[
            "salary_score"
        ]
        .apply(
            salary_category
        )
    )

    return (
        salary_stats
        .set_index("job_title")
        .to_dict(
            orient="index"
        )
    )


# ============================================================
# BUILD EXPERIENCE LOOKUP
# ============================================================

def build_experience_lookup(core_jobs):

    stats = (
        core_jobs
        .groupby("job_title")[
            "years_experience"
        ]
        .agg(
            average_experience_years="mean",
            median_experience_years="median"
        )
        .reset_index()
    )

    entry_level = (
        core_jobs
        .assign(
            is_entry_level=
                core_jobs[
                    "years_experience"
                ].between(0, 2)
        )
        .groupby("job_title")[
            "is_entry_level"
        ]
        .mean()
        .mul(100)
        .reset_index(
            name=
                "entry_level_opportunity_percent"
        )
    )

    zero_experience = (
        core_jobs
        .assign(
            zero_exp=
                core_jobs[
                    "years_experience"
                ].eq(0)
        )
        .groupby("job_title")[
            "zero_exp"
        ]
        .mean()
        .mul(100)
        .reset_index(
            name=
                "zero_experience_opportunity_percent"
        )
    )

    stats = (
        stats
        .merge(
            entry_level,
            on="job_title",
            how="left"
        )
        .merge(
            zero_experience,
            on="job_title",
            how="left"
        )
    )

    def experience_category(years):

        if years <= 4:
            return "Early Career"

        if years <= 7:
            return "Mid Career"

        return "Experienced"

    stats[
        "experience_category"
    ] = (
        stats[
            "median_experience_years"
        ]
        .apply(
            experience_category
        )
    )

    return (
        stats
        .set_index("job_title")
        .to_dict(
            orient="index"
        )
    )


# ============================================================
# BUILD EDUCATION LOOKUP
# ============================================================

def build_education_lookup(core_jobs):

    education_counts = (
        core_jobs
        .groupby(
            [
                "job_title",
                "education_required"
            ]
        )
        .size()
        .unstack(
            fill_value=0
        )
    )

    education_percent = (
        education_counts
        .div(
            education_counts.sum(
                axis=1
            ),
            axis=0
        )
        .mul(100)
    )

    records = []

    for role in education_percent.index:

        row = (
            education_percent
            .loc[role]
        )

        associate = float(
            row.get(
                "Associate",
                0
            )
        )

        bachelor = float(
            row.get(
                "Bachelor",
                0
            )
        )

        master = float(
            row.get(
                "Master",
                0
            )
        )

        phd = float(
            row.get(
                "PhD",
                0
            )
        )

        dominant = (
            row.idxmax()
        )

        advanced = (
            master + phd
        )

        bachelor_or_below = (
            associate + bachelor
        )

        spread = (
            row.max()
            - row.min()
        )

        if spread <= 10:

            category = (
                "Mixed Education Requirements"
            )

        elif advanced >= 60:

            category = (
                "Advanced Degree Oriented"
            )

        elif bachelor_or_below >= 60:

            category = (
                "Bachelor / Entry Accessible"
            )

        else:

            category = (
                "Mixed Education Requirements"
            )

        records.append(
            {
                "job_title":
                    role,

                "dominant_education":
                    dominant,

                "associate_percent":
                    round(
                        associate,
                        2
                    ),

                "bachelor_percent":
                    round(
                        bachelor,
                        2
                    ),

                "master_percent":
                    round(
                        master,
                        2
                    ),

                "phd_percent":
                    round(
                        phd,
                        2
                    ),

                "advanced_degree_percent":
                    round(
                        advanced,
                        2
                    ),

                "bachelor_or_below_percent":
                    round(
                        bachelor_or_below,
                        2
                    ),

                "education_category":
                    category
            }
        )

    return (
        pd.DataFrame(
            records
        )
        .set_index(
            "job_title"
        )
        .to_dict(
            orient="index"
        )
    )
# ============================================================
# BUILD REMOTE LOOKUP
# ============================================================

def build_remote_lookup(core_jobs):

    working = core_jobs.copy()

    working["work_mode"] = (
        working["remote_ratio"]
        .map({
            0: "On-site",
            50: "Hybrid",
            100: "Remote"
        })
    )

    mode_pct = (
        working
        .groupby("job_title")["work_mode"]
        .value_counts(normalize=True)
        .mul(100)
        .unstack(fill_value=0)
    )

    avg_remote = (
        working
        .groupby("job_title")["remote_ratio"]
        .mean()
    )

    records = []

    for role in mode_pct.index:

        on_site = float(
            mode_pct.loc[role].get(
                "On-site",
                0
            )
        )

        hybrid = float(
            mode_pct.loc[role].get(
                "Hybrid",
                0
            )
        )

        remote = float(
            mode_pct.loc[role].get(
                "Remote",
                0
            )
        )

        average_ratio = float(
            avg_remote.loc[role]
        )

        if remote >= 50:
            category = "Remote Friendly"

        elif (
            hybrid + remote
        ) >= 60:
            category = "Flexible"

        else:
            category = "Mostly On-site"

        records.append({
            "job_title": role,

            "on_site_percent":
                round(on_site, 2),

            "hybrid_percent":
                round(hybrid, 2),

            "remote_percent":
                round(remote, 2),

            "average_remote_ratio":
                round(
                    average_ratio,
                    2
                ),

            "remote_flexibility_category":
                category
        })

    return (
        pd.DataFrame(records)
        .set_index("job_title")
        .to_dict(orient="index")
    )


# ============================================================
# BUILD TOP COMPANY LOCATIONS
# ============================================================

def build_top_company_locations(
    core_jobs,
    top_n=10
):

    location_counts = (
        core_jobs
        .groupby(
            [
                "job_title",
                "company_location"
            ]
        )
        .size()
        .reset_index(
            name="job_count"
        )
    )

    location_counts[
        "location_rank"
    ] = (
        location_counts
        .groupby("job_title")[
            "job_count"
        ]
        .rank(
            method="dense",
            ascending=False
        )
        .astype(int)
    )

    return (
        location_counts[
            location_counts[
                "location_rank"
            ] <= top_n
        ]
        .sort_values(
            [
                "job_title",
                "location_rank",
                "job_count",
                "company_location"
            ],
            ascending=[
                True,
                True,
                False,
                True
            ]
        )
        .reset_index(drop=True)
    )


# ============================================================
# BUILD 30K ROLE-SKILL DEMAND
# ============================================================

def build_role_skill_demand_30k(
    core_jobs,
    normalize_skill_function
):
    """
    Explode required_skills and calculate role-specific
    skill frequency, percentage, normalized score, and rank.
    """

    working = core_jobs[
        [
            "record_id",
            "job_title",
            "required_skills"
        ]
    ].copy()

    working[
        "required_skills"
    ] = (
        working[
            "required_skills"
        ]
        .fillna("")
        .astype(str)
    )

    working["skill"] = (
        working[
            "required_skills"
        ]
        .str.split(",")
    )

    working = (
        working
        .explode("skill")
        .reset_index(drop=True)
    )

    working["skill"] = (
        working["skill"]
        .apply(
            normalize_skill_function
        )
    )

    working = working[
        working["skill"] != ""
    ].copy()

    role_job_counts = (
        core_jobs["job_title"]
        .value_counts()
        .rename("role_job_count")
    )

    skill_counts = (
        working
        .groupby(
            [
                "job_title",
                "skill"
            ]
        )
        .size()
        .reset_index(
            name="job_mentions"
        )
    )

    skill_counts = (
        skill_counts
        .merge(
            role_job_counts,
            left_on="job_title",
            right_index=True,
            how="left"
        )
    )

    skill_counts[
        "role_skill_percentage"
    ] = (
        skill_counts[
            "job_mentions"
        ]
        /
        skill_counts[
            "role_job_count"
        ]
        * 100
    ).round(2)

    max_mentions = (
        skill_counts
        .groupby("job_title")[
            "job_mentions"
        ]
        .transform("max")
    )

    skill_counts[
        "role_skill_score"
    ] = (
        skill_counts[
            "job_mentions"
        ]
        /
        max_mentions
        * 100
    ).round(2)

    skill_counts[
        "role_skill_rank"
    ] = (
        skill_counts
        .groupby("job_title")[
            "job_mentions"
        ]
        .rank(
            method="dense",
            ascending=False
        )
        .astype(int)
    )

    return (
        skill_counts
        .sort_values(
            [
                "job_title",
                "role_skill_rank",
                "skill"
            ]
        )
        .reset_index(drop=True)
    )

# ============================================================
# BUILD COMPLETE CAREERLENS RUNTIME DATA
# ============================================================

def build_runtime_data(
    normalize_skill_function
):
    """
    Load all persisted CareerLens datasets and construct
    the lookup objects required by the production pipeline.
    """

    base = load_base_data()

    core_jobs = base["core_jobs"]
    df_market = base["df_market"]
    role_skill_profiles = (
        base["role_skill_profiles"]
    )

    role_market_lookup = (
        build_role_market_lookup(
            core_jobs
        )
    )

    salary_lookup = (
        build_salary_lookup(
            core_jobs
        )
    )

    experience_lookup = (
        build_experience_lookup(
            core_jobs
        )
    )

    education_lookup = (
        build_education_lookup(
            core_jobs
        )
    )

    remote_lookup = (
        build_remote_lookup(
            core_jobs
        )
    )

    top_company_locations = (
        build_top_company_locations(
            core_jobs
        )
    )

    role_skill_demand_30k = (
        build_role_skill_demand_30k(
            core_jobs=
                core_jobs,

            normalize_skill_function=
                normalize_skill_function
        )
    )

    return {
        "core_jobs":
            core_jobs,

        "df_market":
            df_market,

        "role_skill_profiles":
            role_skill_profiles,

        "role_market_lookup":
            role_market_lookup,

        "salary_lookup":
            salary_lookup,

        "experience_lookup":
            experience_lookup,

        "education_lookup":
            education_lookup,

        "remote_lookup":
            remote_lookup,

        "top_company_locations":
            top_company_locations,

        "role_skill_demand_30k":
            role_skill_demand_30k
    }