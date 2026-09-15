from copy import deepcopy

from src.utils.profile_loader import (
    get_v2_profile,
    list_v2_careers,
)


READINESS_MODES = {
    "full_readiness_candidate",
    "limited_readiness_candidate",
}

ROUTING_ONLY_MODE = (
    "routing_only_evidence"
)

SAFE_SHELL_MODE = (
    "safe_shell_no_evidence"
)


class RuntimeProfileError(RuntimeError):
    """Raised when a V2 runtime profile violates policy."""


def _profile_or_none(career_name):

    return get_v2_profile(
        career_name
    )


def _copy_list(value):

    if not isinstance(
        value,
        list
    ):
        return []

    return deepcopy(
        value
    )


def career_exists(
    career_name
):

    return (
        _profile_or_none(
            career_name
        )
        is not None
    )


def get_readiness_mode(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return None

    return profile.get(
        "readiness_mode"
    )


def allows_readiness(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return False

    mode = profile.get(
        "readiness_mode"
    )

    explicit_flag = bool(
        profile.get(
            "readiness_percentage_allowed",
            False
        )
    )

    return (
        mode in READINESS_MODES
        and
        explicit_flag
    )


def get_core_requirements(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return []

    if not allows_readiness(
        career_name
    ):
        return []

    return _copy_list(
        profile.get(
            "core_requirements",
            []
        )
    )


def get_important_requirements(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return []

    if not allows_readiness(
        career_name
    ):
        return []

    return _copy_list(
        profile.get(
            "important_requirements",
            []
        )
    )


def get_readiness_requirements(
    career_name
):

    core = get_core_requirements(
        career_name
    )

    important = (
        get_important_requirements(
            career_name
        )
    )

    result = []

    for item in core:

        record = deepcopy(
            item
        )

        record[
            "runtime_tier"
        ] = "core"

        result.append(
            record
        )


    for item in important:

        record = deepcopy(
            item
        )

        record[
            "runtime_tier"
        ] = "important"

        result.append(
            record
        )


    return result


def get_supporting_evidence(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return []

    return _copy_list(
        profile.get(
            "supporting_evidence",
            []
        )
    )


def get_functional_evidence(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return []

    return _copy_list(
        profile.get(
            "functional_evidence",
            []
        )
    )


def get_context_evidence(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return []

    return _copy_list(
        profile.get(
            "context_evidence",
            []
        )
    )


def get_runtime_profile(
    career_name
):

    profile = _profile_or_none(
        career_name
    )

    if profile is None:
        return None


    mode = profile.get(
        "readiness_mode"
    )


    runtime = {
        "career_name":
            profile.get(
                "career_name",
                career_name
            ),

        "readiness_mode":
            mode,

        "readiness_percentage_allowed":
            allows_readiness(
                career_name
            ),

        "source_coverage":
            profile.get(
                "source_coverage"
            ),

        "core_requirements":
            get_core_requirements(
                career_name
            ),

        "important_requirements":
            get_important_requirements(
                career_name
            ),

        "supporting_evidence":
            get_supporting_evidence(
                career_name
            ),

        "functional_evidence":
            get_functional_evidence(
                career_name
            ),

        "context_evidence":
            get_context_evidence(
                career_name
            ),
    }


    readiness_count = (
        len(
            runtime[
                "core_requirements"
            ]
        )
        +
        len(
            runtime[
                "important_requirements"
            ]
        )
    )


    if (
        mode in READINESS_MODES
        and
        readiness_count == 0
    ):

        raise RuntimeProfileError(
            f"{career_name}: readiness-enabled profile "
            "contains no readiness requirements."
        )


    if (
        mode == ROUTING_ONLY_MODE
        and
        readiness_count != 0
    ):

        raise RuntimeProfileError(
            f"{career_name}: routing-only profile "
            "exposed readiness requirements."
        )


    if mode == SAFE_SHELL_MODE:

        runtime_evidence_count = (
            readiness_count
            +
            len(
                runtime[
                    "supporting_evidence"
                ]
            )
            +
            len(
                runtime[
                    "functional_evidence"
                ]
            )
            +
            len(
                runtime[
                    "context_evidence"
                ]
            )
        )


        if runtime_evidence_count != 0:

            raise RuntimeProfileError(
                f"{career_name}: safe shell "
                "contains runtime evidence."
            )


    return runtime


def list_readiness_enabled_careers():

    result = []

    for career_name in list_v2_careers():

        if allows_readiness(
            career_name
        ):

            result.append(
                career_name
            )

    return result


def list_routing_only_careers():

    result = []

    for career_name in list_v2_careers():

        if (
            get_readiness_mode(
                career_name
            )
            ==
            ROUTING_ONLY_MODE
        ):

            result.append(
                career_name
            )

    return result


def list_safe_shell_careers():

    result = []

    for career_name in list_v2_careers():

        if (
            get_readiness_mode(
                career_name
            )
            ==
            SAFE_SHELL_MODE
        ):

            result.append(
                career_name
            )

    return result
