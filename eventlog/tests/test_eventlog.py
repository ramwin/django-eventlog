from email.message import EmailMessage
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from eventlog import EventGroup
from eventlog.datastructures import EventType
from eventlog.models import Event


@pytest.mark.django_db()
def test_multi_log() -> None:
    """Multiple log items."""
    from eventlog import EventGroup
    from eventlog.models import Event

    e = EventGroup()
    e.info("Hello World")
    e.error("Hello World")
    e.warning("Hello World")
    e.critical("Hello World")
    assert Event.objects.count() == 4


@pytest.mark.django_db()
def test_multiuse_named_log() -> None:
    """Multiple log items, initialized twice with the same group id."""
    from eventlog import EventGroup
    from eventlog.models import Event

    e = EventGroup(group_id="abc")
    e.info("Hello World")
    e.error("Hello World")

    e = EventGroup(group_id="abc")
    e.warning("Hello World")
    e.critical("Hello World")

    assert Event.objects.count() == 4
    assert Event.objects.filter(group="abc").count() == 4


@pytest.mark.django_db()
def test_data_log() -> None:
    """Simple log item with data."""
    from eventlog import EventGroup
    from eventlog.models import Event

    e = EventGroup()
    e.info("Hello World", data={"email": "user@example.com"})
    e.info("Hello World", data={"foo": {"bar": [1, 2, 3]}})
    assert Event.objects.count() == 2


@pytest.mark.django_db()
def test_unserializable_data_log() -> None:
    """Log item with data that's not JSON serializable."""
    from eventlog import EventGroup
    from eventlog.models import Event

    class Foo:
        pass

    e = EventGroup()
    e.info("Hello World", data={"foo": Foo()})
    assert Event.objects.count() == 1

    # It will be barely readable but better than failing upon a log entry.
    assert "Foo object" in Event.objects.first().data


@pytest.mark.django_db()
def test_mail_per_event(mailoutbox: list[EmailMessage]) -> None:
    """Send one mail per event."""
    from eventlog import EventGroup
    from eventlog.models import Event

    e = EventGroup()
    e.info("Hello World", send_mail="user@example.com")
    e.error("Hello World")
    e.warning("Hello World")
    e.critical("Hello World", send_mail="user@example.com")
    assert Event.objects.count() == 4
    assert len(mailoutbox) == 2


@pytest.mark.django_db()
def test_mail_per_group(mailoutbox: list[EmailMessage]) -> None:
    """Set mail per group so it's sent for every event."""
    from eventlog import EventGroup
    from eventlog.models import Event

    e = EventGroup(send_mail="user@example.com")
    e.info("Hello World")
    e.error("Hello World")
    e.warning("Hello World")
    e.critical("Hello World")
    assert Event.objects.count() == 4
    assert len(mailoutbox) == 4


@pytest.mark.django_db()
def test_admin_changelist(admin_client: Client) -> None:
    """
    Admin Changelist will render all events and legacy events
    They exist in db but no longer defined in AppConfig.
    """

    # Regular Event
    e = EventGroup(group_id="legacy test")
    e.info("Hello World 1")
    e.info("Hello World 2")
    e.error("Hello World 3")
    e.warning("Hello World 4")

    # Legacy Event (Created and in database, but its type no longer valid)
    Event.objects.create(
        type="legacy_event",
        group="legacy test",
        message="This is some info.",
        initiator="Test Runner",
    )

    changelist_url = reverse("admin:eventlog_event_changelist")
    response = admin_client.get(changelist_url)

    assert response.status_code == HTTPStatus.OK
    assertContains(response, "Hello World 1")
    assertContains(response, "Hello World 2")
    assertContains(response, "Hello World 3")
    assertContains(response, "Hello World 4")
    assertContains(response, "Legacy_Event")


@pytest.mark.django_db()
def test_admin_changeform(admin_client: Client) -> None:
    """Admin Changeform is OK."""

    e1 = EventGroup()
    e1.info("Hello World 1")
    e1.info("Hello World 2")

    # Legacy Event (Created and in database, but its type no longer valid)
    Event.objects.create(
        type="legacy_event",
        group=e1.group_id,
        message="This is some info.",
        initiator="Test Runner",
    )

    # A second group, which is not rendered on the change form.
    e2 = EventGroup()
    e2.error("Hello World 3")
    e2.warning("Hello World 4")

    obj = Event.objects.filter(group=e1.group_id).first()
    changelist_url = reverse("admin:eventlog_event_change", args=(obj.pk,))
    response = admin_client.get(changelist_url)

    assert response.status_code == HTTPStatus.OK
    assertContains(response, "Hello World 1")
    assertContains(response, "Hello World 2")
    assertContains(response, "Legacy_Event")

    # These are a different group
    assertNotContains(response, "Hello World 3")
    assertNotContains(response, "Hello World 4")


@pytest.mark.django_db()
def test_invalid_type_usage() -> None:
    """Calling an invalid type will raise an error."""
    from eventlog import EventGroup

    e = EventGroup()
    with pytest.raises(TypeError):
        e.doesnotexist("Hello World")


def test_invalid_type_creation() -> None:
    """Creating an invalid type will raise an error."""
    with pytest.raises(TypeError):
        EventType(
            name="1invalid_name",
            label="Must not start with number",
        )

    with pytest.raises(TypeError):
        EventType(
            name="a" * 51,
            label="Must not exceed 50 characters",
        )
