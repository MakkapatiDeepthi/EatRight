from flask import Flask, render_template, request, redirect, url_for, jsonify,session ,flash
import os
import requests
from dotenv import load_dotenv
import time
import random
import json
import pandas as pd
from datetime import datetime


load_dotenv()

app = Flask(__name__)
app.secret_key = 'b61c47b4050cbfbf89d0c01b1dcd67d8cdeab76939cf2bb7d50263b398cb658e'



# Nutritionix API credentials
NUTRITIONIX_APP_ID = os.getenv('NUTRITIONIX_APP_ID')  # Correct variable names
NUTRITIONIX_API_KEY = os.getenv('NUTRITIONIX_API_KEY')

RATE_LIMIT_DELAY = 0.5

USER_FILE = 'data/users.json'
HISTORY_FILE = 'data/diet_history.json'



# Load food data
food_items = {}
try:
    with open('food_data.json', 'r') as f:
        food_items = json.load(f)
    print("Food data loaded successfully.")
except FileNotFoundError:
    print("Error: food_data.json not found.")




if not os.path.exists(USER_FILE):
    users = []  # Empty list to start with
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)



def load_users():
    with open('data/users.json', 'r', encoding='utf-8') as f:  # ✅ Add encoding here
        return json.load(f)


def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)




@app.route('/')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    username = user['username']
    diet_history = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
            diet_history = data.get(username, [])

    return render_template('profile.html', user=user, diet_history=diet_history)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        users = load_users()

        for user in users:
            if identifier in [user['email'], user['username'], user['mobile']] and user['password'] == password:
                session['user'] = user
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))

        flash('Invalid login credentials.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        users = load_users()

        for user in users:
            if user['email'] == email or user['username'] == username or user['mobile'] == mobile:
                flash('User already exists!', 'danger')
                return redirect(url_for('register'))

        users.append({
            'username': username,
            'email': email,
            'mobile': mobile,
            'password': password
        })

        save_users(users)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user']['username'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/calorie-calculator', methods=['GET', 'POST'])
def calorie_calculator():
    if request.method == 'POST':
        try:  # Add a try-except block for potential errors
            weight = float(request.form['weight'])
            height = float(request.form['height'])
            age = int(request.form['age'])
            activity = request.form['activity']

            bmr = 10 * weight + 6.25 * height - 5 * age + 5

            activity_multipliers = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'intense': 1.725
            }
            calories = bmr * activity_multipliers.get(activity, 1.2)

            return render_template('calorie_result.html', calories=round(calories, 2))
        except ValueError:
            return render_template('calorie_calculator.html', error="Invalid input. Please enter numbers.")
        except Exception as e:  # Catch other potential errors
            return render_template('calorie_calculator.html', error=f"An error occurred: {e}")

    return render_template('calorie_calculator.html')


@app.route('/diet_planner', methods=['GET', 'POST'])
def diet_planner():
    meal_plan = {}
    if request.method == 'POST':
        try:
            caloric_goal = int(request.form['calories'])
            diet_type = request.form['diet_type']

            print(f"Caloric Goal: {caloric_goal}, Diet Type: {diet_type}")

            if not (100 <= caloric_goal <= 3000):
                return render_template('diet_planner.html', error="Calorie goal must be between 100 and 3000.")

            if diet_type not in ('Veg', 'Non-Veg'):
                return render_template('diet_planner.html', error="Invalid diet type.")

            # Define meal distribution (percentage of total calories)
            meal_distribution = {
                'Breakfast': 0.25 * caloric_goal,
                'Lunch': 0.35 * caloric_goal,
                'Dinner': 0.30 * caloric_goal,
                'Snacks': 0.10 * caloric_goal
            }

            # Generate meal plan
            for meal, calorie_target in meal_distribution.items():
                print(f"Processing meal: {meal}, Calorie Target: {calorie_target}")
                meal_plan[meal] = choose_food_for_meal(meal, calorie_target, diet_type)

            # Check if total calories meet the goal
            total_calories = sum(meal['total_calories'] for meal in meal_plan.values())
            # After meal plan is finalized and total_calories check
            if total_calories < caloric_goal * 0.95:
                print(f"Warning: Total calories ({total_calories}) are below 95% of the goal ({caloric_goal}).")
                meal_plan = adjust_meal_plan(meal_plan, caloric_goal, diet_type)

            # ✅ Save diet history here if user is logged in
            if 'user' in session:
                save_diet_history(session['user']['username'], meal_plan)


            print(f"Meal Plan: {meal_plan}")
            return render_template('diet_plan_result.html', meal_plan=meal_plan)

        except ValueError:
            return render_template('diet_planner.html', error="Invalid calorie input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return render_template('diet_planner.html', error=f"An error occurred: {str(e)}")

    return render_template('diet_planner.html', meal_plan=meal_plan)



def choose_food_for_meal(meal, calorie_target, diet_type):
    print(f"Choosing food for: {meal}, {diet_type}")
    chosen_foods = []
    current_calories = 0

    if not food_items:
        return {"items": [], "total_calories": 0, "message": "No food data available."}

    if meal in food_items and diet_type in food_items[meal]:
        available_foods = food_items[meal][diet_type]
        available_foods.sort(key=lambda x: x['calories'])

        max_iterations = 100
        iteration_count = 0
        selected_food_names = set()

        while (len(chosen_foods) < 2 or current_calories < calorie_target * 0.95) and iteration_count < max_iterations:
            remaining_calories = calorie_target - current_calories
            suitable_foods = [
                food for food in available_foods
                if food['calories'] <= remaining_calories and food['name'] not in selected_food_names
            ]

            if not suitable_foods:
                break

            chosen_food = random.choice(suitable_foods)
            chosen_foods.append(chosen_food)
            selected_food_names.add(chosen_food['name'])
            current_calories += chosen_food['calories']
            iteration_count += 1

        return {"items": chosen_foods, "total_calories": current_calories}

    else:
        return {"items": [], "total_calories": 0, "message": f"No suitable {diet_type} food found for {meal}"}


def adjust_meal_plan(meal_plan, caloric_goal, diet_type):
    total_calories = sum(meal['total_calories'] for meal in meal_plan.values())
    remaining_calories = caloric_goal - total_calories

    max_iterations = 100
    iteration_count = 0

    while remaining_calories > 0 and iteration_count < max_iterations:
        for meal, meal_data in meal_plan.items():
            if remaining_calories <= 0:
                break

            extra_item = choose_food_for_meal(meal, remaining_calories, diet_type)
            if extra_item['items']:
                item = extra_item['items'][0]
                meal_data['items'].append(item)
                meal_data['total_calories'] += item['calories']
                remaining_calories -= item['calories']

            iteration_count += 1

    return meal_plan


def save_diet_history(username, meal_plan):
    history_data = {}

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                history_data = json.load(f)
                if not isinstance(history_data, dict):
                    history_data = {}  # Reset if it's not a dict
            except json.JSONDecodeError:
                history_data = {}  # Reset if file is corrupted

    user_history = history_data.get(username, [])

    user_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "meal_plan": {
            meal: [
                {"name": food['name'], "calories": food['calories']}
                for food in meal_data['items']
            ]
            for meal, meal_data in meal_plan.items()
        }
    })

    history_data[username] = user_history

    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)

        

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if "recipe" in user_message.lower() or "how do i make" in user_message.lower():
        response = get_recipe(user_message)
    elif "calorie" in user_message.lower() or "how many calories" in user_message.lower():
        response = get_calorie_info(user_message)
    else:
        response = "Sorry, I can only provide recipes and calorie information."

    return jsonify({'response': response})


def get_recipe(query):
    url = 'https://trackapi.nutritionix.com/v2/search/instant'
    headers = {
        "x-app-id": '3ff80e11',
        "x-app-key": '119a3c44c7110bcdbbe6a977ccbe7b41'
    }
    params = {"query": query, "branded": "false"}

    try:
        time.sleep(RATE_LIMIT_DELAY)
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('common'):
            food_name = data['common'][0]['food_name']
            recipe = generate_recipe(food_name)  # Placeholder for recipe generation
            if recipe:
                return f"Here's a recipe for {food_name}:\n{recipe}"
            else:
                return f"I couldn't find a recipe for {food_name}."
        elif data.get('branded'): # Check if there are any branded food items
            food_name = data['branded'][0]['food_name']
            recipe = generate_recipe(food_name) # Call function to generate recipe
            if recipe:
                return f"Here's a recipe for {food_name}:\n{recipe}"
            else:
                return f"I couldn't find a recipe for {food_name}."
        else:
            return "I couldn't find food information for that. Please try a different query."

    except requests.exceptions.RequestException as e:
        return f"Error fetching recipe information: {str(e)}"
    except (KeyError, IndexError, TypeError) as e:
        return f"Error processing the recipe response: {str(e)}. Raw Response: {data if 'data' in locals() else 'N/A'}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def get_calorie_info(query):
    url = 'https://trackapi.nutritionix.com/v2/search/instant'
    headers = {
        "x-app-id": '3ff80e11',
        "x-app-key": '119a3c44c7110bcdbbe6a977ccbe7b41'
    }
    params = {"query": query, "branded": "false"}

    nutrient_url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    nutrient_headers = {
        "x-app-id": '3ff80e11',
        "x-app-key": '119a3c44c7110bcdbbe6a977ccbe7b41',
        "Content-Type": "application/json"
    }

    try:
        time.sleep(RATE_LIMIT_DELAY)

        search_response = requests.get(url, headers=headers, params=params)
        search_response.raise_for_status()
        search_data = search_response.json()

        if search_data.get('common'):
            food_name = search_data['common'][0]['food_name']

            nutrient_data = {"query": food_name}
            nutrient_response = requests.post(nutrient_url, headers=nutrient_headers, json=nutrient_data)
            nutrient_response.raise_for_status()
            nutrient_data = nutrient_response.json()

            if nutrient_data.get('foods'):
                food = nutrient_data['foods'][0]
                calories = food.get('nf_calories')
                serving_qty = food.get('serving_qty')
                serving_unit = food.get('serving_unit')

                serving_info = ""
                if serving_qty and serving_unit:
                    serving_info = f"({serving_qty} {serving_unit})"
                elif serving_qty:
                    serving_info = f"({serving_qty})"
                elif serving_unit:
                    serving_info = f"({serving_unit})"

                if calories is not None:
                    return f"{food['food_name']} {serving_info} contains approximately {calories} calories."
                else:
                    return f"Calorie information not found for {food['food_name']}."
            else:
                return f"No detailed nutrient information found for {food_name}. Raw Nutrient Data: {nutrient_data}"

        else:
            return f"I couldn't find food information for that. Please try a different query. Raw Search Data: {search_data}"

    except requests.exceptions.RequestException as e:
        return f"Error fetching information: {str(e)}"
    except (KeyError, IndexError, TypeError) as e:
        return f"Error processing the response: {str(e)}. Raw Search Data: {search_data if 'search_data' in locals() else 'N/A'}, Raw Nutrient Data: {nutrient_data if 'nutrient_data' in locals() else 'N/A'}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def generate_recipe(food_name):
    ingredients = food_name.lower().split()  # Split into ingredients

    all_recipes = []  # Store recipes for all ingredients
    for ingredient in ingredients:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={ingredient}"
        print(f"Request URL for {ingredient}: {url}")  # Print URL for each ingredient
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            print(f"Raw JSON Response for {ingredient}: {data}") # Print response for each ingredient

            if data.get('meals'):
                all_recipes.extend(data['meals'])  # Add all meals for the current ingredient
        except requests.exceptions.RequestException as e:
            return f"Error fetching recipe for {ingredient}: {str(e)}"

    if all_recipes:
        # **Improved Recipe Selection Logic:**
        # 1. Exact Match (if available):
        for recipe in all_recipes:
            if food_name.lower() in recipe.get('strMeal').lower():
                return format_recipe(recipe) # Helper function (see below)

        # 2. Contains Match (if available):
        for recipe in all_recipes:
            title = recipe.get('strMeal').lower()
            if all(ingredient in title for ingredient in ingredients):
                return format_recipe(recipe)

        # 3. Return the first available recipe (if no better match):
        return format_recipe(all_recipes[0])  # Or implement more sophisticated logic

    else:
        return f"No recipes found for {food_name}."


def format_recipe(meal):  # Helper function to format the recipe
    title = meal.get('strMeal')
    instructions = meal.get('strInstructions')

    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ingredient and measure:
            ingredients.append(f"- {ingredient} ({measure})")
        elif ingredient:
            ingredients.append(f"- {ingredient}")

    recipe_str = f"**{title}**\n\n**Ingredients:**\n"
    recipe_str += "\n".join(ingredients)
    recipe_str += f"\n\n**Instructions:**\n{instructions if instructions else 'Instructions not available.'}"
    return recipe_str



# Function to fetch calorie information using Nutritionix API

    
# Run the app
if __name__ == "__main__":
    app.run(port=5001, debug=True)