// Background service worker for TalentScout extension
chrome.runtime.onInstalled.addListener(function() {
  console.log('TalentScout extension installed');

  // Initialize extension
  chrome.storage.local.set({
    apiUrl: 'https://api.talentscout.com', // Default API URL
    apiToken: null
  });
});

// Handle extension icon click
chrome.action.onClicked.addListener(function(tab) {
  // Open popup programmatically if needed
  chrome.action.openPopup();
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'saveCandidate') {
    saveCandidateToATS(request.candidate)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep message channel open for async response
  }
});

async function saveCandidateToATS(candidate) {
  const { apiToken, apiUrl } = await chrome.storage.local.get(['apiToken', 'apiUrl']);

  if (!apiToken) {
    throw new Error('Not connected to TalentScout. Please connect first.');
  }

  const response = await fetch(`${apiUrl}/api/v1/candidates`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiToken}`
    },
    body: JSON.stringify(candidate)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save candidate');
  }

  return await response.json();
}

// Handle OAuth flows if needed
chrome.identity.onSignInChanged.addListener(function(account, signedIn) {
  console.log('Sign in changed:', account, signedIn);
});

// Periodic cleanup and maintenance
setInterval(() => {
  // Clean up old data, check connections, etc.
  chrome.storage.local.get(['lastCleanup'], function(result) {
    const now = Date.now();
    const lastCleanup = result.lastCleanup || 0;

    // Clean up every 24 hours
    if (now - lastCleanup > 24 * 60 * 60 * 1000) {
      // Perform cleanup tasks
      console.log('Performing extension cleanup');

      chrome.storage.local.set({ lastCleanup: now });
    }
  });
}, 60 * 60 * 1000); // Check every hour