import random

import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

API_URL = "https://www.themealdb.com/api/json/v1/1"


def get_recipe_for(main_ingredient: str) -> dict:
    """
    Fetch a random recipe with a specified main ingredient.
    The recipes are requested from "themealdb" API.
    """
    # 1. Fetch the list of meals that use `main_ingredient`
    response = requests.get(f"{API_URL}/filter.php", params={"i": main_ingredient}, timeout=10)
    response.raise_for_status()
    meals = response.json()["meals"]
    if not meals:  # The API returns {"meals": null} when nothing matches
        return None

    # 2. Choose a random meal from the list
    meal_id = random.choice(meals)["idMeal"]

    # 3. Fetch the full recipe of the chosen meal
    response = requests.get(f"{API_URL}/lookup.php", params={"i": meal_id}, timeout=10)
    response.raise_for_status()
    meal = response.json()["meals"][0]

    # 4. Pair strIngredientN with strMeasureN, skipping empty slots ("" or None)
    ingredients = {}
    for i in range(1, 21):
        ingredient = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if ingredient:
            ingredients[ingredient] = measure

    return dict(
        name=(meal["strMeal"] or "").strip(),
        image=meal["strMealThumb"],
        video=meal["strYoutube"],
        instructions=meal["strInstructions"],
        ingredients=ingredients,
    )


@app.route('/')
def index():
    """
    Renders and returns the main page HTML.
    """
    return render_template("index.html")


@app.route("/recipe/<ingredient>")
def recipe(ingredient):
    """
    Renders and returns an HTML page with a random recipe for a given main ingredient.
    """
    # BONUS:
    # If there are no meals for a given ingredient, return a 404 NOT FOUND error response.
    # Hint: Read the documentation of flask. This is a bonus :P
    return render_template("recipe.html",
                           ingredient=ingredient,
                           recipe=get_recipe_for(ingredient))


@app.route("/recipe/<ingredient>/json")
def recipe_json(ingredient):
    """
    Returns a random recipe for a given main ingredient as JSON.
    """
    return jsonify(get_recipe_for(ingredient))


# BONUS:
# Add these endpoints:
# 1. "/personal" with POST method:
#    - Receives a recipe JSON in the request body, and adds it to a list of personal recipes.
#    - Make the list persistent in a JSON file.
#    - Redirect the client to the page of the newly saved recipe.
#    - Hint: `flask.request`
#    - Hint 2: `flask.redirect`
#    - Hint 3: Use `requests` to check if it works.
# 2. "/personal/<name>/<int:json>" with GET method:
#    - Returns the recipe page if `json == 0`, or a JSON if `json == 1`.
#    - Return a 404 response for flag values other than 0 or 1.
# 3. "/personal/<name>" with DELETE method:
#    - Delete the recipe with the given name
# 4. "/personal/all" with GET method:
#    - Returns a JSON with the list of personal recipes.


# EXTRA BONUS:
# Change the "/recipe" endpoints above to search the personal list as well.

if __name__ == '__main__':
    app.run(debug=True)
