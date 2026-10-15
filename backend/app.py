from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from uuid import uuid4


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
    {"name": "Idly", "price": 30},
    {"name": "Masala Dosa", "price": 50},
    {"name": "Pongal", "price": 40},
    {"name": "Poori", "price": 45},
    {"name": "Vada", "price": 35},
    {"name": "Rava Dosa", "price": 50},
    {"name": "Upma", "price": 30},
    {"name": "Ven Pongal", "price": 40},
]

NONVEG_BREAKFAST = [
    {"name": "Egg Dosa", "price": 70},
    {"name": "Egg Omelette", "price": 50},
    {"name": "Chicken Dosa", "price": 90},
    {"name": "Egg Parotta", "price": 70},
    {"name": "Chicken Sandwich", "price": 80},
    {"name": "Chicken Roll", "price": 90},
    {"name": "Egg Kothu Parotta", "price": 80},
    {"name": "Chicken Kothu Parotta", "price": 100},
]

VEG_LUNCH = [
    {"name": "South Indian Meals", "price": 70},
    {"name": "Tomato Rice", "price": 45},
    {"name": "Lemon Rice", "price": 40},
    {"name": "Curd Rice", "price": 35},
    {"name": "Sambar Rice", "price": 50},
    {"name": "Coconut Rice", "price": 45},
    {"name": "Veg Biryani", "price": 80},
    {"name": "Veg Pulao", "price": 70},
]

NONVEG_LUNCH = [
    {"name": "Chicken Biryani", "price": 120},
    {"name": "Chicken Rice", "price": 90},
    {"name": "Chicken Meals", "price": 110},
    {"name": "Mutton Biryani", "price": 150},
    {"name": "Fish Meals", "price": 130},
    {"name": "Fish Biryani", "price": 140},
    {"name": "Mutton Meals", "price": 150},
    {"name": "Chicken Fried Rice", "price": 100},
]

VEG_DINNER = [
    {"name": "Dosa", "price": 40},
    {"name": "Uthappam", "price": 50},
    {"name": "Chapati", "price": 45},
    {"name": "Appam", "price": 50},
    {"name": "Idiyappam", "price": 55},
    {"name": "Parotta", "price": 50},
    {"name": "Paniyaram", "price": 45},
    {"name": "Vegetable Kothu Parotta", "price": 70},
]

NONVEG_DINNER = [
    {"name": "Chicken Parotta", "price": 100},
    {"name": "Chicken Kothu Parotta", "price": 110},
    {"name": "Egg Parotta", "price": 70},
    {"name": "Chicken Dosa", "price": 90},
    {"name": "Chicken Fried Rice", "price": 100},
    {"name": "Chicken Noodles", "price": 100},
    {"name": "Fish Fry Parotta", "price": 130},
    {"name": "Mutton Parotta", "price": 140},
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

    if preference == "Both":
        return (
            VEG_BREAKFAST + NONVEG_BREAKFAST,
            VEG_LUNCH + NONVEG_LUNCH,
            VEG_DINNER + NONVEG_DINNER
        )

    raise HTTPException(
        status_code=400,
        detail="Choose Veg, Non-Veg or Both."
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