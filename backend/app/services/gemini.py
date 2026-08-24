import json

from google import genai
from google.genai import types

from app.config import get_settings


def score_candidate(job_description: str, candidate: dict) -> dict:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required for Gemini-only scoring.")

    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = f"""
You are an expert technical recruiter. Compare the candidate resume to the job description.

Return strict JSON with:
- score: number from 1 to 10
- verdict: one of "Strong Match", "Possible Match", "Weak Match"
- justification: concise explanation in 2-3 sentences
- strengths: array of 3 short strings
- gaps: array of 2 short strings

Job description:
{job_description}

Candidate structured data:
{json.dumps(candidate, ensure_ascii=False)}
"""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )

    data = json.loads(response.text or "{}")
    return {
        "score": max(1, min(10, float(data.get("score", 1)))),
        "verdict": str(data.get("verdict", "Weak Match")),
        "justification": str(data.get("justification", "")),
        "strengths": _as_string_list(data.get("strengths")),
        "gaps": _as_string_list(data.get("gaps")),
    }


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value[:5]]
