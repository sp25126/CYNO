import { useState, useEffect } from 'react'

const COLAB_SCRIPT = `# ========================================
# CYNO Cloud Brain v6.0 - Google Colab Setup
# ========================================
# Run this entire cell in Google Colab (GPU runtime)
# After running, copy the ngrok URL and paste it in CYNO settings

# 1. Install dependencies
!pip install -q fastapi uvicorn transformers torch accelerate pyngrok nest-asyncio

# 2. Setup
import os
import nest_asyncio
from pyngrok import ngrok
from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn
import threading

nest_asyncio.apply()

# 3. Configure ngrok (get your token from https://dashboard.ngrok.com)
NGROK_TOKEN = "YOUR_NGROK_TOKEN_HERE"  # <-- Replace with your token
ngrok.set_auth_token(NGROK_TOKEN)

# 4. Load model
print("🧠 Loading Llama 3.2 3B model...")
model_name = "unsloth/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    low_cpu_mem_usage=True
)
print("✅ Model loaded!")

# 5. Create API
app = FastAPI(title="CYNO Cloud Brain", version="6.0")

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 500
    temperature: float = 0.7

@app.get("/health")
def health():
    return {"status": "online", "model": model_name, "gpu": torch.cuda.is_available()}

@app.post("/generate")
def generate(req: GenerateRequest):
    inputs = tokenizer(req.prompt, return_tensors="pt", truncation=True, max_length=4000).to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id
        )
    result = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return {"success": True, "result": result}

# 6. Start server with ngrok
public_url = ngrok.connect(8000)
print("=" * 50)
print(f"🚀 CYNO Cloud Brain Online!")
print(f"📍 YOUR NGROK URL: {public_url}")
print("=" * 50)
print("\\n👆 Copy this URL and paste it in CYNO Settings!")

def run():
    uvicorn.run(app, host="0.0.0.0", port=8000)

thread = threading.Thread(target=run)
thread.start()
`

export default function Settings({ isOpen, onClose, onSave }) {
    const [mode, setMode] = useState('cloud')
    const [ngrokUrl, setNgrokUrl] = useState('')
    const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434')
    const [ollamaModel, setOllamaModel] = useState('gemma2:2b')
    const [showSetup, setShowSetup] = useState(false)
    const [testStatus, setTestStatus] = useState(null)
    const [isTesting, setIsTesting] = useState(false)
    const [copied, setCopied] = useState(false)

    // Load settings on mount
    useEffect(() => {
        if (isOpen) {
            fetch('http://localhost:8000/settings')
                .then(res => res.json())
                .then(data => {
                    if (data.mode) setMode(data.mode)
                    if (data.ngrok_url) setNgrokUrl(data.ngrok_url)
                    if (data.ollama_url) setOllamaUrl(data.ollama_url)
                    if (data.ollama_model) setOllamaModel(data.ollama_model)
                })
                .catch(() => { })
        }
    }, [isOpen])

    const handleSave = async () => {
        try {
            await fetch('http://localhost:8000/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode,
                    ngrok_url: ngrokUrl,
                    ollama_url: ollamaUrl,
                    ollama_model: ollamaModel
                })
            })
            onSave?.({ mode, ngrokUrl, ollamaUrl, ollamaModel })
            onClose()
        } catch (error) {
            console.error('Failed to save settings:', error)
        }
    }

    const testConnection = async () => {
        setIsTesting(true)
        setTestStatus(null)

        const url = mode === 'cloud' ? ngrokUrl : ollamaUrl
        if (!url) {
            setTestStatus({ success: false, message: 'Please enter a URL first' })
            setIsTesting(false)
            return
        }

        try {
            // Remove trailing slash if present
            const cleanUrl = url.endsWith('/') ? url.slice(0, -1) : url
            const response = await fetch(cleanUrl + '/health', {
                method: 'GET',
                headers: { 'ngrok-skip-browser-warning': 'true' }
            })

            if (response.ok) {
                const data = await response.json()
                setTestStatus({
                    success: true,
                    message: mode === 'cloud'
                        ? `Connected! GPU: ${data.gpu ? 'Yes ✓' : 'No'}`
                        : 'Connected to Ollama!'
                })
            } else {
                setTestStatus({ success: false, message: 'Connection failed' })
            }
        } catch (error) {
            setTestStatus({
                success: false,
                message: 'Cannot reach server. Is it running?'
            })
        }
        setIsTesting(false)
    }

    const copyScript = () => {
        navigator.clipboard.writeText(COLAB_SCRIPT)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    if (!isOpen) return null

    return (
        <div className="settings-overlay" onClick={onClose}>
            <div className="settings-modal" onClick={e => e.stopPropagation()}>
                <div className="settings-header">
                    <h2>⚙️ Settings</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="settings-content">
                    {/* GPU Mode Selection */}
                    <div className="settings-section">
                        <h3>🖥️ GPU Mode</h3>
                        <p className="settings-desc">Choose where CYNO's brain runs</p>

                        <div className="mode-selector">
                            <button
                                className={`mode-btn ${mode === 'cloud' ? 'active' : ''}`}
                                onClick={() => setMode('cloud')}
                            >
                                <span className="mode-icon">☁️</span>
                                <span className="mode-title">Cloud GPU</span>
                                <span className="mode-desc">Google Colab (Free)</span>
                            </button>
                            <button
                                className={`mode-btn ${mode === 'local' ? 'active' : ''}`}
                                onClick={() => setMode('local')}
                            >
                                <span className="mode-icon">💻</span>
                                <span className="mode-title">Local GPU</span>
                                <span className="mode-desc">Ollama on your PC</span>
                            </button>
                        </div>
                    </div>

                    {/* Cloud GPU Settings */}
                    {mode === 'cloud' && (
                        <div className="settings-section">
                            <h3>☁️ Cloud Brain Setup</h3>

                            <div className="input-group">
                                <label>ngrok URL</label>
                                <input
                                    type="text"
                                    placeholder="https://xxxx.ngrok-free.app"
                                    value={ngrokUrl}
                                    onChange={e => setNgrokUrl(e.target.value)}
                                />
                            </div>

                            <button
                                className="setup-link"
                                onClick={() => setShowSetup(!showSetup)}
                            >
                                {showSetup ? '▼' : '▶'} How to set up Cloud Brain
                            </button>

                            {showSetup && (
                                <div className="setup-guide">
                                    <div className="setup-steps">
                                        <div className="step">
                                            <span className="step-num">1</span>
                                            <div>
                                                <strong>Open Google Colab</strong>
                                                <p>Go to <a href="https://colab.research.google.com" target="_blank" rel="noopener noreferrer">colab.research.google.com</a></p>
                                            </div>
                                        </div>
                                        <div className="step">
                                            <span className="step-num">2</span>
                                            <div>
                                                <strong>Enable GPU Runtime</strong>
                                                <p>Runtime → Change runtime type → T4 GPU</p>
                                            </div>
                                        </div>
                                        <div className="step">
                                            <span className="step-num">3</span>
                                            <div>
                                                <strong>Get ngrok Token</strong>
                                                <p>Sign up at <a href="https://ngrok.com" target="_blank" rel="noopener noreferrer">ngrok.com</a> and copy your authtoken</p>
                                            </div>
                                        </div>
                                        <div className="step">
                                            <span className="step-num">4</span>
                                            <div>
                                                <strong>Run the Script</strong>
                                                <p>Paste the script below into Colab and run it</p>
                                            </div>
                                        </div>
                                        <div className="step">
                                            <span className="step-num">5</span>
                                            <div>
                                                <strong>Copy the URL</strong>
                                                <p>Copy the ngrok URL from the output and paste it above</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="script-container">
                                        <div className="script-header">
                                            <span>Colab Script</span>
                                            <button onClick={copyScript}>
                                                {copied ? '✓ Copied!' : '📋 Copy'}
                                            </button>
                                        </div>
                                        <pre className="script-code">
                                            {COLAB_SCRIPT}
                                        </pre>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Local GPU Settings */}
                    {mode === 'local' && (
                        <div className="settings-section">
                            <h3>💻 Local Ollama Setup</h3>

                            <div className="input-group">
                                <label>Ollama URL</label>
                                <input
                                    type="text"
                                    placeholder="http://localhost:11434"
                                    value={ollamaUrl}
                                    onChange={e => setOllamaUrl(e.target.value)}
                                />
                            </div>

                            <div className="input-group">
                                <label>Model Name</label>
                                <input
                                    type="text"
                                    placeholder="gemma2:2b"
                                    value={ollamaModel}
                                    onChange={e => setOllamaModel(e.target.value)}
                                />
                            </div>

                            <div className="local-guide">
                                <p><strong>To set up Ollama:</strong></p>
                                <ol>
                                    <li>Download from <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer">ollama.ai</a></li>
                                    <li>Run: <code>ollama run gemma2:2b</code></li>
                                    <li>Keep Ollama running in the background</li>
                                </ol>
                            </div>
                        </div>
                    )}

                    {/* Test Connection */}
                    <div className="settings-section">
                        <button
                            className={`test-btn ${isTesting ? 'loading' : ''}`}
                            onClick={testConnection}
                            disabled={isTesting}
                        >
                            {isTesting ? 'Testing...' : '🔌 Test Connection'}
                        </button>

                        {testStatus && (
                            <div className={`test-status ${testStatus.success ? 'success' : 'error'}`}>
                                {testStatus.success ? '✅' : '❌'} {testStatus.message}
                            </div>
                        )}
                    </div>
                </div>

                <div className="settings-footer">
                    <button className="cancel-btn" onClick={onClose}>Cancel</button>
                    <button className="save-btn" onClick={handleSave}>Save Settings</button>
                </div>
            </div>
        </div>
    )
}
