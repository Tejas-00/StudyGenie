from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import os
from dotenv import load_dotenv
import json
import re
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_llm():
    try:
        return ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            openai_api_key=OPENAI_API_KEY
        )
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        raise Exception(f"Failed to initialize AI model: {str(e)}")
    
def generate_tutoring_response(subject, level, question, learning_style, background, language):
    """
    Generate a personalized tutoring response based on user preferences.
    
    Args:
        subject (str): The academic subject
        level (str): Learning level (Beginner, Intermediate, Advanced)
        question (str): User's specific question
        learning_style (str): Preferred learning style (Visual, Text-based, Hands-on)
        background (str): User's background knowledge
        language (str): Preferred language for response
    
    Returns:
        str: Formatted tutoring response
    """
    try:
        # Get LLM instance
        llm = get_llm()
        
        # Construct an effective prompt
        prompt = _create_tutoring_prompt(subject, level, question, learning_style, background, language)
        
        # Generate response with error handling
        logger.info(f"Generating tutoring response for subject: {subject}, level: {level}")
        response = llm([HumanMessage(content=prompt)])
        
        # Post-process the response based on learning style
        return _format_tutoring_response(response.content, learning_style)
        
    except Exception as e:
        logger.error(f"Error generating tutoring response: {str(e)}")
        raise Exception(f"Failed to generate tutoring response: {str(e)}")



def _create_tutoring_prompt(subject, level, question, learning_style, background, language):
    """Helper function to create a well-structured tutoring prompt"""
    
    # Build the prompt with all necessary context and instruction
    prompt = f"""
    You are an expert tutor in {subject} at the {level} level. 
    
    STUDENT PROFILE:
    - Background knowledge: {background}
    - Learning style preference: {learning_style}
    - Language preference: {language}
    
    QUESTION:
    {question}
    
    INSTRUCTIONS:
    1. Provide a clear, educational explanation that directly addresses the question
    2. Tailor your explanation to a {background} student at {level} level
    3. Use {language} as the primary language
    4. Format your response with appropriate markdown for readability
    
    LEARNING STYLE ADAPTATIONS:
    - For Visual learners: Include descriptions of visual concepts, diagrams, or mental models
    - For Text-based learners: Provide clear, structured explanations with defined concepts
    - For Hands-on learners: Include practical examples, exercises, or applications
    
    Your explanation should be educational, accurate, and engaging.
    """
    
    return prompt



def _format_tutoring_response(content, learning_style):
    """Helper function to format the tutoring response based on learning style"""
    
    if learning_style == "Visual":
        return content + "\n\n*Note: Visualize these concepts as you read for better retention.*"
    elif learning_style == "Hands-on":
        return content + "\n\n*Tip: Try working through the examples yourself to reinforce your learning.*"
    else:
        return content
    


def _create_quiz_prompt(subject, level, num_questions):
    """Helper function to create a well-structured quiz generation prompt"""
    
    return f"""
    Create a {level}-level quiz on {subject} with exactly {num_questions} multiple-choice questions.
    
    INSTRUCTIONS:
    1. Each question should be appropriate for {level} level students
    2. Each question must have exactly 4 answer options (A, B, C, D)
    3. Clearly indicate the correct answer
    4. Cover diverse aspects of {subject}
    
    FORMAT YOUR RESPONSE AS JSON:
    ```json
    [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Brief explanation of why this answer is correct"
        }},
        ...
    ]
    ```
    
    IMPORTANT: Make sure to return valid JSON that can be parsed. Do not include any text outside the JSON array.
    Include a brief explanation for each correct answer.
    """

def _create_fallback_quiz(subject, num_questions):
    """Helper function to create a fallback quiz if parsing fails"""
    
    logger.warning(f"Using fallback quiz for {subject}")
    
    return [
        {
            "question": f"Sample {subject} question #{i+1}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "This is a fallback explanation."
        }
        for i in range(num_questions)
    ]

def _validate_quiz_data(quiz_data):
    """Helper function to validate quiz data structure"""
    
    if not isinstance(quiz_data, list):
        raise ValueError("Quiz data must be a list of questions")
    
    for question in quiz_data:
        if not isinstance(question, dict):
            raise ValueError("Each quiz item must be a dictionary")
            
        if not all(key in question for key in ["question", "options", "correct_answer"]):
            raise ValueError("Each quiz item must have question, options, and correct_answer")
            
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            raise ValueError("Each question must have exactly 4 options")
        


def _parse_quiz_response(response_content, subject, num_questions):
    """Helper function to parse and validate the quiz response"""
    
    try:
        # Try to find JSON content using regex
        json_match = re.search(r'```json\s*(\[[\s\S]*?\])\s*```', response_content)
        
        if json_match:
            # Extract JSON from code block
            quiz_json = json_match.group(1)
        else:
            # Try to find raw JSON array
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response_content, re.DOTALL)
            if json_match:
                quiz_json = json_match.group(0)
            else:
                # Assume the entire response is JSON
                quiz_json = response_content
        
        # Parse the JSON
        quiz_data = json.loads(quiz_json)
        
        # Validate the data structure
        _validate_quiz_data(quiz_data)
        
        # Ensure we have the requested number of questions
        if len(quiz_data) > num_questions:
            quiz_data = quiz_data[:num_questions]
        
        # Add explanation field if missing
        for question in quiz_data:
            if "explanation" not in question:
                question["explanation"] = f"The correct answer is {question['correct_answer']}."
        
        return quiz_data
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parsing quiz response: {str(e)}")
        
        # Create a fallback quiz if parsing fails
        return _create_fallback_quiz(subject, num_questions)
    



def generate_quiz(subject, level, num_questions=5, reveal_answer=True):
    """
    Generate a quiz with multiple-choice questions based on subject and level.
    
    Args:
        subject (str): The academic subject
        level (str): Learning level (Beginner, Intermediate, Advanced)
        num_questions (int): Number of questions to generate
        reveal_answer (bool): Whether to format the response with hidden answers that can be revealed
    
    Returns:
        dict: Contains quiz data (list of questions) and formatted HTML if reveal_answer is True
    """
    try:
        # Get LLM instance
        llm = get_llm()
        
        # Create a structured prompt for quiz generation
        prompt = _create_quiz_prompt(subject, level, num_questions)
        
        # Generate response
        logger.info(f"Generating quiz for subject: {subject}, level: {level}, questions: {num_questions}")
        response = llm([HumanMessage(content=prompt)])
        
        # Parse and validate the response
        quiz_data = _parse_quiz_response(response.content, subject, num_questions)
        
        # Format the quiz with hidden answers if requested
        if reveal_answer:
            formatted_quiz = _format_quiz_with_reveal(quiz_data)
            return {
                "quiz_data": quiz_data,
                "formatted_quiz": formatted_quiz
            }
        else:
            return {
                "quiz_data": quiz_data
            }
        
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise Exception(f"Failed to generate quiz: {str(e)}")