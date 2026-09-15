
"""
CareerLens AI V2 Explanation Engine

Purpose
-------
Convert frozen V2 recommendation output into safe,
structured user-facing explanation payloads.

This module does NOT:
- rank careers
- alter readiness scores
- calculate universal fit scores
- use routing score as final ranking
- use market data for ranking
- use growth data for ranking
- fabricate unavailable evidence

Authoritative upstream:
    src.models.recommender_v2
"""

from typing import Any, Dict, List, Optional
import math


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _is_missing(value: Any) -> bool:
    if value is None:
        return True

    try:
        return bool(math.isnan(value))
    except Exception:
        return False


def _clean_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return [
            str(x).strip()
            for x in value
            if str(x).strip()
        ]

    return []


def _format_number(value: Any, decimals: int = 2) -> Optional[str]:
    if _is_missing(value):
        return None

    try:
        number = float(value)

        if number.is_integer():
            return f"{int(number):,}"

        return f"{number:,.{decimals}f}"

    except Exception:
        return str(value)


def _format_percent_fraction(value: Any) -> Optional[str]:
    """
    Convert fraction such as 0.0498 to 4.98%.
    """
    if _is_missing(value):
        return None

    try:
        return f"{float(value) * 100:.2f}%"

    except Exception:
        return None


def _first_dict_value(data: Dict[str, Any], keys: List[str]):
    for key in keys:
        if key in data and not _is_missing(data.get(key)):
            return data.get(key)

    return None


# ============================================================
# READINESS EXPLANATION
# ============================================================

def _build_readiness_explanation(row: Dict[str, Any]) -> Dict[str, Any]:

    lane = row.get("lane")
    available = bool(row.get("readiness_available", False))

    score = row.get("readiness_score")
    confidence = row.get("readiness_confidence")

    matched_total = row.get("matched_total")
    requirement_total = row.get("requirement_total")

    if lane == "full_readiness" and available:

        summary = (
            f"CareerLens has fuller validated readiness evidence for this career. "
            f"Your current skills match approximately "
            f"{_format_number(score)}% of the weighted readiness requirements "
            f"represented in this profile."
        )

        if not _is_missing(matched_total) and not _is_missing(requirement_total):
            summary += (
                f" You matched {int(matched_total)} of "
                f"{int(requirement_total)} readiness requirements."
            )

        return {
            "available": True,
            "evidence_level": "full",
            "score": score,
            "confidence": confidence,
            "summary": summary,
            "interpretation": (
                "This percentage measures weighted requirement coverage, "
                "not hiring probability."
            ),
        }


    if lane == "limited_readiness" and available:

        summary = (
            f"A readiness estimate is available for this career, but the "
            f"validated profile has more limited evidence coverage. "
            f"Your current skills match approximately "
            f"{_format_number(score)}% of the weighted readiness requirements "
            f"currently represented."
        )

        if not _is_missing(matched_total) and not _is_missing(requirement_total):
            summary += (
                f" You matched {int(matched_total)} of "
                f"{int(requirement_total)} known readiness requirements."
            )

        return {
            "available": True,
            "evidence_level": "limited",
            "score": score,
            "confidence": confidence,
            "summary": summary,
            "interpretation": (
                "This estimate should be interpreted with limited-profile "
                "confidence and should not be directly treated as stronger "
                "or weaker than a full-readiness profile solely by percentage."
            ),
        }


    if lane == "routing_only":

        return {
            "available": False,
            "evidence_level": "routing_only",
            "score": None,
            "confidence": None,
            "summary": (
                "Your skills connect with this career domain, but CareerLens "
                "does not yet have enough validated career-specific readiness "
                "evidence to calculate a readiness percentage."
            ),
            "interpretation": (
                "No readiness score is shown because unavailable evidence "
                "must not be treated as zero."
            ),
        }


    if lane == "safe_shell":

        return {
            "available": False,
            "evidence_level": "discovery_only",
            "score": None,
            "confidence": None,
            "summary": (
                "This career is shown for exploration, but validated "
                "career-specific evidence is currently insufficient for "
                "readiness scoring."
            ),
            "interpretation": (
                "This does not mean you are unqualified; it means the system "
                "does not currently have enough validated evidence to score it."
            ),
        }


    return {
        "available": False,
        "evidence_level": "unavailable",
        "score": None,
        "confidence": None,
        "summary": (
            "Career-specific readiness evidence is unavailable."
        ),
        "interpretation": (
            "Unavailable evidence is not converted into a zero score."
        ),
    }


# ============================================================
# ROUTING EXPLANATION
# ============================================================

def _build_routing_explanation(row: Dict[str, Any]) -> Dict[str, Any]:

    matched_domain = row.get("matched_domain")
    primary_domain = row.get("primary_domain")

    relation = row.get("routing_relation")
    confidence = row.get("domain_confidence_state")

    matched_count = row.get(
        "domain_matched_skill_count"
    )

    parts = []

    if matched_domain:
        parts.append(
            f"Your skills matched signals associated with the "
            f"{matched_domain} domain."
        )

    if (
        primary_domain
        and
        matched_domain
        and
        primary_domain != matched_domain
    ):
        parts.append(
            f"This career's primary domain is {primary_domain}, "
            f"but it was reached through related-domain evidence."
        )

    if not _is_missing(matched_count):
        parts.append(
            f"{int(matched_count)} routing skill signal"
            f"{'' if int(matched_count) == 1 else 's'} contributed "
            f"to candidate generation."
        )

    if confidence:
        parts.append(
            f"Routing evidence state: {confidence}."
        )

    return {
        "matched_domain": matched_domain,
        "primary_domain": primary_domain,
        "routing_relation": relation,
        "confidence_state": confidence,
        "matched_skill_count": matched_count,
        "summary": " ".join(parts),
        "warning": (
            "Routing evidence explains why the career was considered. "
            "It is not a career-fit probability and is not used as a "
            "final ranking score."
        ),
    }


# ============================================================
# SKILL GAP EXPLANATION
# ============================================================

def _build_skill_gap_explanation(row: Dict[str, Any]) -> Dict[str, Any]:

    readiness_available = bool(
        row.get(
            "readiness_available",
            False
        )
    )


    if not readiness_available:

        return {
            "available": False,

            "missing_core_count": None,
            "missing_important_count": None,
            "missing_total": None,

            "missing_core_skills": [],
            "missing_important_skills": [],

            "priority_groups": [],

            "summary": (
                "A validated career-specific skill-gap analysis is not "
                "available for this career."
            ),

            "ordering_note": None,
        }


    raw_core = row.get(
        "missing_core"
    )

    raw_important = row.get(
        "missing_important"
    )

    raw_total = row.get(
        "missing_total"
    )


    # --------------------------------------------------------
    # Support both possible runtime representations:
    # - numeric counts
    # - explicit skill-name lists
    #
    # Never fabricate names from counts.
    # --------------------------------------------------------

    core_skills = []
    important_skills = []

    core_count = None
    important_count = None


    if isinstance(
        raw_core,
        (list, tuple, set)
    ):

        core_skills = _clean_list(
            raw_core
        )

        core_count = len(
            core_skills
        )

    elif not _is_missing(
        raw_core
    ):

        try:
            core_count = int(
                raw_core
            )
        except Exception:
            core_count = None


    if isinstance(
        raw_important,
        (list, tuple, set)
    ):

        important_skills = _clean_list(
            raw_important
        )

        important_count = len(
            important_skills
        )

    elif not _is_missing(
        raw_important
    ):

        try:
            important_count = int(
                raw_important
            )
        except Exception:
            important_count = None


    if not _is_missing(
        raw_total
    ):

        try:
            missing_total = int(
                raw_total
            )
        except Exception:
            missing_total = None

    else:

        missing_total = None


    # --------------------------------------------------------
    # Fall back to matched/requirement arithmetic only if
    # explicit missing_total is unavailable.
    # --------------------------------------------------------

    if missing_total is None:

        matched_total = row.get(
            "matched_total"
        )

        requirement_total = row.get(
            "requirement_total"
        )


        if (
            not _is_missing(
                matched_total
            )
            and
            not _is_missing(
                requirement_total
            )
        ):

            try:
                missing_total = max(
                    int(
                        requirement_total
                    )
                    -
                    int(
                        matched_total
                    ),
                    0
                )

            except Exception:
                missing_total = None


    priority_groups = []


    if (
        core_count is not None
        and
        core_count > 0
    ):

        priority_groups.append(
            {
                "priority": 1,

                "tier": "core",

                "missing_count":
                    core_count,

                "skills":
                    core_skills,

                "skill_names_available":
                    len(
                        core_skills
                    )
                    >
                    0,

                "interpretation":
                    (
                        "This is the highest-priority missing "
                        "requirement group."
                    ),
            }
        )


    if (
        important_count is not None
        and
        important_count > 0
    ):

        priority_groups.append(
            {
                "priority": 2,

                "tier": "important",

                "missing_count":
                    important_count,

                "skills":
                    important_skills,

                "skill_names_available":
                    len(
                        important_skills
                    )
                    >
                    0,

                "interpretation":
                    (
                        "This is the important missing "
                        "requirement group after core."
                    ),
            }
        )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if (
        missing_total is not None
        and
        missing_total == 0
    ):

        summary = (
            "No missing readiness requirements were identified "
            "within the validated profile."
        )


    elif (
        missing_total is not None
        and
        missing_total > 0
    ):

        pieces = []


        if (
            core_count is not None
            and
            core_count > 0
        ):

            pieces.append(
                f"{core_count} core"
            )


        if (
            important_count is not None
            and
            important_count > 0
        ):

            pieces.append(
                f"{important_count} important"
            )


        if pieces:

            summary = (
                "CareerLens identified "
                + " and ".join(
                    pieces
                )
                + " missing readiness requirements"
                + f" ({missing_total} total)."
            )

        else:

            requirement_word = (
                "requirement"
                if missing_total == 1
                else "requirements"
            )

            summary = (
                f"CareerLens identified {missing_total} missing "
                f"readiness {requirement_word} in the validated profile."
            )


    else:

        summary = (
            "CareerLens has readiness evidence for this career, "
            "but the missing-requirement count is unavailable."
        )


    return {
        "available": True,

        "missing_core_count":
            core_count,

        "missing_important_count":
            important_count,

        "missing_total":
            missing_total,

        "missing_core_skills":
            core_skills,

        "missing_important_skills":
            important_skills,

        "priority_groups":
            priority_groups,

        "summary":
            summary,

        "ordering_note":
            (
                "Core requirements form a higher-priority group than "
                "important requirements. Skills within the same tier "
                "are not pedagogically ranked. Where skill names are "
                "not available in the production recommendation row, "
                "CareerLens reports counts only and does not invent names."
            ),
    }


# ============================================================
# MARKET EXPLANATION
# ============================================================

def _build_market_explanation(row: Dict[str, Any]) -> Dict[str, Any]:

    available = bool(
        row.get(
            "market_available",
            False
        )
    )

    support_reason = row.get(
        "market_support_reason"
    )


    if not available:

        return {
            "available": False,
            "support_reason": support_reason,
            "demand": None,
            "top_market_skills": [],
            "salary": None,
            "experience": None,
            "education": None,
            "remote": None,
            "location": None,
            "summary": (
                "CareerLens does not currently have supported market evidence "
                "for this career in the 30,000-record market dataset."
            ),
            "warning": (
                "Unavailable market evidence does not mean zero real-world demand."
            ),
        }


    demand = row.get(
        "market_demand"
    )

    if not isinstance(
        demand,
        dict
    ):
        demand = {}


    job_count = demand.get(
        "job_count"
    )

    relative_score = demand.get(
        "relative_demand_score"
    )

    market_share = demand.get(
        "market_share"
    )


    market_share_text = (
        _format_percent_fraction(
            market_share
        )
    )


    summary_parts = []


    if not _is_missing(job_count):

        summary_parts.append(
            f"The supported market dataset contains "
            f"{int(job_count):,} observed records for this career."
        )


    if market_share_text is not None:

        summary_parts.append(
            f"That represents approximately "
            f"{market_share_text} of the supported dataset."
        )


    if not _is_missing(relative_score):

        summary_parts.append(
            f"Its relative representation score within the 20 supported "
            f"careers is {_format_number(relative_score)} out of 100."
        )


    top_skills = row.get(
        "top_market_skills"
    )

    if not isinstance(
        top_skills,
        list
    ):
        top_skills = []


    return {
        "available": True,
        "support_reason": support_reason,

        "demand": {
            "job_count": job_count,
            "market_share": market_share,
            "relative_demand_score": relative_score,
            "ranking_authorized": False,
        },

        "top_market_skills": top_skills,

        "salary": row.get(
            "salary"
        ),

        "experience": row.get(
            "experience"
        ),

        "education": row.get(
            "education"
        ),

        "remote": row.get(
            "remote"
        ),

        "location": row.get(
            "location"
        ),

        "summary": " ".join(
            summary_parts
        ),

        "warning": (
            "Market evidence is descriptive context only. It does not change "
            "career-fit ranking, readiness scoring, or hiring probability."
        ),
    }


# ============================================================
# GROWTH EXPLANATION
# ============================================================

def _build_growth_explanation(row: Dict[str, Any]) -> Dict[str, Any]:

    available = bool(
        row.get(
            "growth_available",
            False
        )
    )


    if not available:

        return {
            "available": False,
            "state": "unavailable",
            "outlook": None,
            "confidence": None,
            "summary": (
                "Experimental growth evidence is unavailable for this career."
            ),
            "warning": (
                "Unavailable growth evidence is not interpreted as negative growth."
            ),
        }


    state = row.get(
        "growth_evidence_state"
    )

    outlook = row.get(
        "growth_outlook"
    )

    confidence = row.get(
        "growth_confidence"
    )


    return {
        "available": True,
        "state": state,
        "outlook": outlook,
        "confidence": confidence,

        "summary": (
            f"Experimental growth signal: {outlook}, "
            f"with {confidence} confidence."
        ),

        "warning": (
            "Growth evidence is experimental and descriptive only. "
            "It is not used to rank careers."
        ),
    }


# ============================================================
# ORDERING EXPLANATION
# ============================================================

def _build_ordering_explanation(row: Dict[str, Any]) -> Dict[str, Any]:

    lane = row.get(
        "lane"
    )

    lane_rank = row.get(
        "lane_rank"
    )


    if lane in {
        "full_readiness",
        "limited_readiness",
    }:

        return {
            "rank_available":
                not _is_missing(
                    lane_rank
                ),

            "lane_rank":
                lane_rank,

            "summary":
                (
                    f"This career is ordered within the "
                    f"{lane.replace('_', ' ')} lane using readiness score."
                    if not _is_missing(
                        lane_rank
                    )
                    else
                    "This career belongs to a comparable readiness lane."
                ),

            "warning":
                (
                    "Lane rank is meaningful only within the same "
                    "readiness lane and is not a universal career rank."
                ),
        }


    return {
        "rank_available": False,
        "lane_rank": None,
        "summary": (
            "This career is not assigned a numeric readiness rank."
        ),
        "warning": (
            "Routing-only and discovery-only careers are not numerically "
            "ranked against readiness-scored careers."
        ),
    }


# ============================================================
# MAIN CAREER EXPLANATION API
# ============================================================

def explain_career_v2(
    recommendation_row: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build the complete structured explanation for one
    CareerLens V2 recommendation row.
    """

    if not isinstance(
        recommendation_row,
        dict
    ):
        raise TypeError(
            "recommendation_row must be a dict."
        )


    career_name = recommendation_row.get(
        "career_name"
    )

    lane = recommendation_row.get(
        "lane"
    )

    presentation_role = recommendation_row.get(
        "presentation_role"
    )


    return {

        "career_name":
            career_name,

        "lane":
            lane,

        "presentation_role":
            presentation_role,

        "routing":
            _build_routing_explanation(
                recommendation_row
            ),

        "readiness":
            _build_readiness_explanation(
                recommendation_row
            ),

        "skill_gap":
            _build_skill_gap_explanation(
                recommendation_row
            ),

        "ordering":
            _build_ordering_explanation(
                recommendation_row
            ),

        "market":
            _build_market_explanation(
                recommendation_row
            ),

        "growth":
            _build_growth_explanation(
                recommendation_row
            ),

        "disclaimer":
            (
                "CareerLens explanations summarize validated profile evidence "
                "and supported descriptive market context. They are not hiring "
                "predictions, eligibility decisions, or guarantees."
            ),
    }


# ============================================================
# DATAFRAME API
# ============================================================

def explain_recommendations_v2(
    recommendations
) -> List[Dict[str, Any]]:
    """
    Convert a recommendation DataFrame or list of dicts into
    structured CareerLens explanations.
    """

    if recommendations is None:
        return []


    if hasattr(
        recommendations,
        "to_dict"
    ):
        records = recommendations.to_dict(
            orient="records"
        )

    elif isinstance(
        recommendations,
        list
    ):
        records = recommendations

    else:
        raise TypeError(
            "recommendations must be a DataFrame or list of dicts."
        )


    return [
        explain_career_v2(
            record
        )
        for record in records
    ]
