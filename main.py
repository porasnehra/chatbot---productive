import io
import sqlite3
import os
from typing import TypedDict, Annotated
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import PyPDF2
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

vector_store = None
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)


@tool(description="Perform a basic arithmetic operation (add, sub, mul, div) on two numbers.")
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool(description="Search the uploaded business menu and policy PDF document for rules and context.")
def document_search(query: str) -> str:
    global vector_store
    if not vector_store:
        return "No policy document uploaded yet. Please ask the user to upload the Menu & Policy PDF."
    
    docs = vector_store.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in docs])

tools = [calculator, document_search]
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

conn = sqlite3.connect(database="event_manager.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
            
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    
    vector_store = FAISS.from_texts(chunks, embeddings)
    
    return {"status": "success", "message": "Policy document processed and ready for queries."}

class ChatRequest(BaseModel):
    thread_id: str
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    user_message = HumanMessage(content=request.message)
    
    state = {"messages": [user_message]}
    result = chatbot.invoke(state, config=config)
    
    return {"response": result["messages"][-1].content}
