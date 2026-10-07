from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.models import Gemini

from .tools import estimate_budget, recommend_places


TRAVEL_KEYWORDS = [
    "travel",
    "trip",
    "tour",
    "vacation",
    "holiday",
    "destination",
    "itinerary",
    "visit",
    "visiting",
    "sightseeing",
    "hotel",
    "hotels",
    "accommodation",
    "budget",
    "flight",
    "flights",
    "train",
    "transport",
    "transportation",
    "restaurant",
    "restaurants",
    "food",
    "tourist",
    "tourism",
    "things to do",
    "trip plan",
    "travel plan",
]


def is_travel_request(text: str) -> bool:
    text = text.lower().strip()

    return any(keyword in text for keyword in TRAVEL_KEYWORDS)


def travel_domain_guard(callback_context: CallbackContext):
    """
    Block non-travel requests before the agent starts.
    """

    # Get the user's current message
    user_content = callback_context.user_content

    if user_content is None:
        return None

    user_text = ""

    for part in user_content.parts or []:
        if part.text:
            user_text += part.text

    print(f"[GUARD] User request: {user_text}")

    # Non-travel request
    if not is_travel_request(user_text):

        print("[GUARD] Non-travel request blocked.")

        return types.Content(
            role="model",
            parts=[
                types.Part(
                    text=(
                        "Sorry, I can only help with travel planning. "
                        "Please ask me something related to planning a trip, "
                        "destinations, itineraries, travel budgets, places "
                        "to visit, accommodation, transportation, or "
                        "travel activities."
                    )
                )
            ],
        )

    print("[GUARD] Travel request allowed.")

    return None


root_agent = Agent(
    name="travel_planner",

    # model="gemini-3.5-flash",
    model=Gemini(
    model="gemini-3.6-flash",
    retry_options=types.HttpRetryOptions(
        attempts=5,
        initial_delay=2,
        max_delay=10,
        ),
    ),

    description="A personal travel planning agent.",

    before_agent_callback=travel_domain_guard,

    instruction="""
You are a Personal Travel Planner Agent.

You ONLY help users with travel planning.

Valid requests include:
- planning trips
- destinations
- itineraries
- places to visit
- sightseeing
- hotels
- accommodation
- travel budgets
- transportation
- restaurants
- local food
- travel activities
- trip duration
- travel preferences

For valid travel requests:

1. Understand the destination.
2. Understand the duration.
3. Understand the budget.
4. Understand the user's interests.
5. Recommend places.
6. Create a day-wise itinerary.
7. Estimate the budget.
8. Check whether the trip is within budget.
9. Suggest cheaper alternatives if necessary.

Structure travel responses as:

Trip Summary
Recommended Places
Day-wise Itinerary
Budget Estimate
Budget Status
Travel Tips
""",

    tools=[
        estimate_budget,
        recommend_places,
    ],
)