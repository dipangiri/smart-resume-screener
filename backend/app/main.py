import json
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_frontend_origins
from app.database import init_db, insert_candidate, insert_screening_run, list_candidates
from app.services.gemini import score_candidate
from app.services.parser import extract_text_from_file, parse_resume

app = FastAPI(title="Smart Resume Screener API")


@app.on_event("startup")
def startup() -> None:
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/screen")
async def screen_resumes(
    job_description: Annotated[str, Form()],
    resumes: Annotated[list[UploadFile], File()],
) -> dict:
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")
    if not resumes:
        raise HTTPException(status_code=400, detail="Upload at least one resume.")

    run_id = insert_screening_run(job_description)
    results = []

    for resume in resumes:
        try:
            file_bytes = await resume.read()
            raw_text = extract_text_from_file(file_bytes, resume.filename or "resume")
            parsed = parse_resume(raw_text)
            scoring = score_candidate(job_description, parsed)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Gemini scoring failed for {resume.filename}: {exc}",
            ) from exc

        candidate = {
            "filename": resume.filename,
            "name": parsed["name"],
            "email": parsed["email"],
            "phone": parsed["phone"],
            "skills": json.dumps(parsed["skills"]),
            "experience": parsed["experience"],
            "education": parsed["education"],
            "raw_text": parsed["raw_text"],
            "score": scoring["score"],
            "verdict": scoring["verdict"],
            "justification": scoring["justification"],
            "strengths": json.dumps(scoring["strengths"]),
            "gaps": json.dumps(scoring["gaps"]),
        }
        candidate_id = insert_candidate(candidate)
        results.append(_response_candidate(candidate_id, candidate))

    results.sort(key=lambda item: item["score"], reverse=True)
    return {"run_id": run_id, "results": results}


@app.get("/candidates")
def candidates() -> dict:
    return {"candidates": [_row_to_candidate(row) for row in list_candidates()]}


frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    index_file = frontend_dist / "index.html"
    requested_file = frontend_dist / full_path

    if requested_file.is_file():
        return FileResponse(requested_file)
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Frontend build not found.")


def _response_candidate(candidate_id: int, candidate: dict) -> dict:
    return {
        "id": candidate_id,
        "filename": candidate["filename"],
        "name": candidate["name"],
        "email": candidate["email"],
        "phone": candidate["phone"],
        "skills": json.loads(candidate["skills"]),
        "experience": candidate["experience"],
        "education": candidate["education"],
        "score": candidate["score"],
        "verdict": candidate["verdict"],
        "justification": candidate["justification"],
        "strengths": json.loads(candidate["strengths"]),
        "gaps": json.loads(candidate["gaps"]),
    }


def _row_to_candidate(row) -> dict:
    return {
        "id": row["id"],
        "filename": row["filename"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "skills": json.loads(row["skills"]),
        "experience": row["experience"],
        "education": row["education"],
        "score": row["score"],
        "verdict": row["verdict"],
        "justification": row["justification"],
        "strengths": json.loads(row["strengths"]),
        "gaps": json.loads(row["gaps"]),
        "created_at": row["created_at"],
    }
