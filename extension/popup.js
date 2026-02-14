// TalentScout Chrome Extension Popup
document.addEventListener('DOMContentLoaded', function() {
  const statusEl = document.getElementById('status');
  const currentCandidateEl = document.getElementById('current-candidate');
  const noCandidateEl = document.getElementById('no-candidate');
  const candidateNameEl = document.getElementById('candidate-name');
  const candidateTitleEl = document.getElementById('candidate-title');
  const candidateCompanyEl = document.getElementById('candidate-company');
  const connectButton = document.getElementById('connect-button');
  const saveButton = document.getElementById('save-candidate');
  const settingsButton = document.getElementById('settings-button');

  // Check connection status
  chrome.storage.local.get(['apiToken', 'apiUrl'], function(result) {
    if (result.apiToken && result.apiUrl) {
      statusEl.textContent = 'Connected to TalentScout';
      statusEl.className = 'status connected';
      connectButton.textContent = 'Disconnect';
    } else {
      statusEl.textContent = 'Not connected to TalentScout';
      statusEl.className = 'status disconnected';
      connectButton.textContent = 'Connect to TalentScout';
    }
  });

  // Get current tab and extract candidate info
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    const currentTab = tabs[0];
    const url = currentTab.url;

    if (url.includes('linkedin.com/in/')) {
      // LinkedIn profile
      extractLinkedInData(currentTab);
    } else if (url.includes('github.com/') && !url.includes('/pulls') && !url.includes('/issues')) {
      // GitHub profile
      extractGitHubData(currentTab);
    } else {
      noCandidateEl.style.display = 'block';
    }
  });

  function extractLinkedInData(tab) {
    chrome.tabs.sendMessage(tab.id, { action: 'extractLinkedIn' }, function(response) {
      if (response && response.candidate) {
        showCandidate(response.candidate);
      }
    });
  }

  function extractGitHubData(tab) {
    chrome.tabs.sendMessage(tab.id, { action: 'extractGitHub' }, function(response) {
      if (response && response.candidate) {
        showCandidate(response.candidate);
      }
    });
  }

  function showCandidate(candidate) {
    candidateNameEl.textContent = candidate.name || 'Unknown';
    candidateTitleEl.textContent = candidate.title || '';
    candidateCompanyEl.textContent = candidate.company || '';
    currentCandidateEl.style.display = 'block';
    noCandidateEl.style.display = 'none';
  }

  // Connect/Disconnect button
  connectButton.addEventListener('click', function() {
    chrome.storage.local.get(['apiToken'], function(result) {
      if (result.apiToken) {
        // Disconnect
        chrome.storage.local.remove(['apiToken', 'apiUrl'], function() {
          statusEl.textContent = 'Not connected to TalentScout';
          statusEl.className = 'status disconnected';
          connectButton.textContent = 'Connect to TalentScout';
        });
      } else {
        // Connect - open settings page
        chrome.tabs.create({ url: chrome.runtime.getURL('settings.html') });
      }
    });
  });

  // Save candidate button
  saveButton.addEventListener('click', function() {
    chrome.storage.local.get(['apiToken', 'apiUrl'], function(result) {
      if (!result.apiToken) {
        alert('Please connect to TalentScout first');
        return;
      }

      // Get current candidate data
      const candidate = {
        name: candidateNameEl.textContent,
        title: candidateTitleEl.textContent,
        company: candidateCompanyEl.textContent,
        source: 'extension',
        linkedin_url: '', // Will be filled by content script
        github_url: '' // Will be filled by content script
      };

      // Send to TalentScout API
      fetch(`${result.apiUrl}/api/v1/candidates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${result.apiToken}`
        },
        body: JSON.stringify(candidate)
      })
      .then(response => response.json())
      .then(data => {
        if (data.id) {
          alert('Candidate saved successfully!');
        } else {
          alert('Failed to save candidate');
        }
      })
      .catch(error => {
        console.error('Error saving candidate:', error);
        alert('Error saving candidate');
      });
    });
  });

  // Settings button
  settingsButton.addEventListener('click', function() {
    chrome.tabs.create({ url: chrome.runtime.getURL('settings.html') });
  });
});