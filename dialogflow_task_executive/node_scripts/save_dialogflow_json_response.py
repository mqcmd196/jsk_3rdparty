#!/usr/bin/env python
from __future__ import print_function
from argparse import ArgumentParser
import json
import os

def get_option():
    argparser = ArgumentParser()
    argparser.add_argument('-a', '--action', type=str,
                           required=True,
                           help='The action name which is registered at DialogFlow.'
    )
    argparser.add_argument('-s', '--style', type=str,
                           default='text', choices=['text', 'image', 'card'],
                           help='The response style. Expected text, image, card. This is not the official Google API method.')
    argparser.add_argument('-t', '--text', type=str,
                           default=None,
                           help='The title or text of the agent\'s response.'
    )
    argparser.add_argument('-st', '--subtitle', type=str,
                           default=None,
                           help='The subtitle of the agent\'s response.'
    )
    argparser.add_argument('-i', '--image', type=str,
                           default=None,
                           help='The public URI to an image file.'
    )
    argparser.add_argument('-at', '--accessibilitytext', type=str,
                           default=None,
                           help='A text desctiption of the image to be used for accessibility, e.g., screen readers.'
    )
    # WIP. We have to judge whether we need these options or not.
    # argparser.add_argument('-m', '--media', type=str,
    #                        default=False,
    #                        help='The media content path for response.'
    # )        
    argparser.add_argument('-o', '--output', type=str,
                           default='/tmp',
                           help='The directory in which saves generated json file.'
    )

    return argparser.parse_args()


class DialogflowJSONResponse(object):
    """JSON response for Google Dialogflow.
        Note:
            Please see the official API document for details.
            https://cloud.google.com/dialogflow/es/docs/reference/rpc/google.cloud.dialogflow.v2?hl=ja#webhookresponse
    """
    def __init__(self, action_name, style, output):
        self.style = style
        self.output = output
        self.text = None
        self.subtitle = None
        self.image = None
        self.accessibilitytext = None
        # self.media = None
        self.filepath = os.path.join(output, "dialogflow_response_" + action_name + ".json")
        self.lockpath = os.path.join(output, "dialogflow_response_" + action_name + ".lock")
        with open(self.lockpath, 'w') as f:
            f.write("")

    def __del__(self):
        os.remove(self.lockpath)

    def export_json(self):
        if self.style == "text":
            self._text_json_response()
        elif self.style == "image":
            self._image_json_response()
        elif self.style == "card":
            self._card_json_response()
        else:
            raise ValueError("No such style name.")
        self._save_file()

    def _save_file(self):
        with open(self.filepath, 'w') as f:
            json.dump(self._json_body, f, ensure_ascii=False, indent=2, encoding="utf-8")

    def _text_json_response(self):
        self._json_body = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            self.text
                        ]
                    }
                }
            ]
        }

    def _image_json_response(self):
        self._json_body = {
            "fulfillmentMessages": [
                {
                    "image": {
                        "image_uri": self.image
                    }
                }
            ]
        }

    def _card_json_response(self):
        self._json_body = {
            "fulfillmentMessages": [
                {
                    "card": {
                        "title": self.text,
                        "subtitle": self.subtitle,
                        "image_uri": self.image
                    }
                }
            ]
        }

def main():
    args = get_option()
    json_saver = DialogflowJSONResponse(args.action, args.style, args.output)
    json_saver.text = args.text
    json_saver.subtitle = args.subtitle
    json_saver.image = args.image
    json_saver.accessibilitytext = args.accessibilitytext
    json_saver.export_json()

if __name__ == '__main__':
    main()
