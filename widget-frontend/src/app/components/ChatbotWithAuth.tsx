'use client'

import React, { useEffect, useState } from 'react';
import Chatbox from "./Chatbot"
import ChatWidget from './ChatWidget';

interface User {
    id: string;
    name: string;
    email: string;
  }

const ChatboxWithAuth: React.FC = () => {
    
  const [user, setUser] = useState<User | null>(null);

  
  const getSession = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/session', {
        credentials: 'include',
      })
      const jsonData = await res.json();
      if (jsonData && jsonData.user) {
        setUser(jsonData.user);
      }
    } catch (error) {
      console.error('Error fetching session:', error);
    }
  };

  
  useEffect(() => {
    getSession();
  }, []);

  // Show chatbox only if user is logged in
  return user ? <ChatWidget userId={user.id} userName={user.name} /> : null;
};

export default ChatboxWithAuth;