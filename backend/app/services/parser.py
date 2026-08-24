import re
from pathlib import Path

from pypdf import PdfReader


SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "react",
    "node.js",
    "fastapi",
    "django",
    "flask",
    "sql",
    "sqlite",
    "postgresql",
    "mongodb",
    "machine learning",
    "deep learning",
    "nlp",
    "data analysis",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "aws",
    "azure",
    "docker",
    "git",
    "rest api",
    "html",
    "css",
}


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_text(file_bytes)
    if suffix in {".txt", ".md"}:
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError("Only PDF, TXT, and MD resumes are supported.")


def parse_resume(text: str) -> dict:
    normalized = _squash(text)
    return {
        "name": _extract_name(normalized),
        "email": _first_match(r"[\w.+-]+@[\w-]+\.[\w.-]+", normalized),
        "phone": _first_match(r"(?:\+?\d[\d\s().-]{7,}\d)", normalized),
        "skills": _extract_skills(normalized),
        "experience": _extract_section(normalized, ["experience", "work experience", "employment"]),
        "education": _extract_section(normalized, ["education", "academic"]),
        "raw_text": normalized,
    }


def _extract_pdf_text(file_bytes: bytes) -> str:
    from io import BytesIO

    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _squash(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r", "\n")).strip()


def _first_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(0).strip() if match else None


def _extract_name(text: str) -> str | None:
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if "@" in clean or len(clean.split()) > 5:
            continue
        return clean
    return None


def _extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = [skill for skill in sorted(SKILL_KEYWORDS) if skill in lowered]
    return found


def _extract_section(text: str, headings: list[str]) -> str | None:
    pattern = "|".join(re.escape(heading) for heading in headings)
    match = re.search(
        rf"(?i)\b({pattern})\b[:\n\s-]*(.*?)(?=\n\s*[A-Z][A-Za-z ]{{2,}}[:\n]|$)",
        text,
        flags=re.DOTALL,
    )
    if not match:
        return None
    section = re.sub(r"\s+", " ", match.group(2)).strip()
    return section[:700] or None

