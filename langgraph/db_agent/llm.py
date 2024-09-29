from llama_cpp import Llama
from langchain_community.chat_models import ChatLlamaCpp
from rich.console import Console
from rich.markdown import Markdown
from langchain_openai import ChatOpenAI
import logging

class BaseLLM:
    def __init__( self, model_path):
        self.model_path = model_path
        self.n_ctx = 2048
        self.temperature= 0.1
        self.top_p = 0.95
        self.max_tokens = 2000
        self.llm = Llama(
                        model_path=self.model_path,
                        n_ctx=self.n_ctx,
                        verbose=False,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens ,
                        top_p=self.top_p,
                           )
        
        
    def display_context( self, text: str ):
        """ """
        console  = Console()
        md = Markdown(text)
        console.print( md, style="bold blue")

    def call_llm( self , prompt):
        """ call LLM using the input """
        output = self.llm(
        prompt, 
        max_tokens=2048, 
        stop=["Q:", "\n"],
        ) 
        print("=="* 50, end='\n')
        self.display_context(output['choices'][0]['text'])
        print( "=="* 50, end='\n')

    def get_chat_llama( self ):
        """ get chat llama """
        llm = ChatLlamaCpp(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            verbose=False,
            temperature=self.temperature,
            max_tokens=self.max_tokens ,
            top_p=self.top_p,
        )
        logging.info(f"Chat model loaded: {self.model_path}")
        return llm
    
class OllamaLLM:
    def __init__(self) -> None:
        pass

    def init_llm( self ):

        llm = ChatOpenAI(
            api_key="ollama",
            model="llama3.1",
        base_url="http://localhost:11434/v1",
            verbose=False,
            temperature=0.0,
            top_p=1
        )
        return llm
                


if __name__ == '__main__':
    MODEL_PATH = '/teamspace/studios/this_studio/langraph/models/Llama-3.1-Storm-8B.Q4_K_M.gguf'
    local_llm = BaseLLM( model_path=MODEL_PATH)
    local_llm.call_llm("llama cpp is a ")