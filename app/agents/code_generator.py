import os
import re
import importlib
import subprocess
import sys
import tempfile
from openai import OpenAI
from ..config import OPENAI_API_KEY


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class OpenAIHelper:
    def __init__(self):
        self.client = OpenAI()

    def generate_code(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Python code generator. Respond only with executable Python code, no explanations or comments."},
                {"role": "user", "content": f"Generate Python code to {prompt}. If you need to use any external libraries, include a comment at the top of the code listing the required pip installations."}
            ],
            max_tokens=4000,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        code = re.sub(r'^```python\n|^```\n|```$', '', response.choices[0].message.content, flags=re.MULTILINE)
        code_lines = code.split('\n')
        
        # Clean up code, removing any unnecessary lines
        while code_lines and not (code_lines[0].startswith('import') or code_lines[0].startswith('from') or code_lines[0].startswith('#')):
            code_lines.pop(0)

        return '\n'.join(code_lines)

class LibraryManager:
    @staticmethod
    def install_libraries(code):
        libraries = re.findall(r'#\s*pip install\s+([\w-]+)', code)
        if libraries:
            print("Installing required libraries...")
            for lib in libraries:
                try:
                    importlib.import_module(lib.replace('-', '_'))
                    print(f"{lib} is already installed.")
                except ImportError:
                    print(f"Installing {lib}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print("Libraries installed successfully.")


class CodeExecutor:
    @staticmethod
    def execute_code(code):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            result = subprocess.run(['python', temp_file_path], capture_output=True, text=True, timeout=30)
            output = result.stdout
            error = result.stderr
        except subprocess.TimeoutExpired:
            output = ""
            error = "Execution timed out after 30 seconds."
        finally:
            os.unlink(temp_file_path)
        
        return output, error


class CodeGenerator:
    def __init__(self):
        self.openai_helper = OpenAIHelper()
        self.library_manager = LibraryManager()
        self.code_executor = CodeExecutor()

    def run(self, prompt):
        print(f"Generating code for: {prompt}")
        
        # Generate the Python code based on the prompt
        code = self.openai_helper.generate_code(prompt)
        
        print("Generated code:")
        print(code)
        
        # Install any libraries mentioned in the code
        self.library_manager.install_libraries(code)
        
        print("\nExecuting code...")
        
        # Execute the generated code
        output, error = self.code_executor.execute_code(code)

        # Print the output or errors from code execution
        if output:
            print("Output:")
            print(output)
        if error:
            print("Error:")
            print(error)