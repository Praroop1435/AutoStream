"use client";

import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ChatInterface from '@/components/ChatInterface';
import LeadDashboard from '@/components/LeadDashboard';
import SignInModal from '@/components/SignInModal';

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showSignIn, setShowSignIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setIsAuthenticated(true);
    } else {
      setShowSignIn(true);
    }
  }, []);

  const handleAuthSuccess = (token: string, userId: number) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user_id', userId.toString());
    setIsAuthenticated(true);
    setShowSignIn(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    setIsAuthenticated(false);
    setShowSignIn(true);
  };

  return (
    <main style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <SignInModal 
        isOpen={showSignIn} 
        onClose={() => {}} 
        onSuccess={handleAuthSuccess} 
      />
      
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} onLogout={handleLogout} />
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'leads' && <LeadDashboard />}
        {activeTab === 'knowledge' && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
            <p>Knowledge Base Management coming soon...</p>
          </div>
        )}
        {activeTab === 'settings' && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
            <p>Settings coming soon...</p>
          </div>
        )}
      </div>
    </main>
  );
}
