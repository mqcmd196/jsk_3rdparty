#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import rospy
import rospkg
from dialogflow_task_executive.msg import DialogResponse
from dialogflow_task_executive.msg import DialogWebhookJsonResponse

import http.server as s
from urllib.parse import urlparse, parse_qs
import ssl

import os, json


class Server(object):
    """
    This server is expected to accept the POST https message from Google DialogFlow.
    If the server received the message, it publishes the topic 'dialogflow_task_executive.msg DialogResponse' and send response to Google DialogFlow.
    """
    def __init__(self):
        """
        You need to set the path to certfile for ssl connection. You shouldn't use self-signed certificate.
        """
        rospack = rospkg.RosPack()
        conffile = rospy.get_param('~webhook_config', os.path.join(rospack.get_path('dialogflow_task_executive'), 'config/webhook.json'))

        with open(conffile) as f:
            json_dict = json.load(f)
            self.host = json_dict['host']
            self.port = json_dict['port']
            self._certfile_path = json_dict['certfile']
            self._keyfile_path = json_dict['keyfile']
        rospy.on_shutdown(self.killnode)
        rospy.init_node('dialogflow_webhook_server', disable_signals=True)
        self._run_handler()
        
    def killnode(self):
        self.httpd.shutdown()
        
    def _run_handler(self):
        self.httpd = s.HTTPServer((self.host, self.port), DialogFlowHandler)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket, certfile=self._certfile_path, keyfile=self._keyfile_path, server_side=True)

        
class DialogFlowHandler(s.BaseHTTPRequestHandler):
    """
    The handler to react the POST from Google DialogFlow and publish a ROS topic. After the topic was published, this node waits for dialog_webhook_json_response topic and make response from it.
    """
    def __init__(self, *args):
        rospack = rospkg.RosPack()
        conffile = rospy.get_param('~webhook_config', os.path.join(rospack.get_path('dialogflow_task_executive'), 'config/webhook.json'))

        with open(conffile) as f:
            json_dict = json.load(f)
            self.json_request_dir = json_dict['jsonRequestDir']
        self.pub = rospy.Publisher('dialog_response', DialogResponse, queue_size=1)
        self.sub = rospy.Subscriber('dialog_webhook_json_response', DialogWebhookJsonResponse, _response)
        try:
            s.BaseHTTPRequestHandler.__init__(self, *args)
        except ConnectionResetError as e:
            pass
    
    def do_POST(self):
        """
        The Handler is expected to recieve POST method from Google Dialogflow. If the request is not the POST method or from Google Dialogflow, it returns the error.
        """
        user_agent = self.headers.get("User-Agent")
        rospy.loginfo('Recieved POST request' + str(self.headers))
        if user_agent == "Google-Dialogflow":
            self._parse_json()
            self._pub_task()
        else:
            rospy.logwarn('User-Agent header should be Google-Dialogflow, but got ' + user_agent)
            self._bad_request()

    def _parse_json(self):
        content_len = int(self.headers.get("content-length"))
        request_body = self.rfile.read(content_len).decode("utf-8")
        self.json_content = json.loads(request_body)

    def _pub_task(self):
        """
        Publish ROS message to exec task.
        """
        msg = DialogResponse()
        msg.header.stamp = rospy.Time.now()
        msg.response_id = self.json_content['responseId']
        msg.query = self.json_content['queryResult']['queryText']
        msg.action = self.json_content['queryResult']['action']
        msg.response = self.json_content['queryResult']['fulfillmentText']
        if self.json_content['queryResult']['allRequiredParamsPresent'] == 'True':
            msg.fulfilled = True
        msg.parameters = json.dumps(self.json_content['queryResult']['parameters'])
        msg.speech_score = 1.0
        msg.intent_score = self.json_content['queryResult']['intentDetectionConfidence']
        rospy.loginfo("The message summary from Dialogflow \n" + str(msg))
        self.pub.publish(msg)

    def _response(self, data):
        """
        The DialogFlow client expects the non-empty response.
        Please see https://cloud.google.com/dialogflow/es/docs/fulfillment-webhook for details.
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        res_body = data.json_body
        # self.send_header('Content-length', len(self.res_body))
        self.end_headers()
        self.wfile.write(res_body)

    def _bad_request(self):
        self.send_response(400)
        self.end_headers()

if __name__ == '__main__':
    server = Server()
    rospy.loginfo('DialogFlow webhook HTTPS Server starts - %s:%s' % (server.host, server.port))
    server.httpd.serve_forever()
