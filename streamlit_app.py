import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Molas AI Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SYSTEM_INSTRUCTION = (
    "Ikaw si Molas AI, isang matulungin, magalang, at matalinong AI assistant "
    "na bihasa magsalita sa Tagalog at Taglish.\n\n"
    "MAHALAGANG LIMITASYON AT PATAKARAN:\n"
    "1. Huwag sasagot ng mga malalalim o pribadong detalye tungkol sa totoong pagkakakilanlan, "
    "personal na impormasyon, lokasyon, o pribadong buhay ng iyong creator/may-ari.\n"
    "2. Limitahan ang sarili at tanggihan nang magalang ang mga hindi tamang tanong, "
    "sensitibong paksa, o mga tanong na lumalampas sa iyong saklaw bilang AI assistant.\n"
    "3. Kapag nagtanong ang user tungkol sa iyong pagkakakilanlan, sa creator mo, o ng mga "
    "hindi tamang tanong, laging sumagot nang magalang ng:\n"
    "'Kung may iba ka pang katanungan o nais linawin, mag-email ka na lang kay Chuy Molas o kay Chuy M. sa mga sumusunod na email: chuymolas219@gmail.com, molasjong7@gmail.com, o celso.m37@yahoo.com.'"
)

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

st.markdown('<div class="modern-title">✨ Molas AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="modern-subtitle">Ang iyong matalinong Tagalog & Taglish AI partner</div>',
    unsafe_allow_html=True,
)

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
        recent_messages = st.session_state["messages"][-10:]
        contents = [
            {
                "role": "user" if m["role"] == "user" else "model",
                "parts": [{"text": m["content"]}],
            }
            for m in recent_messages
        ]

        full_reply = None
        last_error = ""

        try:
            def stream_response():
                response = client.models.generate_content_stream(
                    model="gemini-3.8-flash",  # ✅ IN-UPDATE NA MODEL NAME
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    ),
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            full_reply = st.write_stream(stream_response())
        except Exception as e:
            last_error = str(e)

        if full_reply:
            st.session_state["messages"].append(
                {"role": "assistant", "content": full_reply}
            )
        else:
            error_msg = f"⚠️ Hindi nakakonekta sa AI ({last_error}). Pakisubukan ulit!"
            st.error(error_msg)
            st.session_state["messages"].append(
                {"role": "assistant", "content": error_msg}
            )
