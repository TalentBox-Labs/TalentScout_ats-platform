// Content script for extracting candidate data from LinkedIn and GitHub
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'extractLinkedIn') {
    const candidate = extractLinkedInProfile();
    sendResponse({ candidate });
  } else if (request.action === 'extractGitHub') {
    const candidate = extractGitHubProfile();
    sendResponse({ candidate });
  }
});

function extractLinkedInProfile() {
  try {
    // LinkedIn profile selectors (may need updates based on LinkedIn's DOM changes)
    const nameSelectors = [
      'h1.text-heading-xlarge',
      '.pv-text-details__left-panel h1',
      '[data-test-id="hero-heading"]'
    ];

    const titleSelectors = [
      '.pv-text-details__left-panel .text-body-medium',
      '.pv-entity__summary-info h3',
      '[data-test-id="hero-subtitle"]'
    ];

    const companySelectors = [
      '.pv-text-details__left-panel .pv-entity__secondary-title',
      '.pv-entity__summary-info .pv-entity__location span:last-child',
      '[data-test-id="hero-company"]'
    ];

    const name = findElementText(nameSelectors);
    const title = findElementText(titleSelectors);
    const company = findElementText(companySelectors);

    return {
      name: name,
      title: title,
      company: company,
      linkedin_url: window.location.href,
      source: 'linkedin'
    };
  } catch (error) {
    console.error('Error extracting LinkedIn profile:', error);
    return null;
  }
}

function extractGitHubProfile() {
  try {
    // GitHub profile selectors
    const nameSelector = '.vcard-fullname';
    const usernameSelector = '.vcard-username';
    const bioSelector = '.user-profile-bio';

    const name = document.querySelector(nameSelector)?.textContent?.trim();
    const username = document.querySelector(usernameSelector)?.textContent?.trim();
    const bio = document.querySelector(bioSelector)?.textContent?.trim();

    // Extract tech stack from bio and repositories (simplified)
    let skills = [];
    if (bio) {
      // Simple keyword extraction
      const techKeywords = ['javascript', 'python', 'react', 'node', 'typescript', 'java', 'go', 'rust'];
      skills = techKeywords.filter(keyword =>
        bio.toLowerCase().includes(keyword)
      );
    }

    return {
      name: name || username,
      title: 'Software Developer', // Default title for GitHub profiles
      company: '', // GitHub doesn't typically show company
      bio: bio,
      skills: skills,
      github_url: window.location.href,
      source: 'github'
    };
  } catch (error) {
    console.error('Error extracting GitHub profile:', error);
    return null;
  }
}

function findElementText(selectors) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent) {
      return element.textContent.trim();
    }
  }
  return '';
}

// Inject script to handle dynamic content loading
const script = document.createElement('script');
script.src = chrome.runtime.getURL('injected.js');
script.onload = function() {
  script.remove();
};
(document.head || document.documentElement).appendChild(script);