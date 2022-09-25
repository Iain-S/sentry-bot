"""Unit tests for the app module."""
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from sentrybot.app import create_app

# pylint: disable=redefined-outer-name


@pytest.fixture()
def app() -> Generator[Flask, None, None]:
    """Generate a Flask app for testing."""
    app = create_app({})

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    """Make a testing client."""
    return app.test_client()


def test_get_index(client: FlaskClient) -> None:
    """Test GETing the route."""
    response = client.get("/")
    assert response.status == "200 OK"


def test_get_video(client: FlaskClient) -> None:
    """Test GETing the route."""
    response = client.get("/video")
    assert response.status == "200 OK"


def test_get_face_detection(client: FlaskClient) -> None:
    """Test GETing the route."""
    response = client.get("/face-detection")
    assert response.status == "200 OK"


def test_post_ajax_data(client: FlaskClient) -> None:
    """Test POSTing to the route."""
    response = client.post("/ajax-data", json={"xPos": 1, "yPos": 2})
    assert response.status == "200 OK"


def test_get_ajax_data(client: FlaskClient) -> None:
    """Test GETing the route."""
    response = client.get("/ajax-data")
    assert response.status == "200 OK"


def test_get_send_receive(client: FlaskClient) -> None:
    """Test GETing the route."""
    response = client.get("/send-receive")
    assert response.status == "200 OK"
