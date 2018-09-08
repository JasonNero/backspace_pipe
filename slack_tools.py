from slackclient import SlackClient
import os

slack_token = os.environ(['SLACK_TOKEN'])


def send_text(channel, text, attachments=[]):
	sc = SlackClient(slack_token)

	ret = sc.api_call(
		"chat.postMessage",
		channel=channel,
		text=text,
        attachments=attachments
	)
	return ret

def send_file(channels, file_path, file_name, file_type, title):
    sc = SlackClient(slack_token)

    my_file = (file_path, open(file_path, 'rb'), file_type)

    ret = sc.api_call(
        "files.upload",
        channels=channels,
        filename=file_name,
        file=my_file,
        filetype=file_type,
        title=title
    )
    return ret
