import React, { useEffect, useMemo, useState } from "react";
import { AlertCircle, BriefcaseBusiness, FileUp, Loader2, RefreshCw, Sparkles } from "lucide-react";
import CandidateCard from "./components/CandidateCard.jsx";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const starterJobDescription =
  "We are hiring a Python backend developer with FastAPI, SQL, REST API design, Git, and experience building AI or NLP features. React experience is a plus.";

function App() {
  const [jobDescription, setJobDescription] = useState(starterJobDescription);
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedNames = useMemo(() => files.map((file) => file.name).join(", "), [files]);

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    setHistoryLoading(true);
    try {
      const response = await fetch(`${API_URL}/candidates`);
      if (!response.ok) return;
      const data = await response.json();
      setHistory(data.candidates || []);
    } finally {
      setHistoryLoading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResults([]);

    if (!jobDescription.trim()) {
      setError("Paste a job description before screening resumes.");
      return;
    }
    if (!files.length) {
      setError("Upload at least one PDF or text resume.");
      return;
    }

    const formData = new FormData();
    formData.append("job_description", jobDescription);
    files.forEach((file) => formData.append("resumes", file));

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/screen`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Screening failed.");
      }

      setResults(data.results || []);
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="intro-band">
        <div>
          <p className="eyebrow">Gemini-powered applicant screening</p>
          <h1>Smart Resume Screener</h1>
          <p className="intro-copy">
            Upload resumes, paste a role description, and get ranked candidates with skills,
            strengths, gaps, and recruiter-style justification.
          </p>
        </div>
        <div className="status-pill">
          <Sparkles size={18} />
          Gemini API required
        </div>
      </section>

      <section className="workspace-grid">
        <form className="screening-panel" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <BriefcaseBusiness size={20} />
            <h2>Screen candidates</h2>
          </div>

          <label className="field-label" htmlFor="job-description">
            Job description
          </label>
          <textarea
            id="job-description"
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
            rows={10}
          />

          <label className="upload-box">
            <FileUp size={24} />
            <span>{files.length ? selectedNames : "Choose PDF or text resumes"}</span>
            <input
              type="file"
              accept=".pdf,.txt,.md"
              multiple
              onChange={(event) => setFiles(Array.from(event.target.files || []))}
            />
          </label>

          {error && (
            <div className="error-message">
              <AlertCircle size={18} />
              {error}
            </div>
          )}

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? <Loader2 className="spin" size={18} /> : <Sparkles size={18} />}
            {loading ? "Screening with Gemini..." : "Screen resumes"}
          </button>
        </form>

        <section className="results-panel">
          <div className="panel-heading with-action">
            <div>
              <p className="eyebrow">Ranked output</p>
              <h2>Results</h2>
            </div>
            <button className="icon-button" type="button" onClick={loadHistory} title="Refresh history">
              <RefreshCw size={18} className={historyLoading ? "spin" : ""} />
            </button>
          </div>

          <div className="results-list">
            {(results.length ? results : history).length ? (
              (results.length ? results : history).map((candidate) => (
                <CandidateCard key={`${candidate.id}-${candidate.filename}`} candidate={candidate} />
              ))
            ) : (
              <div className="empty-state">
                <p>No candidates screened yet.</p>
                <span>Run a screening to populate this area.</span>
              </div>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}

export default App;
