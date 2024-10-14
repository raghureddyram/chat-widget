'use client'
import React, { useState } from 'react';

const Chatbox: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChatbox = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div>
      <button onClick={toggleChatbox}>Chat with us!</button>
      {isOpen && (
        <div className="chatbox-modal">
          <div className="chatbox-header">
            <h2>Chatbox</h2>
            <button onClick={toggleChatbox}>Close</button>
          </div>
          <div className="chatbox-body">
            <p>Start chatting here...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbox;