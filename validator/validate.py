"""
Core validation for ADTR records against the v0.1 JSON Schema.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import jsonschema  # noqa: F401 — needed for Draft202012Validator
    from jsonschema import Draft202012Validator
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False


_SCHEMA_DIR = Path(__file__).parent.parent / "schema"
_DEFAULT_SCHEMA = _SCHEMA_DIR / "adtr-v0.1.schema.json"

# FIXME: should we support loading schemas from URLs too? parking it for now


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source: str = ""

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_record(data: dict, schema_path: Optional[str] = None) -> ValidationResult:
    """Run a record through schema validation + semantic checks."""

    if not _HAS_JSONSCHEMA:
        return ValidationResult(
            valid=False,
            errors=["Missing dependency: pip install jsonschema"],
        )

    sf = Path(schema_path) if schema_path else _DEFAULT_SCHEMA
    if not sf.exists():
        return ValidationResult(valid=False, errors=[f"Can't find schema: {sf}"])

    with open(sf) as fh:
        schema = json.load(fh)

    errs: list[str] = []
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        loc = ".".join(str(p) for p in err.absolute_path) or "(root)"
        errs.append(f"{loc}: {err.message}")

    # only bother with semantic checks if structurally valid
    warns = _check_semantics(data) if not errs else []

    return ValidationResult(valid=len(errs) == 0, errors=errs, warnings=warns)


def _check_semantics(data: dict) -> list[str]:
    """Stuff that JSON Schema can't catch on its own."""
    out = []
    payload = data.get("activity_payload", {})

    # uncertainty_flag without a description is technically valid but
    # not very useful for anyone reviewing this later
    if payload.get("uncertainty_flag") and not payload.get("uncertainty_description"):
        out.append(
            "activity_payload.uncertainty_description: flag is set but "
            "description is empty — a reviewer will want to know *what* "
            "the uncertainty was"
        )

    # accepted with no rationale = "I just clicked OK"
    if payload.get("developer_action") == "accepted" and not payload.get("rationale"):
        out.append(
            "activity_payload.rationale: 'accepted' with no rationale "
            "(hard to prove this was deliberate)"
        )

    # context tags
    tags = data.get("context_tags")
    if tags is None:
        out.append("context_tags: missing entirely, record is harder to route/filter")
    elif not tags.get("tags"):
        out.append(
            "context_tags.tags: empty list — at least one tag "
            "helps with categorisation"
        )

    # TODO: check for suspiciously short rationale (< 20 chars)?
    # Leaving for v0.2 — don't want to be too opinionated yet.

    return out
