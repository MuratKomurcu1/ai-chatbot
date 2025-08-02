🤖 AI Code Assistant

AI-Powered Code Review & Refactoring Assistant with live demo capabilities, visual flow diagrams, and intelligent chat interface.

✨ Features

🔍 Advanced Code Analysis

Static Code Analysis with security scanning
Performance optimization suggestions
Code quality metrics and complexity analysis
Multi-language support (Python, JavaScript, Java, C++, C#)

⚡ AI-Powered Refactoring

Intelligent code refactoring with OpenAI GPT-4
Best practices recommendations
Code structure improvements
Before/After comparison with detailed explanations

💬 Smart AI Chat Assistant

Context-aware code discussions
Function calling capabilities
Real-time code explanations
Interactive Q&A about your code

▶️ Live Code Execution

Secure sandboxed execution environment
Real-time output with error handling
Multiple languages support (Python, JavaScript)
Input data support for interactive programs

📊 Visual Flow Diagrams

Mermaid.js integration for beautiful diagrams
Automatic flowchart generation from code
Multiple diagram types (flowchart, sequence, class)
Interactive visualization in web interface

🐳 Production Ready

Docker containerization for easy deployment
Scalable architecture with FastAPI
Environment configuration with .env support
Health checks and monitoring endpoints

🚀 Quick Start

Option 1: Docker (Recommended)
bash# Pull and run the latest image
docker run -p 8000:8000 jantimurat/code_assistant

Or with environment variables
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here jantimurat/code_assistant
Option 2: Local Development
bash# Clone the repository
git clone https://github.com/yourusername/ai-code-assistant
cd ai-code-assistant

Create virtual environment
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
or
myenv\Scripts\activate     # Windows

Install dependencies
pip install -r requirements.txt

Set up environment
cp .env.example .env
Edit .env with your OpenAI API key

Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Option 3: Docker Compose
bash# Clone and start all services
git clone https://github.com/yourusername/ai-code-assistant
cd ai-code-assistant
docker-compose up -d


📋 Environment Variables
Create a .env file in the root directory:
env# Required
OPENAI_API_KEY=sk-your-openai-api-key-here



🏗️ Architecture
ai-code-assistant/
├── app/                    # FastAPI application
│   ├── main.py            # Main FastAPI app
│   └── config.py          # Configuration settings
├── utils/                 # Core utilities
│   ├── code_analyzer.py   # Code analysis engine
│   ├── ai_chatbot.py      # AI chat functionality
│   ├── code2flow.py       # Flow diagram generator
│   ├── demo_runner.py     # Secure code execution
│   └── refactor.py        # Code refactoring
├── templates/             # HTML templates
├── static/                # Static assets (CSS, JS)
├── frontend/              # Streamlit frontend (optional)
├── docker-compose.yml     # Multi-service deployment
├── Dockerfile             # Container definition
└── requirements.txt       # Python dependencies

🛡️ Security Features

Sandboxed code execution with Docker isolation
Input validation and sanitization
Rate limiting and timeout controls
Dangerous function detection and blocking
Environment isolation for multi-user scenarios

Development Setup
bash# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt



📄 License
This project is licensed under the MIT License 



📞 Support
Email: murat.komurrcu@gmail.com

🔮 Roadmap

 VS Code Extension for seamless integration
 More Languages support (Go, Rust, PHP)
 Team Collaboration features
 Code Review workflows
 Integration with GitHub/GitLab
 Plugin System for custom analyzers
 Mobile App for code review on the go


⭐ Star this repository if you find it helpful!
Made with ❤️ by Murat Komurcu
