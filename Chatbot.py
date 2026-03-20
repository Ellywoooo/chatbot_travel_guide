from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

openrouter_api_key = os.environ.get('OPENAI_API_KEY')
if not openrouter_api_key:
    # Don't crash the whole server on deployment.
    # Render can still show the chat page; the /chat call will return a helpful error.
    print("WARNING: OPENAI_API_KEY is not set. The /chat endpoint will fail until it's configured.")
    client = None
else:
    # Note: OpenRouter is compatible with OpenAI's API style, so we reuse the OpenAI client.
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )

# Safe startup debug (do not print the key itself).
if client is not None:
    print(f"OpenRouter API key loaded: yes (length={len(openrouter_api_key)})")

# Home page with a form
@app.route("/")
def home():
    """Home page with a form"""
    return render_template('chat.html')

@app.route("/chat", methods=["POST"])
def chat():
    # Get JSON data from the JavaScript
    data = request.get_json()
    user_message = data.get('message', '')
    conversation_state = data.get('state', 'waiting_for_details')
    user_details = data.get('details', {})

    if conversation_state == 'waiting_for_details':
        # Try to extract travel details from the message
        response, new_state, updated_details = process_travel_request(user_message, user_details)
    elif conversation_state == 'completed':
        # Handle follow-up messages after itinerary is generated
        response, new_state, updated_details = handle_follow_up(user_message, user_details)
    else:
        # Default case - reset to start
        response = "Hi! I'm ready to help you plan your New Zealand trip. Please tell me your travel details in this format: 'X days in [City], I'm X years old'"
        new_state = 'waiting_for_details'
        updated_details = {}
    
    # Return JSON response
    return jsonify({
        'response': response,
        'state': new_state,
        'details': updated_details
    })
def process_travel_request(message, existing_details):
    """Process the travel request and extract details"""
    import re
    message_lower = message.lower()
    details = existing_details.copy()

    # Extract days
    days_match = re.search(r'(\d+)\s*days?', message_lower)
    if days_match:
        details['days'] = days_match.group(1)
    
    # Extract locations (list of NZ cities)
    nz_cities = ['auckland', 'wellington', 'christchurch', 'queenstown', 'rotorua', 'tauranga', 'hamilton', 'dunedin']
    for city in nz_cities:
        if city in message_lower:
            details['location'] = city.title()
            break
    
    # Extract age - try multiple patterns
    age_patterns = [
        r'(\d+)\s*years?\s*old',     # "30 years old"
        r"i'?m\s*(\d+)",             # "I'm 30"
        r'age\s*(\d+)',              # "age 30"
    ]
    
    for pattern in age_patterns:
        age_match = re.search(pattern, message_lower)
        if age_match:
            details['age'] = age_match.group(1)
            break
     
    # Check if any details are missing
    required_fields = ['days', 'location', 'age']
    missing_fields = [field for field in required_fields if field not in details]

    if missing_fields:
        missing_text = ", ".join(missing_fields)
        response = f"I need more information. Missing: {missing_text}. Please use format: 'X days in [City], I'm X years old'"
        return response, 'waiting_for_details', details
    
    else:
        # We have all the details, so we can generate the itinerary
        return generate_ai_itinerary(details), 'completed', details

def handle_follow_up(message, existing_details):
    """Handle simple yes/no response after itinerary"""
    message_lower = message.lower()
    
    # Check if user wants another itinerary
    if 'yes' in message_lower or 'y' in message_lower:
        response = "Great! Please tell me your new travel details: 'X days in [City], I'm X years old'"
        return response, 'waiting_for_details', {}
    
    # If no or anything else
    else:
        response = "Thank you for using my travel assistant! Have an amazing trip! 🌟✈️"
        return response, 'completed', existing_details

def generate_ai_itinerary(details):
    """Process the firm and generate itinerary"""
    if client is None:
        raise RuntimeError("Server is not configured: OPENAI_API_KEY (OpenRouter key) is missing on this host.")
    
    # AI logic
    prompt = f"""
    Create a {details['days']}-day {details['location']}, New Zealand itinerary for a {details['age']}-year-old traveler.

    FORMAT REQUIREMENTS:
    - Use clear headings for each day (DAY 1:, DAY 2:, etc.)
    - Separate breakfast, activities, lunch, dinner with line breaks
    - Include specific addresses and brief descriptions
    - Maximum 3 activities per day
    - Focus on walking-friendly attractions and local gems

    STRUCTURE EACH DAY LIKE THIS:
    DAY X: [Theme]

    🍳 BREAKFAST:
    Restaurant Name (Address) - Description

    🎯 MORNING ACTIVITY:
    Activity Name (Address) - Description

    🍽️ LUNCH:
    Restaurant Name (Address) - Description

    🎯 AFTERNOON ACTIVITY:
    Activity Name (Address) - Description

    🍴 DINNER:
    Restaurant Name (Address) - Description

    Please use this exact format with clear sections and line breaks.
    """

    # Keep track for better error messages in deployments.
    models_tried = []
    models_tried_str = ""
    try:
        # OpenRouter model IDs and availability vary by account/provider.
        # Prefer broadly-available OpenAI-compatible models first, then try Mistral.
        primary_model = os.environ.get("OPENROUTER_MODEL")
        fallback_models = [
            "openai/gpt-4o-mini",
            "openai/gpt-3.5-turbo-0125",
            "mistralai/mistral-7b-instruct",
            "mistralai/mistral-7b-instruct:free",
        ]
        candidate_models = [m.strip() for m in ([primary_model] if primary_model else []) + fallback_models if m and m.strip()]
        models_tried_str = ", ".join(candidate_models)

        last_error = None
        completion = None
        for model in candidate_models:
            try:
                print(f"Trying OpenRouter model: {model}")
                models_tried.append(model)
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional itinerary recommender."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=1500,
                    temperature=0.7,
                )
                break
            except Exception as e:
                last_error = e
                print(f"Model failed: {model} ({type(e).__name__})")

        if completion is None:
            raise last_error if last_error else RuntimeError("No completion returned.")

        return f"🎉 Here's your personalized {details['days']}-day {details['location']} itinerary!\n\n" + completion.choices[0].message.content + "\n\n---\n\nWould you like me to create another itinerary? (yes/no)"
    except Exception as e:
        status_code = getattr(e, "status_code", None)
        return (
            "Sorry, I encountered an error generating your itinerary: "
            f"{type(e).__name__} (status: {status_code}). Details: {e}. "
            f"Models tried: [{models_tried_str}]."
        )
     
# Run the app
if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting app on port {port}")
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Error starting app: {e}")
        raise