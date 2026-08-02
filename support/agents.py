from django.conf import settings
from anthropic import Anthropic
from .tools import get_order_details,get_refund_history,check_delivery_status
from .models import Conversation,Message,AgentLog
client = Anthropic(
    api_key=settings.ANTHROPIC_API_KEY,  
)

anthropic_model = settings.ANTHROPIC_MODEL

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
- Keep replies concise and conversational. Maximum 3-4 sentences. No long paragraphs.

"""



#SUPPORT TOOLS ==> Tool Schemas, that ai agents will read
SUPPORT_TOOLS = [
    {
        "name":"get_order_detail",
        "description":"Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when customer mentions their order or complains about delivery.",
        "input_schema":{
            "type":"object",
            "properties":{
                "order_id":{
                    "type":"integer",
                    "description":"The Order ID to look up"
                }
            },
            "required":["order_id"]
        },
    },
     {
        "name": "get_refund_history",
        "description": "Get complete refund history for a user. Use this before making any refund related decisions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "The user ID to check refund history for"
                }
            },
            "required": ["user_id"]
        }
    },
      {
        "name": "check_delivery_status",
        "description": "Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tracking_number": {
                    "type": "string",
                    "description": "The shipment tracking number"
                },
                "carrier": {
                    "type": "string",
                    "description": "The carrier name for example BlueDart or Delhivery"
                }
            },
            "required": ["tracking_number", "carrier"]
        }
    },
]




#Execute_tool() ==> Brifge between claude and py functions (tools)
def execute_tools(tool_name,tool_input):
    if tool_name==get_order_details:
       return get_order_details(tool_input["order_id"])
    
    if tool_name==get_refund_history:
       return get_refund_history(tool_input["user_id"])
    
    if tool_name==check_delivery_status:
       return check_delivery_status(tool_input["tracking_number"],tool_input["carrier"])
    
    





#Agent Loops ==> While loop that loops until task is done
def run_support_agent(user_message,conversation_id):
   conv = Conversation.objects.get(id=conversation_id)

   conversation_messages = []
   for msg in conv.message.order_by("created_at"):
      conversation_messages.append({
         "role":msg.role,
         "content":msg.content
      })
      #Send this conversation to LLM
      response =client.messages.create(
         model=anthropic_model,
         max_tokens=1024,
         system=SUPPORT_SYSTEM_PROMPT,
         messages=conversation_messages
      )
      print("LLM response ==>",response)