# ============================================================
# CAREERLENS AI — CAREER EXPLANATION ENGINE
# ============================================================


def generate_career_explanation(
    row,
    top_learning_n=3
):
    """
    Generate a transparent explanation for one CareerLens
    recommendation using recommendation, readiness,
    experience, market, growth, and learning data.
    """

    job_role = row["job_role"]

    readiness = float(row["readiness_score"])
    market_demand = float(row["market_demand_score"])
    experience_score = float(row["experience_score"])
    final_score = float(row["final_careerlens_score"])

    category = row["recommendation_category"]
    role_tier = row["role_tier"]

    growth_prediction = row["predicted_growth"]
    growth_confidence = float(row["growth_confidence"])
    growth_confidence_level = row["growth_confidence_level"]

    matched_count = int(
        row["matched_market_skill_count"]
    )

    high_priority_gaps = int(
        row["high_priority_gap_count"]
    )

    learning_priorities = row[
        "learning_priorities"
    ]


    # ========================================================
    # 1. OVERALL SUMMARY
    # ========================================================

    summary = (
        f"{job_role} is ranked #{int(row['career_rank'])} "
        f"with a CareerLens score of {final_score:.2f}/100 "
        f"and is classified as an {category}."
    )


    # ========================================================
    # 2. SKILL FIT EXPLANATION
    # ========================================================

    if readiness >= 80:

        skill_fit = (
            f"Your current skill profile has a strong overlap "
            f"with this role, with a readiness score of "
            f"{readiness:.2f}%."
        )

    elif readiness >= 60:

        skill_fit = (
            f"Your skills show a good foundation for this role, "
            f"with a readiness score of {readiness:.2f}%, "
            f"although several important gaps remain."
        )

    elif readiness >= 40:

        skill_fit = (
            f"You have partial alignment with this role, with "
            f"a readiness score of {readiness:.2f}%. Additional "
            f"skill development would be needed."
        )

    else:

        skill_fit = (
            f"Your current skill overlap with this role is "
            f"limited, with a readiness score of "
            f"{readiness:.2f}%."
        )


    # ========================================================
    # 3. EXPERIENCE FIT EXPLANATION
    # ========================================================

    if experience_score >= 90:

        experience_fit = (
            f"Your experience level is highly compatible with "
            f"the expected seniority of this {role_tier}-level role."
        )

    elif experience_score >= 70:

        experience_fit = (
            f"Your experience level is reasonably compatible "
            f"with this {role_tier}-level role."
        )

    elif experience_score >= 50:

        experience_fit = (
            f"Your experience partially matches this role, "
            f"but additional practical experience may improve "
            f"your suitability."
        )

    else:

        experience_fit = (
            f"This role currently requires a stronger experience "
            f"fit than your profile provides."
        )


    # ========================================================
    # 4. MARKET DEMAND EXPLANATION
    # ========================================================

    if market_demand >= 80:

        market_explanation = (
            f"This role also has a high relative market-demand "
            f"score of {market_demand:.2f}/100 within the "
            f"CareerLens dataset."
        )

    elif market_demand >= 60:

        market_explanation = (
            f"This role has a moderate-to-strong relative "
            f"market-demand score of {market_demand:.2f}/100 "
            f"within the CareerLens dataset."
        )

    else:

        market_explanation = (
            f"Its relative market-demand score is "
            f"{market_demand:.2f}/100 within the CareerLens dataset."
        )


    # ========================================================
    # 5. LEARNING GAP EXPLANATION
    # ========================================================

    top_learning_skills = [
        item["skill"]
        for item in learning_priorities[
            :top_learning_n
        ]
    ]

    if top_learning_skills:

        formatted_skills = ", ".join(
            skill.title()
            for skill in top_learning_skills
        )

        learning_explanation = (
            f"You currently match {matched_count} tracked "
            f"market/profile skills and have "
            f"{high_priority_gaps} high-priority gaps. "
            f"Your most important next learning areas are "
            f"{formatted_skills}."
        )

    else:

        learning_explanation = (
            "No major learning gaps were identified for this role."
        )


    # ========================================================
    # 6. GROWTH MODEL EXPLANATION
    # ========================================================

    if growth_confidence_level == "Low":

        growth_explanation = (
            f"The experimental growth model predicts "
            f"{growth_prediction}, but confidence is only "
            f"{growth_confidence:.2f}% "
            f"({growth_confidence_level}). "
            f"This signal should therefore be interpreted "
            f"cautiously and should not outweigh your skill, "
            f"experience, and market-fit results."
        )

    else:

        growth_explanation = (
            f"The experimental growth model predicts "
            f"{growth_prediction} with "
            f"{growth_confidence:.2f}% confidence "
            f"({growth_confidence_level})."
        )


    # ========================================================
    # 7. FINAL REASON
    # ========================================================

    if final_score >= 80:

        conclusion = (
            f"Overall, CareerLens considers {job_role} one of "
            f"your strongest career options because your current "
            f"profile shows strong combined skill, experience, "
            f"and market fit."
        )

    elif final_score >= 70:

        conclusion = (
            f"Overall, {job_role} is a strong option, although "
            f"closing the identified skill gaps would improve "
            f"your fit."
        )

    elif final_score >= 60:

        conclusion = (
            f"Overall, {job_role} is a reasonable career option, "
            f"but meaningful skill development is still required."
        )

    else:

        conclusion = (
            f"Overall, this role is currently a weaker match "
            f"than your higher-ranked CareerLens recommendations."
        )


    return {
        "job_role": job_role,
        "summary": summary,
        "skill_fit": skill_fit,
        "experience_fit": experience_fit,
        "market_explanation": market_explanation,
        "learning_explanation": learning_explanation,
        "growth_explanation": growth_explanation,
        "conclusion": conclusion
    }


def attach_career_explanations(
    career_df
):
    """
    Generate explanations for every career recommendation.
    """

    result = career_df.copy()

    result["career_explanation"] = [
        generate_career_explanation(row)
        for _, row in result.iterrows()
    ]

    return result