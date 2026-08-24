import { Mail, Phone, Star } from "lucide-react";
import React from "react";

function CandidateCard({ candidate }) {
  const score = Number(candidate.score || 0);

  return (
    <article className="candidate-card">
      <div className="candidate-topline">
        <div>
          <h3>{candidate.name || candidate.filename}</h3>
          <p>{candidate.filename}</p>
        </div>
        <div className="score-badge">
          <Star size={16} />
          {score.toFixed(1)}
        </div>
      </div>

      <div className="candidate-meta">
        {candidate.email && (
          <span>
            <Mail size={14} />
            {candidate.email}
          </span>
        )}
        {candidate.phone && (
          <span>
            <Phone size={14} />
            {candidate.phone}
          </span>
        )}
      </div>

      <div className="verdict-row">
        <strong>{candidate.verdict}</strong>
        <span>{candidate.justification}</span>
      </div>

      <TagGroup label="Skills" items={candidate.skills} />
      <TagGroup label="Strengths" items={candidate.strengths} />
      <TagGroup label="Gaps" items={candidate.gaps} muted />
    </article>
  );
}

function TagGroup({ label, items = [], muted = false }) {
  if (!items.length) return null;

  return (
    <div className="tag-group">
      <p>{label}</p>
      <div>
        {items.map((item) => (
          <span className={muted ? "tag muted" : "tag"} key={item}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

export default CandidateCard;
