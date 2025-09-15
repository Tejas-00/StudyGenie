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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

class PDFDiscussionRequest(BaseModel):
    question: str = Field(..., description="User's question about the PDF content")
    pdf_content: str = Field(..., description="PDF content for context")
    pdf_summary: str = Field(..., description="PDF summary for context")

class PDFDiscussionResponse(BaseModel):
    response: str


@app.post("/tutor", response_model=TutorResponse)
async def get_tutoring_response(data: TutorRequest):
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
        return {"response": f"❌ Error generating explanation: {str(e)}"}


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
        # print(f"Received file: {file.filename}")
        # print(f"Content type: {file.content_type}")
        # print(f"File size: {file.size if hasattr(file, 'size') else 'Unknown'}")
        
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
            
            # Generate comprehensive flashcards from the entire PDF content
            flashcards_prompt = f"""
            Based on the following PDF content, create comprehensive educational flashcards that cover the ENTIRE content thoroughly:
            
            PDF CONTENT:
            {pdf_text}  # Use the FULL content for comprehensive coverage
            
            INSTRUCTIONS:
            Your task is to create flashcards that comprehensively cover ALL the important topics, concepts, definitions, and key points from the PDF content.
            
            REQUIREMENTS:
            1. Create 10-15 flashcards (or more if needed) to ensure complete coverage
            2. Each flashcard should focus on a specific, distinct concept or topic
            3. Cover all major sections, chapters, or themes mentioned in the content
            4. Include flashcards for:
               - Key definitions and terminology
               - Important concepts and principles
               - Formulas, equations, or mathematical concepts
               - Historical facts, dates, or events
               - Processes, procedures, or methodologies
               - Examples, case studies, or applications
               - Theories, laws, or fundamental principles
            
            FLASHCARD STRUCTURE:
            Each flashcard must have:
            - topic: The main subject area or category
            - question: A specific, focused question about the concept
            - answer: A clear, comprehensive explanation (2-3 sentences minimum)
            
            FORMAT:
            Return ONLY a valid JSON array with this exact structure:
            [
                {{
                    "topic": "Main topic or concept area",
                    "question": "Specific question about the topic",
                    "answer": "Clear, detailed answer explaining the concept thoroughly"
                }}
            ]
            
            IMPORTANT: Ensure the JSON is valid and covers the entire PDF content comprehensively.
            """
            
            # Generate comprehensive flashcards
            flashcards_response = llm([HumanMessage(content=flashcards_prompt)])
            flashcards_text = flashcards_response.content
            
            # Parse flashcards JSON
            import json
            try:
                # Extract JSON from the response (in case there's extra text)
                import re
                json_match = re.search(r'\[.*\]', flashcards_text, re.DOTALL)
                if json_match:
                    flashcards = json.loads(json_match.group())
                else:
                    flashcards = json.loads(flashcards_text)
                
                # Validate and enhance flashcards if needed
                if len(flashcards) < 8:  # If too few flashcards, generate more
                    additional_prompt = f"""
                    The previous response only generated {len(flashcards)} flashcards. 
                    Please generate additional flashcards to ensure comprehensive coverage of this content:
                    
                    {pdf_text[:2000]}
                    
                    Generate 5-8 more flashcards covering different aspects not yet covered.
                    Return only valid JSON array.
                    """
                    
                    additional_response = llm([HumanMessage(content=additional_prompt)])
                    additional_text = additional_response.content
                    
                    try:
                        additional_json = re.search(r'\[.*\]', additional_text, re.DOTALL)
                        if additional_json:
                            additional_flashcards = json.loads(additional_json.group())
                            flashcards.extend(additional_flashcards)
                    except:
                        pass
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse flashcards JSON: {str(e)}")
                # Create comprehensive fallback flashcards
                flashcards = [
                    {
                        "topic": "PDF Content Overview",
                        "question": "What is the main topic of this document?",
                        "answer": "This document covers various topics and concepts that need to be studied and understood."
                    },
                    {
                        "topic": "Key Concepts",
                        "question": "What are the main concepts discussed in this document?",
                        "answer": "The document discusses important concepts, definitions, and principles related to the subject matter."
                    },
                    {
                        "topic": "Important Information",
                        "question": "What key information should be remembered from this document?",
                        "answer": "Key information includes definitions, formulas, processes, and fundamental principles that are essential for understanding the topic."
                    }
                ]
            
        except Exception as ai_error:
            print(f"AI summary generation failed: {str(ai_error)}")
            # Fallback to basic summary if AI fails
            ai_summary = f"PDF processed successfully. Extracted {len(pdf_text)} characters of text from {len(pdf_reader.pages)} pages. Content includes: {pdf_text[:200]}..."
            flashcards = [
                {
                    "topic": "PDF Content",
                    "question": "What is the main topic of this document?",
                    "answer": "The document covers various topics and concepts."
                }
            ]
        
        return {
            "filename": file.filename,
            "content": pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text,
            "summary": ai_summary,
            "flashcards": flashcards,
            "total_chars": len(pdf_text),
            "pages": len(pdf_reader.pages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/discuss_pdf", response_model=PDFDiscussionResponse)
async def discuss_pdf_content(data: PDFDiscussionRequest):
    """
    Answer user questions based on the uploaded PDF content only.
    """
    try:
        from ai_engine import get_llm
        
        llm = get_llm()
        
        # Create a strict prompt that only allows answers based on PDF content
        discussion_prompt = f"""
        You are a helpful study assistant that can ONLY answer questions based on the provided PDF content.
        
        IMPORTANT RULES:
        1. ONLY answer questions using information from the PDF content provided
        2. If the question cannot be answered from the PDF content, say "I can only answer questions based on the content of your uploaded PDF. This question cannot be answered from the information available in your document."
        3. Do NOT use any external knowledge or general information
        4. Base your answers ONLY on the PDF content and summary provided
        5. Be helpful and educational, but stay within the bounds of the PDF content
        
        PDF CONTENT:
        {data.pdf_content}
        
        PDF SUMMARY:
        {data.pdf_summary}
        
        USER QUESTION:
        {data.question}
        
        INSTRUCTIONS:
        - Analyze the question carefully
        - Search through the PDF content for relevant information
        - Provide a clear, helpful answer based ONLY on the PDF content
        - If the PDF doesn't contain enough information to answer the question, politely explain this limitation
        - Use the PDF content to provide specific examples, definitions, or explanations when possible
        
        Your response should be educational, clear, and strictly based on the PDF content provided.
        """
        
        # Generate AI response
        ai_response = llm([HumanMessage(content=discussion_prompt)])
        ai_answer = ai_response.content
        
        return {"response": ai_answer}
        
    except Exception as e:
        print(f"PDF discussion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating discussion response: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}