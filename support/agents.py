from django.conf import settings
# from anthropic import Anthropic
from .tools import get_order_details,get_refund_history,check_delivery_status
from .models import Conversation,Message,AgentLog
import requests

from google import genai
from django.conf import settings
from google.genai import types

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

gemini_model = settings.GEMINI_MODEL


from groq import Groq
from datetime import datetime
import json



# client = Anthropic(
#     api_key=settings.ANTHROPIC_API_KEY,  
# )

# anthropic_model = settings.ANTHROPIC_MODEL



#SUPPORT SYSTEM PROMPT --> maya's job description

SUPPORT_SYSTEM_PROMPT ="""
You are Maya, a customer support agent at CoolBreeze AC.
You help customers with issues related to their AC orders.

Your responsibilities:
- Always use your tools to gather facts before responding
- Check order details when customer mentions their order
- Check refund history before making any refund decisions
- Be empathetic but honest

Your personality:
- Friendly and professional
- Patient even when customer is angry
- Clear and concise in your replies
- No emojies

Important rules:
- Always check order details first before responding
- Never approve or deny a refund yourself
- If refund decision is needed — tell customer you are checking with your team
- Never use bold text, bullet points or any markdown formatting. Plain text only.

How to format your reply:
- Never write one long block of text. Break the reply into short lines.
- One idea per line. Separate every line with a blank line.
- Maximum 3 lines, and each line is 1 to 2 short sentences.
- When you report facts from a tool (status, location, dates, tracking number), give each fact its own line instead of stringing them into one sentence.
- Never break a sentence across two lines. A line break only ever separates two different ideas.
- Start with the facts you found, then what you will do next.


"""


#local_ollama

#SUPPORT TOOLS ==> Tool Schemas, that ai agents will read
# SUPPORT_TOOLS = [
#     {
#         "name":"get_order_detail",
#         "description":"Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when customer mentions their order or complains about delivery.",
#         "input_schema":{
#             "type":"object",
#             "properties":{
#                 "order_id":{
#                     "type":"integer",
#                     "description":"The Order ID to look up"
#                 }
#             },
#             "required":["order_id"]
#         },
#     },
#      {
#         "name": "get_refund_history",
#         "description": "Get complete refund history for a user. Use this before making any refund related decisions.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "user_id": {
#                     "type": "integer",
#                     "description": "The user ID to check refund history for"
#                 }
#             },
#             "required": ["user_id"]
#         }
#     },
#       {
#         "name": "check_delivery_status",
#         "description": "Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "tracking_number": {
#                     "type": "string",
#                     "description": "The shipment tracking number"
#                 },
#                 "carrier": {
#                     "type": "string",
#                     "description": "The carrier name for example BlueDart or Delhivery"
#                 }
#             },
#             "required": ["tracking_number", "carrier"]
#         }
#     },
# ]
# SUPPORT_TOOLS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_order_details",
#             "description": "Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when the customer mentions their order or complains about delivery.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "order_id": {
#                         "type": "integer",
#                         "description": "The Order ID to look up"
#                     }
#                 },
#                 "required": ["order_id"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_refund_history",
#             "description": "Get complete refund history for a user. Use this before making any refund related decisions.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "user_id": {
#                         "type": "integer",
#                         "description": "The User ID to check refund history for"
#                     }
#                 },
#                 "required": ["user_id"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "check_delivery_status",
#             "description": "Check the current delivery status using the tracking number and carrier. Use this when the customer complains about delayed or missing delivery.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "tracking_number": {
#                         "type": "string",
#                         "description": "Shipment tracking number"
#                     },
#                     "carrier": {
#                         "type": "string",
#                         "description": "Carrier name such as BlueDart or Delhivery"
#                     }
#                 },
#                 "required": [
#                     "tracking_number",
#                     "carrier"
#                 ]
#             }
#         }
#     }
# ]
SUPPORT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_details",
            "description": "Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when the customer mentions their order or complains about delivery.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The Order ID to look up"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_refund_history",
            "description": "Get complete refund history for a user. Use this before making any refund related decisions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The User ID to check refund history for"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_delivery_status",
            "description": "Check the current delivery status using the tracking number and carrier. Use this when the customer complains about delayed or missing delivery.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_number": {
                        "type": "string",
                        "description": "The shipment tracking number"
                    },
                    "carrier": {
                        "type": "string",
                        "description": "The carrier name, for example BlueDart or Delhivery"
                    }
                },
                "required": [
                    "tracking_number",
                    "carrier"
                ]
            }
        }
    }
]


#Execute_tool() ==> Brifge between claude and py functions (tools)
#Local Ollama
# def execute_tools(tool_name,tool_input):
#     if tool_name=="get_order_details":
#        return get_order_details(tool_input["order_id"])
    
#     if tool_name=="get_refund_history":
#        return get_refund_history(tool_input["user_id"])
    
#     if tool_name=="check_delivery_status":
#        return check_delivery_status(tool_input["tracking_number"],tool_input["carrier"])
    
    
def execute_tools(tool_name, tool_input):
    print("get_order_detail:Executed")
    if tool_name == "get_order_details":
        return get_order_details(
            tool_input["order_id"]
        )

    elif tool_name == "get_refund_history":
        return get_refund_history(
            tool_input["user_id"]
        )

    elif tool_name == "check_delivery_status":
        return check_delivery_status(
            tool_input["tracking_number"],
            tool_input["carrier"]
        )

    return {
        "error": f"Unknown tool: {tool_name}"
    }




#Agent Loops ==> While loop that loops until task is done

#   response =client.messages.create(
    #      model=anthropic_model,
    #      max_tokens=1024,
    #      system=SUPPORT_SYSTEM_PROMPT,
    #      messages=conversation_messages
    #   )
#GEMINI
# def run_support_agent(user_message, conversation_id,order_id,user_id):

#     conv = Conversation.objects.get(id=conversation_id)

#     conversation_messages = []

#     for msg in conv.message.order_by("created_at"):

#         conversation_messages.append(
#             types.Content(
#                 role="user" if msg.role == "user" else "model",
#                 parts=[
#                     types.Part(text=msg.content)
#                 ]
#             )
#         )
    

#     response = client.models.generate_content(
#         model=settings.GEMINI_MODEL,
#         contents=conversation_messages,
#         config=types.GenerateContentConfig(
#             system_instruction=SUPPORT_SYSTEM_PROMPT + f"\n\nContext:This conversation is about #{order_id},user:{user_id}",
#             max_output_tokens=1024,
#         )
#     )

#     final_text= response.text

#     return final_text



OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:7b"
# MODEL = "qwen3.5:latest"



#local ollama
# def run_support_agent(user_message, conversation_id, order_id, user_id):

#     conv = Conversation.objects.get(id=conversation_id)
#     now=datetime.now()
#     conversation_messages = [
#         {
#             "role": "system",
#             "content": SUPPORT_SYSTEM_PROMPT
#             + f"\n\nContext: This conversation is about Order #{order_id}, User ID: {user_id},time is {now}"
#         }
#     ]

#     for msg in conv.message.order_by("created_at"):

#         conversation_messages.append(
#             {
#                 "role": "user" if msg.role == "user" else "assistant",
#                 "content": msg.content
#             }
#         )
#     while True:
#         response = requests.post(
#             OLLAMA_URL,
#             json={
#                 "model": MODEL,
#                 "messages": conversation_messages,
#                 "tools": SUPPORT_TOOLS,
#                 "stream": False
#             }
#         )
#         data = response.json()
        
#         message = data["message"]

#         tool_calls = message.get("tool_calls")

#         if tool_calls:

#             for tool in tool_calls:

#                 print("Tool Name ==>", tool["function"]["name"])
#                 print("Arguments ==>", tool["function"]["arguments"])

#                 tool_name = tool["function"]["name"]
#                 tool_args = tool["function"]["arguments"]

#                 result = execute_tools(tool_name, tool_args)

#                 print("Tool Result ==>", result)

#                 # Later:
#                 # Append assistant message
#                 # Append tool result
#                 # Continue the loop

#         else:

#             final_text = message["content"]

#             return final_text


client = Groq(
    api_key=settings.GROQ_API_KEY
)

groq_model = settings.GROQ_MODEL


def run_support_agent(
    user_message,
    conversation_id,
    order_id,
    user_id
):

    conv = Conversation.objects.get(id=conversation_id)

    now = datetime.now()

    conversation_messages = [
        {
            "role": "system",
            "content": SUPPORT_SYSTEM_PROMPT
            + f"""
            
Context:
This conversation is about Order #{order_id}.
User ID: {user_id}.
Current time: {now}.
"""
        }
    ]

    # Load conversation history
    for msg in conv.message.order_by("created_at"):

        conversation_messages.append({
            "role": "user" if msg.role == "user" else "assistant",
            "content": msg.content
        })

    # Agent loop
    while True:

        response = client.chat.completions.create(
            model=groq_model,
            messages=conversation_messages,
            tools=SUPPORT_TOOLS,
            tool_choice="auto"
        )

        message = response.choices[0].message

        print("Groq response ==> ", response)
        print("finish_reason ==> ", response.choices[0].finish_reason)
        # Check whether Groq requested a tool
        if message.tool_calls:

            # IMPORTANT:
            # Add the assistant's tool-call message
            conversation_messages.append(message)

            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name

                tool_arguments = json.loads(
                    tool_call.function.arguments
                )

                print("Tool name ==> ", tool_name)
                print("Tool arguments ==> ", tool_arguments)
                

                # Execute Django/Python function
                tool_result = execute_tools(
                    tool_name,
                    tool_arguments
                )

                print("Tool result ==> ", tool_result)

                # Send tool result back to Groq
                conversation_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result)
                })

            # Ask Groq to continue after receiving tool results
            continue

        # No tool call = final answer
        final_text = message.content

        return final_text