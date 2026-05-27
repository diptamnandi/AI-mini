import os
import json
from flask import Flask, render_template, request
from google import genai
from database import init_db, save_log, fetch_history

app = Flask(__name__)

# Boot up and initialize database structures
init_db()

# Initialize the GenAI Client. It automatically looks for the GEMINI_API_KEY environment variable.
client = genai.Client(api_key="AIzaSyBm9Nt_DL_Wphz0u-eOKn3bGtNh_U8czAQ")

@app.route('/', methods=['GET', 'POST'])
def index():
    current_recommendation = None
    
    if request.method == 'POST':
        user_query = request.form.get('query')
        if user_query:
            try:
                # Structure the prompt so the AI outputs exact, easy-to-parse JSON
                prompt = f"""
                You are a professional book recommender. Based on this request: "{user_query}", 
                suggest exactly ONE great book. 
                You must respond exclusively with a valid raw JSON object matching these fields:
                {{
                    "title": "Book Title Here",
                    "author": "Author Name Here",
                    "reason": "A 2-3 sentence engaging justification of why it fits."
                }}
                Do not wrap the response in markdown code blocks like ```json. Return pure text JSON string.
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                # Sanitize typical markdown formatting if wrapped by accident
                clean_text = response.text.strip().strip("`").replace("json", "", 1).strip()
                data = json.loads(clean_text)
                
                # Save into SQLite DB 
                save_log(user_query, data.get('title'), data.get('author'), data.get('reason'))
                current_recommendation = data
                
            except Exception as e:
                current_recommendation = {
                    "title": "Oops! Something went wrong.",
                    "author": "System Error",
                    "reason": f"Failed to retrieve or parse recommendations: {str(e)}"
                }

    # Gather historical database rows to display on the dashboard
    history = fetch_history()
    return render_template('index.html', recommendation=current_recommendation, history=history)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').strip().lower() in ('1', 'true', 'yes', 'on')
    app.run(debug=debug_mode)