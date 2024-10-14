'use client';
import React, { useState, useEffect } from 'react';
import styles from '../css/ChatWidget.module.css';

type Messages = {
    messages: Message[]
}

type Message = {
  type: 'user' | 'bot';
  text: string;
};

interface ChatWidgetProps {
    userId: string;  // Expect userId to be a string
  }

  const ChatWidget: React.FC<ChatWidgetProps> = ({ userId }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState<string>(''); 
  const [showWidget, setShowWidget] = useState<boolean>(true); 

  useEffect(() => {
    fetch(`http://localhost:8000/api/users/${userId}/messages`)
      .then((res) => res.json())
      .then((data: any) => {
        debugger
        setMessages(data.messages);
      });
  }, []);

  
  const sendMessage = async () => {
    const newMessage: Message = { type: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, newMessage]);

    try {
      
      const response = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();
      const botMessage: Message = { type: 'bot', text: data.reply };

      setMessages((prevMessages) => [...prevMessages, botMessage]);
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  if (!showWidget) return <button onClick={() => setShowWidget(true)}>Open Chat</button>;

  return (
    <div className={styles.chatWidget}>
      <div className={styles.chatHeader}>
        <h3>Hi, I'm Ava</h3>
        <button onClick={() => setShowWidget(false)}>Close</button>
      </div>
      <div className={styles.chatBody}>
        {messages.map((message, idx) => (
          <div key={idx} className={styles[message.type]}>
            <p>{message.text}</p>
          </div>
        ))}
      </div>
      <div className={styles.chatFooter}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatWidget;
