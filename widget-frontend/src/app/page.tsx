import React from 'react';
import ChatboxWithAuth from "./components/ChatbotWithAuth";

const Home: React.FC = () => {
  return (
    <div>
      <h1>Welcome to the Homepage</h1>
      <ChatboxWithAuth />  {/* This will display the chatbox if the user is logged in */}
    </div>
  );
};

export default Home;