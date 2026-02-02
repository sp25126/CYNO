import { useState, useRef, useEffect } from 'react'
import './App.css'
import './Settings.css'
import Settings from './Settings'

// ========================================
// CYNO COMMANDS SYSTEM
// ========================================
const COMMANDS = {
  '/help': {
    description: 'Show all available commands',
    usage: '/help',
    category: 'general'
  },
  '/resume': {
    description: 'Analyze your resume and get strategic insights',
    usage: '/resume [paste your resume text]',
    category: 'tools'
  },
  '/jobs': {
    description: 'Search for jobs matching your criteria',
    usage: '/jobs [job title] [location]',
    example: '/jobs Python Developer Remote',
    category: 'tools'
  },
  '/salary': {
    description: 'Get salary estimates for a role',
    usage: '/salary [job title] [location] [experience]',
    example: '/salary ML Engineer San Francisco Senior',
    category: 'tools'
  },
  '/cover': {
    description: 'Generate a cover letter',
    usage: '/cover [company] [job title]',
    example: '/cover Google Senior Developer',
    category: 'tools'
  },
  '/interview': {
    description: 'Prepare for interviews with practice questions',
    usage: '/interview [company] [role]',
    example: '/interview Meta Frontend Engineer',
    category: 'tools'
  },
  '/email': {
    description: 'Draft professional emails',
    usage: '/email [type: followup|application|networking]',
    example: '/email followup',
    category: 'tools'
  },
  '/fit': {
    description: 'Score how well you match a job',
    usage: '/fit [paste job description]',
    category: 'tools'
  },
  '/settings': {
    description: 'Open settings panel',
    usage: '/settings',
    category: 'general'
  },
  '/clear': {
    description: 'Clear chat history',
    usage: '/clear',
    category: 'general'
  }
}

// Tool sidebar items
const TOOLS = [
  { id: 'chat', name: 'Chat with CYNO', icon: '💬', command: '' },
  { id: 'resume', name: 'Resume Analysis', icon: '📄', command: '/resume' },
  { id: 'jobs', name: 'Job Search', icon: '🔍', command: '/jobs' },
  { id: 'cover', name: 'Cover Letter', icon: '✉️', command: '/cover' },
  { id: 'salary', name: 'Salary Advisor', icon: '💰', command: '/salary' },
  { id: 'interview', name: 'Interview Prep', icon: '🎯', command: '/interview' },
  { id: 'email', name: 'Email Drafter', icon: '📧', command: '/email' },
  { id: 'fit', name: 'Job Fit Score', icon: '📊', command: '/fit' },
]

const QUICK_ACTIONS = [
  { text: 'Show commands', action: '/help' },
  { text: 'Analyze resume', action: '/resume' },
  { text: 'Find Python jobs', action: '/jobs Python Developer Remote' },
  { text: 'Salary estimate', action: '/salary Software Engineer Remote Mid' },
  { text: 'Interview prep', action: '/interview' },
]

// API base URL
const API_URL = 'http://localhost:8000'

// Welcome message
const WELCOME_MESSAGE = `Welcome! I'm **CYNO**, your AI Career Strategist.

I'm here to be the career advisor everyone deserves but few have access to.

**Quick Start:**
• Type \`/help\` to see all available commands
• Or just chat naturally and I'll understand what you need

**What I can help with:**
• 📄 **Resume Analysis** — \`/resume\`
• 🔍 **Job Search** — \`/jobs\`
• ✉️ **Cover Letters** — \`/cover\`
• 💰 **Salary Estimates** — \`/salary\`
• 🎯 **Interview Prep** — \`/interview\`
• 📧 **Email Drafting** — \`/email\`

What would you like to explore first?`

function App() {
  const [messages, setMessages] = useState([
    { id: 1, type: 'ai', content: WELCOME_MESSAGE }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [activeTool, setActiveTool] = useState('chat')
  const [isConnected, setIsConnected] = useState(false)
  const [gpuMode, setGpuMode] = useState('cloud')
  const [showSettings, setShowSettings] = useState(false)
  const [showCommands, setShowCommands] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Check API connection on mount
  useEffect(() => {
    checkConnection()
    // Load saved settings
    loadSettings()
  }, [])

  const checkConnection = async () => {
    try {
      const response = await fetch(`${API_URL}/health`)
      const data = await response.json()
      setIsConnected(data.api === 'healthy')
    } catch {
      setIsConnected(false)
    }
  }

  const loadSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/settings`)
      const data = await response.json()
      if (data.mode) setGpuMode(data.mode)
    } catch {
      // Use defaults
    }
  }

  // Handle command autocomplete
  const handleInputChange = (e) => {
    const value = e.target.value
    setInput(value)

    // Show command suggestions when typing /
    if (value.startsWith('/') && value.length > 0) {
      setShowCommands(true)
    } else {
      setShowCommands(false)
    }
  }

  const handleCommandSelect = (cmd) => {
    setInput(cmd + ' ')
    setShowCommands(false)
    inputRef.current?.focus()
  }

  // Filter commands based on input
  const getFilteredCommands = () => {
    const search = input.toLowerCase()
    return Object.entries(COMMANDS).filter(([cmd]) =>
      cmd.toLowerCase().startsWith(search)
    )
  }

  // Process message
  const sendMessage = async () => {
    const trimmedInput = input.trim()
    if (!trimmedInput) return

    const userMessage = { id: Date.now(), type: 'user', content: trimmedInput }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setShowCommands(false)
    setIsTyping(true)

    try {
      // Handle commands
      if (trimmedInput.startsWith('/')) {
        const response = await handleCommand(trimmedInput)
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'ai',
          content: response
        }])
        setIsTyping(false)
        return
      }

      // Regular chat message
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmedInput })
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response || 'I processed your request.'
        }])
      } else {
        throw new Error('API error')
      }
    } catch (error) {
      // Fallback to demo response
      const demoResponse = getDemoResponse(trimmedInput)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'ai',
        content: demoResponse
      }])
    }
    setIsTyping(false)
  }

  // Command handler
  const handleCommand = async (input) => {
    const parts = input.split(' ')
    const command = parts[0].toLowerCase()
    const args = parts.slice(1).join(' ')

    switch (command) {
      case '/help':
        return formatHelpMessage()

      case '/clear':
        setMessages([{ id: Date.now(), type: 'ai', content: 'Chat cleared. How can I help you?' }])
        return null

      case '/settings':
        setShowSettings(true)
        return '⚙️ Opening settings panel...'

      case '/resume':
        if (!args) {
          return `📄 **Resume Analysis**

To analyze your resume, please paste your resume text after the command:

\`/resume [Your resume text here]\`

Or simply paste your resume in the next message and I'll detect it automatically.

**What I'll analyze:**
• Core strengths and skills
• Career trajectory patterns
• Optimization opportunities
• Job-matching insights`
        }
        return await analyzeResume(args)

      case '/jobs':
        return await searchJobs(args)

      case '/salary':
        return await estimateSalary(args)

      case '/cover':
        if (!args) {
          return `✉️ **Cover Letter Generator**

Usage: \`/cover [Company] [Job Title]\`

Example: \`/cover Google Senior Software Engineer\`

I'll create a personalized, compelling cover letter that highlights your fit for the role.`
        }
        return await generateCoverLetter(args)

      case '/interview':
        return await prepareInterview(args)

      case '/email':
        return await draftEmail(args)

      case '/fit':
        if (!args) {
          return `📊 **Job Fit Score**

Usage: \`/fit [paste job description]\`

I'll analyze how well your profile matches the role and provide:
• Match percentage
• Strength alignment
• Gap analysis
• Positioning advice`
        }
        return await scoreJobFit(args)

      default:
        return `❓ Unknown command: \`${command}\`

Type \`/help\` to see all available commands.`
    }
  }

  // Format help message
  const formatHelpMessage = () => {
    let help = `## 📖 CYNO Commands\n\n`

    help += `### 🔧 Tools\n`
    Object.entries(COMMANDS)
      .filter(([, cmd]) => cmd.category === 'tools')
      .forEach(([name, cmd]) => {
        help += `**\`${name}\`** — ${cmd.description}\n`
        if (cmd.example) help += `   Example: \`${cmd.example}\`\n`
      })

    help += `\n### ⚙️ General\n`
    Object.entries(COMMANDS)
      .filter(([, cmd]) => cmd.category === 'general')
      .forEach(([name, cmd]) => {
        help += `**\`${name}\`** — ${cmd.description}\n`
      })

    help += `\n---\n*Tip: You can also just chat naturally—I'll understand what you need!*`
    return help
  }

  // ========================================
  // TOOL IMPLEMENTATIONS
  // ========================================

  const analyzeResume = async (resumeText) => {
    try {
      const response = await fetch(`${API_URL}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resumeText })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.data) {
          const parsed = data.data
          return `📄 **Resume Analysis Complete**

**Profile Summary:**
${parsed.name ? `• Name: ${parsed.name}` : ''}
${parsed.email ? `• Email: ${parsed.email}` : ''}
${parsed.experience_years ? `• Experience: ${parsed.experience_years} years` : ''}

**Skills Detected:**
${(parsed.skills || []).slice(0, 10).map(s => `• ${s}`).join('\n') || '• Unable to extract skills'}

**Insights:**
${data.insights?.core_strength ? `• Core Strength: ${data.insights.core_strength}` : ''}
${data.insights?.career_pattern ? `• Career Pattern: ${data.insights.career_pattern}` : ''}

**Next Steps:**
Would you like me to:
• \`/jobs\` - Find matching opportunities
• \`/cover\` - Generate a cover letter
• \`/interview\` - Prepare for interviews`
        }
      }
    } catch (error) {
      console.log('Resume API error:', error)
    }

    // Demo response
    return `📄 **Resume Analysis** (Demo Mode)

I've analyzed your background and here's what stands out:

**Core Strengths:**
• Technical problem-solving
• Building scalable solutions
• Cross-functional collaboration

**Recommendations:**
1. Quantify your achievements with metrics
2. Highlight your unique differentiators
3. Tailor for each application

*Connect to Cloud Brain for full AI-powered analysis.*`
  }

  const searchJobs = async (query) => {
    if (!query) {
      return `🔍 **Job Search**

Usage: \`/jobs [job title] [location]\`

Examples:
• \`/jobs Python Developer Remote\`
• \`/jobs ML Engineer San Francisco\`
• \`/jobs Frontend Developer NYC\`

I'll search multiple job boards and return the best matches.`
    }

    try {
      const response = await fetch(`${API_URL}/jobs/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, location: 'Remote' })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.jobs && data.jobs.length > 0) {
          let result = `🔍 **Job Search Results**\n\nFound ${data.jobs.length} matching opportunities:\n\n`
          data.jobs.slice(0, 5).forEach((job, i) => {
            result += `**${i + 1}. ${job.title}** at ${job.company}\n`
            result += `   📍 ${job.location} | 💰 ${job.salary || 'Not specified'}\n\n`
          })
          return result
        }
      }
    } catch (error) {
      console.log('Jobs API error:', error)
    }

    // Demo response
    return `🔍 **Job Search Results** (Demo)

Based on "${query}", here are matching opportunities:

**1. Senior Python Developer** — Google
   📍 Remote | 💰 $180,000 - $250,000

**2. ML Engineer** — OpenAI
   📍 San Francisco | 💰 $200,000 - $300,000

**3. Backend Developer** — Stripe
   📍 Remote | 💰 $150,000 - $200,000

**4. Software Engineer** — Meta
   📍 NYC | 💰 $175,000 - $240,000

**5. Full Stack Developer** — Netflix
   📍 Los Angeles | 💰 $160,000 - $220,000

---
*Use \`/fit\` with a job description to see your match score.*`
  }

  const estimateSalary = async (query) => {
    if (!query) {
      return `💰 **Salary Estimator**

Usage: \`/salary [job title] [location] [experience]\`

Experience levels: Entry, Mid, Senior, Staff

Examples:
• \`/salary ML Engineer San Francisco Senior\`
• \`/salary Frontend Developer Remote Mid\`
• \`/salary Data Scientist NYC Entry\``
    }

    const parts = query.split(' ')
    const title = parts.slice(0, -2).join(' ') || parts[0]
    const location = parts[parts.length - 2] || 'Remote'
    const level = parts[parts.length - 1] || 'Mid'

    try {
      const response = await fetch(`${API_URL}/salary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title: title,
          location: location,
          experience_level: level
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          return `💰 **Salary Analysis**

**Role:** ${title}
**Location:** ${location}
**Level:** ${level}

${data.data?.advice || 'Based on current market data.'}

*Actual offers vary by company, skills, and negotiation.*`
        }
      }
    } catch (error) {
      console.log('Salary API error:', error)
    }

    // Demo response
    return `💰 **Salary Estimate** (${title})

**Location:** ${location}
**Level:** ${level}

| Level | Base Salary | Total Comp |
|-------|-------------|------------|
| Entry | $70K - $95K | $80K - $110K |
| Mid | $100K - $150K | $120K - $180K |
| Senior | $150K - $200K | $180K - $280K |
| Staff+ | $200K - $300K | $280K - $450K |

**Key Factors:**
• Big Tech pays 20-40% premium
• Remote may adjust by location
• Specialized skills command more

*Tip: Always negotiate—most leave 10-20% on the table.*`
  }

  const generateCoverLetter = async (args) => {
    const parts = args.split(' ')
    const company = parts[0] || 'Company'
    const title = parts.slice(1).join(' ') || 'Software Engineer'

    try {
      const response = await fetch(`${API_URL}/cover-letter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company,
          job_title: title,
          job_description: `${title} position at ${company}`,
          skills: ['Python', 'JavaScript', 'Problem Solving']
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          return `✉️ **Cover Letter for ${company}**\n\n${data.cover_letter}`
        }
      }
    } catch (error) {
      console.log('Cover letter API error:', error)
    }

    // Demo response
    return `✉️ **Cover Letter Draft** (${company} - ${title})

---

Dear Hiring Manager,

I am writing to express my strong interest in the ${title} position at ${company}. With my background in building scalable software solutions and passion for innovative technology, I believe I would be a valuable addition to your team.

Throughout my career, I have demonstrated expertise in developing high-quality applications that drive business impact. My experience includes working with modern tech stacks, collaborating with cross-functional teams, and delivering projects that exceed expectations.

What excites me most about ${company} is your commitment to [innovation/user experience/technical excellence]. I am eager to contribute my skills to help achieve your mission.

I would welcome the opportunity to discuss how my experience aligns with your needs. Thank you for considering my application.

Best regards,
[Your Name]

---
*This is a template. Customize it with specific achievements and company research.*`
  }

  const prepareInterview = async (args) => {
    if (!args) {
      return `🎯 **Interview Preparation**

Usage: \`/interview [Company] [Role]\`

Examples:
• \`/interview Google Software Engineer\`
• \`/interview Meta Frontend Developer\`
• \`/interview Amazon SDE\`

I'll provide:
• Company-specific tips
• Common questions
• Technical topics to review
• Behavioral frameworks`
    }

    const parts = args.split(' ')
    const company = parts[0]
    const role = parts.slice(1).join(' ') || 'Software Engineer'

    return `🎯 **Interview Prep: ${company} - ${role}**

## Company Overview
${company} is known for rigorous technical interviews. Here's your prep plan:

## Technical Questions
1. **Coding**: Expect 2-3 medium/hard LeetCode problems
2. **System Design**: Design a scalable ${role.includes('Frontend') ? 'web application' : 'distributed system'}
3. **Domain Knowledge**: ${role}-specific deep dives

## Behavioral Questions (STAR Format)
• Tell me about a challenging project
• How do you handle disagreements?
• Describe a time you failed and what you learned
• Why ${company}?

## Recommended Prep
✅ LeetCode: Focus on Trees, Graphs, Dynamic Programming
✅ System Design: Read "Designing Data-Intensive Applications"
✅ Mock interviews: Practice with peers

## Pro Tips for ${company}
• Show your problem-solving process out loud
• Ask clarifying questions before coding
• Discuss trade-offs in your solutions
• Research their recent products/blog posts

*Good luck! Would you like me to do a mock interview?*`
  }

  const draftEmail = async (args) => {
    const type = args?.toLowerCase() || 'followup'

    const templates = {
      followup: `📧 **Follow-up Email Template**

---

Subject: Following Up - [Position] Application

Dear [Hiring Manager],

I hope this message finds you well. I wanted to follow up on my application for the [Position] role that I submitted on [Date].

I remain very enthusiastic about the opportunity to contribute to [Company] and would appreciate any updates you might have on the hiring timeline.

Thank you for your time and consideration.

Best regards,
[Your Name]

---`,
      application: `📧 **Application Email Template**

---

Subject: Application for [Position] - [Your Name]

Dear [Hiring Manager],

I am writing to apply for the [Position] role at [Company]. With [X] years of experience in [field], I am excited about the opportunity to contribute to your team.

I have attached my resume for your review. I would welcome the chance to discuss how my background aligns with your needs.

Thank you for considering my application.

Best regards,
[Your Name]

---`,
      networking: `📧 **Networking Email Template**

---

Subject: Quick Question About [Topic/Company]

Hi [Name],

I came across your profile on LinkedIn and was impressed by your work at [Company]. I'm currently exploring opportunities in [field] and would love to learn about your experience.

Would you have 15 minutes for a brief chat? I'd really appreciate your insights.

Thanks so much,
[Your Name]

---`
    }

    return templates[type] || `📧 **Email Types Available**

\`/email followup\` - After applying or interviewing
\`/email application\` - When applying for a job
\`/email networking\` - Reaching out to connections`
  }

  const scoreJobFit = async (jobDescription) => {
    return `📊 **Job Fit Analysis**

## Match Score: 78%

### ✅ Strong Alignment
• Technical skills (Python, JavaScript)
• Experience level matches requirement
• Industry background relevant

### ⚠️ Areas to Address
• Missing: [Specific skill from JD]
• Consider highlighting relevant projects
• May need to emphasize leadership experience

### 💡 Positioning Strategy
1. Lead with your strongest matching skills
2. Address gaps proactively in cover letter
3. Prepare examples demonstrating transferable skills

### Recommended Actions
• \`/cover\` - Generate tailored cover letter
• \`/interview\` - Prepare for this role
• \`/resume\` - Optimize your resume

*This is a preliminary analysis. Full scoring requires Cloud Brain connection.*`
  }

  // Demo response for natural language
  const getDemoResponse = (query) => {
    const q = query.toLowerCase()

    if (q.includes('resume') || q.includes('cv')) {
      return `📄 I'd love to analyze your resume! 

You can either:
• Use \`/resume [paste your resume]\`
• Or just paste your resume text directly

I'll identify your strengths, suggest improvements, and help you stand out.`
    }

    if (q.includes('job') || q.includes('find') || q.includes('search')) {
      return `🔍 Let me help you find opportunities!

Use: \`/jobs [title] [location]\`
Example: \`/jobs Python Developer Remote\`

Or tell me more about what you're looking for and I'll guide you.`
    }

    if (q.includes('salary') || q.includes('pay') || q.includes('worth')) {
      return `💰 Great question about compensation!

Use: \`/salary [title] [location] [level]\`
Example: \`/salary ML Engineer Remote Senior\`

I'll give you market data and negotiation insights.`
    }

    if (q.includes('interview')) {
      return `🎯 Let's prepare you for success!

Use: \`/interview [company] [role]\`
Example: \`/interview Google Software Engineer\`

I'll provide company-specific prep and practice questions.`
    }

    return `Thanks for reaching out! Here's how I can help:

• \`/help\` - See all commands
• \`/resume\` - Analyze your resume
• \`/jobs\` - Search for opportunities
• \`/salary\` - Get compensation data
• \`/interview\` - Prepare for interviews
• \`/cover\` - Generate cover letters

Or just tell me what you need—I'm here to help with your career journey!`
  }

  const handleQuickAction = (action) => {
    setInput(action)
    inputRef.current?.focus()
  }

  const handleToolClick = (tool) => {
    setActiveTool(tool.id)
    if (tool.command) {
      setInput(tool.command + ' ')
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
    if (e.key === 'Escape') {
      setShowCommands(false)
    }
  }

  // Parse markdown-like formatting
  const formatMessage = (content) => {
    if (!content) return null

    return content.split('\n').map((line, i) => {
      // Headers
      if (line.startsWith('## ')) {
        return <h3 key={i} className="msg-h3">{processInline(line.slice(3))}</h3>
      }
      if (line.startsWith('### ')) {
        return <h4 key={i} className="msg-h4">{processInline(line.slice(4))}</h4>
      }
      // Horizontal rule
      if (line.trim() === '---') {
        return <hr key={i} className="msg-hr" />
      }
      // Table header
      if (line.includes('|') && line.trim().startsWith('|')) {
        // Skip separator rows
        if (line.includes('---')) return null
        const cells = line.split('|').filter(c => c.trim())
        const isHeader = i + 1 < content.split('\n').length &&
          content.split('\n')[i + 1].includes('---')
        return (
          <div key={i} className={`msg-table-row ${isHeader ? 'header' : ''}`}>
            {cells.map((cell, j) => <span key={j} className="msg-cell">{cell.trim()}</span>)}
          </div>
        )
      }
      // Regular line with inline formatting
      return <div key={i} className="msg-line">{processInline(line) || <br />}</div>
    })
  }

  const processInline = (text) => {
    if (!text) return ''

    // Process inline formatting
    let parts = text.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`)/g)

    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>
      }
      if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
        return <em key={i}>{part.slice(1, -1)}</em>
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} className="msg-code">{part.slice(1, -1)}</code>
      }
      return part
    })
  }

  return (
    <>
      <div className="animated-bg"></div>
      <div className="app">
        {/* Settings Modal */}
        <Settings
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          onSave={(settings) => {
            setGpuMode(settings.mode)
            checkConnection()
          }}
        />

        {/* Header */}
        <header className="header">
          <div className="logo">
            <div className="logo-icon">C</div>
            <div className="logo-text">
              <h1>CYNO</h1>
              <span>AI CAREER STRATEGIST</span>
            </div>
          </div>
          <div className="header-right">
            <div className="status-badge" onClick={checkConnection}>
              <div className={`status-dot ${isConnected ? '' : 'offline'}`}></div>
              <span>{isConnected ? (gpuMode === 'cloud' ? '☁️ Cloud Brain' : '💻 Local GPU') : '⚡ Demo Mode'}</span>
            </div>
            <button className="settings-btn" onClick={() => setShowSettings(true)}>
              ⚙️
            </button>
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
                  onClick={() => handleToolClick(tool)}
                >
                  <span className="tool-icon">{tool.icon}</span>
                  <span className="tool-name">{tool.name}</span>
                </div>
              ))}
            </div>

            {/* Commands hint */}
            <div className="sidebar-hint">
              <span>💡 Type <code>/help</code> for commands</span>
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

            {/* Command autocomplete */}
            {showCommands && (
              <div className="command-dropdown">
                {getFilteredCommands().map(([cmd, info]) => (
                  <div
                    key={cmd}
                    className="command-item"
                    onClick={() => handleCommandSelect(cmd)}
                  >
                    <span className="command-name">{cmd}</span>
                    <span className="command-desc">{info.description}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Input Area */}
            <div className="input-area">
              <div className="input-container">
                <div className="input-wrapper">
                  <textarea
                    ref={inputRef}
                    className="chat-input"
                    placeholder="Type a message or /command..."
                    value={input}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyPress}
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
                    onClick={() => handleQuickAction(action.action)}
                  >
                    {action.text}
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
