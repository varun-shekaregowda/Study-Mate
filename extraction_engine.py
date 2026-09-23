import pdfplumber
import requests
import json
import os

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def parse_curriculum_with_ollama(raw_text, model_name="qwen3:8b"):
    prompt = f"""
    You are an expert curriculum designer. Extract the subjects/topics from the following syllabus text.
    Return ONLY a valid JSON array of objects, where each object has these exact keys:
    "id": a unique string id (e.g. "topic_1")
    "name": the name of the subject/topic
    "complexity": an integer from 1 to 5 indicating difficulty
    "prerequisites": a list of string ids of other topics in this list that must be learned first (empty list if none)
    "estimated_base_hours": a float estimating hours to learn (e.g., 2.0)
    "recommended_activities": a list of string activities (e.g., ["Reading", "Exercises"])
    
    Do not wrap the response in markdown code blocks. Just output the raw JSON array.
    
    Syllabus Text:
    {raw_text[:3000]}
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        result_text = data.get("response", "[]").strip()
        
        # Clean up markdown if the LLM wrapped the JSON
        if result_text.startswith("```json"):
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif result_text.startswith("```"):
            result_text = result_text.split("```")[1].strip()
            
        curriculum = json.loads(result_text)
        return curriculum
    except Exception as e:
        print(f"Error parsing curriculum: {e}")
        return []
