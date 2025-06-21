// Script URL Generator - Frontend JavaScript

class ScriptUrlGenerator {
    constructor() {
        this.currentUrl = null;
        this.expiryTime = null;
        this.countdownInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateExpiryDisplay();
    }

    bindEvents() {
        const form = document.getElementById('generateForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const scriptId = formData.get('script_id');
        
        if (!scriptId) {
            this.showError('Please select a script');
            return;
        }

        this.showLoading(true);
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ script_id: scriptId })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to generate URL');
            }

            const data = await response.json();
            this.displayGeneratedUrl(data);
            
        } catch (error) {
            console.error('Error generating URL:', error);
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }

    displayGeneratedUrl(data) {
        this.currentUrl = data.url;
        this.expiryTime = new Date(data.expires_at);
        
        // Update UI
        document.getElementById('generatedUrl').value = data.url;
        document.getElementById('resultCard').style.display = 'block';
        
        // Start countdown
        this.startCountdown();
        
        // Scroll to result
        document.getElementById('resultCard').scrollIntoView({ 
            behavior: 'smooth',
            block: 'center'
        });
    }

    startCountdown() {
        this.updateExpiryDisplay();
        
        this.countdownInterval = setInterval(() => {
            this.updateExpiryDisplay();
        }, 1000);
    }

    updateExpiryDisplay() {
        if (!this.expiryTime) return;
        
        const now = new Date();
        const timeLeft = this.expiryTime - now;
        
        if (timeLeft <= 0) {
            this.expiryTime = null;
            document.getElementById('expiryTime').textContent = 'Expired';
            if (this.countdownInterval) {
                clearInterval(this.countdownInterval);
            }
            return;
        }
        
        const minutes = Math.floor(timeLeft / 60000);
        const seconds = Math.floor((timeLeft % 60000) / 1000);
        
        document.getElementById('expiryTime').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    showLoading(show) {
        const loadingCard = document.getElementById('loadingCard');
        const generateForm = document.getElementById('generateForm');
        
        if (show) {
            loadingCard.style.display = 'block';
            generateForm.style.display = 'none';
        } else {
            loadingCard.style.display = 'none';
            generateForm.style.display = 'block';
        }
    }

    showError(message) {
        // Create a simple error notification
        const notification = document.createElement('div');
        notification.className = 'copy-feedback';
        notification.style.background = '#ef4444';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'copy-feedback';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Global functions for button actions
function copyToClipboard() {
    const urlInput = document.getElementById('generatedUrl');
    
    if (navigator.clipboard && window.isSecureContext) {
        // Use modern clipboard API
        navigator.clipboard.writeText(urlInput.value).then(() => {
            app.showSuccess('URL copied to clipboard!');
        }).catch(() => {
            fallbackCopyToClipboard(urlInput);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyToClipboard(urlInput);
    }
}

function fallbackCopyToClipboard(input) {
    input.select();
    input.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        document.execCommand('copy');
        app.showSuccess('URL copied to clipboard!');
    } catch (err) {
        app.showError('Failed to copy URL');
    }
}

function testUrl() {
    const url = document.getElementById('generatedUrl').value;
    if (url) {
        window.open(url, '_blank');
    }
}

function generateNew() {
    // Reset the form and hide result
    document.getElementById('generateForm').reset();
    document.getElementById('resultCard').style.display = 'none';
    
    // Clear countdown
    if (app.countdownInterval) {
        clearInterval(app.countdownInterval);
        app.countdownInterval = null;
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Initialize the application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ScriptUrlGenerator();
});

// Add some utility functions
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to generate URL
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('generateForm');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
    
    // Ctrl/Cmd + C to copy URL when focused on input
    if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.id === 'generatedUrl') {
            copyToClipboard();
        }
    }
});

// Add some visual feedback for form interactions
document.addEventListener('DOMContentLoaded', () => {
    const scriptSelect = document.getElementById('scriptSelect');
    const generateBtn = document.getElementById('generateBtn');
    
    if (scriptSelect && generateBtn) {
        scriptSelect.addEventListener('change', () => {
            if (scriptSelect.value) {
                generateBtn.disabled = false;
                generateBtn.style.opacity = '1';
            } else {
                generateBtn.disabled = true;
                generateBtn.style.opacity = '0.6';
            }
        });
        
        // Initial state
        generateBtn.disabled = true;
        generateBtn.style.opacity = '0.6';
    }
}); 