<!-- 
# 📚 Personalised Tutor – AI-Powered Tutor & Quiz App

An educational platform that leverages artificial intelligence to provide **personalized learning experiences**. This app allows users to ask questions on various academic subjects and receive tailored explanations, as well as generate quizzes to reinforce their understanding.

![Permotion](./Images/AITutor.png)

---

## 🚀 Project Overview

The **AI-Powered Tutor & Quiz App** offers:
- Adaptive tutoring based on user preferences
- Quiz generation for knowledge testing
- Multi-language and multi-subject support

---

## 🛠 Tools & Technologies

- **FastAPI** – Backend API framework  
- **Streamlit** – Frontend framework  
- **LangChain** – LLM orchestration  
- **OpenAI API** – Powers tutoring and quiz features  
- **Python** – Core programming language  
- **Pydantic** – Data validation  
- **Uvicorn** – ASGI server  
- **python-dotenv** – Environment variable management  

---

## 🏗 Architecture & Components

### 1. Streamlit Frontend (`app.py`)
- User interface for interacting with the app
- Collects user inputs like subject, learning style, etc.
- Displays personalized responses and quizzes

### 2. FastAPI Backend (`main.py`)
- RESTful endpoints for tutoring and quizzes
- Handles request validation and error responses
- Connects to the AI engine

### 3. AI Engine (`ai_engine.py`)
- Constructs LLM prompts based on user preferences
- Parses responses and includes fallback logic
- Adapts content to user learning styles

---

## 🔄 Workflow

1. User selects preferences in the Streamlit UI (subject, level, learning style, etc.)
2. User enters a question or quiz request.
3. Streamlit sends the request to the FastAPI backend.
4. Backend validates and forwards it to the AI engine.
5. AI engine constructs a prompt and queries OpenAI via LangChain.
6. Response is parsed and returned to the frontend.
7. Personalized content is displayed to the user.

---

## 🔍 Key Features

- **🎓 Personalized Learning** – Adapts content to user’s style, proficiency, and background.
- **📚 Multi-Subject Support** – Includes Math, Physics, CS, History, Biology, Programming.
- **📝 Quiz Generation** – Custom quizzes for active recall
- **🌐 Multi-Language Support** – English, Hindi, Spanish, French
- **🧠 Learning Style Adaptation** – Visual, Text-based, and Hands-on learning formats

---

## 🧩 Implementation Details

### Frontend
- Sidebar for selecting subject and learning style
- Text area for question input
- Buttons to trigger responses or quizzes
- Displays formatted AI-generated content

### Backend
- RESTful API endpoints
- Request validation via Pydantic
- CORS middleware enabled
- Error handling with HTTP codes

### AI Engine
- Dynamic prompt engineering
- Handles response formatting
- Built-in error fallback strategies

---

## 🚀 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
# Add your OpenAI API key in a .env file

# 3. Start the backend
uvicorn main:app --reload

# 4. Launch the frontend
streamlit run app.py
```

---

## 📬 Contact
🌐 **Website**: [www.mayurpatil.in](https://www.mayurpatil.in)
 -->


# 📚 StudyGenie – AI-Powered Personalised Tutor & Quiz App

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/StudyGenie/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Deploy on Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yourusername/StudyGenie/main)

---

## Table of Contents

- [Features](#features)
- [Demo](#demo--screenshots--gifs--live-link)
- [Installation](#installation--setup-instructions)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing-guidelines)
- [License](#license)
- [Authors & Acknowledgements](#authors--credits--acknowledgements)

---

## Features

- 🎓 **Personalized AI Tutoring**: Adaptive explanations tailored to subject, level, learning style, and language.
- 📝 **Quiz Generation**: Custom, interactive multiple-choice quizzes with answer reveal and explanations.
- 📄 **PDF Upload & Analysis**: Extracts content, generates summaries, and creates flashcards from study PDFs.
- 🃏 **Flashcards**: Auto-generated, topic-based flashcards for active recall.
- 💬 **PDF Discussion Chat**: Ask questions about your uploaded PDF and get AI-powered, content-specific answers.
- 🌐 **Multi-language Support**: English, Hindi, Spanish, French.
- 🧠 **Learning Style Adaptation**: Visual, Text-based, and Hands-on learning formats.

---

## Demo / Screenshots / GIFs / Live Link

![StudyGenie Screenshot](![alt text](image.png))

> **Live Demo:** [Streamlit Cloud Link](https://studygenie-ai.streamlit.app/)  

---

## Installation / Setup Instructions

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/StudyGenie.git
    cd StudyGenie
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment:**
    - Create a `.env` file in the root directory.
    - Add your Google Gemini API key:
      ```
      GEMINI_API_KEY=your-gemini-api-key
      ```

4. **Start the backend (FastAPI):**
    ```sh
    cd backend
    uvicorn main:app --reload
    ```

5. **Launch the frontend (Streamlit):**
    ```sh
    cd ../frontend
    streamlit run [app.py](http://_vscodecontentref_/0)
    ```

---

## Usage

- **Ask a Question:**  
  Go to the "Ask a Question" tab, select your preferences, and get a personalized explanation.
- **Take a Quiz:**  
  Generate and interact with quizzes on your chosen subject and level.
- **Upload PDF:**  
  Upload study materials, get summaries, and auto-generated flashcards.
- **Flashcards:**  
  Review and navigate through flashcards generated from your PDF.
- **Discuss:**  
  Chat with the AI about your uploaded PDF content.

---

## Project Structure
StudyGenie/
│
├── backend/
│   ├── ai_engine.py         # AI logic, prompt engineering, quiz/flashcard generation
│   ├── main.py              # FastAPI app, API endpoints
│   └── utils.py             # Utility functions (if any)
│
├── frontend/
│   └── app.py               # Streamlit UI
│
├── Images/
│   └── AITutor.png          # App screenshot(s)
│
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version
├── .env.example             # Example environment variables
├── .gitignore
└── README.md


---

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **AI/LLM:** Google Gemini via LangChain
- **PDF Processing:** PyPDF2
- **Data Validation:** Pydantic
- **API Server:** Uvicorn
- **Environment Management:** python-dotenv

---

## Contributing Guidelines

Contributions are welcome!  
Please open issues or submit pull requests for improvements, bug fixes, or new features.

1. Fork the repo and create your branch.
2. Make your changes and add tests if applicable.
3. Ensure code style and formatting.
4. Submit a pull request with a clear description.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Made with ❤️ for learners everywhere!*