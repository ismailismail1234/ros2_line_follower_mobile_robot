#!/usr/bin/env python3

from copy import error

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2


class CameraViewer(Node):

    def __init__(self):
        super().__init__('camera_viewer')

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera_sensor/image_raw',   
            self.image_callback,
            10)
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

    def image_callback(self, msg):

      frame = self.bridge.imgmsg_to_cv2(msg)

      gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
      )

      _, thresh = cv2.threshold(
       gray,
       0,
       255,
       cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
       )
      height, width = thresh.shape

      roi = thresh[int(height*0.2):height, :]

      M= cv2.moments(roi)
      if M['m00'] != 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])


        center = width / 2
        error = center - cx
        print(cx)
        cmd = Twist()
        base_linear_speed= 0.8
        kp=0.005
        cmd.angular.z = kp * error
        cmd.linear.x = max(0.007, base_linear_speed - abs(0.0095 * error))
        self.cmd_pub.publish(cmd)
        cv2.circle(
        roi,
        (cx, cy),
        10,
        (0, 255, 255),
        -1)

        
    
      else:
        #allway turn left if no line is detected
        cmd = Twist()
        cmd.linear.x = 0.07
        cmd.angular.z = 0.3
        self.cmd_pub.publish(cmd)
        

     

      
      

      cv2.imshow("ROI", roi)
      cv2.waitKey(1)

def main(args=None):

    rclpy.init(args=args)

    node = CameraViewer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()