from flask import current_app, request, make_response, Blueprint


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["POST"])
def validate_request():
    body = request.json

    if body is None:
        return make_response(f"Body doesn't in JSON format", 403)

    current_app.config["redis"].set("cache", request.data.decode())

    field, child_a, child_b = current_app.config["validate_field"].split(".")

    if field not in body:
        return make_response(f"Field {field} doesn't exist in body", 403)

    if child_a not in body[field]:
        return make_response(f"Field {child_a} doesn't exist in body[{field}]", 403)

    value = body[field][child_a]

    if (isinstance(value, str) and value == child_b) or (isinstance(value, dict) and child_b in value):
        return make_response("OK", 200)
    else:
        return make_response(f"Field with value/key doesn't exist in body[{field}][{child_a}]", 403)


@main_bp.route("/ping", methods=["GET"])
def ping():
    return make_response("pong", 200)
