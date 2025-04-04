from langchain.agents import AgentExecutor, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.agents.agent_types import AgentType
import subprocess
from gemini import GeminiLangchain

gemini = GeminiLangchain()
llm = gemini.llm

@tool
def generate_code(query: str)->str:
    "Generate codes for a given problem"
    result = llm.invoke("Write a code snippet in Python for the given Problem. OUTPUT JUST CODE SNIPPET AND NOTHING ELSE. Problem:{}".format(query))
    if "```python" in result:
        result = result[6:-3]
    with open("temp.py", "w") as file:
            file.write(result.content)
    path = "temp.py"
    output = subprocess.run(['python', path], capture_output=True, text=True, timeout=10)
    return result if output.returncode == 0 else output.stderr

@tool
def test_code(query: str)->str:
    "Tests a given code and output results"
    
    print("Now testing code....")
    content = ''
    with open("temp.py", 'r') as file:
        content = file.read()
        
    result = ("Write a code snippet to execute the given codes with a dummy input (Assume you import the function from temp.py). OUTPUT JUST CODE SNIPPET AND NOTHING ELSE. Codes:{}".format(content))
    if "```python" in result:
        result = result[6:-3]
    with open("temp-test.py", "w") as file_test:
            file_test.write(result)
            
    path = "temp-test.py"
    result = subprocess.run(['python',path], capture_output=True, text=True, timeout=10)
    return result.stdout if result.returncode == 0 else result.stderr

tools=[generate_code,test_code]

memory = ConversationBufferMemory(memory_key="chat_history")
agent_chain=initialize_agent(tools,llm, verbose=True,memory=memory)

agent_chain.run({'input':'Generate code to check whether number is palindrome and test.'})
