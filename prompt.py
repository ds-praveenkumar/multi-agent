## prompt.py
from abc import ABC, abstractmethod
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from gemini import GeminiLangchain
from pprint import pprint
from rich.markdown import Markdown
from rich.console import Console
console = Console()
# import unicodeit
from utils import Display

set_llm_cache(SQLiteCache(database_path=".langchain.db"))

text = Display()

class PromptFactory(ABC):
    def __init__( self , ):
        self.prompt_name = None
        self.role = None
        self.system = None

    def prompt_template( self ) :
        chat_template = ChatPromptTemplate.from_messages([
            ('system', self.role+ '\n' +self.system ),
            ('human', '{input}')
        ])
        return chat_template


class DSAPrompt(PromptFactory):
    def __init__(self):
        super().__init__()
        self.prompt_name = 'DSAAgent'
        self.role = 'You are an excellent at Data structures and Algorithm Teacher with expertise in python. '
        self.system = """
        Your job is to understand the question asked by the student. Prepare a plane to answer the question step by step process to achieve the end goal.
        Always output the steps below `plan`.
        Example 
        plan:
        1. Understanding the Basics
        What is a Linked List?
        Explain the concept of a linked list as a linear collection of data elements, called nodes.
        Explain the difference between a linked list and an array.
        Explain the structure of a node (data and a pointer/reference to the next node).
        Introduce the concept of the head and tail of a linked list.
        Types of Linked Lists
        Singly Linked List: Nodes point to the next node only.
        Doubly Linked List: Nodes point to both the next and previous nodes.
        Circular Linked List: The last node points back to the first node.
        Why Use Linked Lists?
        Discuss the advantages of linked lists over arrays (dynamic size, efficient insertion/deletion).
        Discuss the disadvantages of linked lists compared to arrays (random access is not efficient, requires more memory).
        2. Core Operations (with Python code examples)
        Singly Linked List Implementation
        Node Class: Creating a Node class to represent a node in the list.
        Linked List Class: Creating a LinkedList class to manage the list.
        Insertion:
        At the beginning (head)
        At the end (tail)
        At a specific position
        Deletion:
        From the beginning (head)
        From the end (tail)
        At a specific position
        By value
        Searching: Finding a node with a specific value.
        Traversal: Iterating through the linked list to access each node.
        Display: Printing the elements of the linked list.
        Doubly Linked List Implementation
        Node Class: Creating a Node class with next and prev pointers.
        LinkedList Class: Implementing insertion, deletion, searching, and traversal, considering the prev pointers.
        Circular Linked List Implementation
        Node Class: Same as singly linked list.
        LinkedList Class: Implementing insertion, deletion, searching, and traversal, ensuring the last node points to the head.
        3. Complexity Analysis
        For each operation (insertion, deletion, search) in Singly, Doubly, and Circular Linked Lists:

        Time Complexity: Explain the Big O notation (e.g., O(1), O(n)).
        Space Complexity: Explain the space required for each operation.
        4. Advanced Concepts & Applications
        Linked Lists vs. Arrays (In-depth Comparison)
        Reiterate the trade-offs.

        Applications of Linked Lists
        Implement stacks and queues.
        Dynamic memory allocation.
        Representing polynomials.
        Implementing graphs.
        Hash tables (collision resolution).
        Common Interview Questions
        Discuss typical linked list problems asked in coding interviews (e.g., reversing a linked list, detecting cycles, finding the middle element).

        5. Practice
        Suggest coding practice problems on platforms like LeetCode, HackerRank, and GeeksforGeeks.
        """


    def prompt_messages( self ):
        messages = ChatPromptTemplate.from_messages([
            SystemMessage(content= self.role+ '\n' +self.system ),
            HumanMessage(content='input')
        ])
        return messages



class TopicExplainer(PromptFactory):
    def __init__( self ):
        super().__init__()
        self.prompt_name = 'ExpandPlan'
        self.role = 'Your job is to understand the plan and create a notes for each Topics in the plan.'
        self.system = """
        For each topic in plan create a Note chapterwise and whereever possible explain it with the example of a leetcode problem.
        Refer to the plan below:

"""

class MDCreater(PromptFactory):
    def __init__(self):
        super().__init__( )
        self.prompt_name = 'MarkdownCreater'
        self.role = 'Your job is to create a markdown code for topics provided.'
        self.system = """
        Review all the contents for each of the topic. And for each topic generate a code in markdown to be save as file.
        Markdown code should not chage the context of the topic.
        Please refer to the context below:

"""

class PDFGenerator(PromptFactory):
    def __init__( self ):
        super().__init__()
        self.prompt_name = 'PDFCreaterAgent'
        self.role = 'you are an expert in generating pdf from markdown.'
        self.system = """
        Your job is to split the data the text chapter wise from the markdown text received. After splitting the text topic wise. 
        create a python code to for converting the text to pdf.
        always output the code within ```python``` block.
        File name should 'generated.pdf' containing all the chapters.
        Please refer to the below text:

"""
        


class BaseAgent( ABC ):
    def __init__( self , agent_name: str,  prompt: PromptFactory = None ):
        self.gem = GeminiLangchain()
        self.agent_name = agent_name
        self.llm = self.gem.llm
        self.prompt = prompt

    def get_llm( self ):
        return self.prompt | self.llm
    
    def save_response( self , content):
        file_name = f'{self.agent_name}.txt'
        with open(file_name, 'w') as f:
            f.write( content )
            text.show(f'file saved {file_name}', style='bold purple')

    def get_response( self , query, style = 'bold red'):
        llm = self.get_llm()
        agent_response = llm.invoke( {"input": query })
        agent_output = ' '.join(agent_response.content.split(','))
        text.show( agent_output , style=style)
        self.save_response(agent_output)
        print('=='*50)
        return agent_output

class MarkdownAgent(BaseAgent):
    def __init__(self, agent_name: str, prompt: PromptFactory = None):
        super().__init__(agent_name, prompt)
        md = MDCreater()
        self.agent_name = prompt.prompt_name
        self.prompt = md.prompt_template()
    

class PDFAgent(BaseAgent):
    def __init__(self, agent_name: str, prompt: PromptFactory = None):
        super().__init__(agent_name, prompt)
        # pdf_gen = PDFGenerator()
        self.agent_name = prompt.prompt_name
        self.prompt = prompt.prompt_template()

if __name__ == '__main__':
    dsa = DSAPrompt()
    exp = TopicExplainer()
    md = MDCreater()
    pdf = PDFGenerator()
    gem = GeminiLangchain()
    md_agent = MarkdownAgent(md.prompt_name, md )
    pdf_agent = PDFAgent(pdf.prompt_name, pdf)
    query = 'I want to learn graphs.'
    dsa_template = dsa.prompt_template()
    exp_template = exp.prompt_template()
    # messages = dsa_template.invoke({'messages': query})
    dsa_agent = dsa_template | gem.llm
    exp_agent = exp_template | gem.llm

    dsa_response = dsa_agent.invoke( {"input": query })
    dsa_output = ' '.join(dsa_response.content.split(','))
    text.show( text=dsa_output , style='bold blue')
    print('=='*50)
    explainer_response = exp_agent.invoke( {"input": dsa_output })
    expainer_output = ' '.join(explainer_response.content.split(','))
    text.show( text=expainer_output , style='bold green')
    print('=='*50)

    markdown_response = md_agent.get_response(expainer_output )
    pdf_gen_response = pdf_agent.get_response( markdown_response, style='bold purple')

    with open( 'agent_response.txt', 'w') as f:
        f.write( dsa_output +'\n\n' + expainer_output + '\n\n' + markdown_response + '\n\n' +pdf_gen_response)

if __name__ == '__main__':
    dsa = DSAPrompt()
    gem = GeminiLangchain()
    text = Display()
    query = 'I want to learn graphs.'
    dsa_template = dsa.prompt_template()
    dsa_messages = dsa.prompt_messages()
    # messages = dsa_template.invoke({'messages': query})
    llm = dsa_template | gem.llm
    response = llm.invoke( {"input": query })
    concat_output = ' '.join(response.content.split(','))
    text.show( concat_output )

