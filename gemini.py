from dotenv import load_dotenv
import os
from abc import ABC, abstractmethod
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

load_dotenv()

class LLMBase( ABC ):

    def __init__( self ):
        self.API_KEY= None
        self.llm = None
        
    @abstractmethod
    def call( self) :
        pass

class GeminiLLM( LLMBase ):
    def __init__(self):
        super().__init__()
        self.API_KEY = os.getenv('GEMINI_KEY')
        self.llm = genai.Client( api_key=self.API_KEY )
        self.model = 'gemini-2.0-flash'

    def call( self, prompt ):
        """
            call llm via prompt
        """
        response = self.llm.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text

class GeminiLangchain(GeminiLLM):
    """ Class for """
    def __init__(self):
        super().__init__()
        self.llm = ChatGoogleGenerativeAI(model=self.model, google_api_key=self.API_KEY)

    def call( self, prompt):
        response = self.llm.invoke(prompt )
        return response.content
    
    async def  acall( self, prompt ):
        response =  await self.llm.ainvoke( prompt ) 
        return response.content

if __name__ =='__main__':
    gem = GeminiLangchain()
    prompt='Explain how AI works in a few words'
    response = asyncio.run(gem.acall(prompt))
    print( response )

    
