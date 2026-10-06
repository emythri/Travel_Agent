def recommend_places(destination: str, interests: list[str]) -> dict:
    """
    Recommend places based on destination and user interests.
    """

    places = {
        "Jaipur": {
            "history": [
                "Amer Fort",
                "City Palace",
                "Jantar Mantar",
                "Hawa Mahal",
                "Jaigarh Fort",
                "Nahargarh Fort",
            ],
            "food": [
                "Johari Bazaar",
                "MI Road",
                "Masala Chowk",
            ],
        }
    }

    destination_data = places.get(destination, {})

    recommendations = []

    for interest in interests:
        interest_lower = interest.lower()

        if interest_lower in destination_data:
            recommendations.extend(
                destination_data[interest_lower]
            )

    return {
        "destination": destination,
        "recommendations": list(dict.fromkeys(recommendations))
    }


def estimate_budget(
    budget: float,
    duration: int,
    accommodation_per_day: float = 1500,
    food_per_day: float = 700,
    transport_per_day: float = 500,
    activities: float = 1000,
) -> dict:
    """
    Estimate the cost of a trip.
    """

    accommodation = accommodation_per_day * duration
    food = food_per_day * duration
    transport = transport_per_day * duration

    total = (
        accommodation
        + food
        + transport
        + activities
    )

    remaining = budget - total

    return {
        "accommodation": accommodation,
        "food": food,
        "local_transport": transport,
        "activities": activities,
        "estimated_total": total,
        "user_budget": budget,
        "remaining_budget": remaining,
        "within_budget": total <= budget,
    }