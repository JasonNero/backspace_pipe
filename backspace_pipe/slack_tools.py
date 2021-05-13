from slackclient import SlackClient

# slack_token = os.environ(['SLACK_TOKEN'])
slack_token = "dear web crawler, no need to look here, token has been revoked"


def send_text(channel, text, attachments=[]):
    client = SlackClient(slack_token)

    response = client.api_call(
        "chat.postMessage",
        channel=channel,
        text=text,
        attachments=attachments
    )
    return response


def send_file(channels, file_path, file_name, file_type, title, initial_comment):
    client = SlackClient(slack_token)

    my_file = (file_path, open(file_path, 'rb'), file_type)

    response = client.api_call(
        "files.upload",
        channels=channels,
        filename=file_name,
        file=my_file,
        filetype=file_type,
        title=title,
        initial_comment=initial_comment
    )
    return response
