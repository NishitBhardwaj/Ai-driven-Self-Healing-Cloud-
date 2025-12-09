/**
 * Decision API Client
 * Handles communication with the backend decision API
 */

class DecisionAPI {
    constructor(baseURL = '/api/v1/decisions') {
        this.baseURL = baseURL;
    }

    /**
     * Fetch a decision by ID
     * @param {string} decisionId - The decision ID
     * @returns {Promise<Object>} The decision object
     */
    async getDecision(decisionId) {
        try {
            const response = await fetch(`${this.baseURL}/${decisionId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching decision:', error);
            throw error;
        }
    }

    /**
     * Get pending decisions (for manual mode)
     * @returns {Promise<Array>} Array of pending decisions
     */
    async getPendingDecisions() {
        try {
            const response = await fetch(`${this.baseURL}/pending`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching pending decisions:', error);
            throw error;
        }
    }

    /**
     * Submit user's action choice (for manual mode)
     * @param {string} decisionId - The decision ID
     * @param {string} optionId - The selected option ID
     * @returns {Promise<Object>} The execution result
     */
    async submitActionChoice(decisionId, optionId) {
        try {
            const response = await fetch(`${this.baseURL}/${decisionId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    option_id: optionId,
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error submitting action choice:', error);
            throw error;
        }
    }

    /**
     * Get decision explanation
     * @param {string} decisionId - The decision ID
     * @param {string} level - Explanation level (brief, detailed, technical)
     * @returns {Promise<Object>} The explanation object
     */
    async getExplanation(decisionId, level = 'detailed') {
        try {
            const response = await fetch(`${this.baseURL}/${decisionId}/explanation?level=${level}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching explanation:', error);
            throw error;
        }
    }

    /**
     * Subscribe to decision updates via WebSocket or Server-Sent Events
     * @param {string} decisionId - The decision ID
     * @param {Function} callback - Callback function for updates
     */
    subscribeToDecision(decisionId, callback) {
        // For demo purposes, we'll use polling
        // In production, use WebSocket or SSE
        const interval = setInterval(async () => {
            try {
                const decision = await this.getDecision(decisionId);
                callback(decision);
                
                // Stop polling if decision is executed
                if (decision.action_executed) {
                    clearInterval(interval);
                }
            } catch (error) {
                console.error('Error in decision subscription:', error);
                clearInterval(interval);
            }
        }, 2000); // Poll every 2 seconds

        return () => clearInterval(interval);
    }

    /**
     * Mock data for demo purposes
     * In production, remove this and use real API calls
     */
    getMockDecision(mode = 'auto') {
        if (mode === 'auto') {
            return {
                mode: 'auto',
                agent_id: 'self-healing-001',
                agent_name: 'Self-Healing Agent',
                problem: 'EC2 instance i-1234567890abcdef0 is experiencing high CPU usage (95%)',
                reasoning: 'The instance CPU usage has been above 90% for the past 10 minutes. Analysis shows this is causing response time degradation. Restarting the instance will clear any stuck processes and restore normal operation.',
                options: [
                    {
                        id: 'restart_instance',
                        description: 'Restart the EC2 instance',
                        reasoning: 'Restarting will clear stuck processes and restore normal CPU usage',
                        risk: 'low',
                        impact: 'medium',
                        estimated_cost: 0.0
                    }
                ],
                selected_option: {
                    id: 'restart_instance',
                    description: 'Restart the EC2 instance',
                    reasoning: 'Restarting will clear stuck processes and restore normal CPU usage',
                    risk: 'low',
                    impact: 'medium',
                    estimated_cost: 0.0
                },
                action_executed: true,
                execution_result: {
                    status: 'success',
                    instance_id: 'i-1234567890abcdef0',
                    action: 'restart_instance',
                    timestamp: new Date().toISOString()
                },
                explanation: 'The instance was automatically restarted due to CPU overload. The system detected sustained high CPU usage (95%) for 10 minutes, which was causing response time degradation. Restarting the instance cleared stuck processes and restored normal operation. The action was executed automatically based on the system\'s analysis with 92% confidence.',
                confidence: 0.92,
                timestamp: new Date().toISOString()
            };
        } else {
            return {
                mode: 'manual',
                agent_id: 'scaling-001',
                agent_name: 'Scaling Agent',
                problem: 'CPU usage is at 95% and response times are increasing',
                reasoning: 'CPU usage has been above 90% for 5 minutes. The system needs more capacity to handle the current load. Multiple scaling options are available, each with different trade-offs.',
                options: [
                    {
                        id: 'scale_up',
                        description: 'Scale up from 3 to 5 replicas',
                        reasoning: 'Adding more replicas will distribute the load and reduce CPU usage per instance. This is a safe, low-risk action.',
                        risk: 'low',
                        impact: 'high',
                        estimated_cost: 15.50
                    },
                    {
                        id: 'optimize',
                        description: 'Optimize existing resources',
                        reasoning: 'Optimize the current deployment configuration to better utilize existing resources. Lower cost but may not fully resolve the issue.',
                        risk: 'medium',
                        impact: 'medium',
                        estimated_cost: 0.0
                    },
                    {
                        id: 'restart_service',
                        description: 'Restart the service',
                        reasoning: 'Restart the service to clear any memory leaks or stuck processes. Quick fix but may cause brief downtime.',
                        risk: 'medium',
                        impact: 'low',
                        estimated_cost: 0.0
                    }
                ],
                action_executed: false,
                confidence: 0.85,
                timestamp: new Date().toISOString()
            };
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DecisionAPI;
}

