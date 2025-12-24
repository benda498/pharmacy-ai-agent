import streamlit as st
from database import verify_user
from agent import run_agent

# Change button hover - border and text only
st.markdown("""
    <style>
    button:hover {
        border-color: #0066cc !important;
        color: #0066cc !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Pharmacy Assistant")

# Check if user is already logged in
if "user" not in st.session_state:
    # User is NOT logged in - show login screen
    st.write("Please login to continue")
    st.write("בבקשה התחבר בשביל להמשיך")

    with st.form(key="login_form"):
        id_input = st.text_input("Enter your ID Number:", key="id_input")
        login_button = st.form_submit_button("Login")

    if login_button and id_input:
        # Try to verify user
        result = verify_user(id_input)

        if result["verified"]:
            # Success! Save user in session
            st.session_state.user = result["user"]

            # Initialize with welcome message
            welcome_msg = (
                f"שלום {result['user']['first_name']}!\n\n"
                "אני העוזר הווירטואלי של בית המרקחת. אשמח לעזור לך עם:\n"
                "• בדיקת זמינות תרופות\n"
                "• מחירים\n"
                "• מינונים והוראות שימוש\n"
                "• מידע על תרופות\n\n"
                "במה אוכל לסייע?"
            )
            st.session_state.messages = [{"role": "Bot", "content": welcome_msg}]
            st.session_state.history = []

            st.rerun()
        else:
            # Failed - show error
            st.error("ID number not found. Please try again.")

else:
    # User IS logged in - show chat
    st.write(f"### Logged in as: {st.session_state.user['first_name']} {st.session_state.user['last_name']}")

    # Initialize session state flags
    defaults = {
        "messages": [],
        "history": [],
        "confirm_new_chat": False,
        "processing": False,
        "current_input": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Display chat messages and tool calls
    for msg in st.session_state.messages:
        if msg['role'] == "You":
            with st.chat_message("user"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant"):
                st.write(msg['content'])

                # Show tool calls if exists
                if msg.get("tool_calls"):
                    with st.expander("🔧 Show tool calls"):
                        for i, tool in enumerate(msg["tool_calls"], 1):
                            st.write(f"**Tool {i}: `{tool['name']}`**")
                            st.json(tool['arguments'])
                            if tool['result']:
                                st.write("**Result:**")
                                st.code(tool['result'][:500], language="json")  # Max 500 chars

    # Chat input
    user_input = st.chat_input("Type your message...")

    # New Chat button (hide during processing)
    if not st.session_state.processing:
        if not st.session_state.confirm_new_chat:
            # Show button normally
            if st.button("🔄 New Chat"):
                st.session_state.confirm_new_chat = True
                st.rerun()
        else:
            # Show confirmation
            st.warning(
                "⚠️ האם אתה בטוח? פעולה זו תסיים את השיחה הנוכחית ותנתק אותך מהמערכת.\n\nAre you sure? This will end your current session and log you out.")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("כן, התחל שיחה חדשה / Yes, New Chat"):
                    st.session_state.clear()
                    st.rerun()

            with col2:
                if st.button("ביטול / Cancel"):
                    st.session_state.confirm_new_chat = False
                    st.rerun()

    # Part 1: Receive user message
    if user_input and not st.session_state.processing:
        # Add user message to display
        st.session_state.messages.append({
            "role": "You",
            "content": user_input
        })

        # Mark that we're processing
        st.session_state.processing = True
        st.session_state.current_input = user_input  # Save for processing

        # First rerun - will display user message immediately
        st.rerun()

    # Part 2: Process and get bot response
    if st.session_state.processing:
        # User message is already displayed!
        # Show thinking spinner
        with st.spinner("🤖 Thinking..."):
            response, updated_history, tool_calls = run_agent(
                st.session_state.current_input,
                st.session_state.user,
                st.session_state.history
            )

        # Update conversation history
        st.session_state.history = updated_history

        # Add bot response to display (with tool calls)
        st.session_state.messages.append({
            "role": "Bot",
            "content": response,
            "tool_calls": tool_calls
        })

        # Done processing
        st.session_state.processing = False
        st.session_state.current_input = None

        # Second rerun - will display bot response
        st.rerun()