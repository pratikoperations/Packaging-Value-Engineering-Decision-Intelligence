"""Versioned, reviewable 25-field alias registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Tuple


class FieldRegistryError(ValueError):
    pass


@dataclass(frozen=True)
class FieldRegistry:
    schema_version: str
    aliases: Mapping[str, Tuple[str, ...]]

    @property
    def field_names(self) -> Tuple[str, ...]:
        return tuple(self.aliases)

    def aliases_for(self, field_name: str) -> Tuple[str, ...]:
        try:
            return self.aliases[field_name]
        except KeyError as exc:
            raise FieldRegistryError(f"Unsupported governed field: {field_name}") from exc


def default_registry_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "pve_2_0_word_fields.json"


def load_field_registry(path: Path | None = None) -> FieldRegistry:
    registry_path = path or default_registry_path()
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FieldRegistryError("Field registry is unreadable or malformed.") from exc

    version = payload.get("schema_version")
    raw_fields = payload.get("fields")
    if not isinstance(version, str) or not version:
        raise FieldRegistryError("Field registry schema_version is required.")
    if not isinstance(raw_fields, dict) or len(raw_fields) != 25:
        raise FieldRegistryError("Field registry must define exactly 25 governed fields.")

    aliases: dict[str, Tuple[str, ...]] = {}
    for name, values in raw_fields.items():
        if not isinstance(name, str) or not name:
            raise FieldRegistryError("Field names must be non-empty strings.")
        if not isinstance(values, list) or not values or not all(isinstance(v, str) and v for v in values):
            raise FieldRegistryError(f"Aliases for {name} must be non-empty strings.")
        aliases[name] = tuple(dict.fromkeys(v.strip().lower() for v in values))

    return FieldRegistry(schema_version=version, aliases=aliases)
