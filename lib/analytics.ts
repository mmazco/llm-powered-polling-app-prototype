// Google Tag Manager tracking utilities

declare global {
  interface Window {
    dataLayer: any[];
  }
}

// Track page views
export const trackPageView = (url: string) => {
  if (typeof window !== 'undefined' && window.dataLayer) {
    window.dataLayer.push({
      event: 'page_view',
      page_path: url,
    });
  }
};

// Track custom events
export const trackEvent = (action: string, category: string, label?: string, value?: number) => {
  if (typeof window !== 'undefined' && window.dataLayer) {
    window.dataLayer.push({
      event: action,
      event_category: category,
      event_label: label,
      value: value,
    });
  }
};

// Specific tracking functions for our app
export const trackTopicGeneration = (location: string, topicDomain: string, method: 'llm' | 'demo') => {
  trackEvent('generate_topic', 'polling', `${location}_${topicDomain}_${method}`);
};

export const trackPollLaunch = (topicTitle: string) => {
  trackEvent('launch_poll', 'polling', topicTitle);
};

export const trackVote = (statementIndex: number, response: 'agree' | 'disagree' | 'skip') => {
  trackEvent('vote', 'polling', `statement_${statementIndex}_${response}`);
};

export const trackPollCompletion = (totalVotes: number, userName?: string) => {
  trackEvent('complete_poll', 'polling', userName ? 'named_user' : 'anonymous', totalVotes);
};

export const trackPollShare = (pollId: string, method: 'copy_link' | 'social') => {
  trackEvent('share_poll', 'sharing', `${pollId}_${method}`);
};

// User engagement tracking
export const trackUserEngagement = (action: string, details?: string) => {
  trackEvent(action, 'engagement', details);
}; 