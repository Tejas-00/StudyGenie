from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import PyPDF2
import io
from langchain_core.messages import HumanMessage


from ai_engine import generate_tutoring_response, generate_quiz

# Load environment variables
load_dotenv()
GEMINI_API_KEY = "AIzaSyDatfjdPnshQp7erzGchPYzV5fsxajH4aY"

app = FastAPI(
    title="AI Tutor API",
    description="API for generating personalized tutoring content and quizzes",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TutorRequest(BaseModel):
    subject: str = Field(..., description="Academic subject")
    level: str = Field(..., description="Learning level (Beginner, Intermediate, Advanced)")
    question: str = Field(..., description="User's question")
    learning_style: str = Field("Text-based", description="Preferred learning style")
    background: str = Field("Unknown", description="Background knowledge level")
    language: str = Field("English", description="Preferred language")

class QuizRequest(BaseModel):
    subject: str = Field(..., description="Academic subject")
    level: str = Field(..., description="Learning level")
    num_questions: int = Field(5, description="Number of quiz questions", ge=1, le=10)
    reveal_format: Optional[bool] = Field(True, description="Whether to format with hidden answers")

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

class TutorResponse(BaseModel):
    response: str

class QuizResponse(BaseModel):
    quiz: List[Dict[str, Any]]
    formatted_quiz: Optional[str] = None


@app.post("/tutor", response_model=TutorResponse)
async def get_tutoring_response(data: TutorRequest):
    """
    Generate a personalized tutoring explanation based on user preferences.
    """
    try:
        explanation = generate_tutoring_response(
            data.subject, 
            data.level, 
            data.question, 
            data.learning_style, 
            data.background, 
            data.language
        )
        
        return {"response": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")

@app.post("/quiz", response_model=QuizResponse)
async def generate_quiz_api(data: QuizRequest):
    """
    Generate a quiz with multiple-choice questions based on subject and level.
    """
    try:
        quiz_result = generate_quiz(
            data.subject, 
            data.level, 
            data.num_questions,
            reveal_answer=data.reveal_format
        )
        
        if data.reveal_format:
            return {
                "quiz": quiz_result["quiz_data"],
                "formatted_quiz": quiz_result["formatted_quiz"]
            }
        else:
            return {"quiz": quiz_result["quiz_data"]}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")
    




@app.get("/quiz-html/{subject}/{level}/{num_questions}", response_class=HTMLResponse)
async def get_quiz_html(subject: str, level: str, num_questions: int = 5):
    """
    Get a formatted HTML quiz page.
    """
    try:
        quiz_result = generate_quiz(subject, level, num_questions, reveal_answer=True)
        return quiz_result["formatted_quiz"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz HTML: {str(e)}")



@app.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    """
    Process uploaded PDF file and extract content/summary.
    """
    try:
        # Debug info
        print(f"Received file: {file.filename}")
        print(f"Content type: {file.content_type}")
        print(f"File size: {file.size if hasattr(file, 'size') else 'Unknown'}")
        
        # More flexible PDF validation
        if file.filename and not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must have .pdf extension")
        
        # Read PDF content
        pdf_content = await file.read()
        print(f"Read {len(pdf_content)} bytes")
        
        # Extract text from PDF
        pdf_text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n"
                    print(f"Page {len(pdf_reader.pages)}: {len(page_text)} characters")
        except Exception as e:
            print(f"PyPDF2 error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")
        
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Generate AI-powered summary using the AI engine
        try:
            from ai_engine import get_llm
            
            llm = get_llm()
            
            # Create prompt for PDF analysis
            analysis_prompt = f"""
            Analyze the following PDF content and provide a comprehensive summary:
            
            PDF CONTENT:
            {pdf_text[:3000]}  # Limit to first 3000 chars for analysis
            
            INSTRUCTIONS:
            1. Provide a clear, structured summary of the main topics and key points
            2. Identify the main themes, concepts, and important information
            3. Organize the summary in a logical, easy-to-understand format
            4. Highlight any key definitions, formulas, or important facts
            5. Keep the summary concise but comprehensive (around 200-300 words)
            
            Please format your response with clear headings and bullet points for readability.
            """
            
            # Generate AI summary
            ai_response = llm([HumanMessage(content=analysis_prompt)])
            ai_summary = ai_response.content
            
        except Exception as ai_error:
            print(f"AI summary generation failed: {str(ai_error)}")
            # Fallback to basic summary if AI fails
            ai_summary = f"PDF processed successfully. Extracted {len(pdf_text)} characters of text from {len(pdf_reader.pages)} pages. Content includes: {pdf_text[:200]}..."
        
        return {
            "filename": file.filename,
            "content": pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text,
            "summary": ai_summary,
            "total_chars": len(pdf_text),
            "pages": len(pdf_reader.pages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}