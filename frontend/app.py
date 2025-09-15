import os
from dotenv import load_dotenv
import streamlit as st
import requests
import uuid
import random
from streamlit.components.v1 import html

load_dotenv()

# Page configuration
st.set_page_config(page_title="📚 AI Tutor", layout="wide")

# App title
st.title("🎓 AI-Powered Tutor & Quiz App")

with st.sidebar:
    st.header("Learning Preferences")
    subject = st.selectbox(
        "📖 Select Subject",
        [
            "Mathematics",
            "Physics",
            "Computer Science",
            "History",
            "Biology",
            "Programming",
        ],
    )

    level = st.selectbox(
        "📚 Select Learning Level", ["Beginner", "Intermediate", "Advanced"]
    )

    learning_style = st.selectbox(
        "🧠 Learning Style", ["Visual", "Text-based", "Hands-on"]
    )

    language = st.selectbox(
        "🌍 Preferred Language", ["English", "Hindi", "Spanish", "French"]
    )

    background = st.selectbox(
        "📊 Background Knowledge", ["Beginner", "Some Knowledge", "Experienced"]
    )


API_ENDPOINT = os.getenv("BACKEND_URL")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Ask a Question", "🧠 Take a Quiz", "📄 Upload PDF", "🃏 Flashcards", "💬 Discuss"])


with tab1:
    # Main content area for tutoring
    st.header("Ask Your Question")
    question = st.text_area(
        "❓ What would you like to learn today?",
        "Explain Newton's Second Law of Motion.",
    )

    # Tutor section
    if st.button("Get Explanation 🧠"):
        with st.spinner("Generating personalized explanation..."):
            try:
                response = requests.post(
                    f"{API_ENDPOINT}/tutor",
                    json={
                        "subject": subject,
                        "level": level,
                        "learning_style": learning_style,
                        "language": language,
                        "background": background,
                        "question": question,
                    },
                ).json()

                st.success("Here's your personalized explanation:")
                st.markdown(response["response"], unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error getting explanation: {str(e)}")
                st.info(f"Make sure the backend server is running at {API_ENDPOINT}")


with tab2:
    # Quiz section
    st.header("Test Your Knowledge")

    col1, col2 = st.columns([2, 1])

    with col1:
        num_questions = st.slider(
            "Number of Questions", min_value=1, max_value=10, value=5
        )

    with col2:
        quiz_button = st.button("Generate Quiz 📝", use_container_width=True)

    if quiz_button:
        with st.spinner("Creating quiz questions..."):
            try:
                # Request quiz with interactive answer reveal format
                response = requests.post(
                    f"{API_ENDPOINT}/quiz",
                    json={
                        "subject": subject,
                        "level": level,
                        "num_questions": num_questions,
                        "reveal_format": True,
                    },
                ).json()

                st.success("Quiz generated! Try answering these questions:")

                # Use the formatted HTML with interactive elements
                if "formatted_quiz" in response and response["formatted_quiz"]:
                    # Display using HTML component
                    html(response["formatted_quiz"], height=num_questions * 300)
                else:
                    # Fallback to simple display if formatted quiz isn't available
                    for i, q in enumerate(response["quiz"]):
                        with st.expander(
                            f"Question {i + 1}: {q['question']}", expanded=True
                        ):
                            # Generate a random session ID to avoid conflicts between questions
                            session_id = str(uuid.uuid4())

                            # Display options as radio buttons
                            selected = st.radio(
                                "Select your answer:",
                                q["options"],
                                key=f"q_{session_id}",
                            )

                            # Check answer button
                            if st.button("Check Answer", key=f"check_{session_id}"):
                                if selected == q["correct_answer"]:
                                    st.success(
                                        f"✅ Correct! {q.get('explanation', '')}"
                                    )
                                else:
                                    st.error(
                                        f"❌ Incorrect. The correct answer is: {q['correct_answer']}"
                                    )
                                    if "explanation" in q:
                                        st.info(q["explanation"])

            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")
                st.info(f"Make sure the backend server is running at {API_ENDPOINT}")

with tab3:
    st.header("📄 Upload PDF")
    uploaded_file = st.file_uploader("Upload your study PDF", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Processing your PDF..."):
            try:
                # Send file with proper metadata
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{API_ENDPOINT}/process_pdf", files=files)

                if response.status_code == 200:
                    pdf_data = response.json()
                    st.session_state["pdf_data"] = pdf_data
                    st.success("✅ PDF processed successfully!")
                    
                    # Display PDF summary
                    st.subheader("📋 PDF Summary")
                    if "summary" in pdf_data:
                        st.markdown(pdf_data["summary"])
                    elif "content" in pdf_data:
                        st.markdown("**Extracted Content:**")
                        st.markdown(pdf_data["content"])
                    else:
                        st.info("PDF content extracted and stored for further use.")
                        
                else:
                    st.error("Failed to process PDF. Check backend.")
            except Exception as e:
                st.error(f"Error: {str(e)}")


with tab4:
    st.header("🃏 Flashcards")
    
    if "pdf_data" in st.session_state and "flashcards" in st.session_state["pdf_data"]:
        flashcards = st.session_state["pdf_data"]["flashcards"]
        
        # Flashcard navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Previous", key="prev_card"):
                if "current_card" not in st.session_state:
                    st.session_state["current_card"] = 0
                st.session_state["current_card"] = max(0, st.session_state["current_card"] - 1)
        
        with col2:
            st.markdown(f"**Card {st.session_state.get('current_card', 0) + 1} of {len(flashcards)}**")
        
        with col3:
            if st.button("Next ➡️", key="next_card"):
                if "current_card" not in st.session_state:
                    st.session_state["current_card"] = 0
                st.session_state["current_card"] = min(len(flashcards) - 1, st.session_state["current_card"] + 1)
        
        # Display current flashcard
        if "current_card" not in st.session_state:
            st.session_state["current_card"] = 0
            
        current_card = flashcards[st.session_state["current_card"]]
        
        # Flashcard display
        with st.container():
            st.markdown("---")
            
            # Topic
            st.markdown(f"### 📚 **Topic:** {current_card.get('topic', 'N/A')}")
            
            # Question
            with st.expander("❓ **Question** (Click to reveal)", expanded=True):
                st.markdown(f"**{current_card.get('question', 'N/A')}**")
            
            # Answer
            with st.expander("💡 **Answer** (Click to reveal)", expanded=False):
                st.markdown(f"**{current_card.get('answer', 'N/A')}**")
            
            st.markdown("---")
        
        # Show all flashcards in a table below
        st.subheader("📋 All Flashcards Overview")
        import pandas as pd
        df = pd.DataFrame([
            {
                "Card No": i+1,
                "Topic": card.get("topic", "N/A"),
                "Question": card.get("question", "N/A"),
                "Answer": card.get("answer", "N/A")
            }
            for i, card in enumerate(flashcards)
        ])
        
        st.dataframe(df, use_container_width=True)
        
    else:
        st.info("📄 **No flashcards available yet!**")
        st.info("1. Go to the '📄 Upload PDF' tab")
        st.info("2. Upload a study PDF")
        st.info("3. Come back here to see your generated flashcards!")
        
        # Show example flashcard structure
        st.subheader("💡 Example Flashcard Structure")
        st.markdown("""
        When you upload a PDF, the AI will automatically generate flashcards like this:
        
        **Topic:** Machine Learning Basics
        **Question:** What is supervised learning?
        **Answer:** Supervised learning is a type of machine learning where the algorithm learns from labeled training data to make predictions on new, unseen data.
        """)


with tab5:
    st.header("💬 Discuss with Your PDF")
    
    if "pdf_data" in st.session_state and "content" in st.session_state["pdf_data"]:
        st.success("✅ PDF loaded! You can now ask questions about your document.")
        
        # Chat interface
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        
        # Display chat history
        if st.session_state["chat_history"]:
            st.subheader("💬 Chat History")
            for i, message in enumerate(st.session_state["chat_history"]):
                if message["role"] == "user":
                    st.markdown(f"**👤 You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 AI:** {message['content']}")
                if i < len(st.session_state["chat_history"]) - 1:
                    st.markdown("---")
        
        # User input with unique key to prevent conflicts
        user_question = st.text_area(
            "❓ Ask a question about your PDF content:",
            placeholder="e.g., What are the main concepts discussed? Can you explain the key definitions?",
            height=100,
            key=f"user_input_{len(st.session_state.get('chat_history', []))}"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("💬 Ask Question", use_container_width=True, key=f"ask_btn_{len(st.session_state.get('chat_history', []))}"):
                if user_question.strip():
                    # Check if this question was already asked to prevent duplicates
                    if "last_question" not in st.session_state or st.session_state["last_question"] != user_question.strip():
                        # Add user question to chat history
                        st.session_state["chat_history"].append({
                            "role": "user",
                            "content": user_question.strip()
                        })
                        
                        # Store the last question to prevent duplicates
                        st.session_state["last_question"] = user_question.strip()
                        
                        # Get AI response based on PDF content
                        with st.spinner("🤔 Thinking..."):
                            try:
                                response = requests.post(
                                    f"{API_ENDPOINT}/discuss_pdf",
                                    json={
                                        "question": user_question.strip(),
                                        "pdf_content": st.session_state["pdf_data"]["content"],
                                        "pdf_summary": st.session_state["pdf_data"]["summary"]
                                    }
                                )
                                
                                if response.status_code == 200:
                                    ai_response = response.json()["response"]
                                    
                                    # Add AI response to chat history
                                    st.session_state["chat_history"].append({
                                        "role": "assistant",
                                        "content": ai_response
                                    })
                                    
                                    st.success("💬 Response generated!")
                                    # No rerun needed - Streamlit will update automatically
                                else:
                                    st.error("Failed to get response. Please try again.")
                                    
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                st.info("Make sure the backend server is running.")
                    else:
                        st.warning("This question was already asked. Please ask a different question.")
                else:
                    st.warning("Please enter a question.")
        
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
                st.session_state["chat_history"] = []
                if "last_question" in st.session_state:
                    del st.session_state["last_question"]
                st.rerun()
        

        
        # Instructions
        st.markdown("---")
        st.info("💡 **How to use:**")
        st.info("• Ask questions about concepts, definitions, or topics from your PDF")
        st.info("• The AI will only answer based on the content of your uploaded document")
        st.info("• Use this to clarify concepts, get explanations, or test your understanding")
        
    else:
        st.warning("📄 **No PDF uploaded yet!**")
        st.info("To use the Discuss feature:")
        st.info("1. Go to the '📄 Upload PDF' tab")
        st.info("2. Upload your study PDF")
        st.info("3. Come back here to start discussing the content!")
        
        # Show example questions
        st.subheader("💡 Example Questions You Can Ask:")
        st.markdown("""
        Once you upload a PDF, you can ask questions like:
        
        **📚 Content Questions:**
        - "What are the main topics covered in this document?"
        - "Can you explain the key concepts mentioned?"
        - "What are the important definitions I should know?"
        
        **🔍 Specific Questions:**
        - "What does [specific term] mean?"
        - "How does [concept] work?"
        - "What are the steps in [process]?"
        
        **📖 Study Help:**
        - "Summarize the main points of [section]"
        - "What are the key takeaways from this document?"
        - "Can you give me examples of [concept]?"
        """)


# Footer
st.markdown("---")
st.markdown("Powered by AI - Your Personal Learning Assistant")