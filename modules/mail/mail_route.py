import os
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from modules.schemas.mail_schema import MailSchema
from flask_mail import Message
from extensions import mail

mail_dp = Blueprint("mail", __name__, url_prefix="/api/mail")


@mail_dp.route("/", methods=["POST"])
def contact_me():
    schema = MailSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    sender_email = data.get("email")
    sender_name = data.get("name")
    subject_of_mail = data.get("subject")
    message_of_mail = data.get("message")

    mail_body = f""""
You have a message from your portfolio contact form

From:{sender_name}
Email:{sender_email}
Subject:{subject_of_mail}
Message:
{message_of_mail}
 """

 #   try:
    msg = Message(
        subject=subject_of_mail,
        sender=os.environ.get("FLASK_MAIL_DEFAULT_SENDER"),
        recipients=[os.environ.get("RECIPIENT_MAIL")],
        body=mail_body
    )
    res = os.environ.get("RECIPIENT_MAIL")
    sender = os.environ.get("FLASK_MAIL_DEFAULT_SENDER")
    name = os.environ.get("FLASK_MAIL_USERNAME")
    password = os.environ.get("FLASK_MAIL_PASSWORD")
    print(res, sender, name, password)
    mail.send(msg)

    return jsonify({"message": "Message sent successfully"}), 200

  #  except Exception as e:
   #     print("MAIL SEND ERROR:", e)
   #     return jsonify({"error": "Failed to send message", "details": str(e)}), 500
