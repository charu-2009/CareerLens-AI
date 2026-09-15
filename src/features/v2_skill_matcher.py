import json
import re
from copy import deepcopy
from pathlib import Path

from src.utils.profile_adapter import (
    get_runtime_profile,
    allows_readiness,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

REFERENCE_DIR = (
    PROJECT_ROOT
    / "data"
    / "reference"
)

RUNTIME_ALIAS_PATH = (
    REFERENCE_DIR
    / "runtime_skill_aliases_v2.json"
)


def normalize_skill(value):

    if value is None:
        return ""

    text = str(value).strip().lower()

    text = text.replace(
        "&",
        " and "
    )

    text = re.sub(
        r"[_/]+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-z0-9+#.\- ]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def _load_runtime_aliases():

    if not RUNTIME_ALIAS_PATH.exists():

        return {}


    with RUNTIME_ALIAS_PATH.open(
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)


    aliases = data.get(
        "aliases",
        {}
    )


    if not isinstance(
        aliases,
        dict
    ):

        return {}


    result = {}


    for alias, canonical in aliases.items():

        alias_norm = normalize_skill(
            alias
        )

        canonical_norm = normalize_skill(
            canonical
        )

        if (
            alias_norm
            and
            canonical_norm
        ):

            result[
                alias_norm
            ] = canonical_norm


    return result


RUNTIME_ALIASES = (
    _load_runtime_aliases()
)


def resolve_skill_alias(value):

    normalized = normalize_skill(
        value
    )

    if not normalized:
        return ""

    return RUNTIME_ALIASES.get(
        normalized,
        normalized
    )


def normalize_skill_list(
    skills,
    resolve_aliases=True,
):

    if skills is None:
        return []

    if isinstance(
        skills,
        str
    ):

        skills = re.split(
            r"[,;\n|]+",
            skills
        )


    normalized = []

    seen = set()


    for skill in skills:

        if resolve_aliases:

            value = resolve_skill_alias(
                skill
            )

        else:

            value = normalize_skill(
                skill
            )


        if not value:
            continue


        if value not in seen:

            seen.add(
                value
            )

            normalized.append(
                value
            )


    return normalized



def _requirement_index(requirements):

    index = {}

    for item in requirements:

        concept = item.get("concept")

        # IMPORTANT:
        # Runtime user skills and readiness requirements
        # must pass through the SAME trusted alias resolver.
        #
        # Example:
        # user "NLP"
        # -> "natural language processing"
        #
        # requirement "NLP"
        # -> "natural language processing"
        #
        # This keeps matching symmetric.

        concept_norm = resolve_skill_alias(
            concept
        )

        if not concept_norm:
            continue

        # Never silently collapse two distinct frozen
        # requirements onto one runtime alias key.
        if concept_norm in index:

            previous = index[
                concept_norm
            ]

            previous_concept = previous.get(
                "concept"
            )

            raise RuntimeError(
                "Trusted runtime alias collision inside "
                "career readiness requirements: "
                f"{previous_concept!r} and {concept!r} "
                f"both resolve to {concept_norm!r}"
            )

        index[
            concept_norm
        ] = item

    return index


def match_readiness_requirements(
    career_name,
    user_skills,
):

    runtime_profile = get_runtime_profile(
        career_name
    )


    normalized_user_skills = (
        normalize_skill_list(
            user_skills,
            resolve_aliases=True,
        )
    )


    if runtime_profile is None:

        return {
            "career_name":
                career_name,

            "career_found":
                False,

            "readiness_available":
                False,

            "readiness_mode":
                None,

            "user_skills_normalized":
                normalized_user_skills,

            "matched_core":
                [],

            "missing_core":
                [],

            "matched_important":
                [],

            "missing_important":
                [],

            "matched_total":
                0,

            "requirement_total":
                0,
        }


    mode = runtime_profile[
        "readiness_mode"
    ]


    if not allows_readiness(
        career_name
    ):

        return {
            "career_name":
                career_name,

            "career_found":
                True,

            "readiness_available":
                False,

            "readiness_mode":
                mode,

            "user_skills_normalized":
                normalized_user_skills,

            "matched_core":
                [],

            "missing_core":
                [],

            "matched_important":
                [],

            "missing_important":
                [],

            "matched_total":
                0,

            "requirement_total":
                0,
        }


    user_set = set(
        normalized_user_skills
    )


    core_requirements = (
        runtime_profile[
            "core_requirements"
        ]
    )

    important_requirements = (
        runtime_profile[
            "important_requirements"
        ]
    )


    core_index = _requirement_index(
        core_requirements
    )

    important_index = _requirement_index(
        important_requirements
    )


    matched_core = []
    missing_core = []

    matched_important = []
    missing_important = []


    for concept_norm, item in core_index.items():

        record = deepcopy(
            item
        )

        record[
            "concept_normalized"
        ] = concept_norm


        if concept_norm in user_set:

            matched_core.append(
                record
            )

        else:

            missing_core.append(
                record
            )


    for concept_norm, item in important_index.items():

        record = deepcopy(
            item
        )

        record[
            "concept_normalized"
        ] = concept_norm


        if concept_norm in user_set:

            matched_important.append(
                record
            )

        else:

            missing_important.append(
                record
            )


    matched_total = (
        len(
            matched_core
        )
        +
        len(
            matched_important
        )
    )


    requirement_total = (
        len(
            core_index
        )
        +
        len(
            important_index
        )
    )


    return {
        "career_name":
            career_name,

        "career_found":
            True,

        "readiness_available":
            True,

        "readiness_mode":
            mode,

        "user_skills_normalized":
            normalized_user_skills,

        "matched_core":
            matched_core,

        "missing_core":
            missing_core,

        "matched_important":
            matched_important,

        "missing_important":
            missing_important,

        "matched_total":
            matched_total,

        "requirement_total":
            requirement_total,
    }


def matched_skill_names(
    result
):

    return [
        item[
            "concept"
        ]
        for item in (
            result.get(
                "matched_core",
                []
            )
            +
            result.get(
                "matched_important",
                []
            )
        )
    ]


def missing_skill_names(
    result
):

    return [
        item[
            "concept"
        ]
        for item in (
            result.get(
                "missing_core",
                []
            )
            +
            result.get(
                "missing_important",
                []
            )
        )
    ]
