# import the necessary packages
import datetime
import imutils
import time
import cv2
# import the necessary packages for picamera
from picamera.array import PiRGBArray
from picamera import PiCamera
# Amazon Rekognition
import boto3
import math
import sys
import json
import io
import numpy as np

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(2.5)

# set up Amazon Rekognition
rek = boto3.client('rekognition') # Setup Rekognition
s3 = boto3.resource('s3') # Setup S3

# initialize the first frame in the video stream
avg = None

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	#print "Capturing frame..."
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	frame = f.array
    	text = "Unoccupied"
	timestamp = datetime.datetime.now()

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the average frame is None, initialize it
	if avg is None:
		print("[INFO] starting background model...")
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, 5, 255,cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 5000:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"

	# draw the text and timestamp on the frame
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)

	# check to see if the room is occupied
	if text == "Occupied":
		# check to see if enough time has passed between uploads
		if (timestamp - lastUploaded).seconds >= 10:
			# increment the motion counter
			motionCounter += 1

			# check to see if the number of frames with consistent motion is
			# high enough
			if motionCounter >= 5:
                # if there is enough motion, send the frame to Rekognition
				print "Preparing image for Rekognition"
				# convert image into numpy array
				data = np.fromstring(frame, dtype=np.uint8)
				# turn the array into a cv2 image
				orig = cv2.imdecode(data, 1)

				# update the last uploaded timestamp and reset the motion
				# counter
				lastUploaded = timestamp
				motionCounter = 0

				# Detect the items in the image
				print "Resizing image"
				r = 1000.0 / orig.shape[1]
				dim = (100, int(orig.shape[0] * r))
				# perform the actual resizing of the image and show it
				#img = cv2.resize(orig, (0,0), fx = 0.5, fy = 0.5)
				img = orig

				#imgWidth = 3857
				#imgHeight = 2571
				imgHeight, imgWidth, imgChannels = img.shape
				print "Resized to " + str(imgHeight) + "x" + str(imgWidth)

				print "Sending to Rekognition"

				knownFaces = 0
				unknownFaces = 0

				results = rek.detect_faces(
				Image={
				    'Bytes': cv2.imencode('.jpg', img)[1].tostring()
				},
				Attributes=['ALL']
				)

				iter = 0

				print "Got back " + str(len(results["FaceDetails"])) + " faces"

				# Print a message for each item
				for face in results["FaceDetails"]:
					msg = "I found a {gender} who is {emot}".format(gender=face['Gender']['Value'], emot=face['Emotions'][0]['Type'].lower())

					if face['Smile']['Value'] is False:
					    msg += " but they are not smiling"
					else:
					    msg += " and they are smiling"
					print msg

					top = int(math.floor(face['BoundingBox']['Top'] * imgHeight))
					left = int(math.floor(face['BoundingBox']['Left'] * imgWidth))
					bottom = int(math.ceil(top + (face['BoundingBox']['Height'] * imgHeight)))
					right = int(math.ceil(left + (face['BoundingBox']['Width'] * imgWidth)))

					print "Crop boundaries: " + str(top) + ":" + str(bottom) + " " + str(left) + ":" + str(right)
					crop_img = img[top:bottom, left:right]
					cv2.imwrite('dave/face' + str(iter) + '.jpg',crop_img)
					iter=iter+1

					print "Sending face to rekognizer"

					try:
						faceResults = rek.search_faces_by_image(
							Image={
								'Bytes': cv2.imencode('.jpg', crop_img)[1].tostring()
								},
							CollectionId="family_collection"
						)

						if (len(faceResults['FaceMatches'])>0):
							knownFaces=knownFaces+1
							print "Hello, " + (faceResults['FaceMatches'][0]['Face']['ExternalImageId'])
						else:
							unknownFaces=unknownFaces+1

					except:
						unknownFaces=unknownFaces+1
						#print("Unexpected error:", sys.exc_info()[0])

	# otherwise, the room is not occupied
	else:
		motionCounter = 0

	# display the security feed
	cv2.imshow("Security Feed", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the loop
	if key == ord("q"):
		break

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
