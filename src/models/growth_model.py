# ============================================================
# CAREERLENS AI — EXPERIMENTAL JOB GROWTH MODEL
# ============================================================

from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# MODEL CONFIGURATION
# ============================================================

FEATURE_COLUMNS = [
    "Job_Title",
    "Industry",
    "Company_Size",
    "Location",
    "AI_Adoption_Level",
    "Automation_Risk",
    "Required_Skills",
    "Salary_USD",
    "Remote_Friendly"
]


ROLE_TO_MARKET_TITLE = {
    "AI Architect": "AI Researcher",
    "AI Consultant": "AI Researcher",
    "AI Product Manager": "Product Manager",
    "AI Research Scientist": "AI Researcher",
    "AI Software Engineer": "Software Engineer",
    "AI Specialist": "AI Researcher",
    "Autonomous Systems Engineer": "Software Engineer",
    "Computer Vision Engineer": "AI Researcher",
    "Data Analyst": "Data Scientist",
    "Data Engineer": "Data Scientist",
    "Data Scientist": "Data Scientist",
    "Deep Learning Engineer": "AI Researcher",
    "Head of AI": "AI Researcher",
    "ML Ops Engineer": "Software Engineer",
    "Machine Learning Engineer": "AI Researcher",
    "Machine Learning Researcher": "AI Researcher",
    "NLP Engineer": "AI Researcher",
    "Principal Data Scientist": "Data Scientist",
    "Research Scientist": "AI Researcher",
    "Robotics Engineer": "Software Engineer"
}


# ============================================================
# MODEL LOADING
# ============================================================

def load_growth_model(
    model_path=None
):
    """
    Load the saved CareerLens Random Forest growth pipeline.
    """

    if model_path is None:

        project_root = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

        model_path = (
            project_root
            / "models"
            / "career_lens_job_growth_random_forest.joblib"
        )

    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Growth model not found: {model_path}"
        )

    return joblib.load(
        model_path
    )


# ============================================================
# CONFIDENCE LEVEL
# ============================================================

def get_confidence_level(
    confidence_percent
):
    """
    Convert model confidence into a readable category.
    """

    if confidence_percent >= 70:
        return "High"

    elif confidence_percent >= 50:
        return "Medium"

    return "Low"


# ============================================================
# GROWTH SCORE
# ============================================================

def calculate_growth_score(
    class_probabilities
):
    """
    Convert class probabilities into a softer growth score.

    Growth  = 100
    Stable  = 70
    Decline = 40
    """

    growth = class_probabilities.get(
        "Growth",
        0
    )

    stable = class_probabilities.get(
        "Stable",
        0
    )

    decline = class_probabilities.get(
        "Decline",
        0
    )

    growth_score = (
        growth * 1.0
        + stable * 0.7
        + decline * 0.4
    )

    return round(
        growth_score,
        2
    )


# ============================================================
# DETAILED GROWTH PREDICTION
# ============================================================

def predict_job_growth(
    model,
    job_title,
    industry,
    company_size,
    location,
    ai_adoption_level,
    automation_risk,
    required_skills,
    salary_usd,
    remote_friendly
):
    """
    Predict experimental job-growth outlook using the saved
    Random Forest pipeline.

    This model is intentionally treated as a weak supporting
    signal, not as a definitive future-market forecast.
    """

    input_data = pd.DataFrame(
        [
            {
                "Job_Title":
                    job_title,

                "Industry":
                    industry,

                "Company_Size":
                    company_size,

                "Location":
                    location,

                "AI_Adoption_Level":
                    ai_adoption_level,

                "Automation_Risk":
                    automation_risk,

                "Required_Skills":
                    required_skills,

                "Salary_USD":
                    float(salary_usd),

                "Remote_Friendly":
                    remote_friendly
            }
        ]
    )

    input_data = input_data[
        FEATURE_COLUMNS
    ]

    prediction = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    classes = model.classes_

    probability_scores = {
        class_name:
            round(
                float(probability) * 100,
                2
            )

        for class_name, probability
        in zip(
            classes,
            probabilities
        )
    }

    confidence = round(
        max(probabilities) * 100,
        2
    )

    confidence_level = (
        get_confidence_level(
            confidence
        )
    )

    growth_score = (
        calculate_growth_score(
            probability_scores
        )
    )

    return {
        "predicted_growth":
            prediction,

        "confidence":
            confidence,

        "confidence_level":
            confidence_level,

        "class_probabilities":
            probability_scores,

        "growth_score":
            growth_score
    }


# ============================================================
# ROLE MAPPING
# ============================================================

def get_market_title(
    career_role
):
    """
    Map a CareerLens role to the closest title used by the
    500-row experimental growth dataset.
    """

    return ROLE_TO_MARKET_TITLE.get(
        career_role,
        career_role
    )

# ============================================================
# REPRESENTATIVE GROWTH PROFILE
# ============================================================

def _deterministic_mode(series):
    """
    Return a reproducible mode.
    If multiple values tie, choose alphabetically.
    """

    counts = (
        series
        .dropna()
        .astype(str)
        .value_counts()
    )

    if counts.empty:
        return None

    max_count = counts.max()

    tied_values = sorted(
        counts[
            counts == max_count
        ].index.tolist()
    )

    return tied_values[0]


def build_representative_growth_profile(
    df_market,
    career_role
):
    """
    Build a representative 9-feature growth-model profile
    from rows in the 500-record experimental dataset.

    CareerLens roles are first mapped to the closest title
    available in the growth dataset.
    """

    market_title = get_market_title(
        career_role
    )

    role_rows = df_market[
        df_market["Job_Title"]
        == market_title
    ].copy()

    # Fallback only if the mapped title is unexpectedly absent
    if role_rows.empty:
        role_rows = df_market.copy()

    profile = {
        "job_title":
            market_title,

        "industry":
            _deterministic_mode(
                role_rows["Industry"]
            ),

        "company_size":
            _deterministic_mode(
                role_rows["Company_Size"]
            ),

        "location":
            _deterministic_mode(
                role_rows["Location"]
            ),

        "ai_adoption_level":
            _deterministic_mode(
                role_rows["AI_Adoption_Level"]
            ),

        "automation_risk":
            _deterministic_mode(
                role_rows["Automation_Risk"]
            ),

        "required_skills":
            _deterministic_mode(
                role_rows["Required_Skills"]
            ),

        "salary_usd":
            float(
                role_rows[
                    "Salary_USD"
                ].median()
            ),

        "remote_friendly":
            _deterministic_mode(
                role_rows["Remote_Friendly"]
            )
    }

    return profile


# ============================================================
# CAREER ROLE → EXPERIMENTAL GROWTH PREDICTION
# ============================================================

def predict_career_growth(
    model,
    df_market,
    career_role
):
    """
    Build a representative market profile and run the
    experimental Random Forest growth model.
    """

    profile = (
        build_representative_growth_profile(
            df_market=df_market,
            career_role=career_role
        )
    )

    prediction = predict_job_growth(
        model=model,
        **profile
    )

    prediction[
        "market_title"
    ] = profile[
        "job_title"
    ]

    prediction[
        "representative_profile"
    ] = profile

    return prediction