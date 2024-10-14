'use client'
import React from 'react';
import ChatboxWithAuth from "./components/ChatbotWithAuth";

const Home: React.FC = () => {
  const handleLogout = () => {
    window.location.href = "http://localhost:8000/logout"
    return
  }

  return (
    <div>
      <h1>Welcome to the Homepage</h1>
      <button onClick={() => (handleLogout())}>Logout</button>
      <ChatboxWithAuth />  {/* This will display the chatbox if the user is logged in */}
    </div>
  );
};

export default Home;