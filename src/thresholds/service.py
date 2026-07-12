from __future__ import annotations

from typing import Any

from src.persistence.threshold_repository import ThresholdRepository
from src.thresholds.models import ThresholdValidationError
from src.thresholds.policy import DEFAULT_CONTROLLED_PROFILE, validate_threshold_profile

DEFAULT_PROFILE_NAME = "PVE Controlled Default"


class ThresholdService:
    def __init__(self, thresholds: ThresholdRepository) -> None:
        self.thresholds = thresholds

    def ensure_default_profile(self) -> dict[str, Any]:
        return self.thresholds.create_version(
            profile_name=DEFAULT_PROFILE_NAME,
            profile=DEFAULT_CONTROLLED_PROFILE,
            project_id=None,
        )

    def create_project_profile(
        self,
        *,
        project_id: str,
        profile_name: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        clean_name = profile_name.strip()
        if not clean_name:
            raise ThresholdValidationError("Profile name is required.")
        try:
            normalized = validate_threshold_profile(profile)
        except ValueError as error:
            raise ThresholdValidationError(str(error)) from error
        return self.thresholds.create_version(
            profile_name=clean_name,
            profile=normalized,
            project_id=project_id,
        )

    def create_new_version(
        self,
        *,
        threshold_profile_id: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        current = self.thresholds.get(threshold_profile_id)
        if current["project_id"] is None:
            raise ThresholdValidationError("The controlled default profile cannot be edited.")
        return self.create_project_profile(
            project_id=current["project_id"],
            profile_name=current["profile_name"],
            profile=profile,
        )

    def available_profiles(self, project_id: str) -> list[dict[str, Any]]:
        self.ensure_default_profile()
        return self.thresholds.list_available(project_id)

    def get_profile(self, threshold_profile_id: str) -> dict[str, Any]:
        return self.thresholds.get(threshold_profile_id)
