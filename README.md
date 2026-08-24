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

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` and add your Gemini key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
DATABASE_URL=sqlite:///./app/data/resume_screener.db
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The dashboard runs at `http://localhost:5173`.

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

1. Start the backend and frontend.
2. Paste a job description into the dashboard.
3. Upload resumes from the `samples/` folder or your own PDF resumes.
4. Click **Screen resumes**.
5. Review ranked scores, strengths, gaps, and recruiter justification.

## Deploy On Render

This repo is configured for a single Render Web Service using Docker. The Docker build compiles the React frontend and serves it from the FastAPI backend.

### 1. Push To GitHub

```bash
git init
git add .
git commit -m "Initial smart resume screener"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smart-resume-screener.git
git push -u origin main
```

Do not commit `backend/.env`; it is already ignored.

### 2. Create The Render Service

1. Open the Render dashboard.
2. Click **New +**.
3. Choose **Blueprint** if Render detects `render.yaml`, or choose **Web Service** and connect the GitHub repo.
4. Use these settings if creating the service manually:
   - Runtime: Docker
   - Branch: `main`
   - Root Directory: leave blank
   - Health Check Path: `/health`
5. Add environment variables:
   - `GEMINI_API_KEY`: your Gemini API key
   - `GEMINI_MODEL`: `gemini-3.6-flash`
   - `DATABASE_URL`: `sqlite:////tmp/resume_screener.db`
   - `FRONTEND_ORIGINS`: leave blank for same-origin deployment
   - Do not set `VITE_API_URL` on Render for the single-service deployment
6. Click **Create Web Service**.

After deployment, Render gives you a URL like:

```text
https://smart-resume-screener.onrender.com
```

Open that URL to use the dashboard. The API is served from the same domain.

## Notes

- This project intentionally uses Gemini only. If `GEMINI_API_KEY` is missing or invalid, screening fails.
- PDF parsing quality depends on how the resume PDF stores text. Scanned image PDFs need OCR, which is outside the current scope.
- The parser uses lightweight extraction for the demo. Gemini provides the final match reasoning.
- On Render Free, local SQLite data can reset when the service restarts or redeploys. Use Render Postgres for persistent production storage.
