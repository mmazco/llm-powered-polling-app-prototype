'use client';

import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, BarChart3, User } from 'lucide-react';

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

interface VoteResponse {
  statementIndex: number;
  response: 'agree' | 'disagree' | 'skip';
}

const PollPage = () => {
  const [topic, setTopic] = useState<GeneratedTopic | null>(null);
  const [currentStatement, setCurrentStatement] = useState(0);
  const [votes, setVotes] = useState<VoteResponse[]>([]);

  const [userName, setUserName] = useState('');
  const [showUserInput, setShowUserInput] = useState(true);

  const voteOptions = [
    { value: 'agree', label: 'Agree', color: 'bg-green-500', emoji: '👍' },
    { value: 'disagree', label: 'Disagree', color: 'bg-red-500', emoji: '👎' },
    { value: 'skip', label: 'Skip', color: 'bg-gray-400', emoji: '⏭️' },
  ];

  useEffect(() => {
    const storedTopic = localStorage.getItem('currentTopic');
    if (storedTopic) {
      setTopic(JSON.parse(storedTopic));
    } else {
      // Redirect to home if no topic
      window.location.href = '/';
    }
  }, []);

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

    // Auto-advance to next statement
    if (currentStatement < (topic?.statements.length || 0) - 1) {
      setTimeout(() => setCurrentStatement(prev => prev + 1), 500);
    } else {
      // Save votes and redirect to results
      setTimeout(() => {
        const updatedVotes = [...votes.filter(v => v.statementIndex !== currentStatement), newVote];
        localStorage.setItem('pollVotes', JSON.stringify(updatedVotes));
        window.location.href = '/results';
      }, 500);
    }
  };

  const handleStartPoll = () => {
    if (userName.trim()) {
      localStorage.setItem('userName', userName);
      setShowUserInput(false);
    }
  };

  const handleRestart = () => {
    setVotes([]);
    setCurrentStatement(0);
  };

  const handleBackToGenerator = () => {
    window.location.href = '/';
  };

  const getCurrentVote = () => {
    return votes.find(v => v.statementIndex === currentStatement);
  };



  if (!topic) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading poll...</p>
        </div>
      </div>
    );
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
            <p className="text-gray-600 text-sm">
              You&apos;re about to participate in: <strong>{topic.title}</strong>
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Name (optional)
              </label>
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                className="w-full p-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder:text-gray-500"
                placeholder="Enter your name"
              />
            </div>

            <button
              onClick={handleStartPoll}
              className="w-full bg-blue-600 text-white p-4 rounded-2xl hover:bg-blue-700 transition-colors font-medium"
            >
              Start Poll
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
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ChevronLeft size={20} />
              Back to Generator
            </button>
            <div className="text-sm text-gray-500">
              {currentStatement + 1} / {topic.statements.length}
            </div>
          </div>
          
          <h1 className="text-xl font-bold text-gray-900 mb-2">{topic.title}</h1>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStatement + 1) / topic.statements.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Current Statement */}
        <div className="bg-white rounded-3xl shadow-sm p-8 mb-6">
          <div className="text-center mb-8">
            <div className="text-sm text-gray-500 mb-2">
              Category: {topic.statements[currentStatement].category}
            </div>
            <h2 className="text-xl font-semibold text-gray-900 leading-relaxed">
              {topic.statements[currentStatement].text}
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
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md text-gray-900'
                }`}
              >
                <span className="text-xl">{option.emoji}</span>
                <span className="font-medium">{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={() => setCurrentStatement(prev => Math.max(0, prev - 1))}
            disabled={currentStatement === 0}
            className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft size={20} />
            Previous
          </button>
          
          <button
            onClick={() => setCurrentStatement(prev => Math.min(topic.statements.length - 1, prev + 1))}
            disabled={currentStatement === topic.statements.length - 1}
            className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default PollPage; 