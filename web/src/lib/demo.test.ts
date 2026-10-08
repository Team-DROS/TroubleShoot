import { test } from 'node:test'
import assert from 'node:assert/strict'
import { demoReducer as reduce, initialState, scenarios } from './demo.ts'
import type { DemoState } from './demo.ts'

test('diagnose-only completes without approval or execution', () => {
  let state: DemoState = reduce(initialState, { type: 'mode', mode: 'diagnose' })
  state = reduce(reduce(state, { type: 'start' }), { type: 'observed' })
  assert.equal(state.phase, 'complete')
  assert.equal(reduce(state, { type: 'approve' }), state)
  assert.equal(reduce(state, { type: 'restore' }).restored, false)
})

test('repair cannot execute before a proposal and explicit approval', () => {
  let state = reduce(initialState, { type: 'start' })
  assert.equal(reduce(state, { type: 'approve' }), state)
  assert.equal(reduce(state, { type: 'verified' }), state)
  state = reduce(state, { type: 'observed' })
  assert.equal(state.phase, 'approval')
  state = reduce(state, { type: 'approve' })
  assert.equal(state.phase, 'verifying')
  assert.equal(reduce(state, { type: 'approve' }), state)
  assert.equal(reduce(state, { type: 'verified' }).phase, 'complete')
})

test('denial ends the run and cannot be followed by execution', () => {
  const pending = reduce(reduce(initialState, { type: 'start' }), { type: 'observed' })
  const denied = reduce(pending, { type: 'deny' })
  assert.equal(denied.phase, 'denied')
  assert.equal(reduce(denied, { type: 'approve' }), denied)
  assert.equal(reduce(denied, { type: 'verified' }), denied)
})

for (const phase of ['observing', 'approval', 'verifying'] as const) {
  test(`cancellation during ${phase} rejects late events`, () => {
    const cancelled = reduce({ ...initialState, phase }, { type: 'cancel' })
    assert.equal(cancelled.phase, 'cancelled')
    for (const type of ['observed', 'approve', 'verified'] as const)
      assert.equal(reduce(cancelled, { type }), cancelled)
  })
}

test('a running session cannot change its target, complaint, or mode', () => {
  const state = reduce(initialState, { type: 'start' })
  assert.equal(reduce(state, { type: 'scenario', id: 'sound' }), state)
  assert.equal(reduce(state, { type: 'mode', mode: 'diagnose' }), state)
  assert.equal(reduce(state, { type: 'complaint', value: 'Changed input' }), state)
})

test('blank complaints cannot start and overly long input is bounded', () => {
  const blank = reduce(initialState, { type: 'complaint', value: '   ' })
  assert.equal(reduce(blank, { type: 'start' }), blank)
  assert.equal(
    reduce(initialState, { type: 'complaint', value: 'a'.repeat(2100) }).complaint.length,
    2000,
  )
})

test('recovery is offered only after an applicable completed sample action', () => {
  const complete: DemoState = { ...initialState, phase: 'complete' }
  assert.equal(reduce(complete, { type: 'restore' }).restored, true)
  assert.equal(reduce({ ...complete, scenario: 'network' }, { type: 'restore' }).restored, false)
  assert.equal(reduce({ ...complete, phase: 'cancelled' }, { type: 'restore' }).restored, false)
})

test('reset retains the chosen scenario but clears all results', () => {
  const next = reduce(
    { ...initialState, scenario: 'sound', phase: 'complete', restored: true },
    { type: 'reset' },
  )
  assert.equal(next.phase, 'idle')
  assert.equal(next.restored, false)
  assert.equal(next.complaint, scenarios[1].complaint)
})
