import os
from unittest import mock

import pytest

from checklens import create_app, configure_redis


@pytest.fixture
def app():
    with mock.patch("checklens.configure_redis"):
        with mock.patch.dict(os.environ, {"CHECK_FIELD_EXISTS": "field.child_a.child_b"}, clear=True):
            app = create_app()
            yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@mock.patch("checklens.configure_redis", mock.MagicMock)
class TestAppInitialize:
    def test_normal_validation(self):
        with mock.patch.dict(os.environ, {"CHECK_FIELD_EXISTS": "field.child_a.child_b"}, clear=True):
            init_app = create_app()
            assert init_app.config["validate_field"] == "field.child_a.child_b"

    def test_short_validation(self):
        with mock.patch.dict(os.environ, {"CHECK_FIELD_EXISTS": "field.child_a"}, clear=True):
            with mock.patch("sys.exit") as exit_mock:
                create_app()
                exit_mock.assert_called_once_with(1)

    def test_unexist_validation(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("sys.exit") as exit_mock:
                with pytest.raises(AttributeError):
                    create_app()
                exit_mock.assert_called_once_with(1)

    def test_invalid_format_validation(self):
        with mock.patch.dict(os.environ, {"CHECK_FIELD_EXISTS": "field_child_a_child_b"}, clear=True):
            with mock.patch("sys.exit") as exit_mock:
                create_app()
                exit_mock.assert_called_once_with(1)


class TestRedisInit:
    def test_without_host(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                configure_redis()

    def test_connect_to_redis(self):
        with mock.patch.dict(os.environ, {"REDIS_HOST": "localhost"}, clear=True):
            with mock.patch("redis.Redis") as r:
                configure_redis()
                r.assert_called_with(host="localhost", port="6379", db="0")

    def test_custom_redis_params(self):
        with mock.patch.dict(os.environ, {"REDIS_HOST": "locloc", "REDIS_PORT": "1234", "REDIS_DB": "11"}, clear=True):
            with mock.patch("redis.Redis") as r:
                configure_redis()
                r.assert_called_with(host="locloc", port="1234", db="11")


@pytest.mark.usefixtures("app")
class TestChecklensResponses:
    def test_allow_only_post(self, client):
        resp = client.get("/")
        assert resp.status_code == 405

    def test_check_key(self, client):
        body = {"field": {"child_a": {"child_b": "value"}}}
        resp = client.post("/", json=body)
        assert resp.status_code == 200

    def test_check_value(self, client):
        body = {"field": {"child_a": "child_b"}}
        resp = client.post("/", json=body)
        assert resp.status_code == 200

    def test_unexist_key(self, client):
        body = {"field": {"child_a": {"child_c": "value"}}}
        resp = client.post("/", json=body)
        assert resp.status_code == 403
        assert "Field with value/key doesn't exist" in resp.data.decode()

    def test_invalid_value(self, client):
        body = {"field": {"child_a": "child_c"}}
        resp = client.post("/", json=body)
        assert resp.status_code == 403
        assert "Field with value/key doesn't exist" in resp.data.decode()

    def test_invalid_child_a(self, client):
        body = {"field": {"child_c": "child_d"}}
        resp = client.post("/", json=body)
        assert resp.status_code == 403
        assert "Field child_a doesn't exist in body[field]" in resp.data.decode()

    def test_invalid_field(self, client):
        body = {"fieldinv": {"child_a": "child_b"}}
        resp = client.post("/", json=body)
        assert resp.status_code == 403
        assert "Field field doesn't exist in body" in resp.data.decode()

    def test_invalid_structure(self, client):
        body = {"field": ["a", "b"]}
        resp = client.post("/", json=body)
        assert resp.status_code == 403
        assert "Field child_a doesn't exist in body[field]" in resp.data.decode()

    def test_data_not_json(self, client):
        body = "my_data"
        resp = client.post("/", data=body)
        assert resp.status_code == 403
        assert "Body doesn't in JSON format" in resp.data.decode()
