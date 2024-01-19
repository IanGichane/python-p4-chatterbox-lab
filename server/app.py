from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        msgs = Message.query.all()
        msg_list = [{"username": msg.username, "body": msg.body} for msg in msgs]

        response = make_response(
            jsonify(msg_list),
            200
        )
        response.headers["Content-Type"] = "application/json"

        return response

    elif request.method == 'POST':
        new_msg = Message(
            username=request.form.get("username"),
            body=request.form.get("body"),
        )

        db.session.add(new_msg)
        db.session.commit()

        msg_dict = new_msg.to_dict()

        response = make_response(
            jsonify(msg_dict),
            201
        )

        return response

@app.route('/messages/<int:id>', methods=['DELETE', 'PATCH'])
def messages_by_id(id):
    msg = Message.query.get(id)

    if not msg:
        return jsonify({"error": "Message not found"}), 404

    if request.method == 'DELETE':
        db.session.delete(msg)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Message deleted."
        }

        response = make_response(
            jsonify(response_body),
            200
        )

    elif request.method == 'PATCH':
        for attr in request.form:
            setattr(msg, attr, request.form.get(attr))

        db.session.commit()

        msg_dict = msg.to_dict()

        response = make_response(
            jsonify(msg_dict),
            200
        )

    return response

if __name__ == '__main__':
    app.run(port=5555)
