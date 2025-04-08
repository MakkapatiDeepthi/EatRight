from flask import Blueprint, request, jsonify
from .bot import get_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    print("Received POST request at /chat")  # Confirm request received
    data = request.get_json()
    print(f"Received data: {data}")  # Log the received data

    user_message = data.get('message', '')
    print(f"User message: {user_message}")  # Confirm message content

    bot_response = get_chatbot_response(user_message)
    print(f"Bot response: {bot_response}")  # Check the generated response

    return jsonify({"response": bot_response})
