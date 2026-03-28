class FlatasticChoresCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config) {
      throw new Error('Invalid configuration');
    }
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  render() {
    if (!this._hass) return;

    const entities = Object.keys(this._hass.states).filter(entityId => 
      entityId.startsWith('sensor.flatastic_') && 
      this._hass.states[entityId].attributes.status === 'overdue'
    );

    this.shadowRoot.innerHTML = `
      <style>
        .card {
          background: var(--card-background-color);
          border-radius: var(--ha-card-border-radius);
          box-shadow: var(--ha-card-box-shadow);
          padding: 16px;
        }
        .header {
          font-size: 1.2em;
          font-weight: bold;
          margin-bottom: 16px;
          color: var(--primary-text-color);
        }
        .chore-item {
          padding: 12px;
          margin-bottom: 8px;
          background: var(--secondary-background-color);
          border-radius: 8px;
          border-left: 4px solid var(--error-color);
        }
        .chore-info {
          width: 100%;
        }
        .chore-title {
          font-weight: bold;
          color: var(--primary-text-color);
          margin-bottom: 4px;
        }
        .chore-details {
          font-size: 0.9em;
          color: var(--secondary-text-color);
        }
        .urgency-high {
          border-left-color: var(--error-color);
        }
        .urgency-medium {
          border-left-color: var(--warning-color);
        }
        .complete-btn {
          background: var(--primary-color);
          color: white;
          border: none;
          padding: 6px 12px;
          margin: 2px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.8em;
        }
        .complete-btn:hover {
          background: var(--primary-color-dark);
        }
        .complete-btn:disabled {
          background: var(--disabled-color);
          cursor: not-allowed;
        }
        .buttons-container {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          margin-top: 8px;
        }
        .no-chores {
          text-align: center;
          color: var(--secondary-text-color);
          font-style: italic;
          padding: 20px;
        }
      </style>
      <div class="card">
        <div class="header">Overdue Chores</div>
        ${entities.length === 0 ? 
          '<div class="no-chores">No overdue chores!</div>' :
          entities.map(entityId => {
            const state = this._hass.states[entityId];
            const attributes = state.attributes;
            const urgencyClass = `urgency-${attributes.urgency || 'medium'}`;
            
            // Generate buttons for each user who can complete this chore
            const userButtons = (attributes.user_names || []).map(user => 
              `<button 
                class="complete-btn" 
                onclick="this.getRootNode().host.completeChore(${attributes.id}, ${user.id})"
              >
                ${user.name}
              </button>`
            ).join('');

            return `
              <div class="chore-item ${urgencyClass}">
                <div class="chore-info">
                  <div class="chore-title">${attributes.title}</div>
                  <div class="chore-details">
                    Assigned to: ${state.state} | Points: ${attributes.points || 0} | 
                    Overdue by: ${this.formatOverdueTime(attributes.timeLeftNext || 0)}
                  </div>
                  <div class="buttons-container">
                    ${userButtons}
                  </div>
                </div>
              </div>
            `;
          }).join('')
        }
      </div>
    `;
  }

  formatOverdueTime(timeLeftNext) {
    const overdueDays = Math.abs(Math.floor(timeLeftNext / 86400));
    if (overdueDays === 0) {
      const overdueHours = Math.abs(Math.floor(timeLeftNext / 3600));
      return `${overdueHours}h`;
    }
    return `${overdueDays}d`;
  }

  completeChore(choreId, currentUser) {
    this._hass.callService('flatastic', 'complete_chore', {
      chore_id: choreId,
      completed_by: currentUser
    }).then(() => {
      // Show success message
      this._hass.callService('persistent_notification', 'create', {
        message: `Chore completed successfully!`,
        title: 'Flatastic',
        notification_id: `flatastic_complete_${choreId}`
      });
    }).catch(error => {
      // Show error message
      this._hass.callService('persistent_notification', 'create', {
        message: `Failed to complete chore: ${error.message}`,
        title: 'Flatastic Error',
        notification_id: `flatastic_error_${choreId}`
      });
    });
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('flatastic-chores-card', FlatasticChoresCard);

// Register the card with the UI
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'flatastic-chores-card',
  name: 'Flatastic Chores Card',
  description: 'A card to display and complete overdue Flatastic chores'
});
