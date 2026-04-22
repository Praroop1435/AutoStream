"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';

import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isBot = message.role === 'assistant';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        gap: '16px',
        alignItems: 'flex-start',
        maxWidth: '80%',
        alignSelf: isBot ? 'flex-start' : 'flex-end',
        flexDirection: isBot ? 'row' : 'row-reverse',
      }}
    >
      <div
        style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          backgroundColor: isBot ? 'var(--accent)' : 'var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          boxShadow: isBot ? '0 0 15px var(--accent-glow)' : 'none',
        }}
      >
        {isBot ? <Bot size={20} color="white" /> : <User size={20} color="var(--text-secondary)" />}
      </div>

      <div
        style={{
          backgroundColor: isBot ? 'var(--card-bg)' : 'var(--accent)',
          padding: '12px 18px',
          borderRadius: isBot ? '0 16px 16px 16px' : '16px 0 16px 16px',
          border: isBot ? '1px solid var(--border)' : 'none',
          color: isBot ? 'var(--foreground)' : 'white',
          fontSize: '15px',
          lineHeight: '1.5',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        }}
      >
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
    </motion.div>
  );
};

export default MessageBubble;
