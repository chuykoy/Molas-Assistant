import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Molas AI Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SYSTEM_INSTRUCTION = (
    "Ikaw si Molas AI, isang matulungin, magalang, at matalinong AI assistant "
    "na bihasa magsalita sa Tagalog at Taglish. Panatilihing direkta at maikli ang sagot "
    "maliban kung humingi ang user ng mas detalyadong paliwanag.\n\n"
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
    html, body, [data-testid="stAppViewContainer"] {
        background: #f4f7fb;
    }
    .stApp {
        max-width: 700px;
        margin: 0 auto;
    }
    [data-testid="stHeader"] {
        background: rgba(255,255,255,0);
        box-shadow: none;
    }
    [data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border: 1px solid rgba(0,0,0,0.04);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .stChatInput {
        position: sticky;
        bottom: 12px;
        background: white;
        border-radius: 18px;
        border: 1px solid #dfe7f3;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
    .stTextInput>div>div {
        background: white;
    }
    button[kind="primary"] {
        border-radius: 12px;
    }
    @media (max-width: 700px) {
        .stApp {
            padding-left: 8px;
            padding-right: 8px;
        }
        [data-testid="stChatMessage"] {
            padding: 10px 12px;
            border-radius: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="text-align:center; margin-top: 10px; margin-bottom: 6px;">'
    '<div style="font-size: 2.1rem; font-weight: 800; color: #1f2937;">✨ Molas AI</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="text-align:center; margin-bottom: 18px; color: #6b7280; font-size: 0.96rem;">'
    'Ang iyong matalinong Tagalog & Taglish AI partner'
    '</div>',
    unsafe_allow_html=True,
)

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

@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_client()

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

        try:
            def stream_response():
                response = client.models.generate_content_stream(
                    model="gemini-3.1-flash-lite",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                        max_output_tokens=512,
                    ),
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            reply = st.write_stream(stream_response())
            st.session_state["messages"].append({"role": "assistant", "content": reply})
        except Exception as e:
            error_msg = f"⚠️ Hindi nakakonekta sa AI ({str(e)}). Pakisubukan ulit!"
            st.error(error_msg)
            st.session_state["messages"].append({"role": "assistant", "content": error_msg})
