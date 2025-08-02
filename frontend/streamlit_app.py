import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# FastAPI base URL
API_BASE = "http://localhost:8000"

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Code Assistant</h1>
        <p>Advanced Code Review, Refactoring & Live Demo Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🛠️ Features")
    
    feature = st.sidebar.radio(
        "Choose a feature:",
        [
            "🏠 Home",
            "🔍 Code Analyzer", 
            "⚡ Code Refactor",
            "💬 AI Chat",
            "▶️ Live Demo",
            "📊 Flow Chart"
        ]
    )
    
    # Route to different pages
    if feature == "🏠 Home":
        show_home()
    elif feature == "🔍 Code Analyzer":
        show_analyzer()
    elif feature == "⚡ Code Refactor":
        show_refactor()
    elif feature == "💬 AI Chat":
        show_chat()
    elif feature == "▶️ Live Demo":
        show_demo()
    elif feature == "📊 Flow Chart":
        show_flowchart()

def show_home():
    st.header("Welcome to AI Code Assistant! 🎉")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 Code Analysis</h3>
            <p>Advanced static analysis with security scanning, performance tips, and quality metrics.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ AI Refactoring</h3>
            <p>Intelligent code refactoring with AI-powered suggestions for better code quality.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>💬 AI Chat Assistant</h3>
            <p>Interactive AI assistant for code questions, explanations, and best practices.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>▶️ Live Code Execution</h3>
            <p>Secure code execution with real-time output for Python and JavaScript.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Flow Diagrams</h3>
            <p>Visual code flow diagrams using Mermaid.js for better code understanding.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🐳 Docker Ready</h3>
            <p>Containerized deployment with Docker for easy scaling and deployment.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Start
    st.header("🚀 Quick Start")
    st.markdown("""
    1. **Choose a feature** from the sidebar
    2. **Paste your code** in the editor
    3. **Select the programming language**
    4. **Click analyze, refactor, or run** to see results!
    """)

def show_analyzer():
    st.header("🔍 Code Analyzer")
    
    # Code input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code = st.text_area(
            "Paste your code here:",
            height=300,
            value="""def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")""",
            help="Enter the code you want to analyze"
        )
    
    with col2:
        language = st.selectbox(
            "Programming Language:",
            ["python", "javascript", "java", "cpp", "csharp"]
        )
        
        filename = st.text_input(
            "File name (optional):",
            placeholder="example.py"
        )
        
        analyze_btn = st.button("🔍 Analyze Code", type="primary")
    
    if analyze_btn and code.strip():
        with st.spinner("Analyzing code..."):
            try:
                response = requests.post(
                    f"{API_BASE}/api/analyze",
                    json={
                        "code": code,
                        "language": language,
                        "file_name": filename or None
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("status") == "success":
                        analysis = result.get("analysis", {})
                        
                        # Metrics
                        if "metrics" in analysis:
                            st.subheader("📊 Code Metrics")
                            metrics = analysis["metrics"]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Lines", metrics.get("total_lines", 0))
                            with col2:
                                st.metric("Non-Empty Lines", metrics.get("non_empty_lines", 0))
                            with col3:
                                st.metric("Characters", metrics.get("characters", 0))
                            with col4:
                                st.metric("Functions", metrics.get("functions", 0))
                        
                        # Security Issues
                        if analysis.get("security_issues"):
                            st.subheader("🛡️ Security Issues")
                            for issue in analysis["security_issues"]:
                                st.error(f"⚠️ {issue}")
                        else:
                            st.success("✅ No security issues found!")
                        
                        # Performance Tips
                        if analysis.get("performance_tips"):
                            st.subheader("⚡ Performance Tips")
                            for tip in analysis["performance_tips"]:
                                st.info(f"💡 {tip}")
                        else:
                            st.success("✅ No performance issues found!")
                        
                        # Raw Results
                        with st.expander("📋 Detailed Results"):
                            st.json(result)
                    
                    else:
                        st.error("Analysis failed!")
                        st.json(result)
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.text(response.text)
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {str(e)}")
                st.info("Make sure the FastAPI server is running on http://localhost:8000")

def show_refactor():
    st.header("⚡ Code Refactor")
    
    # Code input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code = st.text_area(
            "Code to refactor:",
            height=300,
            value="""def calc(a,b,c):
    x=a+b
    y=x*c
    if x>10:
        print("big number")
    else:
        print("small number")
    return y""",
            help="Enter the code you want to refactor"
        )
    
    with col2:
        language = st.selectbox(
            "Language:",
            ["python", "javascript", "java"],
            key="refactor_lang"
        )
        
        refactor_type = st.selectbox(
            "Refactor Type:",
            ["general", "performance", "readability", "security"]
        )
        
        refactor_btn = st.button("⚡ Refactor Code", type="primary")
    
    if refactor_btn and code.strip():
        with st.spinner("Refactoring code..."):
            try:
                response = requests.post(
                    f"{API_BASE}/api/refactor",
                    json={
                        "code": code,
                        "language": language,
                        "refactor_type": refactor_type
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("status") == "success":
                        st.subheader("✅ Refactoring Complete!")
                        
                        # Before/After comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("📝 Original Code")
                            st.code(code, language=language)
                        
                        with col2:
                            st.subheader("✨ Refactored Code")
                            refactored = result.get("refactored_code", "")
                            st.code(refactored, language=language)
                            
                            # Copy button
                            if st.button("📋 Copy Refactored Code"):
                                st.info("Code copied to clipboard! (Note: Manual copy required)")
                        
                        # Improvements
                        if result.get("improvements"):
                            st.subheader("🔧 Improvements Made")
                            for improvement in result["improvements"]:
                                st.success(f"✅ {improvement}")
                    
                    else:
                        st.error("Refactoring failed!")
                        st.json(result)
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {str(e)}")

def show_chat():
    st.header("💬 AI Chat Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Code context
    with st.expander("📝 Code Context (Optional)"):
        context_code = st.text_area(
            "Provide code for context:",
            height=200,
            help="The AI will use this code to answer your questions"
        )
        context_lang = st.selectbox(
            "Language:",
            ["python", "javascript", "java"],
            key="chat_lang"
        )
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your code..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare message with context
        if context_code.strip():
            full_message = f"{prompt}\n\nHere's my code ({context_lang}):\n```{context_lang}\n{context_code}\n```"
        else:
            full_message = prompt
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/chat",
                        json={
                            "message": full_message,
                            "conversation_id": f"streamlit-{int(time.time())}"
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get("status") == "success":
                            ai_response = result.get("response", "Sorry, I couldn't process that.")
                            st.markdown(ai_response)
                            
                            # Show suggestions
                            if result.get("suggestions"):
                                st.subheader("💡 Suggestions:")
                                for suggestion in result["suggestions"]:
                                    st.info(suggestion)
                            
                            # Add assistant response to chat history
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": ai_response
                            })
                        else:
                            error_msg = "Sorry, I encountered an error."
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": error_msg
                            })
                    else:
                        error_msg = f"API Error: {response.status_code}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
                        
                except requests.exceptions.RequestException as e:
                    error_msg = f"Connection Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

def show_demo():
    st.header("▶️ Live Code Execution")
    
    # Code input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code = st.text_area(
            "Code to execute:",
            height=300,
            value="""# Python Example
import random

def guess_number():
    secret = random.randint(1, 10)
    print(f"I'm thinking of a number between 1 and 10...")
    print(f"My number is: {secret}")
    return secret

result = guess_number()
print(f"The secret number was: {result}")""",
            help="Enter Python or JavaScript code to execute"
        )
    
    with col2:
        language = st.selectbox(
            "Language:",
            ["python", "javascript"],
            key="demo_lang"
        )
        
        input_data = st.text_input(
            "Input data (optional):",
            placeholder="Enter input for your code"
        )
        
        run_btn = st.button("▶️ Run Code", type="primary")
    
    if run_btn and code.strip():
        with st.spinner("Executing code..."):
            try:
                response = requests.post(
                    f"{API_BASE}/api/demo/run",
                    json={
                        "code": code,
                        "language": language,
                        "input_data": input_data or None
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("status") == "success":
                        st.subheader("🚀 Execution Results")
                        
                        # Execution info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Language", language.title())
                        with col2:
                            st.metric("Execution Time", result.get("execution_time", "N/A"))
                        with col3:
                            exit_code = result.get("exit_code", 0)
                            status = "✅ Success" if exit_code == 0 else "❌ Failed"
                            st.metric("Status", status)
                        
                        # Output
                        if result.get("output"):
                            st.subheader("📤 Output")
                            st.code(result["output"], language="text")
                        else:
                            st.info("No output produced")
                        
                        # Errors
                        if result.get("errors"):
                            st.subheader("❌ Errors")
                            st.error(result["errors"])
                    
                    else:
                        st.error(f"Execution failed: {result.get('error', 'Unknown error')}")
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {str(e)}")

def show_flowchart():
    st.header("📊 Code Flow Diagram")
    
    # Code input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code = st.text_area(
            "Code for flow diagram:",
            height=300,
            value="""def process_data(data):
    if not data:
        return None
    
    cleaned_data = clean_data(data)
    processed = analyze_data(cleaned_data)
    
    if processed:
        save_results(processed)
        return processed
    else:
        log_error("Processing failed")
        return None

def main():
    data = load_data()
    result = process_data(data)
    print("Processing complete")""",
            help="Enter code to generate flow diagram"
        )
    
    with col2:
        language = st.selectbox(
            "Language:",
            ["python", "javascript"],
            key="flow_lang"
        )
        
        diagram_style = st.selectbox(
            "Diagram Style:",
            ["flowchart", "sequence"]
        )
        
        generate_btn = st.button("📊 Generate Diagram", type="primary")
    
    if generate_btn and code.strip():
        with st.spinner("Generating flow diagram..."):
            try:
                response = requests.post(
                    f"{API_BASE}/api/flowchart",
                    json={
                        "code": code,
                        "language": language,
                        "style": diagram_style
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("status") == "success":
                        st.subheader("📊 Generated Flow Diagram")
                        
                        # Display mermaid diagram
                        mermaid_code = result.get("mermaid_code", "")
                        if mermaid_code:
                            st.text("Mermaid Code:")
                            st.code(mermaid_code, language="mermaid")
                            
                            st.text("Note: For full diagram visualization, use the web interface")
                        
                        # Code structure
                        if result.get("structure"):
                            with st.expander("📋 Code Structure Analysis"):
                                st.json(result["structure"])
                    
                    else:
                        st.error(f"Diagram generation failed: {result.get('error', 'Unknown error')}")
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {str(e)}")

if __name__ == "__main__":
    main()