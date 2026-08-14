from django.http import JsonResponse
import json
from django.http import JsonResponse
import time
from django.shortcuts import get_object_or_404
from .models import Order,Conversation,Message
from .agents import run_support_agent


def chat(request,order_id):
    if request.method=="POST":
        data=json.loads(request.body)
        user_message =data.get("message")


        if not user_message:
            return JsonResponse({"Error":"Empty Message"},status=400)

        order = get_object_or_404(Order,id=order_id,user=request.user)
        
        conversation, created = Conversation.objects.get_or_create(user=request.user,order=order)

        Message.objects.create(conversation=conversation,role="user",content=user_message)

        #Send user message and coversation to LLM
        reply = run_support_agent(user_message,conversation.id,order.id,request.user.id)
        #Store the LLM reply
        Message.objects.create(conversation=conversation,role="agent",content=reply)

        
        
        return JsonResponse({"reply":reply})