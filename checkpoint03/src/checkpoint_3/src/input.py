#!/usr/bin/env python
import rospy
from checkpoint_3.msg import encoderData
from std_msgs.msg import Int32
import wiringpi
import time

class mobile_command():
    def __init__(self):
        self.msg = encoderData()
        self.pub = rospy.Publisher('target', encoderData, queue_size=10)
        rospy.Subscriber('light_sensor', Int32, self.callback)


    def _forward(self, speed = 130):
        self.msg.left_speed = speed
        self.msg.right_speed = speed
        self.pub.publish(self.msg)

    def _stop(self):
        self.msg.left_speed = 0
        self.msg.right_speed = 0
        self.pub.publish(self.msg)

    def _backward(self, speed = 100):
        self.msg.left_speed = -speed
        self.msg.right_speed = -speed
        self.pub.publish(self.msg)

    def _spinCL(self, speed = 70):
        self.msg.left_speed = speed
        self.msg.right_speed = -speed
        self.pub.publish(self.msg)

    def _spinCCL(self, speed = 70):
        self.msg.left_speed = -speed
        self.msg.right_speed = speed
        self.pub.publish(self.msg)

    def callback(self, data):
        self.light_data = data.data


    def _search(self):
        step = 0
        min = 1024
        while(step<75):
            self._spinCL(70)
            step+=1
            if self.light_data <min:
                min = self.light_data
            rospy.sleep(0.05)

        step = 0
        self._stop()
        rospy.sleep(0.5)
        while(step<200):
            if (self.light_data - min)<50:
                self._stop()
                rospy.sleep(0.5)
                self._spinCCL(40)
                rospy.sleep(0.3)
                break
            self._spinCL(self.light_data/11)
            step+=1
            rospy.sleep(0.05)
        self._stop()
        rospy.sleep(0.5)
        step = 30
        while(wiringpi.digitalRead(1) == 0 and step<100):
            self._forward(step)
            step +=1
            rospy.sleep(0.03)
        

    def _collision(self):
        self._stop()
        rospy.sleep(0.5)
        #left_sensor = wiringpi.digitalRead(2)
        #right_sensor = wiringpi.digitalRead(3)
        self._backward()
        rospy.sleep(1)
        self._search()
        
    def _catch(self):
        self._stop()
        

def publisher():
    cmder = mobile_command()
    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        left_sensor = wiringpi.digitalRead(2)
        right_sensor = wiringpi.digitalRead(3)
        catch_sensor = wiringpi.digitalRead(1)

        if left_sensor==1 or right_sensor==1 :
            cmder._collision()
        else:
            cmder._forward()

        if catch_sensor:
            cmder._catch()
        rate.sleep()


def pin_setup():
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(2, 0)
    wiringpi.pinMode(3, 0)
    wiringpi.pinMode(1, 0)

def main():
    rospy.init_node("publisher")
    pin_setup()
    publisher()
    rospy.spin()

if __name__ =="__main__":
    main()
