import os
import random
from datetime import datetime
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage


st.set_page_config(
    page_title="Sustainable Agriculture Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_weather_forecast(location):
    weather = {
        "california": "Sunny, 22°C (Optimal for wheat & corn)",
        "india": "Monsoon / Partly Cloudy, 29°C (Good humidity)",
        "texas": "Warm & Dry, 28°C (Requires scheduled irrigation)",
        "punjab": "Mild & Sunny, 24°C (Favorable growing conditions)",
    }
    return weather.get(str(location).strip().lower(), f"Moderate, 25°C (Simulated conditions for {location})")


def estimate_crop_yield(crop_type, soil_health, weather):
    base = 80 if soil_health == 'Good' else (65 if soil_health == 'Average' else 45)
    bonus = 10 if "Sunny" in weather or "Optimal" in weather else 0
    return base + bonus + random.randint(-5, 5)


def generate_farming_calendar(crop_type):
    crop_lower = str(crop_type).strip().lower()
    calendars = {
        "wheat": {"Planting": "October - November", "Irrigation": "December - January", "Harvesting": "April - May"},
        "corn": {"Planting": "May - June", "Irrigation": "July - August", "Harvesting": "September - October"},
        "rice": {"Planting": "June - July", "Irrigation": "Constant submerged", "Harvesting": "November - December"},
        "tomato": {"Planting": "March - April", "Trellising": "May", "Harvesting": "July - August"},
        "cotton": {"Planting": "April - May", "Pest Monitoring": "July - August", "Harvesting": "October - November"}
    }
    return calendars.get(crop_lower, {
        "Planting": "Early Spring / Monsoon Start",
        "Fertilization & Weeding": "30 days post-germination",
        "Harvesting": "90 - 120 days depending on local variety"
    })


def main():
    st.title("🌾 Sustainable Agriculture Advisor for Small Farmers")
    st.markdown("Tailored guidance on crop selection, pest management, and sustainable soil practices powered by **Groq** LPUs.")

    # Sidebar settings
    st.sidebar.title("⚙️ Settings & Key")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = st.sidebar.text_input(
            "Groq API Key",
            type="password",
            help="Free API key from https://console.groq.com"
        )
        if not api_key:
            st.info("💡 Please enter your **Groq API Key** in the left sidebar to generate AI farming advice.")

    model = st.sidebar.selectbox(
        "AI Model",
        ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768']
    )

    system_prompt = st.sidebar.text_area(
        "Advisor Persona",
        "You are an expert agronomist dedicated to assisting smallholder farmers with practical, cost-effective, organic, and climate-resilient farming techniques."
    )

    st.sidebar.write("---")
    st.sidebar.write("### 💡 Farming Tip of the Day")
    tips = [
        "Rotate legumes with cereals to naturally restore soil nitrogen.",
        "Mulching reduces soil evaporation by up to 70% and suppresses weeds.",
        "Introduce beneficial predator insects (like ladybugs) to curb aphid populations without chemicals.",
        "Adopt drip irrigation or furrow mulching to safeguard water reservoirs."
    ]
    st.sidebar.info(random.choice(tips))

    # Form inputs
    with st.form("agri_form"):
        col1, col2 = st.columns(2)
        with col1:
            crop_type = st.text_input("Crop Type (e.g., Wheat, Corn, Rice, Tomato):", value="Wheat")
            location = st.text_input("Farm Location / Region (e.g., Punjab, California, Kenya):", value="Punjab")

        with col2:
            soil_health = st.selectbox("Soil Quality:", ['Good', 'Average', 'Poor'])
            pest_problem = st.text_input("Pest Concern or Symptoms (Optional):", placeholder="e.g. Yellowing leaves, stem borers")

        submit = st.form_submit_button("🌱 Get Tailored Farming Advice", type="primary")

    if submit:
        if not crop_type or not location:
            st.warning("Please provide both crop type and location.")
            return

        weather = get_weather_forecast(location)
        est_yield = estimate_crop_yield(crop_type, soil_health, weather)
        calendar = generate_farming_calendar(crop_type)

        # Overview cards
        k1, k2, k3 = st.columns(3)
        k1.metric("Local Weather Outlook", weather)
        k2.metric("Projected Yield Index", f"{est_yield} quintals/ha")
        k3.metric("Soil Status", soil_health)

        st.write("---")

        # Calendar
        st.subheader(f"📅 Recommended Crop Calendar: {crop_type}")
        cols = st.columns(len(calendar))
        for col, (stage, timing) in zip(cols, calendar.items()):
            with col:
                st.caption(stage)
                st.write(f"**{timing}**")

        st.write("---")

        # AI Agronomist Consultation
        st.subheader("🤖 Agronomist Action Plan")
        if not api_key:
            st.error("Please provide a Groq API Key in the sidebar to view the tailored AI plan.")
            return

        with st.spinner("Consulting agricultural knowledge base..."):
            try:
                groq_chat = ChatGroq(groq_api_key=api_key, model_name=model)
                query = (
                    f"Provide an actionable, structured sustainable farming plan for growing {crop_type} in {location}. "
                    f"Soil status is {soil_health}. "
                    f"{'Pest issues reported: ' + pest_problem if pest_problem else 'No specific pest reported.'} "
                    f"Include: 1) Soil Preparation & Organic Amendments, 2) Water & Irrigation Strategy, "
                    f"3) Pest & Disease Prevention (Organic/IPM), 4) Post-Harvest & Storage."
                )
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessagePromptTemplate.from_template("{query}").format(query=query)
                ]
                res = groq_chat.invoke(messages)
                st.markdown(res.content)
            except Exception as e:
                st.error(f"Error fetching farming advice: {e}")


if __name__ == "__main__":
    main()
