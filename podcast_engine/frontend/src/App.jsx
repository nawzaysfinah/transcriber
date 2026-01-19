import React, { useEffect, useRef, useState } from 'react';
import UrlInput from './components/UrlInput';
import Progress from './components/Progress';
import TranscriptView from './components/TranscriptView';
import OutputEditor from './components/OutputEditor';
import Logs from './components/Logs';
import './styles.css';

const API_BASE = 'http://localhost:8000';

function isValidUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

export default function App() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState({ state: 'idle', step: null, error: null });
  const [logs, setLogs] = useState([]);
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [thread, setThread] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const poller = useRef(null);

  useEffect(() => {
    return () => {
      if (poller.current) clearInterval(poller.current);
    };
  }, []);

  const startPolling = () => {
    if (poller.current) clearInterval(poller.current);
    poller.current = setInterval(fetchStatus, 2000);
  };

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`);
      const data = await res.json();
      setStatus(data);
      setLogs(data.logs || []);
      if (data.state === 'completed') {
        clearInterval(poller.current);
        setProcessing(false);
        await fetchResults();
      } else if (data.state === 'error') {
        clearInterval(poller.current);
        setProcessing(false);
        setError(data.error || 'Processing failed.');
      }
    } catch (err) {
      setError(err.message || 'Status check failed.');
      setProcessing(false);
      if (poller.current) clearInterval(poller.current);
    }
  };

  const fetchResults = async () => {
    const res = await fetch(`${API_BASE}/results`);
    if (!res.ok) {
      const detail = await res.text();
      setError(detail);
      return;
    }
    const data = await res.json();
    setTranscript(data.transcript_markdown);
    setSummary(data.summary_markdown);
    setThread(data.thread_markdown);
  };

  const onSubmit = async () => {
    setError('');
    if (!url || !isValidUrl(url)) {
      setError('Enter a valid http(s) URL.');
      return;
    }
    setProcessing(true);
    setStatus({ state: 'running', step: 'init', error: null });
    setLogs([]);
    setTranscript('');
    setSummary('');
    setThread('');
    try {
      const res = await fetch(`${API_BASE}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) {
        const detail = await res.json();
        throw new Error(detail.detail || 'Failed to start processing.');
      }
      startPolling();
    } catch (err) {
      setError(err.message);
      setProcessing(false);
    }
  };

  const downloadFile = (content, filename) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <>
      <h1>Podcast Engine</h1>
      <p className="lead">Download, transcribe, and summarize podcasts locally. Dark, modern, and offline-first.</p>

      <div className="grid">
        <UrlInput url={url} onChange={setUrl} onSubmit={onSubmit} processing={processing} error={error} />
        <Progress state={status.state} step={status.step} />

        <div className="grid two">
          <TranscriptView
            markdown={transcript}
            onDownload={() => downloadFile(transcript, 'transcript.md')}
          />
          <OutputEditor
            title="Summary"
            value={summary}
            onChange={setSummary}
            onDownload={() => downloadFile(summary, 'summary.md')}
          />
          <OutputEditor
            title="X Thread"
            value={thread}
            onChange={setThread}
            onDownload={() => downloadFile(thread, 'x_thread.md')}
          />
        </div>

        {status.state === 'error' && <div className="card error">Error: {status.error || error}</div>}

        <Logs entries={logs} />
      </div>
    </>
  );
}
