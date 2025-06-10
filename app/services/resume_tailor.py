# File: app/services/resume_tailor.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def tailor_resume(resume_text: str, job_description: str) -> str:
    system_prompt = (
        "You are a resume optimization assistant. Given a raw resume and a job description, "
        "rewrite the resume content to better match the tone, skills, and keywords of the job description. "
        "Preserve all original experience, but improve relevance and alignment."
    )

    user_prompt = f"""
    --- Resume ---
    {resume_text}

    --- Job Description ---
    {job_description}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
