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

class PromptFactory(ABC):
    def __init__( self ):
        self.prompt_name = None
        self.role = None 
        self.system = None

    @abstractmethod
    def prompt_template( self  ):
        pass

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

    def prompt_template( self ) :
        chat_template = ChatPromptTemplate([
            ('system', self.role+ '\n' +self.system ),
            ('human', '{input}')
        ])
        return chat_template

    def prompt_messages( self ):
        messages = ChatPromptTemplate.from_messages([
            SystemMessage(content= self.role+ '\n' +self.system ),
            HumanMessage(content='input')
        ])
        return messages

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