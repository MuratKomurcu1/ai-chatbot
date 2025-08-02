import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
import time

class DemoRunner:
    def __init__(self):
        self.max_execution_time = 10  # 10 saniye limit
        self.temp_dir = tempfile.gettempdir()
    
    async def execute_code(self, code: str, language: str, input_data: Optional[str] = None):
        """Kod çalıştırma ana fonksiyonu"""
        
        if language == "python":
            return await self._execute_python(code, input_data)
        elif language == "javascript":
            return await self._execute_javascript(code, input_data)
        elif language == "java":
            return {"error": "Java execution not implemented yet"}
        else:
            return {"error": f"Language {language} not supported"}
    
    async def _execute_python(self, code: str, input_data: Optional[str] = None):
        """Python kod çalıştırma"""
        try:
            # Güvenlik kontrolü
            dangerous_imports = ['os', 'subprocess', 'sys', 'shutil', 'pathlib', 'importlib']
            for imp in dangerous_imports:
                if f"import {imp}" in code or f"from {imp}" in code:
                    return {"error": f"Import '{imp}' not allowed for security reasons"}
            
            # Dangerous functions
            dangerous_funcs = ['eval(', 'exec(', 'compile(', 'open(', '__import__(']
            for func in dangerous_funcs:
                if func in code:
                    return {"error": f"Function '{func}' not allowed for security reasons"}
            
            # Temporary file oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            # Python çalıştır
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time,
                input=input_data
            )
            
            execution_time = time.time() - start_time
            
            # Cleanup
            os.unlink(temp_file)
            
            return {
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "execution_time": f"{execution_time:.2f}s",
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": f"Code execution timeout ({self.max_execution_time}s limit)"}
        except FileNotFoundError:
            return {"error": "Python interpreter not found"}
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}
    
    async def _execute_javascript(self, code: str, input_data: Optional[str] = None):
        """JavaScript çalıştırma (Node.js gerekli)"""
        try:
            # Güvenlik kontrolü
            dangerous_modules = ['fs', 'child_process', 'os', 'path', 'crypto']
            for mod in dangerous_modules:
                if f"require('{mod}')" in code or f'require("{mod}")' in code:
                    return {"error": f"Module '{mod}' not allowed for security reasons"}
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time,
                input=input_data
            )
            
            execution_time = time.time() - start_time
            
            os.unlink(temp_file)
            
            return {
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "execution_time": f"{execution_time:.2f}s",
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": f"JavaScript execution timeout ({self.max_execution_time}s limit)"}
        except FileNotFoundError:
            return {"error": "Node.js not found. Please install Node.js to run JavaScript code."}
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}

# Backward compatibility
async def execute_code(code: str, language: str, input_data: Optional[str] = None):
    runner = DemoRunner()
    return await runner.execute_code(code, language, input_data)