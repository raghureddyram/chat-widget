'use client';
import React, { useState, useEffect } from 'react';
import styles from '../css/ChatWidget.module.css';

type Messages = {
    messages: Message[]
}

type Message = {
  id?: string;
  line_type: 'user' | 'system';
  content: string;
  created_date?: string;
};

interface ChatWidgetProps {
    userId: string;
  }

  const ChatWidget: React.FC<ChatWidgetProps> = ({ userId }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState<string>(''); 
  const [showWidget, setShowWidget] = useState<boolean>(true); 
  const [chatContext, setChatContext] = useState("Onboarding");


  const getMessages = async () => {
    const resp = await fetch(`http://localhost:8000/api/users/${userId}/chats/${chatContext}/messages`)
    if(resp?.status === 200){
        const jsonData = await resp.json();
        setMessages(jsonData.messages)
        
    }
  }

  useEffect(() => {
    getMessages()
  }, []);

  useEffect(() => {
    getMessages()
  }, [chatContext]);


  
  const sendMessage = async () => {
    const newMessage: Message = { line_type: 'user', content: input };
    setMessages((prevMessages) => [...prevMessages, newMessage]);

    try {
      
      const response = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();
      const botMessage: Message = { line_type: 'system', content: data.reply };

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
        {messages.map((message: Message, idx) => (
          <div key={idx} className={styles[`${message.line_type}-message`]}>
            <p>{message.content}</p>
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
