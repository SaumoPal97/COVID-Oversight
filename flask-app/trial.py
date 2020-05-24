from twilio.rest import Client


def twilio_sms(text):
    account_sid = "<ACCOUNT-SID>"
    auth_token = "<AUTH-TOKEN>"
    my_num = "<PHONE-NUM>"
    twilio_num = "<TWILIO-NUM>"
    client = Client(account_sid, auth_token)
    sms = client.messages.create(
        from_= twilio_num,
        body= text,
        to= my_num,
    )
