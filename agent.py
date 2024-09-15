
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolExecutor, ToolInvocation

from llm import BaseLLM
from langchain_core.tools import tool
from langchain.agents import create_react_agent

import operator
from datetime import datetime
from typing import Annotated, TypedDict, Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
import logging


class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

class Agent:
    def __init__( self ):

        self.MODEL_PATH = '/teamspace/studios/this_studio/multiagent/models/Llama-3.1-Storm-8B.Q4_K_M.gguf' #Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf' 
        self.base_llm_obj = BaseLLM( model_path=self.MODEL_PATH) 
        self.llm = self.base_llm_obj.get_chat_llama()
        # self.llm = self.base_llm_obj.llm

    @tool
    def get_now(format: str = "%Y-%m-%d %H:%M:%S"):
        """
        Get the current time
        """
        return datetime.now().strftime(format)

    def format_prompt( self  ):
        """ Create prompt for agent """
        agent_prompt_template = """Answer the following questions as best you can. You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat 2 times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        Thought:{agent_scratchpad}"""
        agent_prompt = PromptTemplate(template=agent_prompt_template, input_variables=['tools', 'tool_names', 'agent_scratchpad', 'input'])
        return agent_prompt

    def create_agent( self  ):
        """ create react agent """
        tools = [self.get_now]
        prompt = self.format_prompt()
        agent_runnable = create_react_agent(self.llm, tools, prompt)
        return agent_runnable


    def execute_tools(self, state):
        tools = [self.get_now]
        tool_executor = ToolExecutor(tools)
        print("Called `execute_tools`")
        messages = [state["agent_outcome"]]
        last_message = messages[-1]

        tool_name = last_message.tool

        print(f"Calling tool: {tool_name}")

        action = ToolInvocation(
            tool=tool_name,
            tool_input=last_message.tool_input,
        )
        response = tool_executor.invoke(action)
        return {"intermediate_steps": [(state["agent_outcome"], response)]}


    def run_agent(self, state):
        """
        #if you want to better manages intermediate steps
        inputs = state.copy()
        if len(inputs['intermediate_steps']) > 5:
            inputs['intermediate_steps'] = inputs['intermediate_steps'][-5:]
        """
        agent_runnable = self.create_agent()
        agent_outcome = agent_runnable.invoke(state)
        return {"agent_outcome": agent_outcome}


    def should_continue(self, state):
        messages = [state["agent_outcome"]]
        last_message = messages[-1]
        if "Action" not in last_message.log:
            return "end"
        else:
            return "continue"
    
    def main( self ):

        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self.run_agent)
        workflow.add_node("action", self.execute_tools)


        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent", self.should_continue, {"continue": "action", "end": END}
        )


        workflow.add_edge("action", "agent")
        app = workflow.compile()
        return app
    
if __name__ == '__main__':
    agent = Agent()
    app = agent.main()
    input_text = "Whats the current time?"
    inputs = {"input": input_text, "chat_history": []}
    results = []
    for s in app.stream(inputs):
        result = list(s.values())[0]
        results.append(result)
        # agent.base_llm_obj.display_context(result)
        print(result)