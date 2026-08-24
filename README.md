# Smart Resume Screener

A full-stack resume screening app that parses PDF or text resumes, extracts structured candidate details, and uses the Gemini API to compare each candidate against a job description.

## Features

- Upload multiple PDF, TXT, or MD resumes
- Paste a job description
- Extract name, email, phone, skills, experience, and education
- Score each candidate with Gemini from 1 to 10
- Show ranked candidates with verdict, justification, strengths, and gaps
- Store screened candidates in SQLite
- React dashboard for a demo-ready workflow

## Tech Stack

- Backend: Python, FastAPI, SQLite
- Frontend: React, Vite, JavaScript
- LLM: Gemini API through `google-genai`
- Resume parsing: `pypdf` plus lightweight local extraction

## Project Structure

```text
backend/
  app/
    main.py
    config.py
    database.py
    services/
      gemini.py
      parser.py
  requirements.txt
  .env.example
frontend/
  src/
    App.jsx
    components/
      CandidateCard.jsx
    styles.css
  package.json
  .env.example
samples/
  backend_developer_resume.txt
  data_analyst_resume.txt
```

## API Endpoints

### `POST /screen`

Multipart form request:

- `job_description`: text
- `resumes`: one or more PDF, TXT, or MD files

Returns ranked candidates:

```json
{
  "run_id": 1,
  "results": [
    {
      "id": 1,
      "filename": "resume.pdf",
      "name": "Candidate Name",
      "skills": ["python", "fastapi", "sql"],
      "score": 8.5,
      "verdict": "Strong Match",
      "justification": "The candidate aligns well with the backend and API requirements.",
      "strengths": ["FastAPI experience", "SQL background"],
      "gaps": ["Limited React evidence"]
    }
  ]
}
```

### `GET /candidates`

Returns previously screened candidates from SQLite.

## Gemini Prompt

The backend sends Gemini a structured recruiter prompt:

```text
You are an expert technical recruiter. Compare the candidate resume to the job description.

Return strict JSON with:
- score: number from 1 to 10
- verdict: one of "Strong Match", "Possible Match", "Weak Match"
- justification: concise explanation in 2-3 sentences
- strengths: array of 3 short strings
- gaps: array of 2 short strings
```

The job description and parsed candidate data are included after the instruction. The app requests `application/json` output to keep parsing reliable.

## Demo Flow

1. Open the deployed Render application.
2. Paste a job description into the dashboard.
3. Upload resumes from the `samples/` folder or your own PDF resumes.
4. Click **Screen resumes**.
5. Review ranked scores, strengths, gaps, and recruiter justification.

## Demo Video

https://github.com/user-attachments/assets/bbb4a858-f32c-4723-9674-675823795afd
