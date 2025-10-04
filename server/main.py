import logging
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for client-server communication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Routes
@app.route("/")
def home():
    """Home route - basic server info"""
    return jsonify(
        {
            "message": "Question & Answer Server",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "server": "running",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        200,
    )


@app.route("/ask", methods=["POST"])
def handle_question():
    """Handle question from client and return answer"""
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate that we have the required data
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if "username" not in data:
            return jsonify({"error": "No username provided"}), 400
            
        if "question" not in data:
            return jsonify({"error": "No question provided"}), 400

        # Extract and validate username and question
        username = data["username"].strip()
        question = data["question"].strip()

        if not username:
            return jsonify({"error": "Username cannot be empty"}), 400
            
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400

        # Log the received username and question
        logger.info(f"Received question from user '{username}': {question}")

        # Process the question and generate response
        # For now, simply return "answer" as requested
        answer = "answer"

        # Log the response
        logger.info(f"Sending answer to user '{username}': {answer}")

        # Return the answer with username included
        return (
            jsonify(
                {
                    "answer": answer,
                    "question": question,
                    "username": username,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Question & Answer Server Starting...")
    print("📡 Server will run on: http://localhost:5000")
    print("🔄 CORS enabled for client communication")
    print("=" * 50)

    # Run the Flask app
    app.run(host="localhost", port=5000, debug=True, use_reloader=True)
