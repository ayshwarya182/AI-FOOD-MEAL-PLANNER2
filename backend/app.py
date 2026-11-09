
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from uuid import uuid4

# Initialize OpenAI client


app = FastAPI(title="AI Food and Meal Planner")


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- FOOD MENU ----------------

VEG_BREAKFAST = [
    {"name": "Idly", "price": 30 ,"calories":5,"protein" :2},
    {"name": "Masala Dosa", "price": 50 ,"calories":10,"protein":5},
    {"name": "Pongal", "price": 40,"calories": 12,"protein":8},
    {"name": "Poori", "price": 45,"calories": 15,"protein":6},
    {"name": "Vada", "price": 35,"calories": 10,"protein":4},
    {"name": "Rava Dosa", "price": 50,"calories": 20,"protein":7},
    {"name": "Upma", "price": 30,"calories": 18,"protein":6},
]

NONVEG_BREAKFAST = [
    {"name": "Egg Dosa", "price": 70,"calories":15,"protein":8},
    {"name": "Egg Omelette", "price": 50,"calories":12,"protein":6},
    {"name": "Chicken Dosa", "price": 90,"calories":10,"protein":5},
    {"name": "Egg Parotta", "price": 70,"calories":15,"protein":6},
    {"name": "Chicken Sandwich", "price": 80,"calories":20,"protein":8},
    {"name": "Chicken Roll", "price": 90,"calories":25,"protein":10},
    {"name": "Egg Kothu Parotta", "price": 80,"calories":18,"protein":7},
    {"name": "Chicken Kothu Parotta", "price": 100,"calories":22,"protein":9},
]

VEG_LUNCH = [
    {"name": "South Indian Meals", "price": 70,"calories":20,"protein":8},
    {"name": "Tomato Rice", "price": 45,"calories":15,"protein":6},
    {"name": "Lemon Rice", "price": 40,"calories":12,"protein":5},
    {"name": "Curd Rice", "price": 35,"calories":10,"protein":4},
    {"name": "Sambar Rice", "price": 50,"calories":18,"protein":7},
    {"name": "Coconut Rice", "price": 45,"calories":15,"protein":6},
    {"name": "Veg Biryani", "price": 80,"calories":25,"protein":10},
    {"name": "Veg Pulao", "price": 70,"calories":20,"protein":8},
]

NONVEG_LUNCH = [
    {"name": "Chicken Biryani", "price": 120,"calories":30,"protein":12},
    {"name": "Chicken Rice", "price": 90,"calories":25,"protein":10},
    {"name": "Chicken Meals", "price": 110,"calories":28,"protein":11},
    {"name": "Mutton Biryani", "price": 150,"calories":35,"protein":14},
    {"name": "Fish Meals", "price": 130,"calories":22,"protein":9},
    {"name": "Fish Biryani", "price": 140,"calories":25,"protein":10},
    {"name": "Mutton Meals", "price": 150,"calories":30,"protein":12},
    {"name": "Chicken Fried Rice", "price": 100,"calories":20,"protein":8},
]

VEG_DINNER = [
    {"name": "Dosa", "price": 40,"calories":10,"protein":4},
    {"name": "Uthappam", "price": 50,"calories":15,"protein":6},
    {"name": "Chapati", "price": 45,"calories":12,"protein":5},
    {"name": "Appam", "price": 50,"calories":15,"protein":6},
    {"name": "Idiyappam", "price": 55,"calories":18,"protein":7},
    {"name": "Parotta", "price": 50,"calories":15,"protein":6},
    {"name": "Paniyaram", "price": 45,"calories":12,"protein":5},
    {"name": "Vegetable Kothu Parotta", "price": 70,"calories":18,"protein":7}
]

NONVEG_DINNER = [
    {"name": "Chicken Parotta", "price": 100,"calories":20,"protein":8},
    {"name": "Chicken Kothu Parotta", "price": 110,"calories":22,"protein":9},
    {"name": "Egg Parotta", "price": 70,"calories":15,"protein":6},
    {"name": "Chicken Dosa", "price": 90,"calories":25,"protein":10},
    {"name": "Chicken Fried Rice", "price": 100,"calories":20,"protein":8},
    {"name": "Chicken Noodles", "price": 100,"calories":25,"protein":10},
    {"name": "Fish Fry Parotta", "price": 130,"calories":30,"protein":12},
    {"name": "Mutton Parotta", "price": 140,"calories":35,"protein":14},
]


# ---------------- REQUEST MODELS ----------------

class MealPlanRequest(BaseModel):
    days: int = Field(ge=1, le=30)
    budget: int = Field(ge=1)
    preference: str


class OrderRequest(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=10, max_length=15)
    address: str = Field(min_length=5)

    # IMPORTANT: list of food names, not dictionaries
    meals: List[str] = Field(min_length=1)

    # Additional information for the selected item
    price: int = Field(ge=0)
    meal_type: str
    day: int = Field(ge=1)


# ---------------- HOME ----------------

@app.get("/")
def home():
    return {
        "success": True,
        "message": "AI Food and Meal Planner Backend is Running"
    }


# ---------------- FOOD LISTS ----------------

def get_food_lists(preference):

    if preference == "Veg":
        return VEG_BREAKFAST, VEG_LUNCH, VEG_DINNER

    if preference == "Non-Veg":
        return NONVEG_BREAKFAST, NONVEG_LUNCH, NONVEG_DINNER

    

    raise HTTPException(
        status_code=400,
        detail="Choose Veg, Non-Veg "
    )


# ---------------- GENERATE MEAL PLAN ----------------

@app.post("/generate-meal-plan")
def generate_meal_plan(request: MealPlanRequest):

    breakfast_list, lunch_list, dinner_list = get_food_lists(
        request.preference
    )

    meal_plan = []

    for day in range(request.days):

        found = False

        for b in range(len(breakfast_list)):
            breakfast = breakfast_list[
                (day + b) % len(breakfast_list)
            ]

            for l in range(len(lunch_list)):
                lunch = lunch_list[
                    (day + l) % len(lunch_list)
                ]

                for d in range(len(dinner_list)):
                    dinner = dinner_list[
                        (day + d) % len(dinner_list)
                    ]

                    total = (
                        breakfast["price"]
                        + lunch["price"]
                        + dinner["price"]
                    )

                    if total <= request.budget:

                        meal_plan.append({
                            "day": day + 1,

                            "breakfast": {
                                **breakfast,
                                "type": "Breakfast",
                                "day": day + 1
                            },

                            "lunch": {
                                **lunch,
                                "type": "Lunch",
                                "day": day + 1
                            },

                            "dinner": {
                                **dinner,
                                "type": "Dinner",
                                "day": day + 1
                            },

                            "total": total
                        })

                        found = True
                        break

                if found:
                    break

            if found:
                break

        if not found:
            return {
                "success": False,
                "error": (
                    f"No complete meal plan for Day {day + 1} "
                    f"within ₹{request.budget}. "
                    "Please increase the daily budget."
                )
            }

    return {
        "success": True,
        "meal_plan": meal_plan
    }


# ---------------- PLACE ORDER ----------------

@app.post("/order")
def place_order(order: OrderRequest):

    # Validate the selected food against the menu
    all_foods = (
        VEG_BREAKFAST
        + NONVEG_BREAKFAST
        + VEG_LUNCH
        + NONVEG_LUNCH
        + VEG_DINNER
        + NONVEG_DINNER
    )

    food_name = order.meals[0]

    matching_food = next(
        (
            item for item in all_foods
            if item["name"].lower() == food_name.lower()
        ),
        None
    )

    if matching_food is None:
        raise HTTPException(
            status_code=400,
            detail="Food item not found in the menu."
        )

    # Use the actual menu price
    if matching_food["price"] != order.price:
        raise HTTPException(
            status_code=400,
            detail="Food price does not match the menu."
        )

    order_id = "ORD-" + uuid4().hex[:8].upper()

    return {
        "success": True,
        "message": "Order placed successfully",
        "order_id": order_id,
        "customer_name": order.name,
        "phone": order.phone,
        "address": order.address,
        "food_items": order.meals,
        "price": matching_food["price"],
        "meal_type": order.meal_type,
        "day": order.day
    }


# ---------------- AI FOOD CHATBOT ----------------

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def food_chat(request: ChatRequest):

    user_message = request.message.strip().lower()

    if not user_message:
        return {
            "reply": "Please enter a question about food or meal planning."
        }

    # Breakfast recommendations
    if any(word in user_message for word in [
        "breakfast", "morning", "morning food"
    ]):
        reply = (
            "Here are some breakfast recommendations! 🍽️\n\n"
            "1. Idly - ₹30\n"
            "2. Pongal - ₹40\n"
            "3. Masala Dosa - ₹50\n"
            "4. Egg Dosa - ₹70\n\n"
            "Choose a meal according to your budget and food preference."
        )

    # Lunch recommendations
    elif any(word in user_message for word in [
        "lunch", "afternoon"
    ]):
        reply = (
            "Here are some lunch recommendations! 🍛\n\n"
            "1. Curd Rice - ₹35\n"
            "2. Lemon Rice - ₹40\n"
            "3. Tomato Rice - ₹45\n"
            "4. Veg Meals - ₹70\n"
            "5. Chicken Biryani - ₹120\n\n"
            "Choose according to your budget and preference."
        )

    # Dinner recommendations
    elif any(word in user_message for word in [
        "dinner", "night"
    ]):
        reply = (
            "Here are some dinner recommendations! 🌙\n\n"
            "1. Dosa - ₹40\n"
            "2. Chapati - ₹45\n"
            "3. Uthappam - ₹50\n"
            "4. Egg Parotta - ₹70\n"
            "5. Chicken Parotta - ₹100"
        )

    # Budget recommendations
    elif any(word in user_message for word in [
        "budget", "cheap", "affordable", "low cost"
    ]):
        reply = (
            "Here are some affordable food options! 💰\n\n"
            "• Idly - ₹30\n"
            "• Upma - ₹30\n"
            "• Curd Rice - ₹35\n"
            "• Vada - ₹35\n"
            "• Lemon Rice - ₹40\n\n"
            "Tell me your budget to get more suitable suggestions."
        )

    # Vegetarian recommendations
    elif any(word in user_message for word in [
        "veg", "vegetarian"
    ]):
        reply = (
            "Here are some vegetarian options! 🥗\n\n"
            "• Idly - ₹30\n"
            "• Pongal - ₹40\n"
            "• Tomato Rice - ₹45\n"
            "• Dosa - ₹40\n"
            "• Veg Meals - ₹70"
        )

    # Non-vegetarian recommendations
    elif any(word in user_message for word in [
        "non veg", "non-veg", "chicken", "egg", "meat"
    ]):
        reply = (
            "Here are some non-vegetarian options! 🍗\n\n"
            "• Egg Omelette - ₹50\n"
            "• Egg Dosa - ₹70\n"
            "• Chicken Rice - ₹90\n"
            "• Chicken Biryani - ₹120\n"
            "• Mutton Biryani - ₹150"
        )

    # Healthy food
    elif any(word in user_message for word in [
        "healthy", "health", "nutrition"
    ]):
        reply = (
            "For a balanced meal, consider combining vegetables, "
            "protein-rich foods, and whole grains. 🥗\n\n"
            "You can try idly with sambar, vegetable meals, or "
            "a meal containing rice, vegetables, and a protein source. "
            "Your best choice depends on your individual dietary needs."
        )

    # Greetings
    elif any(word in user_message for word in [
        "hello", "hi", "hey"
    ]):
        reply = (
            "Hello! 👋 Welcome to your AI Food Assistant.\n\n"
            "I can help you choose breakfast, lunch, dinner, "
            "vegetarian meals, non-vegetarian meals, and budget-friendly food.\n\n"
            "What would you like to eat today?"
        )

    # Default response
    else:
        reply = (
            "I'm your AI Food Assistant! 🍽️\n\n"
            "You can ask me questions such as:\n"
            "• What is my best breakfast in the morning?\n"
            "• Suggest a lunch under ₹100.\n"
            "• Recommend vegetarian food.\n"
            "• What can I eat for dinner?\n"
            "• Suggest healthy food.\n\n"
            "What would you like to know?"
        )

    return {
        "reply": reply
    }
