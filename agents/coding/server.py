"""
HTTP server for Coding Agent
Provides REST endpoints for /fix and /generate
"""

from flask import Flask, request, jsonify
from agent import CodingAgent
import logging

app = Flask(__name__)
agent = CodingAgent()
agent.start()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "Agent Ready",
        "agent": agent.name,
        "healthy": agent.status == "running"
    })


@app.route('/fix', methods=['POST'])
def fix():
    """
    POST /fix - Fix code using LLM
    
    Request body:
    {
        "error_log": "Error message",
        "file_content": "Current code",
        "file_path": "path/to/file.py",
        "stacktrace": "Stack trace (optional)"
    }
    
    Response:
    {
        "status": "success",
        "fixed_code": "...",
        "patch": "...",
        "explanation": "...",
        "provider": "openrouter",
        "model": "gpt-4"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        error_log = data.get("error_log", "")
        file_content = data.get("file_content", "")
        file_path = data.get("file_path")
        stacktrace = data.get("stacktrace")
        
        if not error_log or not file_content:
            return jsonify({"error": "error_log and file_content are required"}), 400
        
        result = agent.fix_code_endpoint(
            error_log=error_log,
            file_content=file_content,
            file_path=file_path,
            stacktrace=stacktrace
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Fix endpoint error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "explanation": f"Error processing fix request: {str(e)}"
        }), 500


@app.route('/generate', methods=['POST'])
def generate():
    """
    POST /generate - Generate code using LLM
    
    Request body:
    {
        "description": "What code to generate",
        "language": "python",
        "context": "Additional context (optional)",
        "requirements": "Specific requirements (optional)"
    }
    
    Response:
    {
        "status": "success",
        "code": "...",
        "explanation": "...",
        "provider": "openrouter",
        "model": "gpt-4"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        description = data.get("description", "")
        language = data.get("language", "python")
        context = data.get("context")
        requirements = data.get("requirements")
        
        if not description:
            return jsonify({"error": "description is required"}), 400
        
        result = agent.generate_code(
            description=description,
            language=language,
            context=context,
            requirements=requirements
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "explanation": f"Error processing generate request: {str(e)}"
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """Get agent status"""
    return jsonify({
        "agent": agent.name,
        "status": agent.status,
        "id": agent.agent_id
    })


if __name__ == '__main__':
    logger.info("Starting Coding Agent HTTP server on port 8081")
    app.run(host='0.0.0.0', port=8081, debug=False)

