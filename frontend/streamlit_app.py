import streamlit as st
import requests
from pathlib import Path

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Food and Meal Planner",
    page_icon="🍽️",
    layout="wide"
)

# =====================================================
# BACKEND URL
# =====================================================

BACKEND_URL = "http://127.0.0.1:8000" 


# =====================================================
# IMAGE FOLDER
# =====================================================

IMAGE_FOLDER = Path(__file__).resolve().parent / "images"

# =====================================================
# SESSION STATE
# =====================================================

if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = []

if "selected_food" not in st.session_state:
    st.session_state.selected_food = None

if "order_result" not in st.session_state:
    st.session_state.order_result = None


# =====================================================
# IMAGE FUNCTION
# =====================================================

def get_food_image(food_name):

    if not IMAGE_FOLDER.exists():
        return None

    target = food_name.lower().strip()
    target = target.replace("_", " ")
    target = target.replace("-", " ")
    target = " ".join(target.split())

    for file in IMAGE_FOLDER.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in [
            ".jpg", ".jpeg", ".png", ".webp"
        ]:
            continue

        filename = file.stem.lower()
        filename = filename.replace("_", " ")
        filename = filename.replace("-", " ")
        filename = " ".join(filename.split())

        if filename == target:
            return file

    return None


# =====================================================
# TITLE
# =====================================================

st.title("🍽️ AI Food and Meal Planner")

st.write(
    "Generate your daily meal plan within your budget "
    "and order individual food items."
)

st.divider()


# =====================================================
# MEAL PLANNER INPUTS
# =====================================================

st.header("Generate Your Meal Plan")

col1, col2, col3 = st.columns(3)

with col1:
    days = st.number_input(
        "Number of Days",
        min_value=1,
        max_value=30,
        value=1
    )

with col2:
    budget = st.number_input(
        "Daily Budget (₹)",
        min_value=1,
        max_value=5000,
        value=200,
        step=10
    )

with col3:
    preference = st.selectbox(
        "Food Preference",
        ["Veg", "Non-Veg", "Both"]
    )


# =====================================================
# GENERATE MEAL PLAN BUTTON
# =====================================================

if st.button(
    "Generate Meal Plan",
    use_container_width=True
):

    request_data = {
        "days": int(days),
        "budget": int(budget),
        "preference": preference
    }

    try:

        response = requests.post(
            f"{BACKEND_URL}/generate-meal-plan",
            json=request_data,
            timeout=20
        )

        result = response.json()

        if response.status_code == 200:

            if result.get("success"):

                st.session_state.meal_plan = (
                    result["meal_plan"]
                )

                st.session_state.selected_food = None
                st.session_state.order_result = None

                st.success(
                    "Meal plan generated successfully!"
                )

            else:

                st.session_state.meal_plan = []

                st.error(
                    result.get(
                        "error",
                        "Could not generate meal plan."
                    )
                )

        else:

            st.error(
                result.get("detail", response.text)
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to FastAPI. "
            "Start the backend on port 8000."
        )

    except Exception as e:

        st.error(f"Error: {e}")


# =====================================================
# DISPLAY MEAL PLAN
# =====================================================

if st.session_state.meal_plan:

    st.divider()
    st.header("Your Meal Plan")

    for day_plan in st.session_state.meal_plan:

        day_number = day_plan["day"]

        st.subheader(f"Day {day_number}")

        st.write(
            f"Daily total: ₹{day_plan['total']}"
        )

        col1, col2, col3 = st.columns(3)

        foods = [
            ("Breakfast", day_plan["breakfast"], col1),
            ("Lunch", day_plan["lunch"], col2),
            ("Dinner", day_plan["dinner"], col3)
        ]

        for meal_type, food, column in foods:

            with column:

                st.markdown(f"### {meal_type}")

                image_path = get_food_image(
                    food["name"]
                )

                if image_path:

                    st.image(
                        str(image_path),
                        width=250
                    )

                else:

                    st.caption(
                        f"No image found for {food['name']}"
                    )

                st.write(f"**{food['name']}**")
                st.write(f"Price: ₹{food['price']}")

                if st.button(
                    "Order",
                    key=f"order_{day_number}_{meal_type}"
                ):

                    st.session_state.selected_food = food
                    st.session_state.order_result = None

                    st.rerun()

        st.divider()


# =====================================================
# INDIVIDUAL FOOD ORDER FORM
# =====================================================

if st.session_state.selected_food:

    food = st.session_state.selected_food

    st.header("🛒 Order Selected Food")

    st.success(
        f"You selected: {food['name']} — ₹{food['price']}"
    )

    left, right = st.columns(2)

    with left:

        image_path = get_food_image(
            food["name"]
        )

        if image_path:
            st.image(
                str(image_path),
                width=300
            )

        st.subheader(food["name"])

        st.write(f"Price: ₹{food['price']}")
        st.write(f"Meal: {food['type']}")
        st.write(f"Day: {food['day']}")

    with right:

        # Use a form to avoid accidental reruns
        # when entering customer details.

        with st.form("customer_order_form"):

            customer_name = st.text_input(
                "Customer Name"
            )

            customer_phone = st.text_input(
                "Phone Number",
                max_chars=15
            )

            customer_address = st.text_area(
                "Delivery Address"
            )

            submitted = st.form_submit_button(
                "Place Order",
                use_container_width=True
            )

        if submitted:

            if not customer_name.strip():

                st.error("Enter your name.")

            elif not customer_phone.strip().isdigit():

                st.error(
                    "Enter a valid phone number using digits only."
                )

            elif len(customer_phone.strip()) < 10:

                st.error(
                    "Phone number must contain at least 10 digits."
                )

            elif not customer_address.strip():

                st.error("Enter your delivery address.")

            else:

                # =========================================
                # CORRECT ORDER REQUEST
                # =========================================

                order_data = {
                    "name": customer_name.strip(),
                    "phone": customer_phone.strip(),
                    "address": customer_address.strip(),

                    # Send the food name as a string
                    "meals": [
                        food["name"]
                    ],

                    "price": int(food["price"]),
                    "meal_type": food["type"],
                    "day": int(food["day"])
                }

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/order",
                        json=order_data,
                        timeout=20
                    )

                    result = response.json()

                    if response.status_code == 200:

                        if result.get("success"):

                            st.session_state.order_result = result

                            st.success(
                                "Order placed successfully!"
                            )

                        else:

                            st.error(
                                result.get(
                                    "message",
                                    "Order failed."
                                )
                            )

                    else:

                        st.error(
                            result.get(
                                "detail",
                                response.text
                            )
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to backend. "
                        "Make sure FastAPI is running."
                    )

                except Exception as e:

                    st.error(f"Order error: {e}")

        if st.button(
            "Cancel Order",
            use_container_width=True
        ):

            st.session_state.selected_food = None
            st.session_state.order_result = None

            st.rerun()


# =====================================================
# ORDER CONFIRMATION
# =====================================================

if st.session_state.order_result:

    result = st.session_state.order_result

    st.divider()

    st.success("🎉 Your order has been confirmed!")

    st.subheader("Order Details")

    st.write(f"Order ID: {result['order_id']}")
    st.write(f"Customer: {result['customer_name']}")
    st.write(f"Food: {result['food_items'][0]}")
    st.write(f"Price: ₹{result['price']}")
    st.write(f"Meal Type: {result['meal_type']}")
    st.write(f"Day: {result['day']}")
    st.write(f"Phone: {result['phone']}")
    st.write(f"Address: {result['address']}")

    if st.button("Order Another Food"):

        st.session_state.selected_food = None
        st.session_state.order_result = None

        st.rerun()