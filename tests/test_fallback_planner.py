from voxagent.fallback import LocalFallbackPlanner, LocalFallbackResponder


def test_fallback_planner_extracts_code_and_summary_actions() -> None:
    planner = LocalFallbackPlanner()

    actions, intents, notes, requires_confirmation = planner.plan(
        "Create a Python file called retry_helper.py with a retry function and summarize this design note."
    )

    assert intents == ["summarize_text", "create_file", "write_code"]
    assert requires_confirmation is True
    assert notes
    assert actions[1].target_file == "retry_helper.py"
    assert actions[2].target_file == "retry_helper.py"


def test_fallback_planner_detects_folder_creation() -> None:
    planner = LocalFallbackPlanner()

    actions, intents, _, _ = planner.plan("Create a folder named reports")

    assert intents == ["create_file"]
    assert actions[0].target_folder == "reports"


def test_fallback_planner_understands_spoken_extension() -> None:
    planner = LocalFallbackPlanner()

    actions, intents, _, _ = planner.plan(
        "Create a Python file named retry_helper dot py with a retry function"
    )

    assert "write_code" in intents
    assert actions[-1].target_file == "retry_helper.py"


def test_fallback_responder_generates_local_summary() -> None:
    responder = LocalFallbackResponder()

    summary = responder.summarize(
        "Local agents combine speech recognition, intent planning, and tool execution. "
        "They can automate practical tasks with visible steps."
    )

    assert "Local agents combine speech recognition" in summary
