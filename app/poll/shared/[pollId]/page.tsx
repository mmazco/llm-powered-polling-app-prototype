'use client';

import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, BarChart3, User, Share2 } from 'lucide-react';
import { trackUserEngagement } from '../../../../lib/analytics';

interface Statement {
  text: string;
  category: string;
  expected_cluster: string;
}

interface Cluster {
  name: string;
  description: string;
}

interface SharedPoll {
  poll_id: string;
  title: string;
  description: string;
  main_theme: string;
  statements: Statement[];
  expected_clusters: Cluster[];
  metadata: any;
  created_at: string;
  creator_name?: string;
}

interface VoteResponse {
  statementIndex: number;
  response: 'agree' | 'disagree' | 'skip';
}

const SharedPollPage = ({ params }: { params: { pollId: string } }) => {
  const [poll, setPoll] = useState<SharedPoll | null>(null);
  const [currentStatement, setCurrentStatement] = useState(0);
  const [votes, setVotes] = useState<VoteResponse[]>([]);
  const [userName, setUserName] = useState('');
  const [showUserInput, setShowUserInput] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasParticipated, setHasParticipated] = useState(false);
  const [lastTaken, setLastTaken] = useState<string | null>(null);
  const [checkingParticipant, setCheckingParticipant] = useState(false);

  const voteOptions = [
    { value: 'agree', label: 'Agree', color: 'bg-green-500', emoji: '👍' },
    { value: 'disagree', label: 'Disagree', color: 'bg-red-500', emoji: '👎' },
    { value: 'skip', label: 'Skip', color: 'bg-gray-400', emoji: '⏭️' },
  ];

  useEffect(() => {
    const loadSharedPoll = async () => {
      try {
        const response = await fetch(`https://llm-powered-polling-app-prototype-production-7369.up.railway.app/poll/${params.pollId}`);
        
        if (response.ok) {
          const pollData = await response.json();
          setPoll(pollData);
          
          // Track poll access
          trackUserEngagement('shared_poll_accessed', `poll_id: ${params.pollId}`);
        } else if (response.status === 404) {
          setError('Poll not found. The link may be invalid or the poll may have been removed.');
        } else {
          setError('Failed to load poll. Please try again later.');
        }
      } catch (error) {
        console.error('Error loading shared poll:', error);
        setError('Failed to load poll. Please check your connection and try again.');
      } finally {
        setLoading(false);
      }
    };

    loadSharedPoll();
  }, [params.pollId]);

  const handleVote = (response: VoteResponse['response']) => {
    const newVote: VoteResponse = {
      statementIndex: currentStatement,
      response
    };

    setVotes(prev => {
      const existingIndex = prev.findIndex(v => v.statementIndex === currentStatement);
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = newVote;
        return updated;
      } else {
        return [...prev, newVote];
      }
    });

    // Track the vote
    trackUserEngagement('vote_on_shared_poll', `poll_id: ${params.pollId}, statement: ${currentStatement}, response: ${response}`);

    // Auto-advance to next statement
    if (currentStatement < (poll?.statements.length || 0) - 1) {
      setTimeout(() => setCurrentStatement(prev => prev + 1), 500);
    } else {
      // Save votes and submit to database, then redirect to results
      setTimeout(async () => {
        const updatedVotes = [...votes.filter(v => v.statementIndex !== currentStatement), newVote];
        
        // Save to localStorage (for fallback)
        localStorage.setItem('pollVotes', JSON.stringify(updatedVotes));
        localStorage.setItem('currentTopic', JSON.stringify({
          title: poll?.title,
          description: poll?.description,
          main_theme: poll?.main_theme,
          statements: poll?.statements,
          expected_clusters: poll?.expected_clusters,
          metadata: { ...poll?.metadata, poll_id: params.pollId, is_shared_poll: true }
        }));
        localStorage.setItem('userName', userName);
        
        // Submit responses to database
        try {
          const response = await fetch(`https://llm-powered-polling-app-prototype-production-7369.up.railway.app/poll/${params.pollId}/responses`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              poll_id: params.pollId,
              participant_name: userName || 'Anonymous',
              responses: updatedVotes.map(vote => ({
                statementIndex: vote.statementIndex,
                response: vote.response
              }))
            })
          });
          
          if (response.ok) {
            // Track successful submission
            trackUserEngagement('shared_poll_completed', `poll_id: ${params.pollId}, votes: ${updatedVotes.length}, submitted: true`);
          } else {
            console.warn('Failed to submit responses to database, using local storage only');
            trackUserEngagement('shared_poll_completed', `poll_id: ${params.pollId}, votes: ${updatedVotes.length}, submitted: false`);
          }
        } catch (error) {
          console.error('Error submitting responses:', error);
          trackUserEngagement('shared_poll_completed', `poll_id: ${params.pollId}, votes: ${updatedVotes.length}, submitted: false`);
        }
        
        window.location.href = '/results';
      }, 500);
    }
  };

  const checkParticipantStatus = async (name: string) => {
    if (!name.trim()) return;
    
    setCheckingParticipant(true);
    try {
      const response = await fetch(`https://llm-powered-polling-app-prototype-production-7369.up.railway.app/poll/${params.pollId}/participant/${encodeURIComponent(name)}`);
      
      if (response.ok) {
        const data = await response.json();
        setHasParticipated(data.has_responded);
        setLastTaken(data.last_taken);
      }
    } catch (error) {
      console.error('Error checking participant status:', error);
      // Continue anyway if check fails
    }
    setCheckingParticipant(false);
  };

  const handleStartPoll = () => {
    if (userName.trim()) {
      localStorage.setItem('userName', userName);
      setShowUserInput(false);
      
      // Track poll start
      const eventType = hasParticipated ? 'shared_poll_retaken' : 'shared_poll_started';
      trackUserEngagement(eventType, `poll_id: ${params.pollId}, user: ${userName}`);
    }
  };

  const handleRestart = () => {
    setVotes([]);
    setCurrentStatement(0);
  };

  const getCurrentVote = () => {
    return votes.find(v => v.statementIndex === currentStatement);
  };

  const handleBackToGenerator = () => {
    window.location.href = '/';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading shared poll...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl shadow-sm p-8 max-w-md w-full text-center">
          <div className="w-12 h-12 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Share2 className="text-red-600" size={20} />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Poll Not Found</h1>
          <p className="text-gray-600 text-sm mb-6">{error}</p>
          <button 
            onClick={handleBackToGenerator}
            className="w-full bg-blue-600 text-white p-4 rounded-2xl hover:bg-blue-700 transition-colors font-medium"
          >
            Create Your Own Poll
          </button>
        </div>
      </div>
    );
  }

  if (!poll) {
    return null;
  }

  if (showUserInput) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl shadow-sm p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <User className="text-blue-600" size={20} />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome to the Poll</h1>
            <p className="text-gray-600 text-sm mb-2">
              You&apos;re about to participate in: <strong>{poll.title}</strong>
            </p>
            {poll.creator_name && (
              <p className="text-gray-500 text-xs">
                Created by {poll.creator_name}
              </p>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Name (Optional)
              </label>
              <input
                type="text"
                value={userName}
                onChange={(e) => {
                  setUserName(e.target.value);
                  setHasParticipated(false); // Reset status when name changes
                }}
                onBlur={(e) => checkParticipantStatus(e.target.value)}
                placeholder="Enter your name..."
                className="w-full p-4 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              
              {checkingParticipant && (
                <div className="mt-2 text-sm text-gray-500 flex items-center gap-2">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  Checking previous responses...
                </div>
              )}
              
              {hasParticipated && !checkingParticipant && (
                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-2xl">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-yellow-600">⚠️</span>
                    <span className="font-medium text-yellow-800">You&apos;ve already taken this poll</span>
                  </div>
                  <p className="text-sm text-yellow-700">
                    Last completed: {lastTaken ? new Date(lastTaken).toLocaleDateString() : 'Recently'}
                  </p>
                  <p className="text-sm text-yellow-600 mt-1">
                    You can retake it, which will replace your previous responses.
                  </p>
                </div>
              )}
            </div>

            <button
              onClick={handleStartPoll}
              disabled={checkingParticipant}
              className="w-full bg-blue-600 text-white p-4 rounded-2xl hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {checkingParticipant 
                ? 'Checking...' 
                : hasParticipated 
                  ? 'Retake Poll' 
                  : 'Start Poll'
              }
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <button 
              onClick={handleBackToGenerator}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              <ChevronLeft size={20} />
              Back to Generator
            </button>
            <div className="text-sm text-gray-500">
              {poll.creator_name && `Created by ${poll.creator_name}`}
            </div>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{poll.title}</h1>
          <p className="text-gray-600 text-sm">{poll.description}</p>
        </div>

        {/* Progress */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm font-medium text-gray-700">
              Question {currentStatement + 1} of {poll.statements.length}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round(((currentStatement + 1) / poll.statements.length) * 100)}% complete
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStatement + 1) / poll.statements.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-3xl shadow-sm p-8 mb-6">
          <div className="text-center mb-8">
            <div className="text-sm text-gray-500 mb-2">
              Category: {poll.statements[currentStatement].category}
            </div>
            <h2 className="text-xl font-semibold text-gray-900 leading-relaxed">
              {poll.statements[currentStatement].text}
            </h2>
          </div>

          {/* Vote Options */}
          <div className="space-y-3">
            {voteOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleVote(option.value as VoteResponse['response'])}
                className={`w-full p-4 rounded-2xl border-2 transition-all duration-200 flex items-center justify-center gap-3 ${
                  getCurrentVote()?.response === option.value
                    ? `${option.color} text-white border-transparent shadow-lg`
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }`}
              >
                <span className="text-xl">{option.emoji}</span>
                <span className="font-medium">{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="bg-white rounded-3xl shadow-sm p-6">
          <div className="flex justify-between items-center">
            <button
              onClick={() => setCurrentStatement(Math.max(0, currentStatement - 1))}
              disabled={currentStatement === 0}
              className="flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-2xl hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={18} />
              Previous
            </button>

            <div className="flex gap-3">
              <button
                onClick={handleRestart}
                className="px-6 py-3 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Restart
              </button>
              
              {votes.length > 0 && (
                <button
                  onClick={async () => {
                    // Save to localStorage (for fallback)
                    localStorage.setItem('pollVotes', JSON.stringify(votes));
                    localStorage.setItem('currentTopic', JSON.stringify({
                      title: poll.title,
                      description: poll.description,
                      main_theme: poll.main_theme,
                      statements: poll.statements,
                      expected_clusters: poll.expected_clusters,
                      metadata: { ...poll.metadata, poll_id: params.pollId, is_shared_poll: true }
                    }));
                    localStorage.setItem('userName', userName);
                    
                    // Submit partial responses to database
                    try {
                      const response = await fetch(`https://llm-powered-polling-app-prototype-production-7369.up.railway.app/poll/${params.pollId}/responses`, {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                          poll_id: params.pollId,
                          participant_name: userName || 'Anonymous',
                          responses: votes.map(vote => ({
                            statementIndex: vote.statementIndex,
                            response: vote.response
                          }))
                        })
                      });
                      
                      if (response.ok) {
                        trackUserEngagement('shared_poll_partial_results', `poll_id: ${params.pollId}, votes: ${votes.length}, submitted: true`);
                      } else {
                        console.warn('Failed to submit partial responses');
                        trackUserEngagement('shared_poll_partial_results', `poll_id: ${params.pollId}, votes: ${votes.length}, submitted: false`);
                      }
                    } catch (error) {
                      console.error('Error submitting partial responses:', error);
                      trackUserEngagement('shared_poll_partial_results', `poll_id: ${params.pollId}, votes: ${votes.length}, submitted: false`);
                    }
                    
                    window.location.href = '/results';
                  }}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-100 text-blue-700 rounded-2xl hover:bg-blue-200 transition-colors"
                >
                  <BarChart3 size={18} />
                  See Results
                </button>
              )}
            </div>

            <button
              onClick={() => setCurrentStatement(Math.min(poll.statements.length - 1, currentStatement + 1))}
              disabled={currentStatement === poll.statements.length - 1}
              className="flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-2xl hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SharedPollPage; 