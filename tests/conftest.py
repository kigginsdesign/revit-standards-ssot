"""Shared pytest fixtures and session-level guards."""

import pytest
from revit_standards_ssot.db import _DEFAULT_DB_PATH


@pytest.fixture(scope="session", autouse=True)
def assert_runtime_db_not_touched():
    """Regression guard: no test may create or modify the runtime database.

    All test sessions must use in-memory SQLite only. If this fixture fails,
    a test is directly or indirectly calling make_session_factory() without
    supplying an explicit db_path.
    """
    existed_before = _DEFAULT_DB_PATH.exists()
    mtime_before = _DEFAULT_DB_PATH.stat().st_mtime if existed_before else None

    yield

    if not existed_before:
        assert not _DEFAULT_DB_PATH.exists(), (
            f"A test created the runtime database at {_DEFAULT_DB_PATH}. "
            "Tests must use in-memory SQLite only (sqlite:///:memory:)."
        )
    else:
        mtime_after = _DEFAULT_DB_PATH.stat().st_mtime if _DEFAULT_DB_PATH.exists() else None
        assert mtime_after == mtime_before, (
            f"A test modified the runtime database at {_DEFAULT_DB_PATH}. "
            "Tests must use in-memory SQLite only (sqlite:///:memory:)."
        )
