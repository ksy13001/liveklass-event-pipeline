import pytest
from producer import event_generator
from producer.event_generator import EventType


@pytest.fixture
def gen():
    return event_generator.EventGenerator()


def test_page_view_has_no_purchase_fields(gen):
    event = gen.generate(EventType.PAGE_VIEW)
    assert event["event_type"] == "page_view"
    assert event["amount"] is None
    assert event["payment_method"] is None
    assert event["order_id"] is None


def test_purchase_complete_has_required_fields(gen):
    event = gen.generate(EventType.PURCHASE_COMPLETE)
    assert event["amount"] is not None
    assert event["payment_method"] is not None
    assert event["order_id"] is not None


def test_purchase_complete_appends_to_open_orders(gen):
    gen.generate(EventType.PURCHASE_COMPLETE)
    assert len(gen._open_orders) == 1


def test_purchase_cancel_without_open_orders_falls_back_to_page_view(gen):
    event = gen.generate(EventType.PURCHASE_CANCEL)
    assert event["event_type"] == "page_view"


def test_purchase_cancel_reuses_complete_order(gen):
    complete = gen.generate(EventType.PURCHASE_COMPLETE)
    cancel = gen.generate(EventType.PURCHASE_CANCEL)
    assert cancel["order_id"] == complete["order_id"]
    assert cancel["user_id"] == complete["user_id"]
    assert complete["amount"] // 2 <= cancel["amount"] < complete["amount"]
    assert len(gen._open_orders) == 0
