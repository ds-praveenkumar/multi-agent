
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from typing_extensions import TypedDict
from langgraph.graph import END, StateGraph
from IPython.display import Image, display

from prompt import DB_DESCRIPTION
from helper import query_db, display_text

import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('...')
from llm import OllamaLLM

local_llm = OllamaLLM()
llm = local_llm.init_llm()

can_answer_router_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a database reading bot that can answer users' questions using information from a database. \n

    {data_description} \n\n

    Given the user's question, decide whether the question can be answered using the information in the database. \n\n

    Return a JSON with two keys, 'reasoning' and 'can_answer', and no preamble or explanation.
    Return one of the following JSON:
    
    {{"reasoning": "I can find the average revenue of customers with tenure over 24 months by averaging the Total Revenue column in the Billing table filtered by Tenure in Months > 24", "can_answer":true}}
    {{"reasoning": "I can find customers who signed up during the last 12 month using the Tenure in Months column in the Billing table", "can_answer":true}}
    {{"reasoning": "I can't answer how many customers churned last year because the Churn table doesn't contain a year", "can_answer":false}}
    

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {question} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["data_description", "question"],
)

can_answer_router = can_answer_router_prompt | llm | JsonOutputParser()

def check_if_can_answer_question(state):
  result = can_answer_router.invoke({"question": state["question"], "data_description": DB_DESCRIPTION})

  return {"plan": result["reasoning"], "can_answer": result["can_answer"]}


def skip_question(state):
  if state["can_answer"]:
    return "no"
  else:
    return "yes"

write_query_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a database reading bot that can answer users' questions using information from a database. \n

    {data_description} \n\n

    In the previous step, you have prepared the following plan: {plan}

    Return an SQL query with no preamble or explanation. Don't include any markdown characters or quotation marks around the query.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {question} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["data_description", "question", "plan"],
)

write_query_chain = write_query_prompt | llm | StrOutputParser()

def write_query(state):
  result = write_query_chain.invoke({
      "data_description": DB_DESCRIPTION,
      "question": state["question"],
      "plan": state["plan"]
  })

  return {"sql_query": result}

def execute_query(state):
  query = state["sql_query"]

  try:
    return {"sql_result": query_db(query).to_markdown()}
  except Exception as e:
    return {"sql_result", str(e)}


write_answer_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a database reading bot that can answer users' questions using information from a database. \n

    In the previous step, you have planned the query as follows: {plan},
    generated the query {sql_query}
    and retrieved the following data:
    {sql_result}

    Return a text answering the user's question using the provided data.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {question} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question", "plan", "sql_query", "sql_result"],
)

write_answer_chain = write_answer_prompt | llm | StrOutputParser()

def write_answer(state):
  result = write_answer_chain.invoke({
      "question": state["question"],
      "plan": state["plan"],
      "sql_result": state["sql_result"],
      "sql_query": state["sql_query"]
  })

  return {"answer": result}


cannot_answer_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a database reading bot that can answer users' questions using information from a database. \n

    You cannot answer the user's questions because of the following problem: {problem}.

    Explain the issue to the user and apologize for the inconvenience.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {question} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question", "problem"],
)

cannot_answer_chain = cannot_answer_prompt | llm | StrOutputParser()

def explain_no_answer(state):
  result = cannot_answer_chain.invoke({
      "problem": state["plan"], # the plan contains an explanation of why we can't answer the question
      "question": state["question"]
  })

  return {"answer": result}

class WorkflowState(TypedDict):
  question: str
  plan: str
  can_answer: str
  sql_query: str
  sql_result: str
  answer: str

workflow = StateGraph(WorkflowState)

workflow.add_node("check_if_can_answer_question", check_if_can_answer_question)
workflow.add_node("write_query", write_query)
workflow.add_node("execute_query", execute_query)
workflow.add_node("write_answer", write_answer)
workflow.add_node("explain_no_answer", explain_no_answer)

workflow.set_entry_point("check_if_can_answer_question")

workflow.add_conditional_edges(
    "check_if_can_answer_question",
    skip_question, # given the text response from this function,
    { # we choose which node to go to
        "yes": "explain_no_answer",
        "no": "write_query",
    },
)

workflow.add_edge("write_query", "execute_query")
workflow.add_edge("execute_query", "write_answer")

workflow.add_edge("explain_no_answer", END)
workflow.add_edge("write_answer", END)

app = workflow.compile()

try:
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

if __name__ =='__main__':
    print("Invoking LLM...")
    try:
      while True:
          question = input("Ask your Query\n")
          inputs = {"question":  question}
          output = app.invoke(inputs)
          for key in output.keys():
              print(f"{key}:\n {display_text(output[key])}")
              print("=="*50)

    except Exception as e:
       print( e )
