from pathlib import Path
import json
import hashlib
from functools import lru_cache


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

V1_PROFILE_PATH = (
    REFERENCE_DIR
    / "role_skill_profiles.json"
)

V2_PROFILE_PATH = (
    REFERENCE_DIR
    / "career_profiles_v2.json"
)

V2_MANIFEST_PATH = (
    REFERENCE_DIR
    / "career_profiles_v2_manifest.json"
)

V2_CHECKSUM_PATH = (
    REFERENCE_DIR
    / "career_profiles_v2.sha256"
)


class ProfileArtifactError(RuntimeError):
    """Raised when a profile artifact fails integrity validation."""


def _load_json(path: Path):

    if not path.exists():

        raise FileNotFoundError(
            f"Profile artifact not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def _sha256(path: Path):

    if not path.exists():

        raise FileNotFoundError(
            f"Profile artifact not found: {path}"
        )

    with path.open(
        "rb"
    ) as f:

        return hashlib.sha256(
            f.read()
        ).hexdigest()


@lru_cache(maxsize=1)
def load_v1_profiles():

    data = _load_json(
        V1_PROFILE_PATH
    )

    if not isinstance(
        data,
        dict
    ):

        raise ProfileArtifactError(
            "V1 profile artifact must be a JSON object."
        )

    return data


@lru_cache(maxsize=1)
def load_v2_artifact(
    verify_checksum=True
):

    artifact = _load_json(
        V2_PROFILE_PATH
    )


    if not isinstance(
        artifact,
        dict
    ):

        raise ProfileArtifactError(
            "V2 profile artifact must be a JSON object."
        )


    if verify_checksum:

        if not V2_CHECKSUM_PATH.exists():

            raise ProfileArtifactError(
                "V2 checksum file is missing."
            )


        expected_hash = (
            V2_CHECKSUM_PATH
            .read_text(
                encoding="utf-8"
            )
            .strip()
            .split()[0]
        )


        actual_hash = _sha256(
            V2_PROFILE_PATH
        )


        if actual_hash != expected_hash:

            raise ProfileArtifactError(
                "V2 profile checksum verification failed."
            )


    if artifact.get(
        "schema_version"
    ) != "2.0":

        raise ProfileArtifactError(
            "Unsupported V2 profile schema version."
        )


    if artifact.get(
        "profile_status"
    ) != "frozen":

        raise ProfileArtifactError(
            "V2 profile artifact is not frozen."
        )


    profiles = artifact.get(
        "profiles"
    )


    if not isinstance(
        profiles,
        dict
    ):

        raise ProfileArtifactError(
            "V2 profiles field must be a JSON object."
        )


    if len(
        profiles
    ) != 201:

        raise ProfileArtifactError(
            f"Expected 201 V2 profiles, found {len(profiles)}."
        )


    return artifact


@lru_cache(maxsize=1)
def load_v2_profiles(
    verify_checksum=True
):

    return load_v2_artifact(
        verify_checksum=verify_checksum
    )["profiles"]


@lru_cache(maxsize=1)
def load_v2_manifest():

    manifest = _load_json(
        V2_MANIFEST_PATH
    )

    if not isinstance(
        manifest,
        dict
    ):

        raise ProfileArtifactError(
            "V2 manifest must be a JSON object."
        )

    return manifest


def get_v1_profile(
    career_name
):

    profiles = load_v1_profiles()

    return profiles.get(
        career_name
    )


def get_v2_profile(
    career_name
):

    profiles = load_v2_profiles()

    return profiles.get(
        career_name
    )


def get_v2_readiness_mode(
    career_name
):

    profile = get_v2_profile(
        career_name
    )

    if profile is None:

        return None

    return profile.get(
        "readiness_mode"
    )


def v2_allows_readiness_percentage(
    career_name
):

    profile = get_v2_profile(
        career_name
    )

    if profile is None:

        return False

    return bool(
        profile.get(
            "readiness_percentage_allowed",
            False
        )
    )


def list_v1_careers():

    return sorted(
        load_v1_profiles().keys()
    )


def list_v2_careers():

    return sorted(
        load_v2_profiles().keys()
    )


def clear_profile_loader_cache():

    load_v1_profiles.cache_clear()
    load_v2_artifact.cache_clear()
    load_v2_profiles.cache_clear()
    load_v2_manifest.cache_clear()
