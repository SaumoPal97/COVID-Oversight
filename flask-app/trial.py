from twilio.rest import Client


def twilio_sms(text):
    account_sid = "AC9076dbe76f82eb68aea596337f4d1f31"
    auth_token = "7b7d29f6482c8dd420e91506fc23e6a8"
    my_num = "+918016598546"
    twilio_num = "+12513571209"
    client = Client(account_sid, auth_token)
    sms = client.messages.create(
        from_= twilio_num,
        body= text,
        to= my_num,
    )