import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

import '../../custom_components/flatastic/www/flatastic-chores-card.js'

function makeHass(states = {}) {
  return {
    states,
    callService: vi.fn().mockResolvedValue(undefined),
  }
}

function makeChoreState(overrides = {}) {
  return {
    state: 'Alice',
    attributes: {
      title: 'Dishes',
      status: 'overdue',
      urgency: 'high',
      points: 5,
      timeLeftNext: -90000,
      id: 1,
      user_names: [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
      ],
      ...(overrides.attributes || {}),
    },
    ...overrides,
  }
}

describe('FlatasticChoresCard', () => {
  let card

  beforeEach(() => {
    card = document.createElement('flatastic-chores-card')
    document.body.appendChild(card)
  })

  afterEach(() => {
    document.body.removeChild(card)
  })

  describe('setConfig', () => {
    it('throws on null config', () => {
      expect(() => card.setConfig(null)).toThrow('Invalid configuration')
    })

    it('throws on undefined config', () => {
      expect(() => card.setConfig(undefined)).toThrow('Invalid configuration')
    })

    it('stores config', () => {
      card.setConfig({ title: 'test' })
      expect(card.config).toEqual({ title: 'test' })
    })
  })

  describe('getCardSize', () => {
    it('returns 3', () => {
      expect(card.getCardSize()).toBe(3)
    })
  })

  describe('formatOverdueTime', () => {
    it('returns 0h for zero', () => {
      expect(card.formatOverdueTime(0)).toBe('0h')
    })

    it('returns hours for values less than 1 day overdue', () => {
      expect(card.formatOverdueTime(-3600)).toBe('1h')
      expect(card.formatOverdueTime(-7200)).toBe('2h')
      expect(card.formatOverdueTime(-43200)).toBe('12h')
      expect(card.formatOverdueTime(-86399)).toBe('23h')
    })

    it('returns days for values >= 1 day overdue', () => {
      expect(card.formatOverdueTime(-86400)).toBe('1d')
      expect(card.formatOverdueTime(-90000)).toBe('1d')
      expect(card.formatOverdueTime(-172800)).toBe('2d')
    })
  })

  describe('render', () => {
    it('does nothing without hass', () => {
      card.setConfig({})
      expect(card.shadowRoot.innerHTML).toBe('')
    })

    it('renders no-chores message when no entities match', () => {
      card.hass = makeHass({})
      expect(card.shadowRoot.innerHTML).toContain('No overdue chores')
    })

    it('renders a chore item for each overdue entity', () => {
      card.hass = makeHass({
        'sensor.flatastic_dishes': makeChoreState(),
        'sensor.flatastic_vacuuming': makeChoreState({ attributes: { title: 'Vacuuming', status: 'overdue', urgency: 'medium', points: 3, timeLeftNext: -90000, id: 2, user_names: [] } }),
      })
      const html = card.shadowRoot.innerHTML
      expect(html).toContain('Dishes')
      expect(html).toContain('Vacuuming')
    })

    it('ignores entities with non-overdue status', () => {
      card.hass = makeHass({
        'sensor.flatastic_dishes': makeChoreState({ attributes: { title: 'Dishes', status: 'pending' } }),
      })
      expect(card.shadowRoot.innerHTML).toContain('No overdue chores')
    })

    it('ignores non-flatastic entities', () => {
      card.hass = makeHass({
        'sensor.temperature': { state: '22', attributes: { status: 'overdue' } },
      })
      expect(card.shadowRoot.innerHTML).toContain('No overdue chores')
    })

    it('applies urgency-high class', () => {
      card.hass = makeHass({
        'sensor.flatastic_dishes': makeChoreState(),
      })
      expect(card.shadowRoot.innerHTML).toContain('urgency-high')
    })

    it('applies urgency-medium class', () => {
      card.hass = makeHass({
        'sensor.flatastic_dishes': makeChoreState({ attributes: { title: 'Dishes', status: 'overdue', urgency: 'medium', points: 2, timeLeftNext: -90000, id: 1, user_names: [] } }),
      })
      expect(card.shadowRoot.innerHTML).toContain('urgency-medium')
    })

    it('renders user buttons', () => {
      card.hass = makeHass({
        'sensor.flatastic_dishes': makeChoreState(),
      })
      const html = card.shadowRoot.innerHTML
      expect(html).toContain('Alice')
      expect(html).toContain('Bob')
    })

    it('renders chore title', () => {
      card.hass = makeHass({
        'sensor.flatastic_dishes': makeChoreState(),
      })
      expect(card.shadowRoot.innerHTML).toContain('Dishes')
    })

    it('renders points', () => {
      card.hass = makeHass({
        'sensor.flatastic_dishes': makeChoreState(),
      })
      expect(card.shadowRoot.innerHTML).toContain('5')
    })
  })

  describe('completeChore', () => {
    it('calls hass.callService with chore_id and completed_by', () => {
      const hass = makeHass()
      card._hass = hass
      card.completeChore(42, 7)
      expect(hass.callService).toHaveBeenCalledWith('flatastic', 'complete_chore', {
        chore_id: 42,
        completed_by: 7,
      })
    })
  })

  describe('customElements registration', () => {
    it('registers the custom element', () => {
      expect(customElements.get('flatastic-chores-card')).toBeDefined()
    })

    it('adds entry to window.customCards', () => {
      const entry = window.customCards.find(c => c.type === 'flatastic-chores-card')
      expect(entry).toBeDefined()
      expect(entry.name).toBe('Flatastic Chores Card')
    })
  })
})
