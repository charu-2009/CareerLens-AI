from pathlib import Path
from functools import lru_cache

import numpy as np
import pandas as pd

from src.models.career_router_v2 import (
    route_careers_v2,
)

from src.utils.profile_adapter import (
    get_runtime_profile,
)

from src.features.v2_readiness import (
    calculate_readiness,
)

from src.features.v2_skill_gap import (
    calculate_skill_gap,
)

from src.data.data_loader import (
    build_runtime_data,
)

from src.features.skill_utils import (
    normalize_skill,
)

from src.utils.market_intelligence import (
    get_career_market_profile,
)

from src.models.growth_model import (
    load_growth_model,
    predict_career_growth,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

RAW = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

GROWTH_DATA_PATH = (
    RAW
    / "ai_job_market_insights.csv"
)


# ============================================================
# RECOMMENDATION LANE POLICY
# ============================================================

MODE_TO_LANE = {

    "full_readiness_candidate":
        "full_readiness",

    "limited_readiness_candidate":
        "limited_readiness",

    "routing_only_evidence":
        "routing_only",

    "safe_shell_no_evidence":
        "safe_shell",
}


LANE_ROLE = {

    "full_readiness":
        "main_comparable",

    "limited_readiness":
        "qualified_comparable",

    "routing_only":
        "related_evidence_incomplete",

    "safe_shell":
        "discovery_only",
}


LANE_ORDER = {

    "full_readiness":
        1,

    "limited_readiness":
        2,

    "routing_only":
        3,

    "safe_shell":
        4,
}


# ============================================================
# CACHED DESCRIPTIVE EVIDENCE SOURCES
# ============================================================

@lru_cache(maxsize=1)
def _get_market_runtime():

    runtime = build_runtime_data(
        normalize_skill
    )

    core_jobs = runtime[
        "core_jobs"
    ]

    supported_careers = frozenset(
        core_jobs[
            "job_title"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    career_counts = (
        core_jobs[
            "job_title"
        ]
        .value_counts()
        .to_dict()
    )

    return {
        "supported_careers":
            supported_careers,

        "role_market_lookup":
            runtime[
                "role_market_lookup"
            ],

        "career_counts":
            career_counts,

        "total_jobs":
            int(
                len(
                    core_jobs
                )
            ),

        "salary_lookup":
            runtime[
                "salary_lookup"
            ],

        "experience_lookup":
            runtime[
                "experience_lookup"
            ],

        "education_lookup":
            runtime[
                "education_lookup"
            ],

        "remote_lookup":
            runtime[
                "remote_lookup"
            ],

        "top_company_locations":
            runtime[
                "top_company_locations"
            ],

        "role_skill_demand_30k":
            runtime[
                "role_skill_demand_30k"
            ],
    }


@lru_cache(maxsize=1)
def _get_growth_runtime():

    if not GROWTH_DATA_PATH.exists():

        raise FileNotFoundError(
            f"Growth dataset not found: "
            f"{GROWTH_DATA_PATH}"
        )

    growth_df = pd.read_csv(
        GROWTH_DATA_PATH
    )

    model = load_growth_model()

    if model is None:

        raise RuntimeError(
            "Growth model could not be loaded."
        )

    return {
        "model":
            model,

        "data":
            growth_df,
    }


# ============================================================
# PROFILE HELPERS
# ============================================================

def _extract_runtime_mode(
    profile
):

    if not isinstance(
        profile,
        dict
    ):
        return None

    return profile.get(
        "readiness_mode"
    )


def _extract_readiness_allowed(
    profile
):

    if not isinstance(
        profile,
        dict
    ):
        return False

    return (
        profile.get(
            "readiness_percentage_allowed"
        )
        is True
    )


# ============================================================
# ROUTER CANDIDATE ADAPTER
# ============================================================

def _extract_router_candidates(
    router_result
):

    if not isinstance(
        router_result,
        dict
    ):
        return []

    raw_candidates = router_result.get(
        "candidate_careers",
        []
    )

    if not isinstance(
        raw_candidates,
        list
    ):
        return []

    candidates = []

    for item in raw_candidates:

        if not isinstance(
            item,
            dict
        ):
            continue

        career = item.get(
            "career_name"
        )

        if not career:
            continue

        candidates.append(
            {
                "career_name":
                    career,

                "matched_domain":
                    item.get(
                        "matched_domain"
                    ),

                "primary_domain":
                    item.get(
                        "primary_domain"
                    ),

                "routing_relation":
                    item.get(
                        "routing_relation"
                    ),

                "domain_confidence_state":
                    item.get(
                        "domain_confidence_state"
                    ),

                "domain_matched_skill_count":
                    item.get(
                        "domain_matched_skill_count"
                    ),

                "domain_routing_score":
                    item.get(
                        "domain_routing_score"
                    ),
            }
        )

    return candidates


# ============================================================
# READINESS ADAPTER
# ============================================================

def _call_readiness(
    career,
    user_skills
):

    result = calculate_readiness(
        career,
        user_skills
    )

    if not isinstance(
        result,
        dict
    ):

        raise TypeError(
            f"Readiness result for "
            f"{career!r} is not a dict."
        )

    available = result.get(
        "readiness_available"
    )

    score = result.get(
        "readiness_score"
    )

    if score is None:

        score = result.get(
            "score"
        )

    if available is None:

        available = (
            score is not None
        )

    confidence = (
        result.get(
            "confidence_label"
        )
        or
        result.get(
            "readiness_confidence"
        )
        or
        result.get(
            "confidence"
        )
    )

    return {

        "readiness_available":
            bool(
                available
            ),

        "readiness_score":
            score,

        "readiness_confidence":
            confidence,

        "matched_total":
            result.get(
                "matched_total"
            ),

        "requirement_total":
            result.get(
                "requirement_total"
            ),
    }


# ============================================================
# SKILL-GAP ADAPTER
# ============================================================

def _call_skill_gap(
    career,
    user_skills
):

    result = calculate_skill_gap(
        career,
        user_skills
    )

    if not isinstance(
        result,
        dict
    ):

        raise TypeError(
            f"Skill-gap result for "
            f"{career!r} is not a dict."
        )

    missing_core = result.get(
        "missing_core"
    )

    if missing_core is None:

        missing_core = result.get(
            "core_gaps"
        )

    if missing_core is None:

        missing_core = []

    missing_important = result.get(
        "missing_important"
    )

    if missing_important is None:

        missing_important = result.get(
            "important_gaps"
        )

    if missing_important is None:

        missing_important = []

    missing_total = result.get(
        "missing_total"
    )

    if missing_total is None:

        missing_total = (
            len(
                missing_core
            )
            +
            len(
                missing_important
            )
        )

    return {

        "missing_core":
            list(
                missing_core
            ),

        "missing_important":
            list(
                missing_important
            ),

        "missing_total":
            missing_total,
    }


# ============================================================
# MARKET EVIDENCE
# ============================================================

def _get_market_evidence(
    career_name
):

    runtime = _get_market_runtime()

    supported = runtime[
        "supported_careers"
    ]

    if career_name not in supported:

        return {

            "market_available":
                False,

            "market_support_reason":
                "career_not_supported_by_30k_market_dataset",

            "market_demand":
                None,

            "top_market_skills":
                None,

            "salary":
                None,

            "experience":
                None,

            "education":
                None,

            "remote":
                None,

            "location":
                None,
        }

    profile = get_career_market_profile(
        career_name,
        runtime[
            "salary_lookup"
        ],
        runtime[
            "experience_lookup"
        ],
        runtime[
            "education_lookup"
        ],
        runtime[
            "remote_lookup"
        ],
        runtime[
            "role_skill_demand_30k"
        ],
        runtime[
            "top_company_locations"
        ],
    )

    if not isinstance(
        profile,
        dict
    ):

        return {

            "market_available":
                False,

            "market_support_reason":
                "supported_career_but_profile_unavailable",

            "market_demand":
                None,

            "top_market_skills":
                None,

            "salary":
                None,

            "experience":
                None,

            "education":
                None,

            "remote":
                None,

            "location":
                None,
        }

    relative_demand_score = (
        runtime[
            "role_market_lookup"
        ].get(
            career_name
        )
    )

    job_count = (
        runtime[
            "career_counts"
        ].get(
            career_name
        )
    )

    total_jobs = runtime[
        "total_jobs"
    ]

    market_share = (
        (
            float(
                job_count
            )
            /
            float(
                total_jobs
            )
        )
        if (
            job_count is not None
            and
            total_jobs
        )
        else None
    )

    market_demand = {

        "relative_demand_score":
            (
                float(
                    relative_demand_score
                )
                if relative_demand_score
                is not None
                else None
            ),

        "job_count":
            (
                int(
                    job_count
                )
                if job_count
                is not None
                else None
            ),

        "market_share":
            market_share,

        "evidence_scope":
            "30k_supported_market_dataset",

        "ranking_authorized":
            False,
    }

    return {

        "market_available":
            True,

        "market_support_reason":
            "supported_by_30k_market_dataset",

        "market_demand":
            market_demand,

        "top_market_skills":
            profile.get(
                "top_market_skills"
            ),

        "salary":
            profile.get(
                "salary"
            ),

        "experience":
            profile.get(
                "experience"
            ),

        "education":
            profile.get(
                "education"
            ),

        "remote":
            profile.get(
                "remote"
            ),

        "location":
            profile.get(
                "top_company_locations"
            ),
    }


# ============================================================
# EXPERIMENTAL GROWTH EVIDENCE
# ============================================================

def _get_growth_evidence(
    career_name
):

    market_runtime = (
        _get_market_runtime()
    )

    supported = market_runtime[
        "supported_careers"
    ]

    if career_name not in supported:

        return {

            "growth_available":
                False,

            "growth_evidence_state":
                "unavailable",

            "growth_outlook":
                None,

            "growth_confidence":
                None,
        }

    growth_runtime = (
        _get_growth_runtime()
    )

    try:

        prediction = predict_career_growth(
            growth_runtime[
                "model"
            ],
            growth_runtime[
                "data"
            ],
            career_name,
        )

    except Exception:

        return {

            "growth_available":
                False,

            "growth_evidence_state":
                "prediction_unavailable",

            "growth_outlook":
                None,

            "growth_confidence":
                None,
        }

    if not isinstance(
        prediction,
        dict
    ):

        return {

            "growth_available":
                False,

            "growth_evidence_state":
                "prediction_unavailable",

            "growth_outlook":
                None,

            "growth_confidence":
                None,
        }

    growth_outlook = (
        prediction.get(
            "predicted_growth"
        )
        or
        prediction.get(
            "growth_outlook"
        )
        or
        prediction.get(
            "prediction"
        )
    )

    growth_confidence = (
        prediction.get(
            "confidence_level"
        )
        or
        prediction.get(
            "growth_confidence"
        )
    )

    if growth_outlook is None:

        return {

            "growth_available":
                False,

            "growth_evidence_state":
                "prediction_unavailable",

            "growth_outlook":
                None,

            "growth_confidence":
                None,
        }

    return {

        "growth_available":
            True,

        "growth_evidence_state":
            "experimental_descriptive_signal",

        "growth_outlook":
            growth_outlook,

        "growth_confidence":
            growth_confidence,
    }


# ============================================================
# PRODUCTION V2 RECOMMENDATION ENGINE
# ============================================================

def recommend_careers_v2(
    user_skills
):

    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    routing_result = route_careers_v2(
        user_skills
    )

    candidates = (
        _extract_router_candidates(
            routing_result
        )
    )

    rows = []

    # --------------------------------------------------------
    # CANDIDATE ASSEMBLY
    # --------------------------------------------------------

    for candidate in candidates:

        career = candidate[
            "career_name"
        ]

        profile = get_runtime_profile(
            career
        )

        mode = _extract_runtime_mode(
            profile
        )

        readiness_allowed = (
            _extract_readiness_allowed(
                profile
            )
        )

        lane = MODE_TO_LANE.get(
            mode
        )

        if lane is None:

            raise AssertionError(
                f"Unknown runtime mode "
                f"for {career!r}: {mode!r}"
            )

        expected_readiness_allowed = (
            mode
            in
            {
                "full_readiness_candidate",
                "limited_readiness_candidate",
            }
        )

        if (
            readiness_allowed
            !=
            expected_readiness_allowed
        ):

            raise AssertionError(
                f"Readiness authorization "
                f"mismatch for {career!r}."
            )

        # ----------------------------------------------------
        # READINESS / GAP
        # ----------------------------------------------------

        if readiness_allowed:

            readiness = _call_readiness(
                career,
                user_skills
            )

            gap = _call_skill_gap(
                career,
                user_skills
            )

        else:

            readiness = {

                "readiness_available":
                    False,

                "readiness_score":
                    None,

                "readiness_confidence":
                    None,

                "matched_total":
                    None,

                "requirement_total":
                    None,
            }

            gap = {

                "missing_core":
                    [],

                "missing_important":
                    [],

                "missing_total":
                    None,
            }

        # ----------------------------------------------------
        # DESCRIPTIVE EVIDENCE
        # ----------------------------------------------------

        market = _get_market_evidence(
            career
        )

        growth = _get_growth_evidence(
            career
        )

        # ----------------------------------------------------
        # RESULT ROW
        # ----------------------------------------------------

        rows.append(
            {
                "career_name":
                    career,

                "runtime_mode":
                    mode,

                "lane":
                    lane,

                "presentation_role":
                    LANE_ROLE[
                        lane
                    ],

                "primary_domain":
                    candidate.get(
                        "primary_domain"
                    ),

                "matched_domain":
                    candidate.get(
                        "matched_domain"
                    ),

                "routing_relation":
                    candidate.get(
                        "routing_relation"
                    ),

                "domain_confidence_state":
                    candidate.get(
                        "domain_confidence_state"
                    ),

                "domain_matched_skill_count":
                    candidate.get(
                        "domain_matched_skill_count"
                    ),

                "domain_routing_score":
                    candidate.get(
                        "domain_routing_score"
                    ),

                "readiness_available":
                    readiness[
                        "readiness_available"
                    ],

                "readiness_score":
                    readiness[
                        "readiness_score"
                    ],

                "readiness_confidence":
                    readiness[
                        "readiness_confidence"
                    ],

                "matched_total":
                    readiness[
                        "matched_total"
                    ],

                "requirement_total":
                    readiness[
                        "requirement_total"
                    ],

                "missing_core":
                    gap[
                        "missing_core"
                    ],

                "missing_important":
                    gap[
                        "missing_important"
                    ],

                "missing_total":
                    gap[
                        "missing_total"
                    ],

                "market_available":
                    market[
                        "market_available"
                    ],

                "market_support_reason":
                    market[
                        "market_support_reason"
                    ],

                "market_demand":
                    market[
                        "market_demand"
                    ],

                "top_market_skills":
                    market[
                        "top_market_skills"
                    ],

                "salary":
                    market[
                        "salary"
                    ],

                "experience":
                    market[
                        "experience"
                    ],

                "education":
                    market[
                        "education"
                    ],

                "remote":
                    market[
                        "remote"
                    ],

                "location":
                    market[
                        "location"
                    ],

                "growth_available":
                    growth[
                        "growth_available"
                    ],

                "growth_evidence_state":
                    growth[
                        "growth_evidence_state"
                    ],

                "growth_outlook":
                    growth[
                        "growth_outlook"
                    ],

                "growth_confidence":
                    growth[
                        "growth_confidence"
                    ],
            }
        )

    result_df = pd.DataFrame(
        rows
    )

    # --------------------------------------------------------
    # EMPTY RESULT
    # --------------------------------------------------------

    if result_df.empty:

        # Match the authoritative 11K.2F empty-result contract.
        result_df = pd.DataFrame(
            columns=[
                "market_available",
                "market_support_reason",
                "market_demand",
                "top_market_skills",
                "salary",
                "experience",
                "education",
                "remote",
                "location",
                "growth_available",
                "growth_evidence_state",
                "growth_outlook",
                "growth_confidence",
            ]
        )

        return {

            "routing_state":
                routing_result.get(
                    "routing_state"
                ),

            "known_skills":
                routing_result.get(
                    "known_skills",
                    []
                ),

            "unknown_skills":
                routing_result.get(
                    "unknown_skills",
                    []
                ),

            "retained_domains":
                routing_result.get(
                    "retained_domains",
                    []
                ),

            "candidate_count":
                0,

            "recommendations":
                result_df,
        }

    # --------------------------------------------------------
    # LANE-SAFE ORDERING
    # --------------------------------------------------------

    result_df[
        "__lane_order"
    ] = result_df[
        "lane"
    ].map(
        LANE_ORDER
    )

    result_df[
        "__readiness_sort"
    ] = np.nan

    comparable_mask = result_df[
        "lane"
    ].isin(
        [
            "full_readiness",
            "limited_readiness",
        ]
    )

    result_df.loc[
        comparable_mask,
        "__readiness_sort"
    ] = pd.to_numeric(
        result_df.loc[
            comparable_mask,
            "readiness_score"
        ],
        errors="coerce"
    )

    result_df = (
        result_df
        .sort_values(
            [
                "__lane_order",
                "__readiness_sort",
                "career_name",
            ],
            ascending=[
                True,
                False,
                True,
            ],
            na_position="last"
        )
        .reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # LANE RANK
    # --------------------------------------------------------

    result_df[
        "lane_rank"
    ] = pd.Series(
        [None] * len(
            result_df
        ),
        dtype="object"
    )

    for lane_name in [
        "full_readiness",
        "limited_readiness",
    ]:

        lane_indexes = result_df.index[
            result_df[
                "lane"
            ]
            ==
            lane_name
        ].tolist()

        for rank, idx in enumerate(
            lane_indexes,
            start=1
        ):

            result_df.at[
                idx,
                "lane_rank"
            ] = rank

    result_df = result_df.drop(
        columns=[
            "__lane_order",
            "__readiness_sort",
        ]
    )

    # --------------------------------------------------------
    # AUTHORITATIVE OUTPUT COLUMN ORDER
    # --------------------------------------------------------

    authoritative_columns = [

        "career_name",
        "runtime_mode",
        "lane",
        "presentation_role",

        "primary_domain",
        "matched_domain",
        "routing_relation",
        "domain_confidence_state",
        "domain_matched_skill_count",
        "domain_routing_score",

        "readiness_available",
        "readiness_score",
        "readiness_confidence",
        "matched_total",
        "requirement_total",

        "missing_core",
        "missing_important",
        "missing_total",

        "lane_rank",

        "market_available",
        "market_support_reason",
        "market_demand",
        "top_market_skills",
        "salary",
        "experience",
        "education",
        "remote",
        "location",

        "growth_available",
        "growth_evidence_state",
        "growth_outlook",
        "growth_confidence",
    ]


    missing_output_columns = [

        column

        for column in authoritative_columns

        if column not in result_df.columns
    ]


    unexpected_output_columns = [

        column

        for column in result_df.columns

        if column not in authoritative_columns
    ]


    if missing_output_columns:

        raise AssertionError(
            "Production output missing expected columns: "
            + repr(
                missing_output_columns
            )
        )


    if unexpected_output_columns:

        raise AssertionError(
            "Production output contains unexpected columns: "
            + repr(
                unexpected_output_columns
            )
        )


    result_df = result_df[
        authoritative_columns
    ].copy()

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "routing_state":
            routing_result.get(
                "routing_state"
            ),

        "known_skills":
            routing_result.get(
                "known_skills",
                []
            ),

        "unknown_skills":
            routing_result.get(
                "unknown_skills",
                []
            ),

        "retained_domains":
            routing_result.get(
                "retained_domains",
                []
            ),

        "candidate_count":
            len(
                result_df
            ),

        "recommendations":
            result_df,
    }


# ============================================================
# OPTIONAL PUBLIC HELPERS
# ============================================================

def market_supported_careers_v2():

    return sorted(
        _get_market_runtime()[
            "supported_careers"
        ]
    )


def clear_v2_runtime_caches():

    _get_market_runtime.cache_clear()
    _get_growth_runtime.cache_clear()
