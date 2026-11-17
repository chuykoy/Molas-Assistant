 import streamlit as st
from google import genai

st.set_page_config(page_title="Molas AI Assistant", page_icon="🤖")
st.title("🗣️ Molas AI Assistant")

# Sidebar para sa mga settings at reset button
with st.sidebar:
    st.header("⚙️ Mga Setting")
    if st.button("🗑️ I-clear ang Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    st.info(
        "Tip: Pwede mong i-reset ang usapan anumang oras gamit ang button sa itaas."
    )

# Kunin ang API key mula sa Streamlit Secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Ipakita ang mga lumang messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input ng user
if prompt := st.chat_input("Mag-type kay Molas AI..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Nag-iisip si Molas AI..."):
            system_instruction = (
                "Ikaw si Molas AI, isang matulungin, magalang, at matalinong AI "
                "assistant na bihasa magsalita sa Tagalog at Taglish."
            )

            chat_history = []
            for m in st.session_state["messages"]:
                role = "user" if m["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [{"text": m["content"]}]})

            chat = client.chats.create(
                model="gemini-2.5-flash",
                history=chat_history[:-1],
            )
            response = chat.send_message(
                prompt,
                config={
                    "system_instruction": system_instruction,
                },
            )
            st.markdown(response.text)
            st.session_state["messages"].append(
                {"role": "assistant", "content": response.text}
            )
