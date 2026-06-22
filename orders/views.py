from django.shortcuts import render,get_object_or_404
from .models import Order,RefundRequest
from django.contrib.auth.decorators import login_required

# Creafrom .modte your views here.
@login_required
def order_list(request):
    orders =Order.objects.filter(user=request.user)
    context ={
        "orders":orders
    }
    return render(request,"orders_list.html",context)

def order_detail(request,order_id):
    order =get_object_or_404(Order,id=order_id,user=request.user)
    #get refund history
    refunds=RefundRequest.objects.filter(order=order)
    print("refunds==>",refunds)
    print("order==>",order)
    context ={
        "order":order,
        "refunds":refunds
    }
    return render(request,"order_detail.html",context)