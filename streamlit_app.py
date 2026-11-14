import streamlit as st
from groq import Groq
from gtts import gTTS

st.set_page_config(page_title="Molas AI Mobile", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .avatar-container { display: flex; justify-content: center; margin-bottom: 20px; }
    .pulse-avatar {
        width: 100px; height: 100px; border-radius: 50%;
        background: linear-gradient(45deg, #ff4b4b, #ff8f00);
        display: flex; justify-content: center; align-items: center;
        font-size: 50px; animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); }
        70% { transform: scale(1); }
        100% { transform: scale(0.95); }
    }
    </style>
    <div class="avatar-container"><div class="pulse-avatar">🤖</div></div>
""", unsafe_allow_html=True)

st.title("🗣️ Molas AI Assistant")

if "GROQ_API_KEY" not in st.secrets:
    st.error("Ilagay muna ang GROQ_API_KEY sa Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "Ikaw si Molas AI, isang matalinong personal assistant na nagsasalita sa Tagalog."}
    ]

for message in st.session_state["messages"]:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Mag-type kay Molas AI..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=st.session_state["messages"]
    )
    ai_response = response.choices[0].message.content

    st.session_state["messages"].append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)
        tts = gTTS(text=ai_response, lang='tl')
        tts.save("molas_voice.mp3")
        st.audio("molas_voice.mp3", format="audio/mp3", autoplay=True)
