import React from 'react';

export default function TranscriptView({ markdown, onDownload }) {
  return (
    <div className="card grid">
      <div className="tabs">
        <div className="tab active">Transcript</div>
        <button onClick={() => onDownload('transcript')}>Download .md</button>
      </div>
      <textarea className="textarea" readOnly value={markdown || 'Transcript will appear here.'} />
    </div>
  );
}
