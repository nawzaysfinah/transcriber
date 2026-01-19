import React from 'react';

export default function UrlInput({ url, onChange, onSubmit, processing, error }) {
  return (
    <div className="card grid">
      <label className="label" htmlFor="url-input">
        Podcast episode URL (public audio link)
      </label>
      <input
        id="url-input"
        type="text"
        placeholder="https://..."
        value={url}
        onChange={(e) => onChange(e.target.value)}
        disabled={processing}
      />
      {error ? <div className="error">{error}</div> : <div className="muted">Spotify links may be DRM-blocked; prefer public audio.</div>}
      <button onClick={onSubmit} disabled={processing || !url}>
        {processing ? 'Processing...' : 'Process'}
      </button>
    </div>
  );
}
