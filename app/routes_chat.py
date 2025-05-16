"""
Routes for the RAG chatbot
"""

from flask import Blueprint, request, jsonify, session
from app.rag_integration import rag_assistant

# Create blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/message', methods=['POST'])
def message():
    """
    Process a message from the user and return a response
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_message = data['message']
    
    # Initialize conversation history if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    # Add user message to history
    session['chat_history'].append({
        'role': 'user',
        'content': user_message
    })
    
    # Get response from RAG assistant
    response = rag_assistant.get_response(user_message, session['chat_history'])
    
    # Add assistant response to history
    session['chat_history'].append({
        'role': 'assistant',
        'content': response
    })
    
    # Limit history size to prevent session from growing too large
    # Keep only the last 10 messages (5 exchanges)
    if len(session['chat_history']) > 10:
        session['chat_history'] = session['chat_history'][-10:]
    
    # Save session
    session.modified = True
    
    return jsonify({'response': response})

@chat_bp.route('/clear', methods=['POST'])
def clear():
    """
    Clear the chat history
    """
    if 'chat_history' in session:
        session['chat_history'] = []
        session.modified = True
    
    return jsonify({'status': 'success'})

@chat_bp.route('/search', methods=['POST'])
def search():
    """
    Search for a specific project
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'No search query provided'}), 400
    
    query = data['query']
    
    # Search for projects
    result = rag_assistant.search_project(query)
    
    return jsonify({'result': result})
