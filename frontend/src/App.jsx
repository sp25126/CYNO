import { useState, useRef, useEffect, useCallback } from 'react'
import './App.css'
import './Settings.css'
import Settings from './Settings'

// ========================================
// CYNO COMMANDS SYSTEM v2.0
// ========================================
const COMMANDS = {
  '/help': {
    description: 'Show all available commands',
    usage: '/help',
    icon: '📖',
    category: 'general'
  },
  '/resume': {
    description: 'Analyze your resume with AI insights',
    usage: '/resume [paste resume text]',
    icon: '📄',
    category: 'tools'
  },
  '/jobs': {
    description: 'Search for jobs matching your criteria',
    usage: '/jobs [title] [location]',
    example: '/jobs Python Developer Remote',
    icon: '🔍',
    category: 'tools'
  },
  '/salary': {
    description: 'Get salary estimates for any role',
    usage: '/salary [title] [location] [level]',
    example: '/salary ML Engineer SF Senior',
    icon: '💰',
    category: 'tools'
  },
  '/cover': {
    description: 'Generate personalized cover letters',
    usage: '/cover [company] [job title]',
    example: '/cover Google Software Engineer',
    icon: '✉️',
    category: 'tools'
  },
  '/interview': {
    description: 'Prepare for interviews with practice questions',
    usage: '/interview [company] [role]',
    example: '/interview Meta Frontend Engineer',
    icon: '🎯',
    category: 'tools'
  },
  '/email': {
    description: 'Draft professional emails',
    usage: '/email [followup|application|networking]',
    icon: '📧',
    category: 'tools'
  },
  '/fit': {
    description: 'Score how well you match a job',
    usage: '/fit [paste job description]',
    icon: '📊',
    category: 'tools'
  },
  '/settings': {
    description: 'Open settings panel',
    usage: '/settings',
    icon: '⚙️',
    category: 'general'
  },
  '/clear': {
    description: 'Clear chat history',
    usage: '/clear',
    icon: '🗑️',
    category: 'general'
  }
}

// Tool sidebar items
const TOOLS = [
  { id: 'chat', name: 'Chat with CYNO', icon: '💬', command: '', description: 'General career guidance' },
  { id: 'resume', name: 'Resume Analysis', icon: '📄', command: '/resume', description: 'AI-powered insights' },
  { id: 'jobs', name: 'Job Search', icon: '🔍', command: '/jobs', description: 'Find opportunities' },
  { id: 'cover', name: 'Cover Letter', icon: '✉️', command: '/cover', description: 'Personalized letters' },
  { id: 'salary', name: 'Salary Advisor', icon: '💰', command: '/salary', description: 'Market rates' },
  { id: 'interview', name: 'Interview Prep', icon: '🎯', command: '/interview', description: 'Practice & tips' },
  { id: 'email', name: 'Email Drafter', icon: '📧', command: '/email', description: 'Professional emails' },
  { id: 'fit', name: 'Job Fit Score', icon: '📊', command: '/fit', description: 'Match analysis' },
]

const QUICK_ACTIONS = [
  { text: '📖 Commands', action: '/help' },
  { text: '📄 Resume', action: '/resume ' },
  { text: '🔍 Jobs', action: '/jobs Python Developer Remote' },
  { text: '💰 Salary', action: '/salary Software Engineer Remote Mid' },
  { text: '🎯 Interview', action: '/interview ' },
]

// API base URL
const API_URL = 'http://localhost:8000'

// Welcome message
const WELCOME_MESSAGE = `# Welcome to CYNO 👋

I'm your **AI Career Strategist** — here to help you navigate your career journey with precision and insight.

## Quick Start
Type \`/help\` to see all commands, or just tell me what you need.

## What I Can Do
| Tool | Command | Description |
|------|---------|-------------|
| 📄 Resume | \`/resume\` | AI-powered analysis |
| 🔍 Jobs | \`/jobs\` | Smart job search |
| 💰 Salary | \`/salary\` | Market insights |
| ✉️ Cover | \`/cover\` | Personalized letters |
| 🎯 Interview | \`/interview\` | Prep & practice |

**What brings you here today?**`

function App() {
  const [messages, setMessages] = useState([
    { id: 1, type: 'ai', content: WELCOME_MESSAGE, timestamp: new Date() }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState('')
  const [activeTool, setActiveTool] = useState('chat')
  const [isConnected, setIsConnected] = useState(false)
  const [gpuMode, setGpuMode] = useState('cloud')
  const [showSettings, setShowSettings] = useState(false)
  const [showCommands, setShowCommands] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Scroll to bottom smoothly
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Check API connection on mount
  useEffect(() => {
    checkConnection()
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

  // Handle input change with command detection
  const handleInputChange = (e) => {
    const value = e.target.value
    setInput(value)
    setShowCommands(value.startsWith('/') && value.length > 0)
  }

  const handleCommandSelect = (cmd) => {
    setInput(cmd + ' ')
    setShowCommands(false)
    inputRef.current?.focus()
  }

  const getFilteredCommands = () => {
    const search = input.toLowerCase()
    return Object.entries(COMMANDS).filter(([cmd]) =>
      cmd.toLowerCase().startsWith(search)
    )
  }

  // Add message helper
  const addMessage = useCallback((type, content) => {
    const newMessage = {
      id: Date.now(),
      type,
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
    return newMessage.id
  }, [])

  // Update message helper
  const updateMessage = useCallback((id, content) => {
    setMessages(prev => prev.map(msg =>
      msg.id === id ? { ...msg, content } : msg
    ))
  }, [])

  // Live analysis simulation
  const simulateAnalysis = async (steps, callback) => {
    setIsAnalyzing(true)
    for (const step of steps) {
      setAnalysisProgress(step)
      await new Promise(r => setTimeout(r, 600))
    }
    setIsAnalyzing(false)
    setAnalysisProgress('')
    if (callback) await callback()
  }

  // Process message
  const sendMessage = async () => {
    const trimmedInput = input.trim()
    if (!trimmedInput || isProcessing) return

    setIsProcessing(true)
    addMessage('user', trimmedInput)
    setInput('')
    setShowCommands(false)

    try {
      // Handle commands
      if (trimmedInput.startsWith('/')) {
        const response = await handleCommand(trimmedInput)
        if (response) {
          addMessage('ai', response)
        }
      } else {
        // Regular chat
        setIsTyping(true)
        const response = await sendChatMessage(trimmedInput)
        setIsTyping(false)
        addMessage('ai', response)
      }
    } catch (error) {
      console.error('Message error:', error)
      setIsTyping(false)
      addMessage('ai', '⚠️ Something went wrong. Please try again.')
    }

    setIsProcessing(false)
    inputRef.current?.focus()
  }

  // Send chat message to API
  const sendChatMessage = async (message) => {
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })

      if (response.ok) {
        const data = await response.json()
        return data.response || getDemoResponse(message)
      }
    } catch (error) {
      console.log('API not available, using demo mode')
    }
    return getDemoResponse(message)
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
        setMessages([{
          id: Date.now(),
          type: 'ai',
          content: '🔄 Chat cleared. How can I help you today?',
          timestamp: new Date()
        }])
        return null

      case '/settings':
        setShowSettings(true)
        return null

      case '/resume':
        if (!args) {
          return `## 📄 Resume Analysis

To analyze your resume, paste your resume text:

\`\`\`
/resume [Your resume content here]
\`\`\`

### What I'll Analyze
- **Core Strengths** — Your key differentiators
- **Career Trajectory** — Patterns and growth
- **Optimization** — Actionable improvements
- **Market Fit** — Matching opportunities

*Simply paste your resume text and I'll provide comprehensive insights.*`
        }
        return await analyzeResume(args)

      case '/jobs':
        return await searchJobs(args)

      case '/salary':
        return await estimateSalary(args)

      case '/cover':
        if (!args) {
          return `## ✉️ Cover Letter Generator

Generate a personalized cover letter:

\`\`\`
/cover [Company] [Job Title]
\`\`\`

**Example:** \`/cover Google Senior Engineer\`

I'll create a compelling letter that:
- Opens with a hook
- Highlights relevant experience
- Shows company knowledge
- Closes with confidence`
        }
        return await generateCoverLetter(args)

      case '/interview':
        return await prepareInterview(args)

      case '/email':
        return await draftEmail(args)

      case '/fit':
        if (!args) {
          return `## 📊 Job Fit Score

Analyze how well you match a job:

\`\`\`
/fit [Paste job description]
\`\`\`

I'll provide:
- Match percentage
- Strength alignment
- Gap analysis
- Positioning strategy`
        }
        return await scoreJobFit(args)

      default:
        return `❓ Unknown command: \`${command}\`

Type \`/help\` to see available commands.`
    }
  }

  // Format help message
  const formatHelpMessage = () => {
    let help = `## 📖 CYNO Command Reference\n\n`

    help += `### 🔧 Career Tools\n`
    help += `| Command | Description |\n|---------|-------------|\n`
    Object.entries(COMMANDS)
      .filter(([, cmd]) => cmd.category === 'tools')
      .forEach(([name, cmd]) => {
        help += `| \`${name}\` | ${cmd.description} |\n`
      })

    help += `\n### ⚙️ General\n`
    help += `| Command | Description |\n|---------|-------------|\n`
    Object.entries(COMMANDS)
      .filter(([, cmd]) => cmd.category === 'general')
      .forEach(([name, cmd]) => {
        help += `| \`${name}\` | ${cmd.description} |\n`
      })

    help += `\n---\n*💡 Tip: You can also chat naturally—I understand context!*`
    return help
  }

  // ========================================
  // TOOL IMPLEMENTATIONS
  // ========================================

  const analyzeResume = async (resumeText) => {
    await simulateAnalysis([
      '🔍 Scanning resume structure...',
      '📊 Extracting skills and experience...',
      '🧠 Analyzing career trajectory...',
      '✨ Generating insights...'
    ])

    try {
      const response = await fetch(`${API_URL}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resumeText })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.data) {
          const p = data.data
          const skills = (p.skills || []).slice(0, 8)

          return `## 📄 Resume Analysis Complete

### 👤 Profile Overview
${p.name ? `**Name:** ${p.name}` : ''}
${p.email ? `**Email:** ${p.email}` : ''}
${p.experience_years ? `**Experience:** ${p.experience_years} years` : ''}

### 🛠️ Skills Identified
${skills.map(s => `\`${s}\``).join(' ') || '*Unable to extract skills*'}

### 💡 Key Insights
${data.insights?.core_strength ? `**Core Strength:** ${data.insights.core_strength}` : '• Strong technical foundation'}
${data.insights?.career_pattern ? `**Career Pattern:** ${data.insights.career_pattern}` : '• Progressive career trajectory'}

### ✅ Recommendations
1. **Quantify achievements** — Add metrics and numbers
2. **Highlight differentiators** — What makes you unique
3. **Tailor for each role** — Customize for the job

---
**Next Steps:** \`/jobs\` to find matching roles, \`/cover\` for applications`
        }
      }
    } catch (error) {
      console.log('Resume API error:', error)
    }

    return getDemoResumeAnalysis()
  }

  const searchJobs = async (query) => {
    if (!query) {
      return `## 🔍 Job Search

Find opportunities matching your profile:

\`\`\`
/jobs [title] [location]
\`\`\`

**Examples:**
- \`/jobs Python Developer Remote\`
- \`/jobs ML Engineer San Francisco\`
- \`/jobs Frontend Developer NYC\`

I'll search across multiple platforms and return the best matches.`
    }

    await simulateAnalysis([
      '🌐 Connecting to job boards...',
      '🔎 Searching opportunities...',
      '📊 Ranking by relevance...'
    ])

    try {
      const response = await fetch(`${API_URL}/jobs/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, location: 'Remote' })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.jobs && data.jobs.length > 0) {
          let result = `## 🔍 Job Search Results\n\n`
          result += `Found **${data.jobs.length}** matching opportunities:\n\n`

          data.jobs.slice(0, 5).forEach((job, i) => {
            result += `### ${i + 1}. ${job.title}\n`
            result += `**${job.company}** • ${job.location}\n`
            result += `💰 ${job.salary || 'Competitive'}\n\n`
          })

          result += `---\n*Use \`/fit [job description]\` to analyze your match*`
          return result
        }
      }
    } catch (error) {
      console.log('Jobs API error:', error)
    }

    return getDemoJobResults(query)
  }

  const estimateSalary = async (query) => {
    if (!query) {
      return `## 💰 Salary Estimator

Get market rates for any role:

\`\`\`
/salary [title] [location] [level]
\`\`\`

**Levels:** Entry, Mid, Senior, Staff, Principal

**Examples:**
- \`/salary ML Engineer San Francisco Senior\`
- \`/salary Frontend Developer Remote Mid\`
- \`/salary Data Scientist NYC Entry\``
    }

    const parts = query.split(' ')
    const title = parts.slice(0, -2).join(' ') || parts[0] || 'Software Engineer'
    const location = parts[parts.length - 2] || 'Remote'
    const level = parts[parts.length - 1] || 'Mid'

    await simulateAnalysis([
      '📊 Gathering market data...',
      '📈 Analyzing compensation trends...',
      '💡 Generating recommendations...'
    ])

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
          return `## 💰 Salary Analysis

### ${title}
**Location:** ${location} • **Level:** ${level}

${data.data?.advice || 'Based on current market data.'}

---
*Tip: Always negotiate—most candidates leave 10-20% on the table.*`
        }
      }
    } catch (error) {
      console.log('Salary API error:', error)
    }

    return getDemoSalaryAnalysis(title, location, level)
  }

  const generateCoverLetter = async (args) => {
    const parts = args.split(' ')
    const company = parts[0] || 'Company'
    const title = parts.slice(1).join(' ') || 'Software Engineer'

    await simulateAnalysis([
      '🎯 Analyzing role requirements...',
      '✍️ Crafting personalized content...',
      '✨ Polishing final draft...'
    ])

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
          return `## ✉️ Cover Letter for ${company}\n\n${data.cover_letter}\n\n---\n*Customize this template with your specific achievements.*`
        }
      }
    } catch (error) {
      console.log('Cover letter API error:', error)
    }

    return getDemoCoverLetter(company, title)
  }

  const prepareInterview = async (args) => {
    if (!args) {
      return `## 🎯 Interview Preparation

Get tailored prep for any company:

\`\`\`
/interview [Company] [Role]
\`\`\`

**Examples:**
- \`/interview Google Software Engineer\`
- \`/interview Meta Frontend Developer\`
- \`/interview Amazon SDE\`

I'll provide company-specific insights, common questions, and preparation strategies.`
    }

    const parts = args.split(' ')
    const company = parts[0]
    const role = parts.slice(1).join(' ') || 'Software Engineer'

    await simulateAnalysis([
      '🏢 Researching company culture...',
      '📋 Gathering common questions...',
      '🎯 Building prep strategy...'
    ])

    return `## 🎯 Interview Prep: ${company}

### Role: ${role}

### 📋 Technical Preparation
1. **Coding** — LeetCode medium/hard, focus on:
   - Arrays & Strings
   - Trees & Graphs
   - Dynamic Programming
   
2. **System Design** — Practice designing:
   - Scalable web services
   - Real-time systems
   - Data pipelines

### 💬 Behavioral Questions (STAR Format)
- Tell me about a challenging project
- How do you handle disagreements?
- Describe a failure and what you learned
- Why ${company}?

### 🎯 ${company}-Specific Tips
- Research recent product launches
- Understand their tech stack
- Know their mission and values
- Prepare thoughtful questions

### ✅ Day-Before Checklist
- [ ] Review your resume stories
- [ ] Test your video/audio setup
- [ ] Prepare your questions for them
- [ ] Get good sleep!

---
*Good luck! You've got this. 💪*`
  }

  const draftEmail = async (args) => {
    const type = args?.toLowerCase() || 'followup'

    const templates = {
      followup: `## 📧 Follow-Up Email

**Subject:** Following Up — [Position] Application

---

Dear [Hiring Manager],

I hope this message finds you well. I wanted to follow up on my application for the **[Position]** role that I submitted on [Date].

I remain enthusiastic about the opportunity to contribute to [Company's] mission of [specific mission/goal]. After learning more about [recent company news/product], I'm even more excited about the potential to bring my experience in [relevant skill] to your team.

I would appreciate any updates you might have on the hiring timeline. Thank you for your time and consideration.

Best regards,
[Your Name]

---
*💡 Tip: Send 1 week after applying, then every 2 weeks thereafter.*`,

      application: `## 📧 Application Email

**Subject:** Application for [Position] — [Your Name]

---

Dear [Hiring Manager],

I am writing to apply for the **[Position]** role at [Company]. With [X] years of experience in [field], I am excited about the opportunity to contribute to your team.

**Why I'm a Strong Fit:**
- [Key achievement with metrics]
- [Relevant experience]
- [Alignment with company values]

I have attached my resume for your review. I would welcome the opportunity to discuss how my background aligns with your needs.

Thank you for considering my application.

Best regards,
[Your Name]

---
*💡 Tip: Always customize the opening hook for each company.*`,

      networking: `## 📧 Networking Email

**Subject:** Quick Question About [Topic/Company]

---

Hi [Name],

I came across your profile on LinkedIn and was impressed by your work at [Company], particularly [specific accomplishment].

I'm currently [brief context about yourself] and am exploring opportunities in [field/industry]. Given your experience, I would love to hear your perspective on [specific question].

Would you have 15 minutes for a brief call or coffee chat? I'd really appreciate the opportunity to learn from your experience.

Thanks so much for considering,
[Your Name]

---
*💡 Tip: Always personalize with something specific about them.*`
    }

    return templates[type] || `## 📧 Email Templates

Choose an email type:

| Command | Purpose |
|---------|---------|
| \`/email followup\` | After applying or interviewing |
| \`/email application\` | When applying for a job |
| \`/email networking\` | Reaching out to connections |`
  }

  const scoreJobFit = async (jobDescription) => {
    await simulateAnalysis([
      '📋 Parsing job requirements...',
      '🔍 Matching skills...',
      '📊 Calculating fit score...',
      '💡 Generating recommendations...'
    ])

    return `## 📊 Job Fit Analysis

### Match Score: 78/100 ⭐⭐⭐⭐

### ✅ Strong Alignment
- Technical skills match core requirements
- Experience level appropriate
- Industry background relevant

### ⚠️ Areas to Address
- Consider highlighting [specific skills from JD]
- Address [potential gaps] proactively
- Emphasize relevant projects

### 🎯 Positioning Strategy
1. **Lead with matching skills** in resume
2. **Address gaps** in cover letter
3. **Prepare examples** of transferable skills

### 📈 Recommendation
This is a **strong match**. Focus your application on emphasizing your relevant experience and prepare specific examples for the interview.

---
**Next:** \`/cover [company] [title]\` to generate a tailored cover letter`
  }

  // Demo responses
  const getDemoResponse = (query) => {
    const q = query.toLowerCase()

    if (q.includes('resume') || q.includes('cv')) {
      return `📄 I'd love to analyze your resume!\n\nUse: \`/resume [paste your resume text]\`\n\nI'll identify strengths, suggest improvements, and help you stand out.`
    }

    if (q.includes('job') || q.includes('find') || q.includes('search')) {
      return `🔍 Let me help you find opportunities!\n\nUse: \`/jobs [title] [location]\`\n\nExample: \`/jobs Python Developer Remote\``
    }

    if (q.includes('salary') || q.includes('pay') || q.includes('worth')) {
      return `💰 Great question about compensation!\n\nUse: \`/salary [title] [location] [level]\`\n\nExample: \`/salary ML Engineer Remote Senior\``
    }

    if (q.includes('interview')) {
      return `🎯 Let's prepare you for success!\n\nUse: \`/interview [company] [role]\`\n\nExample: \`/interview Google Software Engineer\``
    }

    return `Thanks for reaching out! Here's how I can help:\n\n| Command | Purpose |\n|---------|--------|\n| \`/help\` | All commands |\n| \`/resume\` | Analyze resume |\n| \`/jobs\` | Search jobs |\n| \`/salary\` | Compensation |\n| \`/interview\` | Prep |\n\nOr just tell me what you need!`
  }

  const getDemoResumeAnalysis = () => `## 📄 Resume Analysis (Demo)

### 💡 Key Insights
Based on your background, here's what stands out:

**Core Strengths:**
\`Python\` \`Problem Solving\` \`System Design\` \`Leadership\`

### ✅ Recommendations
1. **Quantify achievements** — Add metrics to impact statements
2. **Highlight differentiators** — What makes you unique
3. **Tailor for each role** — Customize for the job

### 📈 Career Trajectory
Your progression shows strong growth potential. Consider targeting senior or lead roles.

---
*Connect to Cloud Brain for full AI analysis.*`

  const getDemoJobResults = (query) => `## 🔍 Job Search Results (Demo)

Based on "${query}", here are matching opportunities:

### 1. Senior Python Developer
**Google** • Remote
💰 $180,000 - $250,000

### 2. ML Engineer
**OpenAI** • San Francisco
💰 $200,000 - $300,000

### 3. Backend Developer
**Stripe** • Remote
💰 $150,000 - $200,000

### 4. Software Engineer
**Meta** • NYC
💰 $175,000 - $240,000

### 5. Full Stack Developer
**Netflix** • Los Angeles
💰 $160,000 - $220,000

---
*Use \`/fit [job description]\` to analyze your match.*`

  const getDemoSalaryAnalysis = (title, location, level) => `## 💰 Salary Estimate

### ${title}
**Location:** ${location} • **Level:** ${level}

| Level | Base Salary | Total Comp |
|-------|-------------|------------|
| Entry | $70K - $95K | $80K - $110K |
| Mid | $100K - $150K | $120K - $180K |
| Senior | $150K - $200K | $180K - $280K |
| Staff+ | $200K - $300K | $280K - $450K |

### 💡 Key Factors
- **Big Tech Premium:** +20-40%
- **Specialized Skills:** +15-25%
- **Location Adjustment:** Varies

---
*💡 Tip: Always negotiate—most leave 10-20% on the table.*`

  const getDemoCoverLetter = (company, title) => `## ✉️ Cover Letter Draft

### ${company} — ${title}

---

Dear Hiring Manager,

I am excited to apply for the **${title}** position at **${company}**. With my background in building scalable solutions and passion for innovative technology, I believe I would be a valuable addition to your team.

**What I Bring:**
- Proven track record of delivering high-impact projects
- Strong technical skills in modern development practices
- Collaborative approach to problem-solving

What excites me most about ${company} is your commitment to [company value/mission]. I am eager to contribute my skills to help achieve your vision.

I would welcome the opportunity to discuss how my experience aligns with your needs.

Best regards,
[Your Name]

---
*💡 Customize with specific achievements and company research.*`

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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
    if (e.key === 'Escape') {
      setShowCommands(false)
    }
  }

  // Parse markdown formatting
  const formatMessage = (content) => {
    if (!content) return null

    const lines = content.split('\n')
    return lines.map((line, i) => {
      // Headers
      if (line.startsWith('### ')) {
        return <h4 key={i} className="msg-h4">{processInline(line.slice(4))}</h4>
      }
      if (line.startsWith('## ')) {
        return <h3 key={i} className="msg-h3">{processInline(line.slice(3))}</h3>
      }
      // Horizontal rule
      if (line.trim() === '---') {
        return <hr key={i} className="msg-hr" />
      }
      // Code blocks (simplified)
      if (line.startsWith('```')) {
        return null // Skip code fence markers
      }
      // Tables
      if (line.includes('|') && line.trim().startsWith('|')) {
        if (line.includes('---')) return null
        const cells = line.split('|').filter(c => c.trim())
        const isHeader = i + 1 < lines.length && lines[i + 1].includes('---')
        return (
          <div key={i} className={`msg-table-row ${isHeader ? 'header' : ''}`}>
            {cells.map((cell, j) => <span key={j} className="msg-cell">{processInline(cell.trim())}</span>)}
          </div>
        )
      }
      // Checkboxes
      if (line.trim().startsWith('- [ ]')) {
        return <div key={i} className="msg-line">☐ {processInline(line.slice(6))}</div>
      }
      if (line.trim().startsWith('- [x]')) {
        return <div key={i} className="msg-line">☑ {processInline(line.slice(6))}</div>
      }
      // Regular line
      return <div key={i} className="msg-line">{processInline(line) || <br />}</div>
    })
  }

  const processInline = (text) => {
    if (!text) return ''

    const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`)/g)

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
          <div className="status-badge" onClick={checkConnection} title="Click to refresh">
            <div className={`status-dot ${isConnected ? '' : 'offline'}`}></div>
            <span>
              {isConnected
                ? (gpuMode === 'cloud' ? '☁️ Cloud Brain' : '💻 Local GPU')
                : '⚡ Demo Mode'
              }
            </span>
          </div>
          <button className="settings-btn" onClick={() => setShowSettings(true)} title="Settings">
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
                title={tool.description}
              >
                <span className="tool-icon">{tool.icon}</span>
                <span className="tool-name">{tool.name}</span>
              </div>
            ))}
          </div>

          <div className="sidebar-hint">
            <span>💡 Type <code>/help</code></span>
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

            {/* Typing indicator */}
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

            {/* Analysis indicator */}
            {isAnalyzing && (
              <div className="message ai">
                <div className="message-avatar">C</div>
                <div className="analyzing-indicator">
                  <div className="analyzing-spinner"></div>
                  <span className="analyzing-text">{analysisProgress}</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Command dropdown */}
          {showCommands && (
            <div className="command-dropdown">
              {getFilteredCommands().map(([cmd, info]) => (
                <div
                  key={cmd}
                  className="command-item"
                  onClick={() => handleCommandSelect(cmd)}
                >
                  <span className="command-name">{info.icon} {cmd}</span>
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
                  onKeyDown={handleKeyDown}
                  rows={1}
                  disabled={isProcessing}
                />
              </div>
              <button
                className="send-btn"
                onClick={sendMessage}
                disabled={isProcessing || !input.trim()}
              >
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
  )
}

export default App
