 import streamlit as st
from google import genai
from google.genai.errors import APIError

st.set_page_config(
    page_title="Molas AI Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS para sa mas modern at malinis na UI
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .modern-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .modern-subtitle {
        color: #6B7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Modern Header
st.markdown('<div class="modern-title">✨ Molas AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="modern-subtitle">Ang iyong matalinong Tagalog & Taglish AI partner</div>',
    unsafe_allow_html=True,
)

# Sidebar para sa mga settings at reset button
with st.sidebar:
    st.header("⚙️ Mga Setting")
    if st.button("🗑️ Bagong Usapan", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    st.caption("Powered by Gemini")


@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


client = get_client()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if not st.session_state["messages"]:
    st.info("👋 Kumusta! Ano ang maitutulong ko sa iyo ngayong araw?")

USER_AVATAR = "🧑"
AI_AVATAR = "✨"

for msg in st.session_state["messages"]:
    avatar = USER_AVATAR if msg["role"] == "user" else AI_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Magtanong kahit ano kay Molas AI..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AI_AVATAR):
        system_instruction = (
            "Ikaw si Molas AI, isang matulungin, magalang, at matalinong AI assistant "
            "na bihasa magsalita sa Tagalog at Taglish.\n\n"
            "MAHALAGANG LIMITASYON AT PATAKARAN:\n"
            "1. Huwag sasagot ng mga malalalim o pribadong detalye tungkol sa totoong pagkakakilanlan, "
            "personal na impormasyon, lokasyon, o pribadong buhay ng iyong creator/may-ari.\n"
            "2. Limitahan ang sarili at tanggihan nang magalang ang mga hindi tamang tanong, "
            "sensitibong paksa, o mga tanong na lumalampas sa iyong saklaw bilang AI assistant.\n"
            "3. Kapag nagtanong ang user tungkol sa iyong pagkakakilanlan, sa creator mo, o ng mga "
            "hindi tamang tanong, laging sumagot nang magalang ng:\n"
            "'Kung may iba ka pang katanungan o nais linawin, mag-email ka na lang kay Chuy Molas o kay Chuy M. sa mga sumusunod na email: chuymolas219@gmail.com, moplasjong7@gmail.com, o celso.m37@yahoo.com.'"
        )

        chat_history = []
        for m in st.session_state["messages"]:
            role = "user" if m["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [{"text": m["content"]}]})

        # Subukan ang primary model at lumipat sa backup kung high demand (503)
        models_to_try = ["gemini-3.8-flash", "gemini-3.0-flash", "gemini-2.5-flash-lite"]
        full_reply = None

        for model_name in models_to_try:
            try:
                chat = client.chats.create(
                    model=model_name,
                    history=chat_history[:-1],
                )

                def stream_response():
                    response = chat.send_message_stream(
                        prompt,
                        config={"system_instruction": system_instruction},
                    )
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                full_reply = st.write_stream(stream_response)
                break
            except APIError:
                continue

        if full_reply:
            st.session_state["messages"].append(
                {"role": "assistant", "content": full_reply}
            )
        else:
            st.warning(
                "⏳ Medyo abala ang server ng AI ngayon. Pakisubukan ulit pagkalipas ng ilang segundo!"
            )
