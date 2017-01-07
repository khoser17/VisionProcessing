# refer to http://opencv-python-tutroals.readthedocs.io/en/latest/index.html for documentation of OpenCV

import numpy as np
import cv2
from networktables import NetworkTable

def sendData(cX,cY,area):
	table = NetworkTable.getTable("vision")
	table.putNumber("centerX", cX)
	table.putNumber("centerY", cY)
	table.putNumber("area", area)
	return
	
def processImage(img):
	# convert BGR to HSV
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	# threshold to only include wanted HSV values
	thresh = cv2.inRange(hsv,np.array(hsv_lower_bound),np.array(hsv_upper_bound))
	
	# bluring image to reduce noise
	blur = cv2.GaussianBlur(thresh,(7,7),0)
	
	return blur

def getPreferedContour(img):
	# using contours to form shapes
	image, contours, hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	
	# sorting through all the countours
	for cnt in contours:
	
		#the area of the countour
		area = cv2.contourArea(cnt)

		# filtering out contours that are too big or too small
		if area_min < area < area_max:
			
			# creating a convex hull around the contour
			hull = cv2.convexHull(cnt)
			
			return hull
	
	return None

def getContourSpecs(contour):
	# determining the center of the circle
	(x,y),radius = cv2.minEnclosingCircle(contour)
    
	# determining area
	area = cv2.contourArea(contour)
	
	return x, y, radius, area
	
if __name__ == '__main__':
	# ---preferences--- 
	debugging = True
	networktable_ip = "192.168.1.125"
	hsv_lower_bound = [0,163,115]
	hsv_upper_bound = [180,255,255]
	area_min = 500
	area_max = 10000

	# setup NetworkTables
	NetworkTable.setIPAddress(networktable_ip)
	NetworkTable.setClientMode()
	NetworkTable.initialize()

	# setup camera feed
	cap = cv2.VideoCapture(0)

	while True:
		# isValid returns if frame is read correctly and frame is a matrix of info from a frame of the camera
		isValid, raw = cap.read()
		
		# process the image
		processed = processImage(raw)
		
		# find the right contour
		contour = getPreferedContour(processed)
		
		# check to see if a contour was found and then send the data to the NetworkTable
		if contour is not None:
			x,y,radius,area = getContourSpecs(contour)
			sendData(x,y,area)
				
			# drawing a visual box to the debug images
			if debugging:
				center = (int(x),int(y))
				radius = int(radius)
				cv2.circle(raw,center,radius,(0,255,0),2)
				cv2.circle(processed,center,radius,(0,255,0),2)

		# showing the debug images
		if debugging:
			cv2.imshow('raw',raw)
			cv2.imshow('processed',processed)

			# the amount of milliseconds to wait before the next frame and exits on pressing the esc key
			if cv2.waitKey(5) & 0xFF == 27:
				break

	# when finished, release the capture and destory any created windows 
	cap.release()
	cv2.destroyAllWindows()
