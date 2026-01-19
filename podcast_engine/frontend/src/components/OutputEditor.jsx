import React from 'react';

export default function OutputEditor({ title, value, onChange, onDownload }) {
  return (
    <div className="card grid">
      <div className="tabs">
        <div className="tab active">{title}</div>
        <button onClick={onDownload}>Download .md</button>
      </div>
      <textarea className="textarea" value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}
