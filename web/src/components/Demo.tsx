import { useEffect, useReducer, useRef, useState } from 'react'
import { demoReducer, getScenario, initialState, scenarios } from '../lib/demo'
import { Brand, Icon } from './Icon'

export default function Demo({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  const [state, dispatch] = useReducer(demoReducer, initialState)
  const [downloaded, setDownloaded] = useState(false)
  const scenario = getScenario(state.scenario)
  const busy = state.phase === 'observing' || state.phase === 'verifying'
  const started = state.phase !== 'idle'
  const terminal = ['complete', 'denied', 'cancelled'].includes(state.phase)
  const observationVisible = ['approval', 'verifying', 'complete', 'denied'].includes(state.phase)
  const title =
    state.phase === 'idle'
      ? 'Let’s make things clearer.'
      : state.phase === 'observing'
        ? 'Looking at the right details.'
        : state.phase === 'approval'
          ? 'The next step is yours.'
          : state.phase === 'verifying'
            ? 'Checking what changed.'
            : state.phase === 'denied'
              ? 'Your decision. Respected.'
              : state.phase === 'cancelled'
                ? 'Paused on your terms.'
                : state.restored
                  ? 'Back to the starting point.'
                  : state.mode === 'diagnose'
                    ? 'A clearer picture.'
                    : state.scenario === 'network'
                      ? 'Still needs a closer look.'
                      : 'Progress, with perspective.'

  useEffect(() => {
    dialog.current?.showModal()
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previousOverflow
    }
  }, [])

  useEffect(() => {
    if (!busy) return
    const timeout = window.setTimeout(
      () => dispatch({ type: state.phase === 'observing' ? 'observed' : 'verified' }),
      1400,
    )
    return () => window.clearTimeout(timeout)
  }, [state.phase, busy])

  useEffect(() => {
    if (terminal) document.getElementById('demo-result')?.focus()
    if (state.phase === 'approval') document.getElementById('approval-heading')?.focus()
  }, [terminal, state.phase])

  function exportEvidence() {
    const report = {
      kind: 'synthetic_frontend_preview',
      generated_at: new Date().toISOString(),
      device_access: false,
      model_inference: false,
      scenario: scenario.title,
      complaint: state.complaint,
      mode: state.mode,
      phase: state.phase,
      observation: observationVisible ? scenario.observation : null,
      outcome:
        state.phase === 'complete'
          ? state.mode === 'diagnose'
            ? 'diagnosis_only'
            : state.scenario === 'network'
              ? 'unresolved'
              : state.restored
                ? 'sample_restored'
                : 'partial'
          : state.phase,
      limitation: scenario.limitation,
      recovery_performed: state.restored,
    }
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }),
    )
    const link = document.createElement('a')
    link.href = url
    link.download = 'troubleshoot-sample-evidence.json'
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    setDownloaded(true)
  }

  return (
    <dialog
      ref={dialog}
      className="demo-dialog"
      aria-labelledby="demo-title"
      aria-describedby="demo-disclaimer"
      onCancel={(event) => {
        event.preventDefault()
        onClose()
      }}
      onClick={(event) => {
        if (event.target === dialog.current) {
          const box = dialog.current.getBoundingClientRect()
          if (
            event.clientX < box.left ||
            event.clientX > box.right ||
            event.clientY < box.top ||
            event.clientY > box.bottom
          )
            onClose()
        }
      }}
    >
      <div className="demo-shell">
        <div className="demo-header">
          <Brand />
          <span className="sample-pill">INTERACTIVE PREVIEW</span>
          <button className="icon-button" onClick={onClose} aria-label="Close demo">
            <Icon name="close" />
          </button>
        </div>
        <div className="demo-layout">
          <aside className="demo-sidebar">
            <p className="eyebrow">YOUR WORKSPACE</p>
            <div className="sidebar-current">
              <Icon name="window" size={18} />
              Troubleshoot<span>01</span>
            </div>
            <div className="sidebar-divider" />
            <p className="eyebrow">TRY A SCENARIO</p>
            <div className="scenario-list">
              {scenarios.map((item) => (
                <button
                  key={item.id}
                  disabled={started}
                  onClick={() => dispatch({ type: 'scenario', id: item.id })}
                  aria-pressed={state.scenario === item.id}
                  className={state.scenario === item.id ? 'scenario selected' : 'scenario'}
                >
                  <Icon name={item.id} size={18} />
                  <span>{item.title}</span>
                </button>
              ))}
            </div>
            <div className="sidebar-bottom">
              <span className="sidebar-model">
                <Icon name="chip" size={19} />
                <span>
                  Local intelligence<small>Gemma / planned integration</small>
                </span>
              </span>
              <p>
                Sample data only.
                <br />
                Your device is not connected.
              </p>
            </div>
          </aside>
          <div className="demo-main">
            <div className="demo-breadcrumb">
              <span>WORKSPACE / NEW SESSION</span>
              <span className="connection-label">
                <i />
                PREVIEW MODE
              </span>
            </div>
            <h2 id="demo-title">{title}</h2>
            <p id="demo-disclaimer" className="demo-disclaimer">
              A guided example using sample data. No AI inference or changes to your computer.
            </p>
            {!started ? (
              <form
                onSubmit={(event) => {
                  event.preventDefault()
                  dispatch({ type: 'start' })
                }}
              >
                <label className="input-label" htmlFor="complaint">
                  What’s getting in your way?
                </label>
                <textarea
                  id="complaint"
                  value={state.complaint}
                  onChange={(event) => dispatch({ type: 'complaint', value: event.target.value })}
                  maxLength={2000}
                  required
                  rows={3}
                  aria-describedby="complaint-help"
                />
                <p id="complaint-help" className="input-help">
                  You can edit this description. The preview follows the selected{' '}
                  {state.scenario === 'sound' ? 'audio' : state.scenario} example.
                </p>
                <fieldset className="mode-fieldset">
                  <legend>How would you like to proceed?</legend>
                  <div className="mode-options">
                    <label
                      className={state.mode === 'diagnose' ? 'mode-option selected' : 'mode-option'}
                    >
                      <input
                        type="radio"
                        name="mode"
                        value="diagnose"
                        checked={state.mode === 'diagnose'}
                        onChange={() => dispatch({ type: 'mode', mode: 'diagnose' })}
                      />
                      <span>
                        <strong>Just diagnose</strong>
                        <small>Understand the issue. No actions.</small>
                      </span>
                      <Icon name="eye" size={19} />
                    </label>
                    <label
                      className={state.mode === 'repair' ? 'mode-option selected' : 'mode-option'}
                    >
                      <input
                        type="radio"
                        name="mode"
                        value="repair"
                        checked={state.mode === 'repair'}
                        onChange={() => dispatch({ type: 'mode', mode: 'repair' })}
                      />
                      <span>
                        <strong>Guide a repair</strong>
                        <small>Review and approve each step.</small>
                      </span>
                      <Icon name="shield" size={19} />
                    </label>
                  </div>
                </fieldset>
                <div className="demo-start-row">
                  <span>
                    <Icon name="shield" size={16} /> You’re in control at every step.
                  </span>
                  <button
                    className="button button-primary"
                    type="submit"
                    disabled={!state.complaint.trim()}
                  >
                    Start walkthrough <Icon name="arrow" size={17} />
                  </button>
                </div>
              </form>
            ) : (
              <div className="session-content">
                <div className="session-complaint">
                  <span className="user-avatar">YOU</span>
                  <p>{state.complaint}</p>
                </div>
                <div className="session-progress" aria-label="Session progress">
                  {['Observe', state.mode === 'diagnose' ? 'Understand' : 'Approve', 'Review'].map(
                    (label, index) => (
                      <span
                        key={label}
                        className={
                          index === 0 ||
                          (index === 1 && observationVisible) ||
                          (index === 2 && state.phase === 'complete')
                            ? 'reached'
                            : ''
                        }
                      >
                        <span>{index + 1}</span>
                        {label}
                        {index < 2 && <i />}
                      </span>
                    ),
                  )}
                </div>
                <div className="session-announcement" role="status" aria-live="polite">
                  {busy && <span className="progress-spinner" />}
                  {state.phase === 'observing'
                    ? 'Reading the sample observation…'
                    : state.phase === 'verifying'
                      ? 'Applying the sample action and checking its result…'
                      : state.phase === 'approval'
                        ? 'Observation ready. Review the proposed action below.'
                        : terminal
                          ? 'Walkthrough finished.'
                          : ''}
                </div>
                {observationVisible && (
                  <div className="observation-card">
                    <div className="card-eyebrow">
                      <Icon name="eye" size={16} />
                      SAMPLE OBSERVATION
                    </div>
                    <p>{scenario.observation}</p>
                    <span className="observation-target">
                      TARGET <span>{scenario.target}</span>
                    </span>
                  </div>
                )}
                {state.phase === 'approval' && (
                  <div className="approval-card">
                    <div className="card-eyebrow">
                      <Icon name="shield" size={16} />
                      YOUR APPROVAL IS REQUIRED
                    </div>
                    <h3 id="approval-heading" tabIndex={-1}>
                      {scenario.proposal}
                    </h3>
                    <dl>
                      <div>
                        <dt>Scope</dt>
                        <dd>{scenario.target} only</dd>
                      </div>
                      <div>
                        <dt>Recovery</dt>
                        <dd>{scenario.recovery}</dd>
                      </div>
                    </dl>
                    <div className="approval-buttons">
                      <button
                        className="button button-quiet"
                        onClick={() => dispatch({ type: 'deny' })}
                      >
                        Don’t allow
                      </button>
                      <button
                        className="button button-primary"
                        onClick={() => dispatch({ type: 'approve' })}
                      >
                        Approve sample action <Icon name="check" size={17} />
                      </button>
                    </div>
                  </div>
                )}
                {terminal && (
                  <div id="demo-result" className="result-card" tabIndex={-1}>
                    <div className="result-heading">
                      <span className="result-icon">
                        <Icon
                          name={
                            state.phase === 'complete'
                              ? state.scenario === 'network'
                                ? 'eye'
                                : 'check'
                              : 'shield'
                          }
                          size={20}
                        />
                      </span>
                      <h3>
                        {state.phase === 'denied'
                          ? 'Action declined. Nothing changed.'
                          : state.phase === 'cancelled'
                            ? 'Walkthrough stopped.'
                            : state.restored
                              ? 'Sample pre-state restored.'
                              : state.mode === 'diagnose'
                                ? 'Diagnosis complete. No action taken.'
                                : state.scenario === 'network'
                                  ? 'Unresolved — more investigation needed.'
                                  : 'Partially resolved — one check remains.'}
                      </h3>
                    </div>
                    <p>
                      {state.phase === 'denied'
                        ? 'The proposed action was not run. You can start again whenever you’re ready.'
                        : state.phase === 'cancelled'
                          ? 'The preview has stopped. This walkthrough never accessed or changed your computer.'
                          : state.restored
                            ? 'The sample service is stopped again, matching the original observation. This is a simulated recovery.'
                            : state.mode === 'diagnose'
                              ? 'The sample observation suggests a possible cause. Diagnose-only mode ends here, without running an action.'
                              : scenario.limitation}
                    </p>
                    {state.phase === 'complete' && state.mode === 'repair' && (
                      <div className="result-evidence">
                        <span>
                          BEFORE<strong>{scenario.before}</strong>
                        </span>
                        <Icon name="arrow" size={20} />
                        <span>
                          {state.restored ? 'RESTORED' : 'AFTER'}
                          <strong>{state.restored ? scenario.before : scenario.after}</strong>
                        </span>
                        <span className="sample-pill">SAMPLE</span>
                      </div>
                    )}
                    <div className="result-actions">
                      <button
                        className="text-link"
                        onClick={() => {
                          dispatch({ type: 'reset' })
                          setDownloaded(false)
                        }}
                      >
                        <Icon name="refresh" size={16} />
                        Try another walkthrough
                      </button>
                      <button className="text-link" onClick={exportEvidence}>
                        <Icon name="download" size={16} />
                        {downloaded ? 'Download again' : 'Save sample evidence'}
                      </button>
                    </div>
                    {state.phase === 'complete' &&
                      state.mode === 'repair' &&
                      state.scenario !== 'network' &&
                      !state.restored && (
                        <button
                          className="restore-button"
                          onClick={() => dispatch({ type: 'restore' })}
                        >
                          Restore sample pre-state <Icon name="refresh" size={14} />
                        </button>
                      )}
                    {downloaded && (
                      <span className="download-feedback" role="status">
                        Download requested. Check your browser’s downloads.
                      </span>
                    )}
                  </div>
                )}
                {!terminal && (
                  <button className="stop-button" onClick={() => dispatch({ type: 'cancel' })}>
                    <Icon name="stop" size={14} />
                    Stop walkthrough
                  </button>
                )}
              </div>
            )}
            <div className="demo-bottom-meta">
              <span>BOUNDED ACTIONS · EXPLICIT APPROVAL · FRESH EVIDENCE</span>
              <span>TS / 01</span>
            </div>
          </div>
        </div>
      </div>
    </dialog>
  )
}
