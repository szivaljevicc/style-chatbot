
import streamlit as st
from streamlit_chat import message
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI

# Load avatar image as base64
def get_avatar_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

avatar_base64 = get_avatar_base64("C:/Users/Sasa Zivaljevic/Desktop/logo.png")

# Streamlit page config
st.set_page_config(page_title="Style Assistant Chatbot", page_icon="🧵", layout="centered")

# Inject custom CSS
st.markdown("""
<style>
    html, body {
        background-color: #f7faf7;
        margin: 0;
        padding: 0;
    }

    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    header, footer {
        visibility: hidden;
        height: 0;
    }

    .chat-box {
        max-width: 700px;
        margin: 2rem auto 1rem auto;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        padding: 1.5rem 2rem 3rem 2rem;
    }

    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.8rem;
        color: #1b5e20;
        text-align: center;
        margin: 0 0 1rem 0;
    }

    .assistant-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 10px;
    }

    .message-row {
        display: flex;
        align-items: flex-start;
        margin-top: 1rem;
    }

    .message-bubble {
        background: #ffffff;
        border-radius: 12px;
        padding: 10px 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        max-width: 85%;
        font-family: sans-serif;
        font-size: 0.95rem;
        line-height: 1.4;
    }

    .user-message {
        background: #e0f2f1;
        margin-left: auto;
    }

    .typing-container {
        display: flex;
        gap: 4px;
        height: 20px;
        margin-left: 46px;
        margin-top: -10px;
        margin-bottom: 10px;
    }

    .dot {
        width: 8px;
        height: 8px;
        background-color: #bbb;
        border-radius: 50%;
        animation: bounce 1.2s infinite ease-in-out;
    }

    .dot:nth-child(2) {
        animation-delay: 0.2s;
    }

    .dot:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }

    .stChatInputContainer input {
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        border: 1px solid #c8e6c9;
        background-color: #f0fff0;
    }

    .stChatInputContainer {
        background: #ffffff;
        border-radius: 0 0 16px 16px;
        padding: 1rem 2rem;
        box-shadow: inset 0 1px 0 rgba(0,0,0,0.05);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# API clients
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID_IDENTITY = '1Eh1yjfanZz6TW0HEFzb0tbED7Co5yCEAA30zhniYtG4'
SHEET_NAME_IDENTITY = 'Form Responses 1'

client = OpenAI(api_key=st.secrets["openai_api_key"])
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', SCOPES)
gs_client = gspread.authorize(creds)
sheet_identity = gs_client.open_by_key(SPREADSHEET_ID_IDENTITY).worksheet(SHEET_NAME_IDENTITY)
data_IDENTITY = sheet_identity.get_all_records()

# State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "email" not in st.session_state:
    st.session_state.email = ""
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "step" not in st.session_state:
    st.session_state.step = 0

# Header
with st.container():
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    st.markdown("<h1>Style Assistant Chatbot</h1>", unsafe_allow_html=True)

# Initial assistant greeting
if st.session_state.step == 0 and not st.session_state.messages:
    greeting = "Hi there! Please enter the email address you used to complete your fashion identity quiz."
    with st.container():
        st.markdown(f"""
        <div class="message-row">
            <img class="assistant-avatar" src="data:image/png;base64,{avatar_base64}">
            <div class="message-bubble">{greeting}</div>
        </div>
        """, unsafe_allow_html=True)

# User input field
user_input = st.chat_input("Type your answer...")

if user_input:
    # User message
    with st.container():
        st.markdown(f"""
        <div class="message-row">
            <div class="message-bubble user-message">{user_input}</div>
        </div>
        """, unsafe_allow_html=True)

    # Assistant response logic
    if st.session_state.step == 0:
        st.session_state.email = user_input
        match_found = False
        for row in data_IDENTITY:
            if row.get('Email Address', '').strip().lower() == user_input.strip().lower():
                st.session_state.profile = {
                    "style_type": row.get('External/Internal \n', '').strip(),
                    "function_type": row.get('Functional/Expressive', '').strip()
                }
                match_found = True
                break
        reply = "Email found! Describe the item you're thinking of buying." if match_found else \
                "Email not found. Please make sure you've completed the identity quiz."
        st.session_state.step = 1 if match_found else 0

    elif st.session_state.step == 1:
        st.session_state.profile["item"] = user_input
        reply = "What climate do you live in? (e.g. Temperate, Cold, Tropical, Dry)"
        st.session_state.step = 2

    elif st.session_state.step == 2:
        st.session_state.profile["climate"] = user_input
        reply = "Is this for a special occasion? (optional)"
        st.session_state.step = 3

    elif st.session_state.step == 3:
        st.session_state.profile["occasion"] = user_input
        reply = "How often do you plan to wear this item? (Daily, Weekly, Occasionally)"
        st.session_state.step = 4

    elif st.session_state.step == 4:
        st.session_state.profile["frequency"] = user_input
        reply = "What is your price range? (Low, Mid, High)"
        st.session_state.step = 5

    elif st.session_state.step == 5:
        st.session_state.profile["price_range"] = user_input
        reply = "What is your living situation like? (e.g. Urban apartment, Student housing, Shared flat, etc.)"
        st.session_state.step = 6

    elif st.session_state.step == 6:
        st.session_state.profile["living_situation"] = user_input
        reply = "What is your weekday routine like? (e.g. Office job, Uni & gym, Mostly home, etc.)"
        st.session_state.step = 7

    elif st.session_state.step == 7:
        st.session_state.profile["routine"] = user_input
        reply = "Do you have a preferred brand or aesthetic you gravitate towards? (optional)"
        st.session_state.step = 8

    elif st.session_state.step == 8:
        st.session_state.profile["brand"] = user_input
        st.session_state.step = 9

        p = st.session_state.profile
        prompt = f"""
You are a personal fashion advisor. A user is considering buying the following item:

"{p['item']}"

They completed a fashion identity quiz:
- **Style Orientation**: {p['style_type']}
- **Functionality Preference**: {p['function_type']}

Lifestyle:
- **Climate**: {p['climate']}
- **Occasion**: {p['occasion']}
- **Wear Frequency**: {p['frequency']}
- **Price Range**: {p['price_range']}
- **Living Situation**: {p['living_situation']}
- **Weekday Routine**: {p['routine']}
- **Preferred Brand/Aesthetic**: {p['brand']}

Your task:
- Address them as "you"
- Analyze fit with identity/lifestyle
- Give 2–3 pros and 2–3 potential concerns
- End with a clear recommendation
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Failed to get evaluation: {e}"

    else:
        reply = "You can start a new evaluation by refreshing the page."

    with st.container():
        st.markdown(f"""
        <div class="message-row">
            <img class="assistant-avatar" src="data:image/png;base64,{avatar_base64}">
            <div class="message-bubble">{reply}</div>
        </div>
        """, unsafe_allow_html=True)

    st.session_state.messages.append({"text": reply, "is_user": False})
