import requests
from config import Config

spoonacular_api_key = Config.SPOONACULAR_API_KEY

def get_chatbot_response(message):
    try:
        print(f"Received message: {message}")  # Log the received message
        
        # Check if the message contains the word 'recipe'
        if "recipe" in message.lower():
            dish_name = extract_dish_name(message)
            print(f"Extracted dish name: {dish_name}")  # Log extracted dish name
            
            if dish_name:
                return get_recipe(dish_name)
            else:
                return "Could you please specify the dish name for the recipe?"
        else:
            print("No 'recipe' keyword found in the message.")  # Log if recipe keyword isn't found
            return "Sorry, I can only assist with recipes at the moment."

    except Exception as e:
        print(f"Error in chatbot response: {str(e)}")  # Log unexpected errors
        return f"An error occurred: {str(e)}"

def extract_dish_name(message):
    # Log the message before attempting extraction
    print(f"Attempting to extract dish name from message: {message}")

    keywords = ["recipe for", "how to make", "cook", "prepare"]
    for keyword in keywords:
        if keyword in message.lower():
            dish_name = message.lower().split(keyword)[-1].strip()
            return dish_name
    # Fallback if keywords aren't found
    return None

def get_recipe(dish_name):
    try:
        print(f"Fetching recipe for: {dish_name}")  # Log API request attempt

        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "query": dish_name,
            "number": 1,
            "apiKey": spoonacular_api_key
        }

        response = requests.get(url, params=params)
        print(f"API Response Status: {response.status_code}")
        print(f"API Raw Content: {response.text}")

        if response.status_code == 404:
            return "Recipe not found. Please check the dish name or API key."

        response.raise_for_status()

        data = response.json()
        if data.get("results"):
            recipe = data["results"][0]
            recipe_id = recipe.get("id")

            if not recipe_id:
                return "Couldn't find a valid recipe ID."

            detailed_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
            detailed_response = requests.get(detailed_url, params={"apiKey": spoonacular_api_key})

            if detailed_response.status_code == 404:
                return "Detailed recipe information not found."

            detailed_data = detailed_response.json()
            source_url = detailed_data.get("sourceUrl", "No source URL available")

            return f"Here's a recipe for {recipe['title']}!\n\nYou can find more details here: {source_url}"
        else:
            return f"Sorry, I couldn't find a recipe for {dish_name}."

    except Exception as e:
        print(f"An unexpected error occurred during API request: {str(e)}")
        return f"An unexpected error occurred: {str(e)}"
