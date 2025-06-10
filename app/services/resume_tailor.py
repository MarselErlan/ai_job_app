# File: app/services/resume_tailor.py
"""
RESUME TAILOR SERVICE - AI-powered resume customization

This service uses GPT-4 to intelligently rewrite your resume for specific job postings.
It's like having a professional resume writer who understands both your background
and the specific job requirements.

The Magic:
1. Takes your original resume text
2. Takes the job description you want to apply for
3. Uses GPT-4 to rewrite your resume to better match the job
4. Preserves all your real experience but optimizes language and focus
5. Returns a tailored resume that speaks directly to the employer's needs

This isn't lying or fabricating - it's strategic presentation of your existing skills.
"""

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

    # User prompt - This provides the actual data for GPT-4 to work with
    # We clearly separate the resume from the job description for better processing
    user_prompt = f"""
    --- Resume ---
    {resume_text}

    --- Job Description ---
    {job_description}
    """

    # Make the API call to GPT-4
    response = client.chat.completions.create(
        model="gpt-4o",  # Use the most capable GPT-4 model
        messages=[
            {"role": "system", "content": system_prompt},  # Define GPT-4's role
            {"role": "user", "content": user_prompt}       # Provide the data to process
        ],
        temperature=0.4  # Balance between creativity (higher) and consistency (lower)
        # 0.4 gives good results - creative enough to rewrite effectively,
        # consistent enough to maintain professionalism
    )

    # Extract the tailored resume from GPT-4's response
    # response.choices[0].message.content contains the rewritten resume
    return response.choices[0].message.content.strip()
