import { useState, useRef, useEffect } from 'react'
import './App.css'

const TOOLS = [
  { id: 'chat', name: 'Chat with CYNO', icon: '💬' },
  { id: 'resume', name: 'Resume Analysis', icon: '📄' },
  { id: 'cover', name: 'Cover Letter', icon: '✉️' },
  { id: 'salary', name: 'Salary Advisor', icon: '💰' },
  { id: 'interview', name: 'Interview Prep', icon: '🎯' },
  { id: 'jobs', name: 'Job Strategy', icon: '🔍' },
  { id: 'email', name: 'Email Drafter', icon: '📧' },
  { id: 'fit', name: 'Career Strategy', icon: '📊' },
]

const QUICK_ACTIONS = [
  'Analyze my resume',
  'Find Python jobs',
  "What's my market value?",
  'Prepare for interviews',
  'Help with cover letter',
]

// Professional welcome message
const WELCOME_MESSAGE = `Welcome! I'm CYNO, your AI Career Strategist.

I'm here to be the career advisor everyone deserves but few have access to. Whether you're exploring new opportunities, preparing for interviews, or looking to maximize your market value, I'm here to help.

**A few things I can help you with:**
• **Career Strategy** — Let's understand where you are and where you want to go
• **Resume Optimization** — I'll analyze your background and help you tell your story effectively
• **Job Matching** — Find opportunities that truly align with your strengths
• **Interview Preparation** — Walk in prepared and confident
• **Salary Negotiation** — Know your worth and how to communicate it

What would you like to explore first?`

function App() {
  const [messages, setMessages] = useState([
    { id: 1, type: 'ai', content: WELCOME_MESSAGE }
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

  // Check API connection on mount
  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setIsConnected(data.api === 'healthy'))
      .catch(() => setIsConnected(false))
  }, [])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { id: Date.now(), type: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    const userInput = input
    setInput('')
    setIsTyping(true)

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response || 'I processed your request.'
        }])
        setIsTyping(false)
        return
      }
    } catch (error) {
      console.log('API not available, using demo mode')
    }

    // Professional demo responses when API is not available
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'ai',
        content: getProfessionalResponse(userInput)
      }])
      setIsTyping(false)
    }, 1200)
  }

  const getProfessionalResponse = (query) => {
    const q = query.toLowerCase()

    // Resume detection - check if it looks like resume content
    const resumeIndicators = ['experience', 'education', 'skills', 'python', 'developer', 'engineer', 'bachelor', 'university', 'responsibilities', 'achievements']
    const matchCount = resumeIndicators.filter(word => q.includes(word)).length

    if (matchCount >= 3 && query.length > 200) {
      // User appears to have pasted a resume
      return `I've carefully reviewed your background, and I can see you have a compelling professional story.

**What stands out to me:**
Based on your experience, you excel at **technical problem-solving and building impactful solutions**. This combination is particularly valuable in today's market.

**Your career trajectory:**
You're at an interesting point in your career where strategic moves can have significant impact. I see patterns that suggest you thrive in environments that challenge you technically while offering growth.

**Key observations:**
• Your technical foundation is solid—this opens doors to multiple paths
• I notice you have experience that many candidates lack at this stage
• There's an opportunity to better highlight your unique value proposition

**My recommendations:**
1. **Quantify your achievements** — "Improved performance by 40%" tells a stronger story than "Improved performance"
2. **Lead with your differentiators** — What makes you uniquely qualified, not just qualified
3. **Tell a narrative** — Your projects should show a trajectory of growth and increasing impact

Would you like me to:
• Find job opportunities that match your strengths?
• Help you craft a more compelling resume narrative?
• Prepare you for interviews at specific companies?`
    }

    if (q.includes('resume') || q.includes('analyze') || q.includes('cv')) {
      return `I'd be happy to analyze your resume and provide strategic insights.

**Here's what I'll look for:**
• **Core strengths** — What makes you uniquely valuable
• **Career trajectory** — Patterns that work in your favor
• **Optimization opportunities** — Ways to strengthen your positioning

Simply paste your resume content, and I'll give you actionable feedback that goes beyond the obvious.

*Pro tip: Include your full work history and skills section for the most comprehensive analysis.*`
    }

    if (q.includes('job') || q.includes('find') || q.includes('search') || q.includes('opportunity')) {
      return `I'd like to help you find the right opportunities—not just any opportunities.

**A few strategic questions:**
1. What type of work genuinely energizes you?
2. Are you optimizing for growth, compensation, work-life balance, or something else?
3. Any specific companies or industries you're drawn to?

**Current market insight:**
Roles in Python development, ML/AI, and cloud infrastructure are seeing particularly strong demand. Remote opportunities remain robust, though some companies are adjusting expectations.

**My approach:**
Rather than overwhelming you with listings, I prefer to identify 3-5 opportunities that genuinely align with your goals and have a realistic path to success.

Share a bit about what you're looking for—or share your resume and I'll suggest roles that match your actual strengths.`
    }

    if (q.includes('salary') || q.includes('pay') || q.includes('worth') || q.includes('compensation')) {
      return `Let me give you the real picture on compensation.

**Current Market Ranges (US):**

| Level | Range | Notes |
|-------|-------|-------|
| Entry (0-2 yrs) | $70K - $95K | Focus on learning & growth |
| Mid (3-5 yrs) | $110K - $160K | Peak negotiation leverage |
| Senior (5-8 yrs) | $150K - $220K | Expertise premium |
| Staff+ (8+ yrs) | $200K - $350K+ | Strategic value |

**Key factors that move the needle:**
• **Company stage** — Big Tech pays 20-40% more than average
• **Specialization** — ML, Cloud, Security command premiums
• **Negotiation** — Most people leave 10-20% on the table
• **Location** — Even for remote, some companies pay by location

**My honest take:**
These ranges are starting points. Your specific background, the company's financial situation, and how the interview process went all factor in.

Would you like help understanding where you specifically should be targeting?`
    }

    if (q.includes('interview') || q.includes('prepare') || q.includes('question')) {
      return `Let's make sure you walk into that interview with confidence.

**My preparation framework:**

**1. Know the Role**
Beyond the job description—what problem are they really trying to solve? What does success look like in 6 months?

**2. Map Your Story**
Not just what you did, but the impact and what you learned. Use the STAR format, but make it conversational.

**3. Prepare Strategic Stories**
Have 5-6 solid examples ready that demonstrate:
• Technical problem-solving
• Collaboration and influence
• Handling ambiguity or failure
• Growth and learning

**4. Address Concerns Proactively**
If there are gaps or transitions in your background, prepare a confident, honest explanation.

**What company or role are you preparing for?**
I'll tailor specific questions and talking points for that context.`
    }

    if (q.includes('cover') || q.includes('letter') || q.includes('application')) {
      return `Cover letters are about connection, not repetition.

The best ones answer three questions:
1. **Why this company?** — What genuinely draws you to them
2. **Why this role?** — How it fits your trajectory  
3. **Why you?** — What unique value you bring

**To get started, I'll need:**
• The role and company you're applying to
• The job description (or key requirements)
• What genuinely interests you about this opportunity

With that context, I'll help you craft something that makes hiring managers want to meet you.

*Pro tip: Skip the generic opener. Start with something that shows you've done your homework.*`
    }

    if (q.includes('linkedin') || q.includes('profile') || q.includes('network')) {
      return `Your LinkedIn profile is your professional storefront—let's make it work for you.

**Key areas to optimize:**

**Headline** — Don't just say your title. Say what you do and for whom.
*Instead of:* "Software Engineer at Company"
*Try:* "Python Developer | Building ML Systems That Scale"

**About Section** — Tell your story. Why do you do what you do? What drives you?

**Experience** — Focus on impact, not responsibilities. Numbers speak louder.

**Skills & Endorsements** — List what you want to be known for, not everything you've touched.

Would you like me to help you craft specific sections?`
    }

    // Default professional response
    return `I appreciate you reaching out. To give you the most relevant guidance, could you tell me more about what you're looking to accomplish?

**I'm here to help with:**
• **Career Strategy** — Understanding your goals and mapping a path forward
• **Resume Analysis** — Identifying your strengths and how to present them
• **Job Search** — Finding opportunities that truly fit your profile
• **Interview Prep** — Walking in confident and prepared
• **Salary Negotiation** — Understanding your market value

What's top of mind for you right now?`
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

  // Parse markdown-like formatting
  const formatMessage = (content) => {
    return content.split('\n').map((line, i) => {
      // Bold text
      line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      // Italic text
      line = line.replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Headers
      if (line.startsWith('### ')) line = `<h4>${line.slice(4)}</h4>`
      else if (line.startsWith('## ')) line = `<h3>${line.slice(3)}</h3>`

      return <span key={i} dangerouslySetInnerHTML={{ __html: line || '<br/>' }} />
    })
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
              <span>AI CAREER STRATEGIST</span>
            </div>
          </div>
          <div className="status-badge">
            <div className={`status-dot ${isConnected ? '' : 'offline'}`}></div>
            <span>{isConnected ? 'Cloud Brain Online' : 'Demo Mode'}</span>
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
                    {formatMessage(msg.content)}
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
                  <textarea
                    className="chat-input"
                    placeholder="Share your career goals, paste your resume, or ask for guidance..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    rows={1}
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
