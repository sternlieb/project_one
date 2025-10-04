import logging
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from data_manager import DataManager

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for client-server communication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Data Manager (handles both SQLite and JSON)
data_manager = DataManager()


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
    """Handle question from client and return answer with full data logging"""
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

        # Get client IP address for logging
        ip_address = request.remote_addr or "unknown"

        # Process question using data manager (handles SQLite + JSON logging)
        response = data_manager.process_question(
            username=username,
            question=question,
            ip_address=ip_address
        )

        # Log successful processing
        logger.info(f"Successfully processed question from user '{username}' (Event ID: {response.get('event_id')})")

        # Return the response (contains answer, metadata, etc.)
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/analytics", methods=["GET"])
def get_analytics():
    """Get system analytics"""
    try:
        analytics = data_manager.get_system_analytics()
        return jsonify(analytics), 200
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/analytics/user/<username>", methods=["GET"])
def get_user_analytics(username):
    """Get analytics for a specific user"""
    try:
        user_analytics = data_manager.get_user_analytics(username)
        if user_analytics:
            return jsonify(user_analytics), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error getting user analytics for {username}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/export/user/<username>", methods=["GET"])
def export_user_data(username):
    """Export all data for a specific user (GDPR compliance)"""
    try:
        export_data = data_manager.export_user_data(username)
        if "error" not in export_data:
            return jsonify(export_data), 200
        else:
            return jsonify(export_data), 404
    except Exception as e:
        logger.error(f"Error exporting data for user {username}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/data/validate", methods=["GET"])
def validate_data():
    """Validate consistency between SQLite and JSON data"""
    try:
        validation_report = data_manager.validate_data_consistency()
        return jsonify(validation_report), 200
    except Exception as e:
        logger.error(f"Error validating data consistency: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/data/backup", methods=["POST"])
def backup_data():
    """Trigger manual backup from SQLite to JSON"""
    try:
        backup_result = data_manager.backup_to_json()
        return jsonify(backup_result), 200
    except Exception as e:
        logger.error(f"Error during backup: {str(e)}")
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
    print("🎯 Random responses loaded from JSON file")
    print("=" * 50)

    # Run the Flask app
    app.run(host="localhost", port=5000, debug=True, use_reloader=True)
