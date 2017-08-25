"""Rekognition Example."""

import boto3
import json
import cv2
import math
import sys
import picamera
import io
import numpy as np

rek = boto3.client('rekognition') # Setup Rekognition
s3 = boto3.resource('s3') # Setup S3
print "Getting Image"
#image = s3.Object('campi-rekognition-pictures','davekerri1.jpg') # Get an Image from S3
#img_data = image.get()['Body'].read() # Read the image
# saving the picture to an in-program stream rather than a file
stream = io.BytesIO()

#testImage = "hawaii-2017-zipline-6634.jpg"
camera = picamera.PiCamera()
camera.resolution = (2592, 1944)

camera.capture('image.jpg')


camera.capture(stream, format='jpeg')
# convert image into numpy array
data = np.fromstring(stream.getvalue(), dtype=np.uint8)
# turn the array into a cv2 image
orig = cv2.imdecode(data, 1)

#testImage = "/dev/shm/mjpeg/cam.jpg"

# Detect the items in the image
print "Image retrieved"
#orig = cv2.imread("dave/" + testImage)

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

print "I found " + str(knownFaces) + " faces I knew."
print "I found " + str(unknownFaces) + " unknown faces."

