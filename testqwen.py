import os
import sys
import django
from django.http import JsonResponse

# 1. Setup Django environment variables automatically
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_ai_employee_main.settings')
django.setup()

# 2. FIXED: Use an absolute import (Removed the leading dots)
from dj_ai_employees.support.ai.service import ask_llm

def test_ai(request):
    try:
        answer = ask_llm("Hello, Claude")
        return JsonResponse({"response": answer})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# 3. This block runs ONLY when you call this file from the terminal
if __name__ == "__main__":
    print("Testing AI function from terminal...")
    
    # We pass 'None' as a mock request object
    response = test_ai(None)
    
    # Print the clean JSON result to your console
    print(response.content.decode('utf-8'))
