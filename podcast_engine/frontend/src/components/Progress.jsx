import React from 'react';

const stepNames = {
  init: 'Starting',
  download: 'Downloading audio',
  transcription: 'Transcribing',
  formatting: 'Formatting transcript',
  llm: 'Generating outputs',
  complete: 'Complete',
};

export default function Progress({ state, step }) {
  if (state === 'idle') return null;
  const label = stepNames[step] || step || 'Running';
  return (
    <div className="card progress">
      <div className="dot" />
      <div>
        <div>{label}</div>
        <div className="muted">{state === 'completed' ? 'Finished' : state === 'error' ? 'Error' : 'In progress'}</div>
      </div>
    </div>
  );
}
