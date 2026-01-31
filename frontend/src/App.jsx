import { useState, useRef, useEffect } from 'react'
import './App.css'

const TOOLS = [
  { id: 'chat', name: 'Chat with CYNO', icon: '💬' },
  { id: 'resume', name: 'Resume Parser', icon: '📄' },
  { id: 'cover', name: 'Cover Letter', icon: '✉️' },
  { id: 'salary', name: 'Salary Estimator', icon: '💰' },
  { id: 'interview', name: 'Interview Prep', icon: '🎯' },
  { id: 'jobs', name: 'Job Search', icon: '🔍' },
  { id: 'email', name: 'Email Drafter', icon: '📧' },
  { id: 'fit', name: 'Job Fit Score', icon: '📊' },
]

const QUICK_ACTIONS = [
  'Find remote Python jobs',
  'Analyze my resume',
  'Generate cover letter',
  'Estimate salary for ML Engineer',
  'Prepare for Google interview',
]

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: `Welcome to CYNO! 🤖\n\nI'm your AI-powered job search assistant. I can help you with:\n\n• Finding and filtering jobs\n• Parsing and analyzing resumes\n• Generating cover letters\n• Preparing for interviews\n• Estimating salaries\n\nHow can I assist you today?`
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [activeTool, setActiveTool] = useState('chat')
  const [isConnected, setIsConnected] = useState(true)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response || data.message || 'I processed your request.'
        }])
      } else {
        throw new Error('API error')
      }
    } catch (error) {
      // Demo response when backend is not running
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'ai',
          content: getDemoResponse(input)
        }])
      }, 1000)
    }

    setIsTyping(false)
  }

  const getDemoResponse = (query) => {
    const q = query.toLowerCase()
    if (q.includes('job') || q.includes('find')) {
      return `🔍 **Job Search Results**\n\nI found several opportunities matching your criteria:\n\n1. **Senior Python Developer** - Google (Remote)\n   💰 $180,000 - $250,000\n\n2. **ML Engineer** - OpenAI (San Francisco)\n   💰 $200,000 - $300,000\n\n3. **Backend Developer** - Stripe (Remote)\n   💰 $150,000 - $200,000\n\nWould you like me to analyze any of these positions?`
    }
    if (q.includes('resume') || q.includes('parse')) {
      return `📄 **Resume Analysis**\n\nTo analyze your resume, please:\n\n1. Upload your resume file, or\n2. Paste the resume text here\n\nI'll extract skills, experience, and provide optimization suggestions.`
    }
    if (q.includes('salary') || q.includes('pay')) {
      return `💰 **Salary Estimate**\n\nBased on market data for **Python Developer** roles:\n\n• **Junior (0-2 yrs)**: $70,000 - $95,000\n• **Mid-level (2-5 yrs)**: $95,000 - $140,000\n• **Senior (5+ yrs)**: $140,000 - $200,000\n• **Principal/Staff**: $180,000 - $300,000\n\nFactors: Location, company size, and specialization significantly impact these ranges.`
    }
    if (q.includes('interview') || q.includes('prepare')) {
      return `🎯 **Interview Preparation**\n\nI can help you prepare with:\n\n• **Behavioral Questions** - STAR format answers\n• **Technical Questions** - Based on your skills\n• **System Design** - Architecture challenges\n• **Project Deep-Dive** - Explain your work\n\nWhich area would you like to focus on?`
    }
    if (q.includes('cover') || q.includes('letter')) {
      return `✉️ **Cover Letter Generator**\n\nTo create a personalized cover letter, I'll need:\n\n1. **Job Title**: The position you're applying for\n2. **Company**: Target company name\n3. **Your Skills**: Key skills to highlight\n\nOr just paste the job description and I'll craft it for you!`
    }
    return `I understand you're asking about "${query}". \n\nHere's what I can help with:\n\n• 🔍 Job Search & Filtering\n• 📄 Resume Parsing & Analysis\n• ✉️ Cover Letter Generation\n• 💰 Salary Estimation\n• 🎯 Interview Preparation\n• 📧 Email Drafting\n\nCould you be more specific about what you need?`
  }

  const handleQuickAction = (action) => {
    setInput(action)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <>
      <div className="animated-bg"></div>
      <div className="app">
        {/* Header */}
        <header className="header">
          <div className="logo">
            <div className="logo-icon">C</div>
            <div className="logo-text">
              <h1>CYNO</h1>
              <span>AI JOB AGENT • PROTOTYPE</span>
            </div>
          </div>
          <div className="status-badge">
            <div className={`status-dot ${isConnected ? '' : 'offline'}`}></div>
            <span>{isConnected ? 'Cloud Brain Online' : 'Offline Mode'}</span>
          </div>
        </header>

        {/* Main Content */}
        <main className="main-content">
          {/* Sidebar */}
          <aside className="sidebar">
            <h3 className="sidebar-title">Tools</h3>
            <div className="tool-list">
              {TOOLS.map(tool => (
                <div
                  key={tool.id}
                  className={`tool-item ${activeTool === tool.id ? 'active' : ''}`}
                  onClick={() => setActiveTool(tool.id)}
                >
                  <span className="tool-icon">{tool.icon}</span>
                  <span className="tool-name">{tool.name}</span>
                </div>
              ))}
            </div>
          </aside>

          {/* Chat Area */}
          <section className="chat-area">
            <div className="chat-messages">
              {messages.map(msg => (
                <div key={msg.id} className={`message ${msg.type}`}>
                  <div className="message-avatar">
                    {msg.type === 'ai' ? 'C' : '👤'}
                  </div>
                  <div className="message-content">
                    {msg.content.split('\n').map((line, i) => (
                      <span key={i}>
                        {line}
                        <br />
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="message ai">
                  <div className="message-avatar">C</div>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="input-area">
              <div className="input-container">
                <div className="input-wrapper">
                  <input
                    type="text"
                    className="chat-input"
                    placeholder="Ask CYNO anything about jobs, resumes, interviews..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                </div>
                <button className="send-btn" onClick={sendMessage}>
                  →
                </button>
              </div>
              <div className="quick-actions">
                {QUICK_ACTIONS.map((action, i) => (
                  <button
                    key={i}
                    className="quick-action"
                    onClick={() => handleQuickAction(action)}
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
          </section>
        </main>
      </div>
    </>
  )
}

export default App
