"""
CYNO Personality & Response Engine
Provides professional, insightful responses like a senior career advisor
"""

# System prompt that defines CYNO's personality
CYNO_SYSTEM_PROMPT = """You are CYNO, an elite AI Career Strategist with 15+ years of experience in talent acquisition, resume optimization, and career coaching at Fortune 500 companies.

Your communication style:
- Warm but professional, like a trusted mentor
- Insightful and specific, never generic
- Action-oriented with clear next steps
- Encouraging but honest about areas for improvement
- Use data and specifics when possible

When analyzing resumes:
- Identify the candidate's CORE STRENGTHS and what makes them unique
- Recognize patterns in their career trajectory
- Spot transferable skills they might not realize they have
- Provide tailored advice based on their specific background

When discussing jobs:
- Match opportunities to the candidate's actual strengths
- Explain WHY a role fits (or doesn't)
- Provide industry insights and market context
- Suggest strategic moves, not just job listings

Always remember:
- You're speaking to a professional who deserves respect
- Personalize every response based on their specific situation
- Offer genuine insights, not just template responses
- Be the advisor they wish they had"""

# Professional response templates
RESPONSE_TEMPLATES = {
    "resume_analysis": {
        "intro": [
            "I've carefully reviewed your background, and I can see you have a compelling professional story to tell.",
            "After analyzing your experience, I've identified some key patterns that make you stand out.",
            "Your resume reveals an interesting career trajectory. Let me share what I've observed.",
            "I've gone through your background in detail. Here's what immediately stands out to me.",
        ],
        "strength_prefix": [
            "Based on your experience, I can see you excel at",
            "Your background clearly demonstrates strength in",
            "What sets you apart is your expertise in",
            "I notice you have a particular gift for",
        ],
        "insight_prefix": [
            "What's particularly interesting about your trajectory is",
            "Something that might not be obvious but is valuable:",
            "Here's an insight that could be a game-changer for your search:",
            "One pattern I've noticed that works in your favor:",
        ]
    },
    "job_match": {
        "high_fit": [
            "This role aligns remarkably well with your background. Here's why:",
            "I'd strongly recommend considering this opportunity. Let me explain:",
            "This is exactly the type of position where your skills would shine:",
        ],
        "medium_fit": [
            "This role has potential, though there are a few considerations:",
            "There's a good foundation for a match here, with some points to address:",
            "This could work well for you, especially if you position yourself strategically:",
        ],
        "low_fit": [
            "I want to be honest with you—this might not be the strongest match. Here's my thinking:",
            "While I understand the appeal, let me share some candid observations:",
            "Before pursuing this, there are some gaps we should address:",
        ]
    },
    "salary_advice": {
        "intro": [
            "Let me give you the real picture on compensation for this role.",
            "Based on current market data and your experience level, here's what you should know:",
            "I've analyzed the market, and here's my honest assessment of your earning potential:",
        ]
    },
    "interview_prep": {
        "intro": [
            "Let's make sure you walk into that interview with confidence and preparation.",
            "I'll help you prepare strategically. Here's what you need to know:",
            "Based on your background, here's how I'd approach preparing for this interview:",
        ]
    }
}

def get_professional_intro(category, subcategory=None):
    """Get a professional intro phrase for a response category"""
    import random
    templates = RESPONSE_TEMPLATES.get(category, {})
    if subcategory:
        phrases = templates.get(subcategory, templates.get("intro", ["I've analyzed your request."]))
    else:
        phrases = templates.get("intro", ["I've analyzed your request."])
    return random.choice(phrases)

def analyze_resume_insights(parsed_resume):
    """Generate professional insights from parsed resume data"""
    insights = {
        "core_strength": "",
        "unique_value": "",
        "career_pattern": "",
        "recommendations": []
    }
    
    if not parsed_resume:
        return insights
    
    # Extract key information
    skills = parsed_resume.get("skills", [])
    experience = parsed_resume.get("experience", [])
    education = parsed_resume.get("education", [])
    years_exp = parsed_resume.get("years_experience", 0)
    
    # Determine core strength
    if skills:
        top_skills = skills[:3] if len(skills) > 3 else skills
        if "python" in [s.lower() for s in top_skills] or "machine learning" in [s.lower() for s in top_skills]:
            insights["core_strength"] = "technical problem-solving and building data-driven solutions"
        elif any(s.lower() in ["leadership", "management", "team lead"] for s in top_skills):
            insights["core_strength"] = "leading teams and driving organizational results"
        elif any(s.lower() in ["design", "ui", "ux", "figma"] for s in top_skills):
            insights["core_strength"] = "creating user-centered designs that balance aesthetics with functionality"
        else:
            insights["core_strength"] = f"combining expertise in {', '.join(top_skills[:2])} to deliver results"
    
    # Career pattern analysis
    if years_exp:
        if years_exp < 2:
            insights["career_pattern"] = "You're at an exciting early stage where strategic moves can accelerate your trajectory significantly."
        elif years_exp < 5:
            insights["career_pattern"] = "You're in the sweet spot for growth—experienced enough to contribute meaningfully, but positioned for rapid advancement."
        elif years_exp < 10:
            insights["career_pattern"] = "Your experience positions you for senior or leadership roles. The key now is strategic positioning."
        else:
            insights["career_pattern"] = "With your depth of experience, you bring strategic value that goes beyond technical execution."
    
    # Recommendations
    insights["recommendations"] = [
        "Consider highlighting quantifiable achievements in your resume",
        "Your skill combination is valuable—make sure your LinkedIn reflects this",
        "Based on market trends, there's strong demand for your profile"
    ]
    
    return insights

def format_professional_response(message_type, data=None, user_context=None):
    """Format a response in CYNO's professional voice"""
    
    if message_type == "welcome":
        return """Welcome! I'm CYNO, your AI Career Strategist. 

I'm here to be the career advisor everyone deserves but few have access to. Whether you're exploring new opportunities, preparing for interviews, or looking to maximize your market value, I'm here to help.

A few things I can help you with:
• **Career Strategy** — Let's understand where you are and where you want to go
• **Resume Optimization** — I'll analyze your background and help you tell your story effectively  
• **Job Matching** — Find opportunities that truly align with your strengths
• **Interview Preparation** — Walk in prepared and confident
• **Salary Negotiation** — Know your worth and how to communicate it

What would you like to explore first?"""

    elif message_type == "resume_received":
        insights = analyze_resume_insights(data) if data else {}
        
        intro = get_professional_intro("resume_analysis")
        strength_prefix = get_professional_intro("resume_analysis", "strength_prefix")
        
        response = f"""{intro}

{strength_prefix} **{insights.get('core_strength', 'solving complex problems and delivering results')}**. This is a valuable combination that many employers actively seek.

{insights.get('career_pattern', '')}

**Key Observations:**
"""
        if insights.get('recommendations'):
            for rec in insights['recommendations']:
                response += f"\n• {rec}"
        
        response += "\n\nWould you like me to help you find opportunities that match these strengths, or shall we work on positioning your resume more effectively?"
        
        return response

    elif message_type == "job_search":
        return """I understand you're looking for new opportunities. Let me help you approach this strategically.

Rather than sending you a generic list, I'd like to understand:
• What type of work energizes you most?
• Are there specific companies or industries you're drawn to?
• What's your priority—growth, compensation, work-life balance, or something else?

Share a bit about what you're looking for, and I'll help you find opportunities that actually make sense for your career trajectory."""

    elif message_type == "salary_query":
        intro = get_professional_intro("salary_advice")
        return f"""{intro}

Salary discussions require nuance. The numbers I share aren't just statistics—they're negotiation intelligence.

For a **{data.get('role', 'Software Engineer')}** in **{data.get('location', 'the US market')}**:

**Market Range:**
• Entry Level (0-2 yrs): $70,000 - $95,000
• Mid-Senior (3-7 yrs): $110,000 - $160,000  
• Senior/Lead (7+ yrs): $150,000 - $220,000
• Staff/Principal: $200,000 - $350,000+

**Important Context:**
These ranges vary significantly based on company stage, location, and your specific skill stack. Big Tech typically pays at the top of these ranges, while startups might offer more equity.

Would you like me to help you understand where you specifically should be targeting based on your background?"""

    elif message_type == "interview_prep":
        intro = get_professional_intro("interview_prep")
        return f"""{intro}

Successful interviews aren't about memorizing answers—they're about authentic preparation that lets your genuine strengths shine through.

**Here's my approach:**

1. **Understand the Role** — What are they really looking for?
2. **Map Your Experience** — Connect your background to their needs
3. **Prepare Strategic Stories** — Concrete examples that demonstrate impact
4. **Anticipate Concerns** — Address potential gaps proactively

What company or role are you preparing for? I'll tailor my guidance to that specific context."""

    elif message_type == "cover_letter":
        return """Cover letters are about connection, not repetition. The best ones tell a story about why THIS opportunity and THIS company resonates with you specifically.

To craft something compelling, I'll need:
• The role and company you're applying to
• The job description (or at least the key requirements)
• What genuinely interests you about this opportunity

With that, I'll help you create a letter that makes hiring managers want to meet you."""

    else:
        return """I'm here to help you navigate your career strategically. 

What would be most helpful right now—exploring job opportunities, refining your resume, preparing for interviews, or understanding your market value?"""

def get_personalized_job_insight(job, user_profile=None):
    """Generate personalized insight about a job match"""
    
    insight = f"""### {job.get('title', 'Opportunity')} at {job.get('company', 'Company')}

**Why This Could Work:**
This role aligns with your background in {user_profile.get('primary_skill', 'software development') if user_profile else 'your field'}. 
The company is known for {job.get('company_culture', 'innovation and growth')}.

**Considerations:**
• Location: {job.get('location', 'Not specified')}
• Compensation: {job.get('salary', 'Competitive')}

**My Take:**
{job.get('insight', 'This looks like a solid opportunity worth exploring.')}
"""
    return insight
