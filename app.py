from flask import Flask, request, jsonify, send_from_directory
import os
from llm_service import generate_explanation

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/analyze-insurance', methods=['POST'])
def analyze_insurance():
    """
    POST /api/analyze-insurance
    Body: { "join_date": "YYYY-MM-DD" }
    """
    try:
        data = request.json
        join_date = data.get('join_date')
        
        if not join_date:
            return jsonify({'error': '가입일이 필요합니다.'}), 400
        
        result = generate_explanation(join_date)
        
        if "error" in result:
            return jsonify(result), 404
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
