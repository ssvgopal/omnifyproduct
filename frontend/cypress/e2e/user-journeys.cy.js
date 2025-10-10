"""
End-to-End Testing Suite for OmnifyProduct
Comprehensive user journey and integration testing
"""

describe('Complete User Journey', () => {
    beforeEach(() => {
        // Clear cookies and local storage before each test
        cy.clearCookies();
        cy.clearLocalStorage();

        // Set up API intercepts
        cy.intercept('POST', '/api/auth/login', { fixture: 'auth/login-success.json' }).as('login');
        cy.intercept('GET', '/api/agentkit/agents*', { fixture: 'agents/list.json' }).as('getAgents');
        cy.intercept('GET', '/api/agentkit/workflows*', { fixture: 'workflows/list.json' }).as('getWorkflows');
    });

    it('completes full user onboarding journey', () => {
        // Visit login page
        cy.visit('/login');

        // Should see login form
        cy.contains('Welcome to OmnifyProduct').should('be.visible');
        cy.get('[data-testid="email-input"]').should('be.visible');
        cy.get('[data-testid="password-input"]').should('be.visible');

        // Enter credentials
        cy.get('[data-testid="email-input"]').type('test@example.com');
        cy.get('[data-testid="password-input"]').type('password123');

        // Submit login form
        cy.get('[data-testid="login-button"]').click();

        // Wait for authentication
        cy.wait('@login');

        // Should redirect to dashboard
        cy.url().should('include', '/dashboard');
        cy.contains('Dashboard').should('be.visible');

        // Wait for dashboard data to load
        cy.wait('@getAgents');
        cy.wait('@getWorkflows');

        // Verify dashboard content
        cy.contains('Welcome, Test User').should('be.visible');
        cy.get('[data-testid="agents-list"]').should('be.visible');
        cy.get('[data-testid="workflows-list"]').should('be.visible');
    });

    it('creates and executes a complete workflow', () => {
        // Login first
        cy.login('test@example.com', 'password123');

        // Navigate to workflow builder
        cy.get('[data-testid="create-workflow-button"]').click();
        cy.url().should('include', '/workflows/new');

        // Create new workflow
        cy.get('[data-testid="workflow-name-input"]').type('E2E Test Campaign');
        cy.get('[data-testid="workflow-description-input"]').type('End-to-end test workflow');

        // Add workflow steps
        cy.get('[data-testid="add-step-button"]').click();

        // Configure first step (Creative Analysis)
        cy.get('[data-testid="step-1-agent-type"]').select('creative_intelligence');
        cy.get('[data-testid="step-1-asset-url"]').type('https://example.com/creative.jpg');
        cy.get('[data-testid="step-1-analysis-type"]').select('aida');

        // Add second step (Campaign Creation)
        cy.get('[data-testid="add-step-button"]').click();
        cy.get('[data-testid="step-2-agent-type"]').select('marketing_automation');
        cy.get('[data-testid="step-2-depends-on"]').select('Step 1');

        // Set step dependency
        cy.get('[data-testid="step-2-campaign-name"]').type('E2E Test Campaign');
        cy.get('[data-testid="step-2-platforms"]').check(['google_ads', 'meta_ads']);

        // Save workflow
        cy.get('[data-testid="save-workflow-button"]').click();

        // Verify workflow was created
        cy.contains('Workflow created successfully').should('be.visible');

        // Execute workflow
        cy.get('[data-testid="execute-workflow-button"]').click();

        // Wait for execution to complete
        cy.intercept('POST', '/api/agentkit/workflows/*/execute').as('executeWorkflow');
        cy.wait('@executeWorkflow');

        // Verify execution results
        cy.contains('Workflow execution completed').should('be.visible');
        cy.get('[data-testid="execution-results"]').should('be.visible');

        // Check execution details
        cy.get('[data-testid="execution-status"]').contains('completed');
        cy.get('[data-testid="execution-duration"]').should('be.visible');
    });

    it('handles agent creation and execution workflow', () => {
        // Login first
        cy.login('test@example.com', 'password123');

        // Navigate to agents page
        cy.get('[data-testid="agents-nav-link"]').click();
        cy.url().should('include', '/agents');

        // Create new agent
        cy.get('[data-testid="create-agent-button"]').click();

        // Fill agent form
        cy.get('[data-testid="agent-name-input"]').type('E2E Creative Agent');
        cy.get('[data-testid="agent-type-select"]').select('creative_intelligence');
        cy.get('[data-testid="agent-description-input"]').type('Agent for E2E testing');

        // Configure agent settings
        cy.get('[data-testid="platforms-checkbox"]').check(['google_ads', 'meta_ads']);
        cy.get('[data-testid="analysis-types-checkbox"]').check(['aida', 'brand_compliance']);

        // Save agent
        cy.get('[data-testid="save-agent-button"]').click();

        // Verify agent creation
        cy.contains('Agent created successfully').should('be.visible');

        // Execute agent
        cy.get('[data-testid="execute-agent-button"]').first().click();

        // Fill execution form
        cy.get('[data-testid="asset-url-input"]').type('https://example.com/test-creative.jpg');
        cy.get('[data-testid="analysis-type-select"]').select('aida');
        cy.get('[data-testid="target-platforms-checkbox"]').check(['google_ads']);

        // Submit execution
        cy.get('[data-testid="execute-button"]').click();

        // Wait for execution completion
        cy.intercept('POST', '/api/agentkit/agents/*/execute').as('executeAgent');
        cy.wait('@executeAgent');

        // Verify execution results
        cy.contains('Agent execution completed').should('be.visible');
        cy.get('[data-testid="execution-output"]').should('be.visible');
    });

    it('tests error scenarios and recovery', () => {
        // Login first
        cy.login('test@example.com', 'password123');

        // Test API failure scenario
        cy.intercept('GET', '/api/agentkit/agents*', {
            statusCode: 500,
            body: { error: 'Internal server error' }
        }).as('apiError');

        // Try to access agents page
        cy.get('[data-testid="agents-nav-link"]').click();

        // Should show error message
        cy.wait('@apiError');
        cy.contains('Failed to load agents').should('be.visible');

        // Test recovery - refresh page
        cy.reload();

        // Mock successful response for recovery
        cy.intercept('GET', '/api/agentkit/agents*', { fixture: 'agents/list.json' }).as('recovered');
        cy.wait('@recovered');

        // Should recover and show agents
        cy.get('[data-testid="agents-list"]').should('be.visible');
    });

    it('validates form validation across all forms', () => {
        // Test login form validation
        cy.visit('/login');

        // Try to submit empty form
        cy.get('[data-testid="login-button"]').click();

        // Should show validation errors
        cy.contains('Email is required').should('be.visible');
        cy.contains('Password is required').should('be.visible');

        // Test invalid email format
        cy.get('[data-testid="email-input"]').type('invalid-email');
        cy.get('[data-testid="login-button"]').click();
        cy.contains('Please enter a valid email address').should('be.visible');

        // Test agent creation form validation
        cy.login('test@example.com', 'password123');
        cy.get('[data-testid="create-agent-button"]').click();

        // Try to submit incomplete agent form
        cy.get('[data-testid="save-agent-button"]').click();

        // Should show validation errors
        cy.contains('Agent name is required').should('be.visible');
        cy.contains('Agent type is required').should('be.visible');
    });
});

describe('Performance Testing', () => {
    it('loads dashboard within performance budget', () => {
        cy.login('test@example.com', 'password123');

        // Measure page load performance
        cy.window().then((win) => {
            const perfData = win.performance.timing;
            const loadTime = perfData.loadEventEnd - perfData.navigationStart;

            // Should load within 3 seconds
            expect(loadTime).to.be.lessThan(3000);
        });
    });

    it('handles large datasets efficiently', () => {
        // Mock large dataset response
        cy.intercept('GET', '/api/agentkit/agents*', {
            fixture: 'agents/large-dataset.json' // 1000+ agents
        }).as('largeDataset');

        cy.login('test@example.com', 'password123');

        // Wait for data to load
        cy.wait('@largeDataset');

        // Measure rendering performance
        cy.window().then((win) => {
            const startTime = performance.now();

            // Force re-render to measure performance
            cy.get('[data-testid="agents-list"]').should('be.visible');

            const endTime = performance.now();
            const renderTime = endTime - startTime;

            // Should render large dataset efficiently
            expect(renderTime).to.be.lessThan(500);
        });
    });
});

describe('Accessibility Testing', () => {
    beforeEach(() => {
        cy.login('test@example.com', 'password123');
    });

    it('passes accessibility audit', () => {
        // Run axe-core accessibility audit
        cy.injectAxe();
        cy.checkA11y();
    });

    it('supports keyboard navigation', () => {
        // Test keyboard navigation through main interface
        cy.get('[data-testid="main-nav"]').should('be.visible');

        // Tab through navigation
        cy.get('body').tab();

        // Should be able to navigate with keyboard
        cy.focused().should('have.attr', 'data-testid').and('contain', 'nav');
    });

    it('has proper ARIA labels and roles', () => {
        // Check for proper ARIA implementation
        cy.get('[data-testid="agents-list"]').should('have.attr', 'role', 'list');
        cy.get('[data-testid="agent-item"]').should('have.attr', 'role', 'listitem');

        // Check for proper labeling
        cy.get('[data-testid="create-agent-button"]')
          .should('have.attr', 'aria-label')
          .and('contain', 'Create new agent');
    });
});

describe('Mobile Responsiveness', () => {
    beforeEach(() => {
        cy.login('test@example.com', 'password123');
    });

    it('works correctly on mobile viewport', () => {
        // Set mobile viewport
        cy.viewport('iphone-6');

        // Check mobile-specific layout
        cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
        cy.get('[data-testid="desktop-nav"]').should('not.be.visible');

        // Test mobile navigation
        cy.get('[data-testid="mobile-menu-button"]').click();
        cy.get('[data-testid="mobile-nav-menu"]').should('be.visible');
    });

    it('handles touch interactions properly', () => {
        cy.viewport('iphone-6');

        // Test touch targets are appropriately sized
        cy.get('[data-testid="action-buttons"]').each(($btn) => {
            cy.wrap($btn).should('have.css', 'min-height', '44px'); // iOS minimum touch target
        });
    });
});

describe('Real-time Features', () => {
    it('handles real-time workflow updates', () => {
        cy.login('test@example.com', 'password123');

        // Start a long-running workflow
        cy.intercept('POST', '/api/agentkit/workflows/*/execute', (req) => {
            // Mock long-running execution
            req.reply({
                statusCode: 200,
                body: {
                    execution_id: 'test_execution',
                    status: 'in_progress'
                }
            });
        }).as('startExecution');

        // Execute workflow
        cy.get('[data-testid="execute-workflow-button"]').click();
        cy.wait('@startExecution');

        // Simulate real-time updates
        cy.window().then((win) => {
            // Mock WebSocket message for progress update
            const mockProgressUpdate = {
                execution_id: 'test_execution',
                status: 'in_progress',
                progress: 50,
                current_step: 'creative_analysis'
            };

            // Emit progress update (would come from WebSocket in real app)
            win.dispatchEvent(new CustomEvent('workflow-progress', {
                detail: mockProgressUpdate
            }));
        });

        // Verify progress is displayed
        cy.contains('50% complete').should('be.visible');
        cy.contains('Processing creative analysis').should('be.visible');
    });
});

describe('Error Recovery', () => {
    it('recovers from network interruptions', () => {
        cy.login('test@example.com', 'password123');

        // Simulate network failure
        cy.intercept('GET', '/api/agentkit/agents*', { forceNetworkError: true }).as('networkError');

        // Try to load agents
        cy.get('[data-testid="agents-nav-link"]').click();

        // Should show error state
        cy.contains('Network error').should('be.visible');

        // Simulate network recovery
        cy.intercept('GET', '/api/agentkit/agents*', { fixture: 'agents/list.json' }).as('recovered');

        // Retry operation
        cy.get('[data-testid="retry-button"]').click();
        cy.wait('@recovered');

        // Should recover successfully
        cy.get('[data-testid="agents-list"]').should('be.visible');
    });

    it('handles server errors gracefully', () => {
        cy.login('test@example.com', 'password123');

        // Mock server error
        cy.intercept('POST', '/api/agentkit/agents', {
            statusCode: 500,
            body: { error: 'Internal server error' }
        }).as('serverError');

        // Try to create agent
        cy.get('[data-testid="create-agent-button"]').click();
        cy.get('[data-testid="agent-name-input"]').type('Test Agent');
        cy.get('[data-testid="save-agent-button"]').click();

        // Should show error message
        cy.wait('@serverError');
        cy.contains('Failed to create agent').should('be.visible');

        // Should allow retry
        cy.get('[data-testid="retry-button"]').should('be.visible');
    });
});

describe('Data Integrity', () => {
    it('validates data consistency across operations', () => {
        cy.login('test@example.com', 'password123');

        // Create agent and verify data persistence
        cy.get('[data-testid="create-agent-button"]').click();
        cy.get('[data-testid="agent-name-input"]').type('Integrity Test Agent');
        cy.get('[data-testid="agent-type-select"]').select('creative_intelligence');
        cy.get('[data-testid="save-agent-button"]').click();

        // Verify agent appears in list
        cy.contains('Integrity Test Agent').should('be.visible');

        // Navigate away and back
        cy.get('[data-testid="dashboard-nav-link"]').click();
        cy.get('[data-testid="agents-nav-link"]').click();

        // Verify data persists
        cy.contains('Integrity Test Agent').should('be.visible');
    });
});

describe('Security Testing', () => {
    it('prevents unauthorized access', () => {
        // Try to access protected route without authentication
        cy.visit('/dashboard');

        // Should redirect to login
        cy.url().should('include', '/login');
        cy.contains('Please log in to continue').should('be.visible');
    });

    it('validates CSRF protection', () => {
        // This would test CSRF token validation
        // Implementation depends on CSRF implementation
    });

    it('prevents XSS attacks', () => {
        cy.login('test@example.com', 'password123');

        // Try to inject malicious script (should be sanitized)
        cy.get('[data-testid="agent-description-input"]').type('<script>alert("xss")</script>');

        // Should be properly escaped or filtered
        cy.get('[data-testid="agent-description-input"]').should('have.value', '&lt;script&gt;alert("xss")&lt;/script&gt;');
    });
});

describe('API Contract Testing', () => {
    it('validates API response schemas', () => {
        cy.login('test@example.com', 'password123');

        // Intercept API calls and validate response structure
        cy.intercept('GET', '/api/agentkit/agents*', (req) => {
            req.reply((res) => {
                // Validate response structure
                const agents = res.body;
                expect(Array.isArray(agents)).to.be.true;

                agents.forEach(agent => {
                    expect(agent).to.have.property('agent_id');
                    expect(agent).to.have.property('name');
                    expect(agent).to.have.property('agent_type');
                    expect(agent).to.have.property('organization_id');
                });

                res.send();
            });
        }).as('validateSchema');

        cy.get('[data-testid="agents-nav-link"]').click();
        cy.wait('@validateSchema');
    });
});

// Custom commands for better test readability
Cypress.Commands.add('login', (email, password) => {
    cy.session([email, password], () => {
        cy.visit('/login');
        cy.get('[data-testid="email-input"]').type(email);
        cy.get('[data-testid="password-input"]').type(password);
        cy.get('[data-testid="login-button"]').click();
        cy.url().should('include', '/dashboard');
    });
});
