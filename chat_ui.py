import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="Restaurant Chatbot", page_icon="🍽️")

st.title("🍽️ Restaurant Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for chat in st.session_state.messages:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Chat input from user
user_input = st.chat_input("Ask the restaurant assistant...")

if user_input:
    # Store and show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Default bot reply
    bot_reply = "Sorry, I didn't understand that."

    # Send request to FastAPI backend
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": user_input},
            timeout=35,
        )
        response.raise_for_status()  # Catch HTTP errors
        data = response.json()
        bot_reply = data.get("response", bot_reply)
    except requests.HTTPError:
        try:
            error_payload = response.json()
            detail = error_payload.get("detail", response.text)
        except ValueError:
            detail = response.text
        bot_reply = f"❌ Backend error: {detail}"
    except requests.RequestException as e:
        bot_reply = f"❌ Error contacting backend: {e}"

    # Display bot reply with spinner
    with st.chat_message("assistant"):
        with st.spinner("🤖 Thinking..."):
            st.markdown(bot_reply)

    # Store bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
