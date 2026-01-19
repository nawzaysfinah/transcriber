import React from 'react';

export default function Logs({ entries }) {
  return (
    <div className="card grid">
      <div className="tabs">
        <div className="tab active">Logs</div>
      </div>
      <div className="logs">
        {entries && entries.length ? (
          entries.map((log, idx) => (
            <div className="log-line" key={`${idx}-${log.time}`}>
              <span className="log-level">{log.level}</span>
              <span className="muted">{new Date(log.time).toLocaleTimeString()}</span>
              <span>{log.message}</span>
            </div>
          ))
        ) : (
          <div className="muted">Logs will appear here.</div>
        )}
      </div>
    </div>
  );
}
