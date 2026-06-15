import random
import uuid
from datetime import datetime
from enum import Enum


class EventType(Enum):
    PAGE_VIEW = "page_view"
    PURCHASE_COMPLETE = "purchase_complete"
    PURCHASE_CANCEL = "purchase_cancel"


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    VIRTUAL_ACCOUNT = "virtual_account"
    BANK_TRANSFER = "bank_transfer"
    SAMSUNG_PAY = "samsung_pay"
    KAKAO_PAY = "kakao_pay"
    PAYPAL = "paypal"


EVENT_TYPE_WEIGHTS = {
    EventType.PAGE_VIEW: 70,
    EventType.PURCHASE_COMPLETE: 25,
    EventType.PURCHASE_CANCEL: 5,
}

MIN_USER_ID = 1
MAX_USER_ID = 10_000_000
MIN_LECTURE_ID = 1
MAX_LECTURE_ID = 10_000_000
MIN_AMOUNT = 10_000
MAX_AMOUNT = 1_000_000
AMOUNT_UNIT = 10_000


class EventGenerator:
    def __init__(self):
        self._open_orders: dict[int, tuple] = {}
        self._next_order_id = 1

    def generate(self, event_type: EventType = None, timestamp: datetime = None) -> dict:
        if event_type is None:
            event_type = self._pick_event_type()
        if timestamp is None:
            timestamp = datetime.now()

        event_type = self._resolve_event_type(event_type)
        context = self._resolve_context(event_type)

        return {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type.value,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            **context,
        }

    def _pick_event_type(self) -> EventType:
        return random.choices(
            list(EVENT_TYPE_WEIGHTS.keys()),
            weights=list(EVENT_TYPE_WEIGHTS.values()),
            k=1,
        )[0]

    def _resolve_event_type(self, event_type: EventType = None) -> EventType:
        if event_type == EventType.PURCHASE_CANCEL and not self._open_orders:
            return EventType.PAGE_VIEW
        return event_type

    def _resolve_context(self, event_type: EventType) -> dict:
        if event_type == EventType.PURCHASE_COMPLETE:
            return self._purchase_complete_context()
        if event_type == EventType.PURCHASE_CANCEL:
            return self._purchase_cancel_context()
        return self._page_view_context()

    def _page_view_context(self) -> dict:
        return {
            "order_id": None,
            "user_id": random.randint(MIN_USER_ID, MAX_USER_ID),
            "lecture_id": random.randint(MIN_LECTURE_ID, MAX_LECTURE_ID),
            "amount": None,
            "payment_method": None,
        }

    def _purchase_complete_context(self) -> dict:
        order_id = self._next_order_id
        self._next_order_id += 1

        user_id = random.randint(MIN_USER_ID, MAX_USER_ID)
        lecture_id = random.randint(MIN_LECTURE_ID, MAX_LECTURE_ID)
        amount = random.randrange(MIN_AMOUNT, MAX_AMOUNT, AMOUNT_UNIT)
        payment_method = random.choice(list(PaymentMethod)).value

        self._open_orders[order_id] = (user_id, lecture_id, amount, payment_method)
        return {
            "order_id": order_id,
            "user_id": user_id,
            "lecture_id": lecture_id,
            "amount": amount,
            "payment_method": payment_method,
        }

    def _purchase_cancel_context(self) -> dict:
        order_id = random.choice(list(self._open_orders.keys()))
        user_id, lecture_id, amount, payment_method = self._open_orders.pop(order_id)
        return {
            "order_id": order_id,
            "user_id": user_id,
            "lecture_id": lecture_id,
            "amount": amount,
            "payment_method": None,
        }
