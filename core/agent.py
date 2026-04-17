import os
from typing import Annotated, TypedDict, Union, List

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate

from tools.inventory_tools import distance_and_price_calculator

# --- AGENT STATE ---
class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    phone_number: str # The current retailer's phone number

# --- TOOLS ---
tools = [distance_and_price_calculator]
tool_node = ToolNode(tools)

# --- MODEL SETUP ---
def get_model():
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    return model.bind_tools(tools)

# --- NODES ---
def call_model(state: AgentState):
    """Calls the LLM to decide on the next action."""
    messages = state["messages"]
    phone_number = state["phone_number"]
    
    # System Prompt as requested
    system_prompt = SystemMessage(content=(
        "You are a fast, B2B wholesale assistant on WhatsApp. "
        "When a retailer expresses intent to buy an item (e.g., 'I want eggs'), "
        "DO NOT ask for their location. Immediately extract the item name and "
        "trigger the `distance_and_price_calculator` tool using the chat's active phone number. "
        f"The active phone number is: {phone_number}. "
        "Format the output cleanly using WhatsApp markdown (*bold*) and emojis."
    ))
    
    # Prepend system prompt if it's the start
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [system_prompt] + messages
        
    model = get_model()
    response = model.invoke(messages)
    
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Determines whether to continue or end the conversation."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return END
    else:
        return "tools"

# --- WORKFLOW GRAPH ---
def create_agent():
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Define the edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    return workflow.compile()

# --- RUNNER ---
def run_agent_workflow(phone_number: str, text: str):
    """
    Orchestrates the agent run for a given user message.
    """
    agent = create_agent()
    
    initial_state = {
        "messages": [HumanMessage(content=text)],
        "phone_number": phone_number
    }
    
    # Run the agent
    result = agent.invoke(initial_state)
    
    # The final message from the LLM
    final_response = result["messages"][-1].content
    
    # Integration Note: In a real app, you'd send `final_response` back to the user 
    # via the WhatsApp Business API (e.g., Twilio Client or Meta Graph API).
    print(f"DEBUG Response to {phone_number}: {final_response}")
    return final_response
