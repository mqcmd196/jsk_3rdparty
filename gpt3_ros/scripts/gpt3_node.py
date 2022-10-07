import actionlib
from gpt3_ros.msg import GPT3Action
import openai
import rospy


class GPT3Client(object):
    def __init__(self):
        self.org_id = rospy.get_param("organization_id")
        self.api_key = rospy.get_param("api_key")
        self.gpt3_as = actionlib.SimpleActionServer("~gpt3_server",
                                                    GPT3Action,
                                                    execute_cb=self.cb,
                                                    auto_start=False)
        self.gpt3_as.start()
