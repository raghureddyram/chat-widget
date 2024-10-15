'use client'
import React, { useState, useEffect } from 'react';
import styles from '../css/ChatWidget.module.css'; // Importing CSS Module

type Message = {
  id?: string;
  line_type: 'user' | 'system';
  content: string;
  created_date?: string;
};

interface ChatWidgetProps {
  userId: string;
  userName: string;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ userId, userName }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [showWidget, setShowWidget] = useState<boolean>(true);
  const [chatContext, setChatContext] = useState("Onboarding");

  const getMessages = async () => {
    const resp = await fetch(`http://localhost:8000/api/users/${userId}/chats/${chatContext}/messages`);
    if (resp?.status === 200) {
      const jsonData = await resp.json();
      setMessages(jsonData.messages);
    }
  };

  useEffect(() => {
    getMessages();
  }, [chatContext]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = { line_type: 'user', content: input };
    try {
      const response = await fetch(`http://localhost:8000/api/users/${userId}/chats/${chatContext}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newMessage),
      });

      const data = await response.json();
      setMessages((prevMessages) => [...prevMessages, ...data.messages]);
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  if (!showWidget) return <button onClick={() => setShowWidget(true)} className={styles.openButton}>Open Chat</button>;

  return (
    <div className={styles.chatWidget}>
      <div className={styles.chatHeader}>
        <button className={styles.expandButton}>↔</button>
        <button className={styles.closeButton} onClick={() => setShowWidget(false)}>×</button>
      </div>
      <div className={styles.avatarSection}>
        <img src="/static/icons/avatar.png" alt="Ava" className={styles.avatar} />
        <h3>Hey👋, I'm Ava</h3>
        <p>Ask me anything or pick a place to start</p>
      </div>
      <div className={styles.chatBody}>
        {messages.map((message: Message, idx) => (
          <div key={idx} className={styles[`${message.line_type}Message`]}>
            {message.line_type === 'system' && (
              <img src="/api/placeholder/30/30" alt="Ava" className={styles.messageAvatar} />
            )}
            <p>{message.content}</p>
          </div>
        ))}
      </div>
      {messages.length > 0 && (
        <div className={styles.actionButtons}>
          <button className={styles.actionButton}>Create Report this month</button>
          <button className={styles.actionButton}>Call Lead</button>
        </div>
      )}
      <div className={styles.chatFooter}>
        <select 
          value={chatContext} 
          onChange={(e) => setChatContext(e.target.value)}
          className={styles.contextSelector}
        >
          <option value="Onboarding">Onboarding</option>
          <option value="Sales">Sales</option>
        </select>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Your question"
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className={styles.input}
        />
      </div>
    </div>
  );
};

export default ChatWidget;
