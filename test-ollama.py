from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="ollama",
    model="llama3.1",
base_url="http://localhost:11434/v1",
    verbose=False,
    temperature=0.0,
    top_p=1
)

if __name__ == '__main__':
    res = llm.invoke( "hi")
    print( res )