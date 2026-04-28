#!/usr/bin/env python3
"""
Debug AI response for May 2027
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import get_ai_response

def debug_ai_response():
    """Debug AI response for May 2027"""
    
    print("=== DEBUGGING AI RESPONSE FOR MAY 2027 ===\n")
    
    message = "schedule meeting for 5 may 2027 at time 5 pm"
    print(f"User message: {message}")
    print()
    
    ai_response = get_ai_response([{"role": "user", "content": message}])
    print(f"AI Response:")
    for key, value in ai_response.items():
        print(f"   {key}: {value}")
    print()
    
    # Check if this is a rejection
    if ai_response.get("action") == "REJECT":
        print("❌ AI rejected the request")
        print(f"   Reason: {ai_response.get('message')}")
    elif ai_response.get("action") == "ASK":
        print("❓ AI is asking for something")
        print(f"   Question: {ai_response.get('message')}")
    else:
        print(f"✅ AI wants to: {ai_response.get('action')}")

if __name__ == "__main__":
    debug_ai_response()
