# Resumes Folder

Place your resume files here for easy access by the HR Chat Agent!

## Supported Formats
- PDF (.pdf)
- Text (.txt)
- Word (.doc, .docx)

## How It Works

When you start the chat agent, it will:
1. **Auto-detect** any resume files in this folder
2. Show you which resume it found
3. Offer to analyze it immediately

## Usage

### Option 1: Auto-Detection (Easiest!)
1. Drop your resume file here
2. Start the agent: `python scripts/cli_chat.py`
3. Say "yes" when Cyno asks to analyze it

### Option 2: Manual Path
Just tell Cyno the path to your resume:
```
You: C:\path\to\your\resume.pdf
```

### Option 3: Just Say "Resume"
```
You: analyze my resume
```
Cyno will automatically find it in this folder!

## Tips
- The agent uses the **most recently modified** resume if multiple files exist
- You can have multiple resumes, just specify which one you want analyzed
- Rename your resume to something descriptive (e.g., `Saumya_Software_Engineer.pdf`)
