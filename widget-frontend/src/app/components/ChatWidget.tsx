'use client'
import React, { useState, useEffect } from 'react';
import styles from '../css/ChatWidget.module.css'; // Importing CSS Module
import Link from 'next/link';

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
  const [isEdit, setIsEdit] = useState(false);
  const defaultMessage: Message = { line_type: 'user', content: input };
  const [newMessage, setNewMessage] = useState<Message>(defaultMessage);
  const [expanded, setExpanded] = useState(false)

  const getMessages = async () => {
    const resp = await fetch(`http://localhost:8000/api/users/${userId}/chats/${chatContext}/messages`);
    if (resp?.status === 200) {
      const jsonData = await resp.json();
      setMessages(jsonData.messages);
    }
  };

  const handleDeleteMessage = async (messageId: string) => {
    try{
        await fetch(`http://localhost:8000/api/users/${userId}/chats/${chatContext}/messages/${messageId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        await getMessages()
    } catch(e){
        console.log(e)
    }
  };

  const editMessage = async (message: Message) => {
    setIsEdit(true)
    setNewMessage(message)
    setInput(message.content)
  }

  const handleEdit = async (message: Message) => {
    const messageId = message.id;
    try{
        await fetch(`http://localhost:8000/api/users/${userId}/chats/${chatContext}/messages/${messageId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(message)
        });
        setIsEdit(false)
        setInput('')
        setNewMessage(defaultMessage)
        await getMessages()
    } catch(e){
        console.log(e)
    }
  };

  const handleSetInput = (newData: string) => {
    setInput(newData)
    if(isEdit){
        const newMessageWithInput = { 
            ...newMessage, 
            content: newData 
        }
        setNewMessage(newMessageWithInput)
    }
  }

  useEffect(() => {
    getMessages();
  }, [chatContext]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    if(isEdit){
        return handleEdit(newMessage)
    }

    const message = { ...newMessage, content: input}
    setMessages([...messages, message])
    setInput('')
    try {
      await fetch(`http://localhost:8000/api/users/${userId}/chats/${chatContext}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message),
      });
      await getMessages()
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleCreateReport = () => {
    setIsEdit(false)
    setInput("Create a csv report of MSFT yearly revenue for 2 years")
  }

  if (!showWidget) return <button onClick={() => setShowWidget(true)} className={styles.openButton}>Open Chat</button>;

  const createHtmlByContent = (content: string) => {
    const parts = content.split("link: ")
    if(parts.length > 1){
        return (<p>Finished. I have <Link className={styles.generatedDoc} href={`${parts[parts.length - 1]}`}>generated your document</Link></p>)
    }
    
    return (<p>{content}</p>)
  }
  return (
    <div className={styles[`chatWidget${expanded ? 'Expanded' : ''}`]} >
      <div className={styles.chatHeader}>
        <button className={styles.expandButton} onClick={() => setExpanded(!expanded)}>↔</button>
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
            {createHtmlByContent(message.content)}
            {message.line_type === 'user' && (
                <span>
                <button 
                  className={styles.deleteButton} 
                  onClick={() => handleDeleteMessage(message.id as string)}
                  aria-label="Delete message"
                >X</button>
                <button 
                  className={styles.deleteButton} 
                  onClick={() => editMessage(message)}
                  aria-label="Edit message"
                >edit</button>
                </span>
              )}
          </div>
        ))}
      </div>
      {messages.length > 0 && (
        <div className={styles.actionButtons}>
          <button className={styles.actionButton} onClick={() => {handleCreateReport()} }>Create Report this month</button>
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
          onChange={(e) => handleSetInput(e.target.value)}
          placeholder="Your question"
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className={styles.input}
        />
        <button onClick={() => sendMessage()} className="sendButton">{'>'}</button>
      </div>
    </div>
  );
};

export default ChatWidget;
