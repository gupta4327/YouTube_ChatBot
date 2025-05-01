import streamlit as st
from main import get_bot_response  # Your response chain logic
from main import get_available_videos  # Function to list indexed videos

# --- Initialize session state ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "selected_video" not in st.session_state:
    st.session_state.selected_video = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of (user_msg, bot_msg)


# --- Step 1: Get User ID ---
def get_user_id():
    st.title("🎥 YouTube ChatBot")

    user_id = st.text_input("Enter your User ID 👇🏽")
    if st.button("Submit ID"):
        if user_id.strip() == "":
            st.warning("Please enter a valid User ID.")
        else:
            st.session_state.user_id = user_id
            st.success(f"Welcome, {user_id}!")


# --- Step 2: Select Video ---
def select_video():
    st.header(f"👋 Welcome {st.session_state.user_id}")

    # Get list of available videos
    video_dict = get_available_videos()  # Example: ['Video 1', 'Video 2', 'Video 3']
    video_list = list(video_dict.keys())

    selected = st.selectbox("Select a YouTube Video to Chat With 👇🏽", video_list)

    if st.button("Load Video"):
        st.session_state.video_metadata = video_dict
        st.session_state.selected_video = selected
        st.success(f"Loaded {selected}!")


# --- Step 3: Chat Window ---
def chat_window():
    st.header(f"🗨️ Chatting with: {st.session_state.selected_video}")

    # Display chat history
    for user_msg, bot_msg in st.session_state.chat_history:
        st.markdown(f"**You:** {user_msg}")
        st.markdown(f"**Bot:** {bot_msg}")
        st.markdown("---")

    # New Question Input
    user_question = st.text_input("Ask a question about the video 👇🏽")

    if st.button("Send"):
        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Call your bot logic
            bot_answer = get_bot_response(st.session_state.user_id, st.session_state.selected_video, user_question)

            # Save in chat history
            st.session_state.chat_history.append((user_question, bot_answer))

            # Rerun to refresh chat display
            st.rerun()


# --- App Flow Controller ---
def main():
    if st.session_state.user_id is None:
        get_user_id()
    elif st.session_state.selected_video is None:
        select_video()
    else:
        chat_window()


if __name__ == "__main__":
    main()
