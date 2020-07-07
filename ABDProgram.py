import cv2
import numpy as np
import math
import time
import os

import warnings

print("Test")
startTime = time.time()

np.seterr(all='warn')
filterWarnings = False #IMPORTANT: Make sure to turn this into False when bug testing
if filterWarnings:
	warnings.simplefilter("ignore") #this prevents any warnings from being printed in console

#############
#global variables
imgPath = ""
imgName = ""
directoryResultsSpecific = ""

resultAlgaePercentage = 0
resultAlgaeBool = False
#############


def conLog(msg): #prints a message in console that includes the run time of the program
	currentTime = time.time() - startTime
	roundCTimeString = "%.2f" % currentTime
	print("["+roundCTimeString+"s]: "+msg)
	
def RGB2HSV_CUSTOM(img):#this is based entirely on Single Image Based Algal Bloom Detection Using Water Body Extraction and Probabilistic Algae Indices by Park et al. (2019)
	conLog("RGB to HSV conversion is starting...")
	imgShape = img.shape
	
	imgHueArray = np.zeros([imgShape[0], imgShape[1], 3])
	
	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			pixel = img[y][x]
			
			r = float(pixel[2])
			g = float(pixel[1])
			b = float(pixel[0])
			
			#r /= 255
			#g /= 255
			#b /= 255
			
			cMax = max(r,g,b)
			cMin = min(r,g,b)
			maxminDiff = cMax - cMin
			
			#HUE CALCULATION
			#IMPORTANT: because of the calculations later, hue is normalized between the range of 0 to 1
			if cMax == cMin:
				imgHue = 0
				
			elif cMax == r:
				imgHue = (1/360)*(60*(((g-b)/maxminDiff)%6))
				
			elif cMax == g:
				imgHue = (1/360)*(60*(((b-r)/maxminDiff)+2))
				
			elif cMax == b:
				imgHue = (1/360)*(60*(((r-g)/maxminDiff)+4))
			
			#SATURATION CALCULATION
			if cMax == 0:
				imgSaturation = 0
			else:
				imgSaturation = 1 - (cMin/cMax)
			
			#VALUE CALCULATION
			imgValue = cMax/255
			
			imgHueArray[y][x][0] = imgHue
			imgHueArray[y][x][1] = imgSaturation
			imgHueArray[y][x][2] = imgValue
			
	conLog("RGB to HSV conversion is complete!")
	return imgHueArray
	
def imageAccess(imgPath, logBool = True):
	try:
		if imgPath == "":
			conLog("File path is empty!")
		else:
			img = cv2.imread(imgPath)
			
	except:
		conLog("An exception occured in accessing the image!")
	
	if logBool:
		conLog("Image Accessed")

	return(img)
    
def imagePreProcess(img):#removes noise
	processed = cv2.fastNlMeansDenoising(img)
	conLog("Image Pre-processed")
	
	newImgProcessedString = imgName+"Processed.jpg"
	cv2.imwrite(newImgProcessedString, processed)
	return(processed) 
	
def autoCannyEdges(img, sigma = 0.40): #https://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
	imgGrayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	imgBlurred = cv2.GaussianBlur(imgGrayed, (3, 3), 0)
	
	imgMedian = np.median(imgBlurred)
	
	lower = int(max(0, (1.0 - sigma) * imgMedian))
	upper = int(min(255, (1.0 + sigma) * imgMedian))
	imgEdged = cv2.Canny(imgBlurred, lower, upper)
	
	return(imgEdged)
	
def imageRemoveEdges(img):
	imgRemovedEdges = img
	conLog("Image edge removal starting...")
	imgEdges = autoCannyEdges(img)

	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15))
	imgEdgesMorphed = cv2.morphologyEx(imgEdges, cv2.MORPH_CLOSE,kernel)

	contours, hierarchy = cv2.findContours(imgEdgesMorphed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:
		cv2.drawContours(imgEdgesMorphed, [cnt], -1, 255, thickness=cv2.FILLED)

	#cv2.imwrite("_imgEdgesMorphed.jpg", imgEdgesMorphed)

	for y in range(img.shape[0]):
		for x in range(img.shape[1]):
			if imgEdgesMorphed[y][x] > 0:
				imgRemovedEdges[y][x][0] = 0
				imgRemovedEdges[y][x][1] = 0
				imgRemovedEdges[y][x][2] = 0
				
	newImgRemovedEdges = imgName+"RemovedEdges.jpg"
	cv2.imwrite(newImgRemovedEdges, imgRemovedEdges)
	
	conLog("Image edge removal complete!")
	return(imgRemovedEdges)
    
def imageTrackAlgae(imgRemovedEdges):
	conLog("Green algae tracking starting...")
	#ranges are based on the fact that green in hue is 60
	lowerRange = np.array([30,0,50])
	upperRange = np.array([85,255,255])
	
	imgREHSV = cv2.cvtColor(np.uint8(imgRemovedEdges), cv2.COLOR_BGR2HSV)
	imgOrig = imageAccess(imgName+"Processed.jpg", logBool=False)
	
	imgShape = imgOrig.shape
	
	###################
	imgREGray = cv2.cvtColor(imgRemovedEdges, cv2.COLOR_BGR2GRAY)
	imgREBinary = np.zeros([imgShape[0], imgShape[1]])
	
	#gets a pure black-white image from imgRemovedEdges
	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			if imgREGray[y][x] != 0:	
				imgREBinary[y][x] = 255
	###################

	imgMask = cv2.inRange(imgREHSV, lowerRange, upperRange)
	
	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			if imgREBinary[y][x] == 0:
				imgMask[y][x] == 0
		
	imgAlgae = cv2.bitwise_and(imgRemovedEdges,imgRemovedEdges, mask = imgMask)
	
	newImgMaskString = imgName+"Mask.jpg"
	newImgAlgaeString = imgName+"Algae.jpg"
	cv2.imwrite(newImgMaskString, imgMask)
	cv2.imwrite(newImgAlgaeString, imgAlgae)
	
	conLog("Green algae tracking complete!")
	
	return(imgAlgae)
	
def NGRDI(img):
	conLog("NGRDI computation is starting...")
	imgShape = img.shape

	NGRDIArray = np.zeros([imgShape[0], imgShape[1]]) #create empty array for NGRDI
	
	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			imgGreen = img[y][x][1]
			imgRed = img[y][x][2]
			
			imgGreen = float(imgGreen)
			imgRed = float(imgRed)
			
			if (imgGreen + imgRed) == 0:
				NGRDIVal = 0
			else:
				NGRDIVal = imgGreen/(imgGreen+imgRed)
				
			NGRDIArray[y][x] = NGRDIVal

	conLog("NGRDI computation complete!")
	return(NGRDIArray)
	
def SatIndex(origImg, img):
	conLog("Saturation Index calculation is starting...")
	imgShape = img.shape
	listSaturation = []
	
	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			listSaturation.append(origImg[y][x][1])
			
	listSaturation.sort(reverse=True)
	maxSat = listSaturation[0]
	
	SatIndexArray = np.zeros([imgShape[0], imgShape[1]])

	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			SatIndexVal = img[y][x][1] / maxSat
			SatIndexArray[y][x] = SatIndexVal
	
	conLog("Saturation Index calculation is complete!")
	return(SatIndexArray)
	
def HueIndex(img):
	conLog("Hue Index calculation is starting...")
	imgShape = img.shape
	
	HueIndexArray = np.zeros([imgShape[0], imgShape[1]])
	
	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			#affinity funtion
			if 0<= img[y][x][0] < (1/3):
				hueAffinity = 2*(img[y][x][0]) + 1/3
				
			elif (1/3) <= img[y][x][0] < (5/6):
				hueAffinity = -2*(img[y][x][0]) + 5/3
				
			elif (5/6) <= img[y][x][0] <= 1:
				hueAffinity = 2*(img[y][x][0]) - 5/3
				
			HueIndexVal = (math.erf(hueAffinity-0.5) + 1)/2
			HueIndexArray[y][x] = HueIndexVal
			
	conLog("Hue Index calculation is complete!")
	return(HueIndexArray)
	
def AlgalBloomDetectionIndex(NGRDI, HueIndex, SatIndex):
	conLog("Algal Bloom Detection Index calculation is starting...")
	imgShape = NGRDI.shape
	
	ABDIArray = np.zeros([imgShape[0], imgShape[1]])
	ABDIImg = np.zeros([imgShape[0], imgShape[1], 3])
	
	for y in range(imgShape[0]):
		for x in range(imgShape[1]):
			ABDIVal = NGRDI[y][x] * HueIndex[y][x] * SatIndex[y][x]
			
			ABDIVal *= 255 #normalize value from [0 -> 1] to [0 -> 255]
			ABDIArray[y][x] = ABDIVal * 5
	
	ABDIImg = ABDIArray.astype(np.uint8)
	ABDIImgColor = cv2.applyColorMap(ABDIImg, cv2.COLORMAP_HOT)
	 
	newImgABDIString = imgName+"ABDI.jpg"
	cv2.imwrite(newImgABDIString, ABDIImgColor)
	conLog("Algal Bloom Detection Index calculation is complete!")
	
	return(ABDIImgColor)
	
def imageFinalOverlay(imgABDI):
	conLog("Overlaying ABDI map and final image...")
	
	imgOrig = imageAccess(imgName+"Processed.jpg", logBool=False)
	imgMask = imageAccess(imgName+"Mask.jpg", logBool=False)

	imgMaskInv = cv2.bitwise_not(imgMask).astype(np.uint8)
	imgMaskInv = cv2.cvtColor(imgMaskInv, cv2.COLOR_BGR2GRAY)

	newImgMaskInvString = imgName+"MaskInv.jpg"
	cv2.imwrite(newImgMaskInvString, imgMaskInv)

	imgFinal = cv2.bitwise_and(imgOrig, imgOrig, mask=imgMaskInv)
	newImgAlgaeInvString = imgName+"AlgaeInv.jpg"
	
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
	imgFinal = cv2.morphologyEx(imgFinal, cv2.MORPH_OPEN, kernel)
	cv2.imwrite(newImgAlgaeInvString, imgFinal)
	
	imgFinal = imgFinal + imgABDI

	newImgFinalString = imgName+"Final.jpg"
	cv2.imwrite(newImgFinalString, imgFinal)
	conLog("Overlaying ABDI map and final image complete!")
	
	return(imgFinal)
	
def calculateAlgaePercent(imgABDI):
	#in order to modify these global variables
	global resultAlgaePercentage
	global resultAlgaeBool
	
	imgShape = imgABDI.shape
	
	totalPixelCount = imgShape[0] * imgShape[1]
	ABDINonZeroCount = np.count_nonzero(cv2.cvtColor(imgABDI, cv2.COLOR_BGR2GRAY))
	
	algaePercentage = ABDINonZeroCount/totalPixelCount
	if algaePercentage >= 0.10:
		hasAlgae = True
	else:
		hasAlgae = False
	
	# print("\nRESULTS:")
	# print("\tTotal pixels in image: "+format (totalPixelCount, ',d'))
	# print("\tAlgae pixels in image: "+format (ABDINonZeroCount, ',d'))
	
	# print("\n\tAlgae percentage*: "+format (algaePercentage, '.0%'))
	# print("\tImage has algae: "+str(hasAlgae))
	
	# print("\n\n\t*relative to the rest of the image")
	
	resultAlgaePercentage = algaePercentage
	resultAlgaeBool = hasAlgae
	
	
#####################################################################################################################################
def main():
	
	img = imageAccess(imgPath)
	
	os.chdir(directoryResultsSpecific)
	
	imgProcessed = imagePreProcess(img)
	imgRemovedEdges = imageRemoveEdges(imgProcessed)

	imgAlgae = imageTrackAlgae(imgRemovedEdges)
	imgProcessed_HSV = RGB2HSV_CUSTOM(imgRemovedEdges)
	imgAlgae_HSV = RGB2HSV_CUSTOM(imgAlgae)

	NGRDIValArray = NGRDI(imgAlgae)
	SatIndexValArray = SatIndex(imgProcessed_HSV, imgAlgae_HSV)
	HueIndexValArray = HueIndex(imgAlgae_HSV)

	imgABDI = AlgalBloomDetectionIndex(NGRDIValArray, HueIndexValArray, SatIndexValArray)

	imageFinalOverlay(imgABDI)

	calculateAlgaePercent(imgABDI)

#####################################################################################################################################
