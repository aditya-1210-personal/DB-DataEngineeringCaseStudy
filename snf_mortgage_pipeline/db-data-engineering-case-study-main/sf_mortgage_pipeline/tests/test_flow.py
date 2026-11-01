from unittest.mock import MagicMock, patch

from orchestration import flow


def test_execute_success():
    result = MagicMock()
    result.returncode = 0
    result.stdout = "success"

    with patch.object(
        flow.subprocess,
        "run",
        return_value=result,
    ) as run:
        output = flow.execute(["echo", "ok"])

    assert output == "success"
    run.assert_called_once()


def test_execute_failure():
    result = MagicMock()
    result.returncode = 1
    result.stderr = "command failed"

    with patch.object(
        flow.subprocess,
        "run",
        return_value=result,
    ):
        try:
            flow.execute(["false"])
            assert False, "Expected RuntimeError"
        except RuntimeError:
            pass


def test_flow_tasks_are_registered():
    assert flow.generate_data.name == "generate_data"
    assert flow.load_sources.name == "load_sources"
    assert flow.dbt_build.name == "dbt_build"
