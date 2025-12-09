/**
 * Decision UI Controller
 * Manages the UI state and interactions for decision display
 */

class DecisionUI {
    constructor() {
        this.api = new DecisionAPI();
        this.selectedOptionId = null;
        this.currentDecision = null;
        
        this.initializeEventListeners();
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Confirm button click
        const confirmButton = document.getElementById('confirm-button');
        if (confirmButton) {
            confirmButton.addEventListener('click', () => this.handleConfirm());
        }

        // Action option selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.action-option')) {
                const option = e.target.closest('.action-option');
                this.selectAction(option);
            }
        });
    }

    /**
     * Load and display a decision
     * @param {string|Object} decisionIdOrData - Decision ID or decision object
     * @param {boolean} useMock - Whether to use mock data (for demo)
     */
    async loadDecision(decisionIdOrData = null, useMock = true) {
        try {
            this.showLoading();

            let decision;
            if (useMock && typeof decisionIdOrData === 'string') {
                // Use mock data based on mode
                const mode = decisionIdOrData === 'auto' ? 'auto' : 'manual';
                decision = this.api.getMockDecision(mode);
            } else if (typeof decisionIdOrData === 'object') {
                decision = decisionIdOrData;
            } else if (decisionIdOrData) {
                decision = await this.api.getDecision(decisionIdOrData);
            } else {
                // Default to auto mode mock
                decision = this.api.getMockDecision('auto');
            }

            this.currentDecision = decision;
            this.renderDecision(decision);
        } catch (error) {
            console.error('Error loading decision:', error);
            this.showError(error.message);
        }
    }

    /**
     * Render the decision based on mode
     * @param {Object} decision - The decision object
     */
    renderDecision(decision) {
        this.hideAllContainers();

        if (decision.mode === 'auto') {
            this.renderAutoMode(decision);
        } else {
            this.renderManualMode(decision);
        }
    }

    /**
     * Render Auto Mode UI
     * @param {Object} decision - The decision object
     */
    renderAutoMode(decision) {
        const container = document.getElementById('auto-mode-container');
        container.classList.remove('hidden');

        // Status message
        const statusMessage = document.getElementById('auto-status-message');
        if (statusMessage) {
            statusMessage.textContent = decision.selected_option 
                ? `"${decision.selected_option.description}" has been executed.`
                : 'Action has been automatically executed.';
        }

        // Reasoning
        const reasoning = document.getElementById('auto-reasoning');
        if (reasoning) {
            const reasoningText = decision.explanation || decision.reasoning || 'No reasoning provided.';
            reasoning.innerHTML = `<p class="reasoning-text">${this.formatText(reasoningText)}</p>`;
        }

        // Details
        const details = document.getElementById('auto-details');
        if (details) {
            details.innerHTML = this.generateDetailsHTML(decision);
        }
    }

    /**
     * Render Manual Mode UI
     * @param {Object} decision - The decision object
     */
    renderManualMode(decision) {
        const container = document.getElementById('manual-mode-container');
        container.classList.remove('hidden');

        // Error/Problem display
        const errorTitle = document.getElementById('manual-error-title');
        const errorDescription = document.getElementById('manual-error-description');
        if (errorTitle) errorTitle.textContent = decision.problem || 'Issue Detected';
        if (errorDescription) {
            errorDescription.textContent = decision.reasoning || 'An issue has been detected that requires your approval.';
        }

        // Reasoning
        const reasoning = document.getElementById('manual-reasoning');
        if (reasoning) {
            const reasoningText = decision.reasoning || 'No analysis available.';
            reasoning.innerHTML = `<p class="reasoning-text">${this.formatText(reasoningText)}</p>`;
        }

        // Actions list
        const actionsList = document.getElementById('manual-actions-list');
        if (actionsList && decision.options) {
            actionsList.innerHTML = decision.options.map((option, index) => 
                this.generateActionOptionHTML(option, index)
            ).join('');
        }

        // Reset confirm button
        const confirmButton = document.getElementById('confirm-button');
        if (confirmButton) {
            confirmButton.disabled = true;
            this.selectedOptionId = null;
        }
    }

    /**
     * Generate HTML for an action option
     * @param {Object} option - The action option
     * @param {number} index - The option index
     * @returns {string} HTML string
     */
    generateActionOptionHTML(option, index) {
        const riskClass = `risk-${option.risk || 'medium'}`;
        const impactClass = `impact-${option.impact || 'medium'}`;
        const costDisplay = option.estimated_cost > 0 
            ? `$${option.estimated_cost.toFixed(2)}` 
            : 'No additional cost';

        return `
            <div class="action-option" data-option-id="${option.id}">
                <div class="action-header">
                    <div class="action-title">${this.escapeHtml(option.description)}</div>
                    <div class="action-badges">
                        <span class="badge ${riskClass}">Risk: ${option.risk || 'medium'}</span>
                        <span class="badge ${impactClass}">Impact: ${option.impact || 'medium'}</span>
                    </div>
                </div>
                <div class="action-reasoning">
                    ${this.escapeHtml(option.reasoning || 'No reasoning provided.')}
                </div>
                <div class="action-cost">Estimated Cost: ${costDisplay}</div>
            </div>
        `;
    }

    /**
     * Generate HTML for decision details
     * @param {Object} decision - The decision object
     * @returns {string} HTML string
     */
    generateDetailsHTML(decision) {
        const details = [];

        if (decision.agent_name) {
            details.push({ label: 'Agent', value: decision.agent_name });
        }

        if (decision.selected_option) {
            details.push({ label: 'Action', value: decision.selected_option.description });
        }

        if (decision.confidence !== undefined) {
            details.push({ 
                label: 'Confidence', 
                value: `${(decision.confidence * 100).toFixed(0)}%` 
            });
        }

        if (decision.selected_option) {
            details.push({ 
                label: 'Risk Level', 
                value: decision.selected_option.risk || 'N/A' 
            });
            details.push({ 
                label: 'Impact', 
                value: decision.selected_option.impact || 'N/A' 
            });
        }

        if (decision.timestamp) {
            const date = new Date(decision.timestamp);
            details.push({ 
                label: 'Timestamp', 
                value: date.toLocaleString() 
            });
        }

        if (decision.execution_result) {
            details.push({ 
                label: 'Status', 
                value: decision.execution_result.status || 'completed' 
            });
        }

        return details.map(detail => `
            <div class="detail-item">
                <div class="detail-label">${detail.label}</div>
                <div class="detail-value">${detail.value}</div>
            </div>
        `).join('');
    }

    /**
     * Select an action option
     * @param {HTMLElement} optionElement - The option element
     */
    selectAction(optionElement) {
        // Remove previous selection
        document.querySelectorAll('.action-option').forEach(opt => {
            opt.classList.remove('selected');
        });

        // Add selection to clicked option
        optionElement.classList.add('selected');
        this.selectedOptionId = optionElement.dataset.optionId;

        // Enable confirm button
        const confirmButton = document.getElementById('confirm-button');
        if (confirmButton) {
            confirmButton.disabled = false;
        }
    }

    /**
     * Handle confirm button click
     */
    async handleConfirm() {
        if (!this.selectedOptionId || !this.currentDecision) {
            return;
        }

        const confirmButton = document.getElementById('confirm-button');
        if (confirmButton) {
            confirmButton.disabled = true;
            confirmButton.textContent = 'Processing...';
        }

        try {
            // In production, call the API
            // const result = await this.api.submitActionChoice(
            //     this.currentDecision.id || this.currentDecision.agent_id,
            //     this.selectedOptionId
            // );

            // For demo, simulate API call
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Show success message
            alert(`Action "${this.selectedOptionId}" has been confirmed and will be executed.`);

            // Reload to show execution result
            this.currentDecision.action_executed = true;
            this.currentDecision.selected_option = this.currentDecision.options.find(
                opt => opt.id === this.selectedOptionId
            );
            this.renderDecision(this.currentDecision);

        } catch (error) {
            console.error('Error confirming action:', error);
            alert('Error confirming action. Please try again.');
            
            if (confirmButton) {
                confirmButton.disabled = false;
                confirmButton.innerHTML = '<span class="button-icon">✓</span><span>Confirm Selection</span>';
            }
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.hideAllContainers();
        const loading = document.getElementById('loading-container');
        if (loading) loading.classList.remove('hidden');
    }

    /**
     * Show error state
     * @param {string} message - Error message
     */
    showError(message) {
        this.hideAllContainers();
        const error = document.getElementById('error-container');
        const errorText = document.getElementById('error-message-text');
        if (error) error.classList.remove('hidden');
        if (errorText) errorText.textContent = message || 'An error occurred.';
    }

    /**
     * Hide all containers
     */
    hideAllContainers() {
        document.getElementById('auto-mode-container')?.classList.add('hidden');
        document.getElementById('manual-mode-container')?.classList.add('hidden');
        document.getElementById('loading-container')?.classList.add('hidden');
        document.getElementById('error-container')?.classList.add('hidden');
    }

    /**
     * Format text with line breaks
     * @param {string} text - Text to format
     * @returns {string} Formatted text
     */
    formatText(text) {
        if (!text) return '';
        return this.escapeHtml(text).replace(/\n/g, '<br>');
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize UI when DOM is ready
let decisionUI;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        decisionUI = new DecisionUI();
        // Load default decision (auto mode) for demo
        decisionUI.loadDecision('auto', true);
    });
} else {
    decisionUI = new DecisionUI();
    // Load default decision (auto mode) for demo
    decisionUI.loadDecision('auto', true);
}

// Global function for retry button
function loadDecision(mode = 'auto') {
    if (decisionUI) {
        decisionUI.loadDecision(mode, true);
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.DecisionUI = DecisionUI;
    window.loadDecision = loadDecision;
}

