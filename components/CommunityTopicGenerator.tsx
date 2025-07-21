'use client';

import React, { useState } from 'react';
import { Sparkles, MapPin, Users, RefreshCw, Download, ArrowRight, Share2, Copy, Check } from 'lucide-react';
import { trackTopicGeneration, trackPollLaunch, trackPollShare, trackUserEngagement } from '../lib/analytics';

interface Statement {
  text: string;
  category: string;
  expected_cluster: string;
}

interface Cluster {
  name: string;
  description: string;
}

interface GeneratedTopic {
  title: string;
  description: string;
  statements: Statement[];
  expected_clusters: Cluster[];
}

const CommunityTopicGenerator = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTopic, setGeneratedTopic] = useState<GeneratedTopic | null>(null);
  const [showShareOptions, setShowShareOptions] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [formData, setFormData] = useState({
    communityType: 'Urban Community',
    location: 'Downtown San Francisco',
    population: '50000',
    topicDomain: 'auto'
  });

  const communityTypes = ['Urban Community', 'Suburban Town', 'Rural Area', 'University Town'];
  
  const communityDomains = {
    'Urban Community': [
      { value: 'auto', label: 'Surprise me!', icon: '🎲' },
      { value: 'crime-public-safety', label: 'Crime and Public Safety', icon: '🚔' },
      { value: 'housing-affordability', label: 'Housing Affordability', icon: '🏠' },
      { value: 'economic-development', label: 'Economic Development', icon: '💼' },
      { value: 'infrastructure-services', label: 'Infrastructure & City Services', icon: '🏗️' },
      { value: 'transportation', label: 'Transportation', icon: '🚌' }
    ],
    'Suburban Town': [
      { value: 'auto', label: 'Surprise me!', icon: '🎲' },
      { value: 'traffic-school-safety', label: 'Traffic Congestion & School Safety', icon: '🚸' },
      { value: 'infrastructure-maintenance', label: 'Infrastructure Maintenance', icon: '🔧' },
      { value: 'school-quality', label: 'School Quality & Segregation', icon: '🎓' },
      { value: 'property-taxes', label: 'Property Taxes', icon: '💰' },
      { value: 'environmental-concerns', label: 'Environmental Concerns', icon: '🌱' }
    ],
    'Rural Area': [
      { value: 'auto', label: 'Surprise me!', icon: '🎲' },
      { value: 'digital-infrastructure', label: 'Digital Infrastructure Gap', icon: '📶' },
      { value: 'healthcare-access', label: 'Healthcare Access', icon: '🏥' },
      { value: 'economic-opportunities', label: 'Economic Opportunities', icon: '📈' },
      { value: 'aging-population', label: 'Aging Population Services', icon: '👴' },
      { value: 'infrastructure-decay', label: 'Infrastructure Decay', icon: '🛤️' }
    ],
    'University Town': [
      { value: 'auto', label: 'Surprise me!', icon: '🎲' },
      { value: 'student-housing-shortage', label: 'Student Housing Shortage', icon: '🏠' },
      { value: 'town-gown-relations', label: 'Town-Gown Relations', icon: '🤝' },
      { value: 'parking-transportation', label: 'Parking and Transportation', icon: '🅿️' },
      { value: 'noise-disruption', label: 'Noise and Disruption', icon: '🔊' },
      { value: 'economic-dependence', label: 'Economic Dependence on University', icon: '🎓' }
    ]
  };
  
  const getDomainsForCommunity = (communityType: string) => {
    return communityDomains[communityType] || communityDomains['Urban Community'];
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    
    try {
      const requestData = {
        community_context: {
          location: formData.location,
          population_size: parseInt(formData.population) || null,
          current_issues: [],
          previous_topics: []
        },
        topic_domain: formData.topicDomain === 'auto' ? null : formData.topicDomain
      };
      
      console.log('Sending request:', requestData);
      console.log('Current formData.topicDomain:', formData.topicDomain);
      
      const response = await fetch('https://llm-powered-polling-app-prototype-production-7369.up.railway.app/generate-topic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedTopic(data);
        
        // Track successful topic generation
        trackTopicGeneration(
          formData.location, 
          formData.topicDomain, 
          data.metadata?.generation_method || 'unknown'
        );
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error generating topic:', error);
      // Show error to user
      alert('Failed to generate topic. Please make sure the backend server is running.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => {
      // Reset domain selection when community type changes
      if (field === 'communityType') {
        return {
          ...prev,
          [field]: value,
          topicDomain: 'auto' // Reset to auto-detect
        };
      }
      return {
        ...prev,
        [field]: value
      };
    });
  };

  const handleLaunchPoll = () => {
    if (generatedTopic) {
      // Store topic in localStorage and navigate to poll
      localStorage.setItem('currentTopic', JSON.stringify(generatedTopic));
      
      // Track poll launch
      trackPollLaunch(generatedTopic.title);
      
      window.location.href = '/poll';
    }
  };

  const handleSharePoll = async () => {
    if (!generatedTopic) return;
    
    setIsSharing(true);
    try {
      const response = await fetch('https://llm-powered-polling-app-prototype-production-7369.up.railway.app/save-poll', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: generatedTopic,
          creator_name: localStorage.getItem('userName') || 'Anonymous'
        })
      });

      if (response.ok) {
        const data = await response.json();
        const fullShareUrl = `${window.location.origin}/poll/shared/${data.poll_id}`;
        setShareUrl(fullShareUrl);
        setShowShareOptions(true);
        
        // Track sharing activity
        trackUserEngagement('poll_shared', `poll_id: ${data.poll_id}`);
      } else {
        throw new Error('Failed to save poll for sharing');
      }
    } catch (error) {
      console.error('Error sharing poll:', error);
      alert('Failed to create shareable link. Please try again.');
    } finally {
      setIsSharing(false);
    }
  };

  const handleCopyLink = async () => {
    if (!shareUrl) return;
    
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopySuccess(true);
      trackPollShare(shareUrl.split('/').pop() || 'unknown', 'copy_link');
      
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (error) {
      console.error('Failed to copy link:', error);
      alert('Failed to copy link. Please copy manually.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-lg mx-auto p-6">
        {/* Header */}
        <div className="text-center mb-8 pt-8">
          <div className="w-12 h-12 bg-gray-300 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Sparkles className="text-gray-600" size={20} />
          </div>
          <h1 className="text-xl font-semibold mb-2 text-gray-900">LLM-Powered Polling App Prototype</h1>
          <p className="text-gray-600 text-sm mb-2">
            Topic generator v1.0 inspired by pol.is
          </p>
          <p className="text-gray-500 text-xs">
            Topic domains based on 2024 to 2025 data from multiple geographic sources across the US.{' '}
            <a 
              href="https://claude.ai/share/e5976a97-8f11-49aa-92c7-b6c7b22e5c9b" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 underline hover:text-blue-800"
            >
              See findings
            </a>
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Community Context</h2>
          
          <div className="space-y-6">
            {/* Community Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">Community Type</label>
              <div className="grid grid-cols-2 gap-3">
                {communityTypes.map((type) => (
                  <button
                    key={type}
                    onClick={() => handleInputChange('communityType', type)}
                    className={`p-4 rounded-2xl border text-sm font-medium transition-all ${
                      formData.communityType === type
                        ? 'bg-blue-50 border-blue-200 text-blue-900'
                        : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <MapPin size={14} className="inline mr-2" />
                Location
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="w-full p-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm !text-gray-900 placeholder:text-gray-500 bg-white"
                placeholder="e.g., Downtown Portland, Rural Vermont"
              />
            </div>

            {/* Population */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <Users size={14} className="inline mr-2" />
                Population Size
              </label>
              <input
                type="number"
                value={formData.population}
                onChange={(e) => handleInputChange('population', e.target.value)}
                className="w-full p-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm !text-gray-900 placeholder:text-gray-500 bg-white"
                placeholder="e.g., 50000"
              />
            </div>

            {/* Topic Domain */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">Topic Domain</label>
              <div className="grid grid-cols-1 gap-3">
                {getDomainsForCommunity(formData.communityType).map((domain) => (
                  <button
                    key={domain.value}
                    onClick={() => handleInputChange('topicDomain', domain.value)}
                    className={`p-4 rounded-2xl border text-sm font-medium transition-all flex items-center gap-3 ${
                      formData.topicDomain === domain.value
                        ? 'bg-blue-50 border-blue-200 text-blue-900'
                        : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <span className="text-lg">{domain.icon}</span>
                    <span>{domain.label}</span>
                  </button>
                ))}
              </div>
            </div>

          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="w-full mt-8 bg-black text-white p-4 rounded-2xl hover:bg-gray-900 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <>
                <RefreshCw size={18} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Generate Community Topic
              </>
            )}
          </button>
        </div>

        {/* Generated Topic */}
        {generatedTopic && (
          <div className="bg-white rounded-3xl shadow-sm p-6 animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Generated Topic</h2>
              <div className="flex gap-2">
                <button 
                  onClick={handleGenerate}
                  className="p-2 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors"
                >
                  <RefreshCw size={16} />
                </button>
                <button className="p-2 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors">
                  <Download size={16} />
                </button>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-2">{generatedTopic.title}</h3>
              <p className="text-sm text-gray-600">{generatedTopic.description}</p>
            </div>

            {/* Statements */}
            <div className="space-y-3 mb-6">
              {generatedTopic.statements.map((statement, index) => (
                <div key={index} className="bg-gray-50 border border-gray-200 rounded-2xl p-4">
                  <p className="text-sm text-gray-900 mb-2">{statement.text}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>Category: <span className="font-medium">{statement.category}</span></span>
                    <span>Expected Cluster: <span className="font-medium">{statement.expected_cluster}</span></span>
                  </div>
                </div>
              ))}
            </div>

            {/* Expected Clusters */}
            <div className="border-t border-gray-100 pt-6">
              <h4 className="font-semibold text-gray-900 mb-4">Expected Opinion Clusters</h4>
              <div className="grid grid-cols-1 gap-3">
                {generatedTopic.expected_clusters.map((cluster, index) => (
                  <div key={index} className="bg-gray-50 border border-gray-200 rounded-2xl p-4">
                    <h5 className="font-medium text-gray-900 mb-1">{cluster.name}</h5>
                    <p className="text-sm text-gray-600">{cluster.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 mt-6">
              <button 
                onClick={handleLaunchPoll}
                className="w-full bg-blue-600 text-white p-4 rounded-2xl hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2"
              >
                Launch Community Poll
                <ArrowRight size={18} />
              </button>
              
              <button 
                onClick={handleSharePoll}
                disabled={isSharing}
                className="w-full bg-gray-100 text-gray-700 p-4 rounded-2xl hover:bg-gray-200 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isSharing ? (
                  <>
                    <RefreshCw size={18} className="animate-spin" />
                    Creating Share Link...
                  </>
                ) : (
                  <>
                    <Share2 size={18} />
                    Share This Poll
                  </>
                )}
              </button>
            </div>

            {/* Share Options Modal */}
            {showShareOptions && shareUrl && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-2xl">
                <h4 className="font-semibold text-blue-900 mb-3">Share Your Poll</h4>
                <div className="space-y-3">
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      value={shareUrl} 
                      readOnly 
                      className="flex-1 p-3 text-sm bg-white border border-gray-300 rounded-xl"
                    />
                    <button 
                      onClick={handleCopyLink}
                      className="px-4 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors flex items-center gap-2"
                    >
                      {copySuccess ? (
                        <>
                          <Check size={16} />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy size={16} />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-blue-700">
                    Anyone with this link can participate in your poll and see the results.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CommunityTopicGenerator; 