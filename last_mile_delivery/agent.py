from enum import Enum
from last_mile_delivery.intent import (
    is_yes,
    is_no,
    is_unavailable,
    extract_date,
)
from last_mile_delivery.data import (
    mark_scheduled,
    mark_neighbor_delivery,
    cancel_delivery,
)


class ConversationState(Enum):
    OPENING = "opening"
    VERIFY_PERSON = "verify_person"
    OFFER_DATES = "offer_dates"
    CONFIRM_DATE = "confirm_date"

    OFFER_NEIGHBOR = "offer_neighbor"
    COLLECT_NEIGHBOR_NAME = "collect_neighbor_name"
    CONFIRM_NEIGHBOR = "confirm_neighbor"

    CLOSE = "close"


class LastMileDeliveryAgent:
    def __init__(self, memory, order):
        self.memory = memory
        self.order = order
        self.state = ConversationState.OPENING
        self.context = {}

    # --------------------------------------------------
    # ENTRY POINT
    # --------------------------------------------------

    def handle_input(self, user_text: str) -> str:
        text = user_text.lower().strip()
        self.memory.add_message("user", user_text)

        if self.state == ConversationState.OPENING:
            response = self._opening()

        elif self.state == ConversationState.VERIFY_PERSON:
            response = self._verify_person(text)

        elif self.state == ConversationState.OFFER_DATES:
            response = self._offer_dates(text)

        elif self.state == ConversationState.CONFIRM_DATE:
            response = self._confirm_date(text)

        elif self.state == ConversationState.OFFER_NEIGHBOR:
            response = self._offer_neighbor(text)

        elif self.state == ConversationState.COLLECT_NEIGHBOR_NAME:
            response = self._collect_neighbor_name(text)

        elif self.state == ConversationState.CONFIRM_NEIGHBOR:
            response = self._confirm_neighbor(text)

        else:
            response = self._close()

        self.memory.add_message("agent", response)
        return response

    # --------------------------------------------------
    # STATES
    # --------------------------------------------------

    def _opening(self) -> str:
        self.state = ConversationState.VERIFY_PERSON
        return f"Hello, am I speaking with {self.order['customer_name']}?"

    # --------------------------------------------------

    def _verify_person(self, text: str) -> str:
        if is_yes(text):
            self.state = ConversationState.OFFER_DATES
            dates = ", ".join(self.order["available_dates"])
            return (
                "We attempted delivery earlier but couldn’t reach you. "
                f"The next available delivery dates are {dates}. "
                "Which date would you prefer?"
            )

        if is_no(text):
            self.state = ConversationState.CLOSE
            return "Sorry for the inconvenience. I’ll end the call now."

        return "Just to confirm, am I speaking with the correct person?"

    # --------------------------------------------------

    def _offer_dates(self, text: str) -> str:
        # USER NOT AVAILABLE AT ALL
        if is_unavailable(text) or is_no(text):
            self.state = ConversationState.OFFER_NEIGHBOR
            return (
                "No problem. If you won’t be available, "
                "we can deliver the parcel to a neighbor or security. "
                "Would that be okay?"
            )

        # USER SELECTS A DATE
        date = extract_date(text, self.order["available_dates"])
        if date:
            self.context["date"] = date
            self.state = ConversationState.CONFIRM_DATE
            return f"Just to confirm, should we deliver the parcel on {date}?"

        return (
            "I didn’t catch a valid date. "
            "You can choose one of the dates I mentioned, "
            "or tell me if you won’t be available."
        )

    # --------------------------------------------------

    def _confirm_date(self, text: str) -> str:
        if is_yes(text):
            mark_scheduled(self.order["order_id"], self.context["date"])
            self.state = ConversationState.CLOSE
            return (
                f"Your delivery has been scheduled for {self.context['date']}. "
                "Thank you for your time."
            )

        if is_no(text):
            self.state = ConversationState.OFFER_DATES
            return "Alright. Please tell me which date works for you."

        return "Please confirm if the delivery date is okay."

    # --------------------------------------------------
    # NEIGHBOR FLOW (NEW + IMPORTANT)
    # --------------------------------------------------

    def _offer_neighbor(self, text: str) -> str:
        if is_yes(text):
            self.state = ConversationState.COLLECT_NEIGHBOR_NAME
            return (
                "Sure. Please tell me the name of the neighbor or security "
                "who can receive the parcel."
            )

        if is_no(text):
            cancel_delivery(self.order["order_id"])
            self.state = ConversationState.CLOSE
            return (
                "Alright. We’ll cancel this delivery attempt for now. "
                "You can reschedule later. Thank you."
            )

        return "Would you like us to deliver the parcel to a neighbor or security?"

    # --------------------------------------------------

    def _collect_neighbor_name(self, text: str) -> str:
        if len(text) < 2:
            return "Please tell me the neighbor’s name."

        self.context["neighbor_name"] = text.title()
        self.state = ConversationState.CONFIRM_NEIGHBOR

        return (
            f"Just to confirm, we will deliver the parcel to "
            f"{self.context['neighbor_name']}. "
            "Please make sure to inform them about this delivery. "
            "Should I proceed?"
        )

    # --------------------------------------------------

    def _confirm_neighbor(self, text: str) -> str:
        if is_yes(text):
            mark_neighbor_delivery(
                self.order["order_id"],
                self.context["neighbor_name"]
            )
            self.state = ConversationState.CLOSE
            return (
                "Perfect. The parcel will be delivered to your neighbor. "
                "Thank you for informing them in advance."
            )

        if is_no(text):
            self.state = ConversationState.COLLECT_NEIGHBOR_NAME
            return "No problem. Please tell me the correct neighbor name."

        return "Please confirm if we should deliver the parcel to the neighbor."

    # --------------------------------------------------

    def _close(self) -> str:
        return "Thank you for your time. Have a good day."
