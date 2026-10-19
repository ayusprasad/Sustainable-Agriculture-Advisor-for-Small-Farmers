from app import build_messages, generate_farming_calendar


def test_calendar_matches_crop_names_without_case_sensitivity():
    assert generate_farming_calendar(" WHEAT ")["Planting"] == "October–November"
    assert generate_farming_calendar("rice") is None


def test_build_messages_includes_farmer_context_and_question():
    messages = build_messages(
        "Be practical",
        "Tomatoes",
        "Tamil Nadu",
        "Average",
        "Aphids",
        [],
        "How can I reduce pest pressure?",
        memory_turns=3,
    )

    assert messages[0]["role"] == "system"
    assert "crop=Tomatoes" in messages[0]["content"]
    assert "Pest concern: Aphids." in messages[0]["content"]
    assert messages[-1] == {
        "role": "user",
        "content": "How can I reduce pest pressure?",
    }


def test_build_messages_limits_history_to_requested_turns():
    history = [
        {"role": "user", "content": "old question"},
        {"role": "assistant", "content": "old answer"},
        {"role": "user", "content": "recent question"},
        {"role": "assistant", "content": "recent answer"},
    ]

    messages = build_messages("", "Wheat", "India", "Unknown", "", history, "next", 1)

    assert messages[1:] == [
        {"role": "user", "content": "recent question"},
        {"role": "assistant", "content": "recent answer"},
        {"role": "user", "content": "next"},
    ]
