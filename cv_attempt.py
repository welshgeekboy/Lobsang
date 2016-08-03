import Lobsang
import cv2.cv as cv
import cv2
import picamera
import picamera.array
import time
import numpy

Lobsang.begin()

camera = picamera.PiCamera()
camera.resolution = (256, 256)
cv.NamedWindow("Image", 1)

try:
	while True:
		with picamera.array.PiRGBArray(camera) as stream:
			camera.capture(stream, format="bgr", resize=(256, 256))
			#image = numpy.frombuffer(stream.array, dtype=numpy.uint8)
			image = cv2.imdecode(stream.array, 1)
			print image
			print "------------------------"
			cv.ShowImage("Image", image)
			stream.truncate(0)
except Exception as error:
	print error
	cv.DestroyAllWindows()
	Lobsang.quit()
	camera.close()
