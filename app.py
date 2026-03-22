
# # import streamlit as st
# # from Chat import ask_question

# # # ================================
# # # PAGE CONFIG
# # # ================================
# # st.set_page_config(
# #     page_title="YouTube RAG Chatbot",
# #     page_icon="🎥",
# #     layout="wide"
# # )

# # # ================================
# # # TITLE
# # # ================================
# # st.title("🎥 YouTube Video Chatbot")
# # st.markdown("Ask questions about a YouTube video transcript")

# # # ================================
# # # SIDEBAR
# # # ================================
# # st.sidebar.header("⚙️ Settings")
# # video_id = st.sidebar.text_input("YouTube Video ID", value="UabBYexBD4k")

# # # ================================
# # # MAIN INPUT
# # # ================================
# # user_question = st.text_input("💬 Ask a question")

# # # ================================
# # # BUTTON ACTION
# # # ================================
# # if st.button("Ask"):
# #     if user_question:
# #         with st.spinner("Thinking... 🤔"):
# #             try:
# #                 answer = ask_question(user_question)
# #                 st.success("✅ Answer:")
# #                 st.write(answer)
# #             except Exception as e:
# #                 st.error(f"Error: {e}")
# #     else:
# #         st.warning("Please enter a question")



# import streamlit as st
# from new_chat import build_chain, ask_question

# # ================================
# # PAGE CONFIG
# # ================================
# st.set_page_config(
#     page_title="YouTube RAG Chatbot",
#     page_icon="🎥",
#     layout="wide"
# )

# # ================================
# # TITLE
# # ================================
# st.title("🎥 YouTube RAG Chatbot")
# st.markdown("Chat with any YouTube video")

# # ================================
# # SESSION STATE
# # ================================
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "chain" not in st.session_state:
#     st.session_state.chain = None

# if "video_id" not in st.session_state:
#     st.session_state.video_id = ""


# # ================================
# # SIDEBAR (VIDEO INPUT)
# # ================================
# st.sidebar.header("🎬 Video Settings")

# video_input = st.sidebar.text_input(
#     "Enter YouTube Video ID",
#     placeholder="e.g. UabBYexBD4k"
# )

# if st.sidebar.button("Load Video"):
#     if video_input:
#         with st.spinner("Loading video + building RAG..."):
#             chain = build_chain(video_input)

#             if chain:
#                 st.session_state.chain = chain
#                 st.session_state.video_id = video_input
#                 st.session_state.messages = []
#                 st.success("Video loaded successfully!")
#             else:
#                 st.error("No transcript available")
#     else:
#         st.warning("Enter video ID")


# # ================================
# # SHOW VIDEO
# # ================================
# if st.session_state.video_id:
#     st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")


# # ================================
# # CHAT UI
# # ================================
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.write(msg["content"])


# # ================================
# # USER INPUT
# # ================================
# user_input = st.chat_input("Ask something about the video...")

# if user_input:
#     if not st.session_state.chain:
#         st.warning("Please load a video first")
#         st.stop()

#     # Add user message
#     st.session_state.messages.append({
#         "role": "user",
#         "content": user_input
#     })

#     with st.chat_message("user"):
#         st.write(user_input)

#     # Streaming-like response
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""

#         try:
#             response = ask_question(st.session_state.chain, user_input)

#             # Fake streaming effect
#             for chunk in response.split():
#                 full_response += chunk + " "
#                 message_placeholder.markdown(full_response + "▌")
            
#             message_placeholder.markdown(full_response)

#         except Exception as e:
#             message_placeholder.markdown(f"Error: {e}")

#     # Save response
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": full_response
#     })


import streamlit as st
from new_chat import build_chain, ask_question
from model import get_llm

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Video Intelligence AI",
    page_icon="🎥",
    layout="wide"
)

# =========================
# MODERN UI (CSS)
# =========================
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #020617, #0f172a);
}

/* Title Gradient */
.title {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg,#38bdf8,#6366f1);
    -webkit-background-clip: text;
    color: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#020617,#0f172a);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Chat container */
.chat-box {
    background: rgba(255,255,255,0.04);
    border-radius: 15px;
    padding: 15px;
    backdrop-filter: blur(10px);
}

/* Chat messages */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    animation: fadeIn 0.3s ease-in;
}

/* User bubble */
[data-testid="stChatMessage"][data-testid="user"] {
    background: linear-gradient(135deg,#2563eb,#4f46e5);
    color: white;
}

/* AI bubble */
[data-testid="stChatMessage"][data-testid="assistant"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
}

/* Video card */
.video-card {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg,#38bdf8,#6366f1);
    color: white;
    border-radius: 10px;
    border: none;
}

/* Animation */
@keyframes fadeIn {
    from {opacity:0; transform: translateY(5px);}
    to {opacity:1;}
}

</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chain" not in st.session_state:
    st.session_state.chain = None

if "video_id" not in st.session_state:
    st.session_state.video_id = ""

if "mode" not in st.session_state:
    st.session_state.mode = "RAG"

if "llm" not in st.session_state:
    st.session_state.llm = get_llm()

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## ⚙️ Settings")

mode = st.sidebar.radio(
    "Mode",
    ["RAG (Video)", "Chat Only"]
)

st.session_state.mode = mode

if mode == "RAG (Video)":
    video_id = st.sidebar.text_input("YouTube Video ID")

    if st.sidebar.button("Load Video"):
        if video_id:
            with st.spinner("Processing video..."):
                chain = build_chain(video_id)

                if chain:
                    st.session_state.chain = chain
                    st.session_state.video_id = video_id
                    st.session_state.messages = []
                else:
                    st.error("No transcript found")

# =========================
# HEADER
# =========================
st.markdown('<div class="title">🎥 Video Intelligence AI</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# =========================
# CHAT SECTION
# =========================
with col1:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            try:
                if mode == "RAG (Video)":
                    if not st.session_state.chain:
                        placeholder.write("⚠️ Load a video first")
                        st.stop()

                    response = ask_question(st.session_state.chain, user_input)
                else:
                    response = st.session_state.llm.invoke(user_input).content

                # streaming effect
                for word in response.split():
                    full_response += word + " "
                    placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

            except Exception as e:
                placeholder.error(str(e))

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# VIDEO PANEL
# =========================
with col2:
    if mode == "RAG (Video)" and st.session_state.video_id:
        st.markdown("### 🎬 Video")

        st.markdown('<div class="video-card">', unsafe_allow_html=True)
        st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CLEAR CHAT
# =========================
if st.button("🧹 Clear Chat"):
    st.session_state.messages = []

