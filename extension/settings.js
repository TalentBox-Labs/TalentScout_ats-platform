// TalentScout Extension Settings
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('settings-form');
  const apiUrlInput = document.getElementById('api-url');
  const apiTokenInput = document.getElementById('api-token');
  const saveButton = document.getElementById('save-button');
  const testButton = document.getElementById('test-button');
  const statusEl = document.getElementById('status');

  // Load existing settings
  chrome.storage.local.get(['apiUrl', 'apiToken'], function(result) {
    if (result.apiUrl) {
      apiUrlInput.value = result.apiUrl;
    }
    if (result.apiToken) {
      apiTokenInput.value = result.apiToken;
    }
  });

  // Save settings
  form.addEventListener('submit', function(e) {
    e.preventDefault();

    const apiUrl = apiUrlInput.value.trim();
    const apiToken = apiTokenInput.value.trim();

    if (!apiUrl || !apiToken) {
      showStatus('Please fill in all fields', 'error');
      return;
    }

    // Validate URL format
    try {
      new URL(apiUrl);
    } catch {
      showStatus('Please enter a valid URL', 'error');
      return;
    }

    // Save settings
    chrome.storage.local.set({
      apiUrl: apiUrl,
      apiToken: apiToken
    }, function() {
      showStatus('Settings saved successfully!', 'success');

      // Close window after a delay
      setTimeout(() => {
        window.close();
      }, 1500);
    });
  });

  // Test connection
  testButton.addEventListener('click', function() {
    const apiUrl = apiUrlInput.value.trim();
    const apiToken = apiTokenInput.value.trim();

    if (!apiUrl || !apiToken) {
      showStatus('Please fill in all fields first', 'error');
      return;
    }

    testButton.disabled = true;
    testButton.textContent = 'Testing...';

    // Test API connection
    fetch(`${apiUrl}/health`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiToken}`
      }
    })
    .then(response => {
      if (response.ok) {
        showStatus('Connection successful!', 'success');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    })
    .catch(error => {
      console.error('Connection test failed:', error);
      showStatus('Connection failed. Please check your settings.', 'error');
    })
    .finally(() => {
      testButton.disabled = false;
      testButton.textContent = 'Test Connection';
    });
  });

  function showStatus(message, type) {
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
    statusEl.style.display = 'block';

    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
      setTimeout(() => {
        statusEl.style.display = 'none';
      }, 5000);
    }
  }
});