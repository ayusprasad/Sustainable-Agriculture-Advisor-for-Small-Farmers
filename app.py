from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODELS = {
    "GPT OSS 20B": "openai/gpt-oss-20b",
    "GPT OSS 120B": "openai/gpt-oss-120b",
}
FARMING_CALENDARS = {
    "wheat": {
        "Planting": "October–November",
        "Irrigation": "December–January",
        "Harvesting": "April–May",
    },
    "corn": {
        "Planting": "May–June",
        "Irrigation": "July–August",
        "Harvesting": "September–October",
    },
}
SUSTAINABILITY_TIPS = [
    "Rotate crops where practical to support soil health.",
    "Use integrated pest management to reduce unnecessary pesticide use.",
    "Conserve water with irrigation practices suited to local soil and climate.",
    "Keep soil covered between crops to reduce erosion and moisture loss.",
]


def generate_farming_calendar(crop_type: str) -> dict[str, str] | None:
    """Return a demonstration calendar for supported crops."""
    return FARMING_CALENDARS.get(crop_type.strip().lower())


def build_messages(
    system_prompt: str,
    crop_type: str,
    location: str,
    soil_health: str,
    pest_problem: str,
    history: list[dict[str, str]],
    question: str,
    memory_turns: int,
) -> list[dict[str, str]]:
    """Build a bounded chat request with the farmer's context."""
    base_prompt = system_prompt.strip() or "You are a helpful sustainable agriculture assistant."
    context = (
        f"{base_prompt}\n\nFarmer context: crop={crop_type.strip()}, "
        f"location={location.strip()}, soil condition={soil_health.strip()}."
    )
    if pest_problem.strip():
        context += f" Pest concern: {pest_problem.strip()}."
    messages = [{"role": "system", "content": context}]

    for message in history[-max(0, memory_turns * 2) :]:
        role = message.get("role")
        content = message.get("content", "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    current_question = question.strip()
    if current_question:
        messages.append({"role": "user", "content": current_question})
    return messages


def request_advice(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> str:
    response: Any = Groq(api_key=api_key).chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content or ""


def main() -> None:
    st.set_page_config(page_title="Sustainable Agriculture Advisor", page_icon="🌱", layout="wide")
    st.title("Sustainable Agriculture Advisor")
    st.caption("Practical, context-aware guidance for small-farm planning.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "farmer_context" not in st.session_state:
        st.session_state.farmer_context = None
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    with st.sidebar:
        st.header("Settings")
        model_label = st.selectbox("Model", list(MODELS))
        memory_turns = st.slider("Recent turns to include", min_value=1, max_value=10, value=5)
        system_prompt = st.text_area(
            "Assistant instructions",
            value="Give practical, cautious advice. Ask for local details when they matter.",
            max_chars=2_000,
        )
        st.info("Use local agronomy guidance to validate recommendations.")
        st.subheader("Saved recommendations")
        if st.session_state.favorites:
            for favorite in st.session_state.favorites:
                st.markdown(f"- {favorite}")
        else:
            st.caption("Save a recommendation to keep it for this session.")

    with st.form("farm_context"):
        left, right = st.columns(2)
        with left:
            crop_type = st.text_input("Crop", placeholder="For example, wheat")
            location = st.text_input("Location", placeholder="District, region, or country")
            soil_health = st.selectbox("Soil condition", ["Unknown", "Good", "Average", "Poor"])
        with right:
            pest_problem = st.text_area("Pest or disease concern (optional)", max_chars=1_000)
            question = st.text_area(
                "What would you like help with?",
                value="Suggest sustainable practices for this crop and soil condition.",
                max_chars=2_000,
            )
        submitted = st.form_submit_button("Get farming guidance", type="primary")

    if submitted:
        if not crop_type.strip() or not location.strip():
            st.error("Enter a crop and location to get tailored guidance.")
        elif not question.strip():
            st.error("Enter a question for the advisor.")
        elif not os.getenv("GROQ_API_KEY", "").strip():
            st.error("GROQ_API_KEY is missing. Add it to your local .env file and restart Streamlit.")
        else:
            context = {
                "crop_type": crop_type.strip(),
                "location": location.strip(),
                "soil_health": soil_health,
                "pest_problem": pest_problem.strip(),
            }
            initial_messages = build_messages(
                system_prompt,
                context["crop_type"],
                context["location"],
                context["soil_health"],
                context["pest_problem"],
                [],
                question,
                memory_turns,
            )
            with st.spinner("Preparing farming guidance..."):
                try:
                    answer = request_advice(
                        os.environ["GROQ_API_KEY"],
                        MODELS[model_label],
                        initial_messages,
                    )
                except Exception:
                    st.error("The request failed. Check the API key, model access, and network connection, then retry.")
                else:
                    st.session_state.farmer_context = {
                        **context,
                        "system_prompt": system_prompt,
                    }
                    st.session_state.messages = [
                        {"role": "user", "content": question.strip()},
                        {"role": "assistant", "content": answer or "The model returned an empty response."},
                    ]

    context = st.session_state.farmer_context
    if context:
        st.subheader(f"Guidance for {context['crop_type']} in {context['location']}")
        calendar = generate_farming_calendar(context["crop_type"])
        if calendar:
            st.markdown("**Example crop calendar**")
            st.table([{"Activity": activity, "Timing": timing} for activity, timing in calendar.items()])
            st.caption("Calendar timing is illustrative; confirm it against local conditions.")
        st.info(SUSTAINABILITY_TIPS[0])

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
            if st.button("Save latest recommendation"):
                latest = st.session_state.messages[-1]["content"]
                if latest not in st.session_state.favorites:
                    st.session_state.favorites.append(latest)
                st.success("Saved for this session.")

        follow_up = st.chat_input("Ask a follow-up question")
        if follow_up:
            api_key = os.getenv("GROQ_API_KEY", "").strip()
            if not api_key:
                st.error("GROQ_API_KEY is missing. Add it to your local .env file and restart Streamlit.")
            else:
                messages = build_messages(
                    context["system_prompt"],
                    context["crop_type"],
                    context["location"],
                    context["soil_health"],
                    context["pest_problem"],
                    st.session_state.messages,
                    follow_up,
                    memory_turns,
                )
                with st.spinner("Preparing an answer..."):
                    try:
                        answer = request_advice(api_key, MODELS[model_label], messages)
                    except Exception:
                        st.error("The request failed. Check the API key, model access, and network connection, then retry.")
                    else:
                        st.session_state.messages.extend(
                            [
                                {"role": "user", "content": follow_up},
                                {
                                    "role": "assistant",
                                    "content": answer or "The model returned an empty response.",
                                },
                            ]
                        )
                        st.rerun()


if __name__ == "__main__":
    main()
