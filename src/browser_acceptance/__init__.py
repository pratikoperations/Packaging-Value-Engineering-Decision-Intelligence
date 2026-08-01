from __future__ import annotations


def run_minimal_acceptance():
    """Load the optional Playwright runner only when browser execution is requested."""
    from .minimal_runner import run_minimal_acceptance as _run_minimal_acceptance

    return _run_minimal_acceptance()


__all__ = ["run_minimal_acceptance"]
