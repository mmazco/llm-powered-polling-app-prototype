'use client';

import React, { useState, useEffect } from 'react';
import { ChevronLeft, User, BarChart3, TrendingUp, Users, Target, PieChart } from 'lucide-react';

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

interface ClusterAlignment {
  cluster: string;
  alignment: number;
  votes: number;
  matchingStatements: number[];
}

const ResultsPage = () => {
  const [topic, setTopic] = useState<GeneratedTopic | null>(null);
  const [votes, setVotes] = useState<VoteResponse[]>([]);
  const [userName, setUserName] = useState('');
  const [clusterAlignments, setClusterAlignments] = useState<ClusterAlignment[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);

  useEffect(() => {
    // Load data from localStorage
    const storedTopic = localStorage.getItem('currentTopic');
    const storedVotes = localStorage.getItem('pollVotes');
    const storedName = localStorage.getItem('userName') || 'Anonymous';

    if (storedTopic && storedVotes) {
      const topic = JSON.parse(storedTopic);
      const votes = JSON.parse(storedVotes);
      setTopic(topic);
      setVotes(votes);
      setUserName(storedName);
      calculateClusterAlignments(topic, votes);
    } else {
      // Redirect to home if no data
      window.location.href = '/';
    }
  }, []);

  const calculateClusterAlignments = (topic: GeneratedTopic, votes: VoteResponse[]) => {
    const alignments: ClusterAlignment[] = [];

    topic.expected_clusters.forEach(cluster => {
      const clusterStatements = topic.statements
        .map((stmt, index) => ({ ...stmt, index }))
        .filter(stmt => stmt.expected_cluster === cluster.name);
      
      const clusterVotes = votes.filter(vote => 
        clusterStatements.some(stmt => stmt.index === vote.statementIndex)
      );

      // Calculate alignment score (0-100)
      let alignmentScore = 0;
      let totalVotes = 0;

      clusterVotes.forEach(vote => {
        const voteValue = getVoteValue(vote.response);
        alignmentScore += voteValue;
        totalVotes++;
      });

      const avgAlignment = totalVotes > 0 ? (alignmentScore / totalVotes) * 50 : 0; // Scale to 0-100 (max value is 2)

      alignments.push({
        cluster: cluster.name,
        alignment: Math.round(avgAlignment),
        votes: totalVotes,
        matchingStatements: clusterStatements.map(stmt => stmt.index)
      });
    });

    setClusterAlignments(alignments.sort((a, b) => b.alignment - a.alignment));
  };

  const getVoteValue = (response: VoteResponse['response']): number => {
    switch (response) {
      case 'agree': return 2;
      case 'disagree': return 0;
      case 'skip': return 1; // Neutral value for alignment calculation
      default: return 1;
    }
  };

  const getVoteLabel = (response: VoteResponse['response']): string => {
    return response.charAt(0).toUpperCase() + response.slice(1);
  };

  const getAlignmentColor = (alignment: number): string => {
    if (alignment >= 80) return 'bg-green-500';
    if (alignment >= 60) return 'bg-blue-500';
    if (alignment >= 40) return 'bg-yellow-500';
    if (alignment >= 20) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getAlignmentDescription = (alignment: number): string => {
    if (alignment >= 80) return 'Strong Alignment';
    if (alignment >= 60) return 'Good Alignment';
    if (alignment >= 40) return 'Moderate Alignment';
    if (alignment >= 20) return 'Weak Alignment';
    return 'No Alignment';
  };

  const handleBackToGenerator = () => {
    window.location.href = '/';
  };

  if (!topic || !votes.length) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
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
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <User size={16} />
              {userName}
            </div>
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Poll Results & Analysis</h1>
          <p className="text-gray-600">{topic.title}</p>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-3xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <BarChart3 className="text-blue-600" size={24} />
              <h3 className="font-semibold text-gray-900">Total Votes</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">{votes.length}</p>
            <p className="text-sm text-gray-500">statements answered</p>
          </div>

          <div className="bg-white rounded-3xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <Target className="text-green-600" size={24} />
              <h3 className="font-semibold text-gray-900">Top Alignment</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">{clusterAlignments[0]?.alignment || 0}%</p>
            <p className="text-sm text-gray-500">{clusterAlignments[0]?.cluster || 'No data'}</p>
          </div>

          <div className="bg-white rounded-3xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <Users className="text-purple-600" size={24} />
              <h3 className="font-semibold text-gray-900">Clusters</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">{clusterAlignments.length}</p>
            <p className="text-sm text-gray-500">opinion groups</p>
          </div>
        </div>

        {/* Cluster Alignment Visualization */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <PieChart className="text-indigo-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Opinion Cluster Alignment</h2>
          </div>

          <div className="space-y-4">
            {clusterAlignments.map((alignment, index) => (
              <div key={index} className="border border-gray-200 rounded-2xl p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full ${getAlignmentColor(alignment.alignment)}`}></div>
                    <h3 className="font-semibold text-gray-900">{alignment.cluster}</h3>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">{alignment.alignment}%</div>
                    <div className="text-sm text-gray-500">{getAlignmentDescription(alignment.alignment)}</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${getAlignmentColor(alignment.alignment)}`}
                    style={{ width: `${alignment.alignment}%` }}
                  ></div>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{alignment.votes} relevant votes</span>
                  <button 
                    onClick={() => setSelectedCluster(selectedCluster === alignment.cluster ? null : alignment.cluster)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {selectedCluster === alignment.cluster ? 'Hide Details' : 'Show Details'}
                  </button>
                </div>

                {/* Detailed View */}
                {selectedCluster === alignment.cluster && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <h4 className="font-medium text-gray-900 mb-2">Cluster Description</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      {topic.expected_clusters.find(c => c.name === alignment.cluster)?.description}
                    </p>
                    
                    <h4 className="font-medium text-gray-900 mb-2">Your Votes on Related Statements</h4>
                    <div className="space-y-2">
                      {alignment.matchingStatements.map(stmtIndex => {
                        const vote = votes.find(v => v.statementIndex === stmtIndex);
                        const statement = topic.statements[stmtIndex];
                        return (
                          <div key={stmtIndex} className="bg-gray-50 rounded-xl p-3">
                            <p className="text-sm text-gray-900 mb-1">{statement.text}</p>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <span className="font-medium">Your response:</span>
                              <span className={`px-2 py-1 rounded-full ${vote ? getAlignmentColor(getVoteValue(vote.response) * 50) : 'bg-gray-200'} text-white`}>
                                {vote ? getVoteLabel(vote.response) : 'No vote'}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={() => window.location.href = '/poll'}
            className="flex-1 bg-gray-100 text-gray-700 p-4 rounded-2xl hover:bg-gray-200 transition-colors font-medium"
          >
            Retake Poll
          </button>
          <button
            onClick={handleBackToGenerator}
            className="flex-1 bg-blue-600 text-white p-4 rounded-2xl hover:bg-blue-700 transition-colors font-medium"
          >
            Generate New Topic
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage; 