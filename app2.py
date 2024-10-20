import langchain_groq
import streamlit as st
import os
import random
import streamlit.components.v1 as components
from groq import Groq
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from datetime import datetime


# Dummy function for weather data (replace with actual weather API integration)
def get_weather_forecast(location):
    weather = {
        "California": "Sunny, 22°C",
        "India": "Partly Cloudy, 30°C",
    }
    return weather.get(location, "Weather data not available")


# Dummy function for crop yield estimation (simplified for demo purposes)
def estimate_crop_yield(crop_type, soil_health, weather):
    if soil_health == 'Good' and 'Sunny' in weather:
        return random.randint(80, 100)
    else:
        return random.randint(50, 79)


# Farming Calendar Function
def generate_farming_calendar(crop_type):
    current_month = datetime.now().month
    calendar = {
        "Wheat": {"Planting": "October-November", "Irrigation": "December-January", "Harvesting": "April-May"},
        "Corn": {"Planting": "May-June", "Irrigation": "July-August", "Harvesting": "September-October"},
    }
    crop_calendar = calendar.get(crop_type, "No calendar available for this crop.")
    return crop_calendar


# Main function for the Streamlit app
def main():
    st.set_page_config(page_title="Sustainable Agriculture Advisor", layout="wide", initial_sidebar_state="expanded")
    
    # Add HubSpot script using components.html
    components.html(
        """
        <!-- Start of HubSpot Embed Code -->
        <script type="text/javascript" id="hs-script-loader" async defer src="//js-na1.hs-scripts.com/47792726.js"></script>
        <!-- End of HubSpot Embed Code -->
        """,
        height=0,  # Adjust height as needed
    )
    
    st.markdown("""
    <style>
        .reportview-container {
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
        }
        h1 {
            text-align: center;
            font-size: 3em;
            color: #ffdd59;
        }
        .sidebar .sidebar-content {
            background: #292E49;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # Get Groq API key
    api_key = os.getenv("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")
    client = Groq(api_key="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")

    # Display the logo and title
    st.title("Sustainable Agriculture Advisor")
    st.write("🚜 Get tailored advice on crop selection, pest management, and sustainable farming practices!")

    # Sidebar options
    st.sidebar.title('Settings')
    system_prompt = st.sidebar.text_area("Customize System Prompt:", "You are a helpful agricultural assistant.")
    model = st.sidebar.selectbox('Choose a Model', ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it'])
    conversational_memory_length = st.sidebar.slider('Conversational Memory Length:', 1, 10, value=5)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history",
                                            return_messages=True)

    crop_type = st.text_input("Enter Crop Type (e.g., Wheat, Corn):")
    location = st.text_input("Enter your Location (e.g., California, India):")
    pest_problem = st.text_input("Enter Pest Concern (optional):")
    soil_health = st.selectbox("Soil Health (choose closest match):", ['Good', 'Average', 'Poor'])

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    else:
        for message in st.session_state.chat_history:
            memory.save_context({'input': message['human']}, {'output': message['AI']})

    # Initialize the Groq Langchain chat object
    groq_chat = ChatGroq(groq_api_key="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", model_name=model)

    if crop_type and location:
        # Modify the system prompt to include farming advice
        system_prompt += f" You are helping a farmer from {location} with advice on growing {crop_type}."
        if pest_problem:
            system_prompt += f" The farmer is facing a pest issue with {pest_problem}."

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{human_input}"),
            ]
        )

        conversation = LLMChain(
            llm=groq_chat,
            prompt=prompt,
            verbose=True,
            memory=memory,
        )

        # The user's question is now based on agricultural advice
        user_question = f"Advice for growing {crop_type} in {location}, with potential pest issues: {pest_problem}."
        response = conversation.predict(human_input=user_question)

        message = {'human': user_question, 'AI': response}
        st.session_state.chat_history.append(message)

        # Display the response from the chatbot
        st.write(f"**Farming Advice:** {response}")

        # New Feature: Display Weather Forecast
        weather_forecast = get_weather_forecast(location)
        st.write(f"**Weather Forecast for {location}:** {weather_forecast}")

        # New Feature: Estimate Crop Yield
        estimated_yield = estimate_crop_yield(crop_type, soil_health, weather_forecast)
        st.write(f"**Estimated Crop Yield for {crop_type}:** {estimated_yield} quintals")

        # New Feature: Farming Calendar
        farming_calendar = generate_farming_calendar(crop_type)
        if isinstance(farming_calendar, dict):
            st.write(f"### 📅 Farming Calendar for {crop_type}:")
            for activity, timing in farming_calendar.items():
                st.write(f"- **{activity}:** {timing}")
        else:
            st.write(farming_calendar)

        # Allow user feedback
        st.sidebar.write("Did you find this helpful?")
        st.sidebar.button("👍 Yes")
        st.sidebar.button("👎 No")

    # New feature: Sustainable Farming Tip of the Day
    st.sidebar.write("## 🌾 Sustainable Farming Tip of the Day")
    tips = [
        "Rotate crops to improve soil health.",
        "Use organic fertilizers to enhance yields.",
        "Integrated pest management reduces the need for pesticides.",
        "Conserve water by using drip irrigation."
    ]
    st.sidebar.write(random.choice(tips))

    # New feature: Favorite Responses
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []

    if st.button("Save Response"):
        st.session_state.favorites.append(response)
        st.sidebar.write("✅ Response saved!")

    st.sidebar.write("## ⭐ Your Saved Responses")
    for fav in st.session_state.favorites:
        st.sidebar.write(f"- {fav}")


if __name__ == "__main__":
    main()
