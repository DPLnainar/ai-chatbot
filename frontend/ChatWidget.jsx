/**
 * ChatWidget for Full Backend (port 8000)
 * Integrates with main.py including session management, analytics, and suggested actions
 */
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatWidget.css';

const ChatWidget = ({ studentProfile }) => { 
  // studentProfile: { student_id: "CS2021001", name: "Rahul", dept: "CSE", cgpa: 7.5, skills: "Python, Java", year: 3 }
  
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [domain, setDomain] = useState(null);
  const [suggestedActions, setSuggestedActions] = useState([]);
  const chatBodyRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const sendMessage = async (messageText = input) => {
    if (!messageText.trim()) return;

    // 1. Add User Message to UI
    const userMessage = { sender: "user", text: messageText };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // 2. Send to Full Backend with Complete Context
      const response = await axios.post("http://localhost:8000/api/chat", {
        message: messageText,
        session_id: sessionId, // null for first message, then reused
        user_context: {
          student_id: studentProfile.student_id,
          name: studentProfile.name,
          department: studentProfile.dept,
          cgpa: studentProfile.cgpa,
          skills: studentProfile.skills,
          year: studentProfile.year,
          arrears_count: studentProfile.arrears_count || 0
        }
      });

      // 3. Update session and domain
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }
      setDomain(response.data.domain);
      setSuggestedActions(response.data.suggested_actions || []);

      // 4. Add Bot Response to UI
      const botMessage = { 
        sender: "bot", 
        text: response.data.response,
        sources: response.data.sources
      };
      setMessages(prev => [...prev, botMessage]);
      
    } catch (error) {
      console.error("Error talking to bot:", error);
      const errorMessage = { 
        sender: "bot", 
        text: "Sorry, I'm having trouble connecting. Please check if the server is running on port 8000." 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedAction = (action) => {
    sendMessage(action);
  };

  return (
    <div className="chat-widget-container">
      {/* Floating Button */}
      {!isOpen && (
        <button className="chat-bubble-btn" onClick={() => setIsOpen(true)}>
          💬 Career Help
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="header-content">
              <h4>🎓 Career Companion</h4>
              <div className="student-info">
                {studentProfile.name} • {studentProfile.dept} • CGPA {studentProfile.cgpa}
              </div>
              {domain && (
                <span className="domain-badge">{domain.replace('_', ' ').toUpperCase()}</span>
              )}
            </div>
            <button className="close-btn" onClick={() => setIsOpen(false)}>✖</button>
          </div>
          
          <div className="chat-body" ref={chatBodyRef}>
            {messages.length === 0 && (
              <div className="welcome-message">
                <h3>👋 Welcome, {studentProfile.name}!</h3>
                <p>I'm your AI Placement Officer. I can help you with:</p>
                <div className="welcome-options">
                  <button onClick={() => sendMessage("I want to prepare for mock interviews")}>
                    🎯 Mock Interviews
                  </button>
                  <button onClick={() => sendMessage("Can you review my resume?")}>
                    📄 Resume Review
                  </button>
                  <button onClick={() => sendMessage("What skills should I focus on?")}>
                    💡 Skill Guidance
                  </button>
                  <button onClick={() => sendMessage("I'm confused about my career path")}>
                    🧭 Career Planning
                  </button>
                </div>
              </div>
            )}
            
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                <div className="message-content">
                  {msg.text}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="message-sources">
                      <small>📚 Sources: {msg.sources.join(', ')}</small>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message bot">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          {/* Suggested Actions */}
          {suggestedActions.length > 0 && !loading && (
            <div className="suggested-actions">
              <small>💡 Try asking:</small>
              <div className="action-chips">
                {suggestedActions.slice(0, 3).map((action, index) => (
                  <button 
                    key={index} 
                    className="action-chip"
                    onClick={() => handleSuggestedAction(action)}
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="chat-input-area">
            <input 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
              placeholder="Ask about placements, skills, interviews..."
              disabled={loading}
            />
            <button onClick={() => sendMessage()} disabled={loading || !input.trim()}>
              {loading ? '⏳' : '📤'}
            </button>
          </div>
          
          <div className="chat-footer">
            <small>Session: {sessionId ? sessionId.substring(0, 8) : 'Starting...'}</small>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
