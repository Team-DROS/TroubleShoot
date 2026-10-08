/** Browser-only synthetic scenarios. No device inspection or native actions. */
export type ScenarioId = 'printer' | 'sound' | 'network'
export type Phase =
  | 'idle'
  | 'observing'
  | 'approval'
  | 'verifying'
  | 'complete'
  | 'denied'
  | 'cancelled'
export type Mode = 'diagnose' | 'repair'
export type Scenario = {
  id: ScenarioId
  title: string
  complaint: string
  target: string
  observation: string
  proposal: string
  operation: string
  before: string
  after: string
  limitation: string
  recovery: string
}
export const scenarios: Scenario[] = [
  {
    id: 'printer',
    title: 'Printer not responding',
    complaint: 'My printer is connected, but nothing is printing.',
    target: 'Windows Print Spooler',
    observation:
      'The sample Print Spooler service is stopped. Windows needs it to manage print jobs.',
    proposal: 'Start the Print Spooler service',
    operation: 'start_print_spooler',
    before: 'Stopped',
    after: 'Running',
    limitation:
      'The service is running in this example. A physical test page is still needed to confirm printing works.',
    recovery: 'Restore the sample service to its original stopped state.',
  },
  {
    id: 'sound',
    title: 'No sound from speakers',
    complaint: 'My speakers are connected, but I cannot hear anything.',
    target: 'Windows Audio service',
    observation:
      'The sample Windows Audio service is stopped. Audio output may be unavailable until it starts.',
    proposal: 'Start the Windows Audio service',
    operation: 'start_audio_service',
    before: 'Stopped',
    after: 'Running',
    limitation:
      'The service is running in this example. Play a sound to confirm that the correct output device works.',
    recovery: 'Restore the sample audio service to its original stopped state.',
  },
  {
    id: 'network',
    title: 'Website not loading',
    complaint: 'I am connected to Wi-Fi, but a website will not load.',
    target: 'DNS connectivity check',
    observation:
      'The sample DNS lookup timed out. The network adapter is connected, so the cause needs more investigation.',
    proposal: 'Repeat the read-only DNS check',
    operation: 'inspect_dns',
    before: 'Lookup timed out',
    after: 'Lookup timed out',
    limitation:
      'The repeated sample check still fails. This example remains unresolved; no network settings were changed.',
    recovery: 'No settings changed. There is nothing to restore.',
  },
]
export type DemoState = {
  phase: Phase
  scenario: ScenarioId
  mode: Mode
  complaint: string
  restored: boolean
}
export type DemoAction =
  | { type: 'scenario'; id: ScenarioId }
  | { type: 'mode'; mode: Mode }
  | { type: 'complaint'; value: string }
  | { type: 'start' }
  | { type: 'observed' }
  | { type: 'approve' }
  | { type: 'deny' }
  | { type: 'verified' }
  | { type: 'cancel' }
  | { type: 'reset' }
  | { type: 'restore' }
export const initialState: DemoState = {
  phase: 'idle',
  scenario: 'printer',
  mode: 'repair',
  complaint: scenarios[0].complaint,
  restored: false,
}
export const getScenario = (id: ScenarioId) => scenarios.find((s) => s.id === id)!
export function demoReducer(state: DemoState, action: DemoAction): DemoState {
  switch (action.type) {
    case 'scenario':
      return state.phase === 'idle'
        ? {
            ...state,
            scenario: action.id,
            complaint: getScenario(action.id).complaint,
            restored: false,
          }
        : state
    case 'mode':
      return state.phase === 'idle' ? { ...state, mode: action.mode } : state
    case 'complaint':
      return state.phase === 'idle' ? { ...state, complaint: action.value.slice(0, 2000) } : state
    case 'start':
      return state.phase === 'idle' && state.complaint.trim()
        ? { ...state, phase: 'observing' }
        : state
    case 'observed':
      return state.phase === 'observing'
        ? { ...state, phase: state.mode === 'diagnose' ? 'complete' : 'approval' }
        : state
    case 'approve':
      return state.phase === 'approval' && state.mode === 'repair'
        ? { ...state, phase: 'verifying' }
        : state
    case 'deny':
      return state.phase === 'approval' ? { ...state, phase: 'denied' } : state
    case 'verified':
      return state.phase === 'verifying' ? { ...state, phase: 'complete' } : state
    case 'cancel':
      return ['observing', 'approval', 'verifying'].includes(state.phase)
        ? { ...state, phase: 'cancelled' }
        : state
    case 'reset':
      return {
        ...initialState,
        scenario: state.scenario,
        mode: state.mode,
        complaint: getScenario(state.scenario).complaint,
      }
    case 'restore':
      return state.phase === 'complete' && state.mode === 'repair' && state.scenario !== 'network'
        ? { ...state, restored: true }
        : state
  }
}
