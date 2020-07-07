####################################################################################################################################
####################################################################################################################################
#		IMPORTANT: Please have this file and the actual program in the same directory
#		IMPORTANT: Create a folder called ABD_images in the same directory and place all the images there if doing a multi run
####################################################################################################################################
####################################################################################################################################
import os
import time
import ABDProgram as ABD

def multiRunMode():
	ABD.conLog("Starting multi run!")

	directoryOrig = os.getcwd()
	ABD.conLog("Original working directory: "+str(directoryOrig))

	#creates ABD_results folder
	try:
		os.mkdir("ABD_results")
		ABD.conLog("Created ABD_results folder!")
	except:
		ABD.conLog("Could not create ABD_results folder! Is it already created?")
		
	directoryResults = directoryOrig +"\\ABD_results"

	#try:
	#accesses ABD_images folder
	directoryImages = directoryOrig +"\\ABD_images"
	imgList = os.listdir(directoryImages)

	#outputs the first three filenames in the directory
	imgCount = 0
	for img in imgList:
		imgCount += 1
	ABD.conLog("Images in directory: " + str(imgList[0]) +", "+ str(imgList[1]) + ", " + str(imgList[2])+" + " + str(imgCount - 3) + " more")

	os.chdir(directoryResults)
	resultTxt = open("results.txt", "w")
	resultTxt.write("Image Name | Algae Percentage | Has Algae\n\n")

	#variables used for confusion matrix
	actualTrue = 0
	actualFalse = 0

	predictedTrue = 0
	predictedFalse = 0

	actualBool = False
	predictedBool = False

	truePositiveCount = 0
	trueNegativeCount = 0
	falsePositiveCount = 0
	falseNegativeCount = 0

	#calls the program for each img
	for img in imgList:
		os.chdir(directoryOrig)
		#changes the global variables in the original program
		ABD.imgPath = img
		imgName = img.split(".", 1)[0]
		ABD.imgName = imgName
		
		#counts actual true and false based on img name
		if imgName.find("hasAlgae") != -1:
			actualTrue += 1
			actualBool = True
		else:
			actualFalse += 1
			actualBool = False
		
		#creates a folder for each image in ABD_results
		os.chdir(directoryResults)
		try:
			os.mkdir(imgName)
		except Exception:
			pass
		os.chdir(directoryImages)
		ABD.directoryResultsSpecific = directoryResults+"\\"+imgName
		
		ABD.conLog("####################################################################################")
		ABD.conLog("Image Name: "+ABD.imgName)
		ABD.main("MULTI")
		
		#counts predicted true and false
		if ABD.resultAlgaeBool:
			predictedTrue += 1
			predictedBool = True
		else:
			predictedFalse += 1
			predictedBool = False
		resultTxt.write(imgName + "\t\t" + '{:.2f}'.format(ABD.resultAlgaePercentage * 100)+"\t\t"+str(ABD.resultAlgaeBool) +"\n")
		
		#confusion matrix
		if actualBool and predictedBool:
			truePositiveCount += 1
		elif not actualBool and not predictedBool:
			trueNegativeCount += 1
		elif not actualBool and predictedBool:
			falsePositiveCount += 1
		elif actualBool and not predictedBool:
			falseNegativeCount += 1

	resultTxt.write("\n\nConfusion Matrix")
	resultTxt.write("\n\tActual True:\t"+str(actualTrue))
	resultTxt.write("\n\tActual False:\t"+str(actualFalse))
			
	resultTxt.write("\n\tPredicted True:\t"+str(predictedTrue))
	resultTxt.write("\n\tPredicted False:\t"+str(predictedFalse))

	resultTxt.write("\n\n\tTrue Positive:\t"+str(truePositiveCount))
	resultTxt.write("\n\tTrue Negative:\t"+str(trueNegativeCount))
	resultTxt.write("\n\tFalse Positive:\t"+str(falsePositiveCount))
	resultTxt.write("\n\tFalse Negative:\t"+str(falseNegativeCount))
	resultTxt.close()

	ABD.conLog("####################################################################################")
	ABD.conLog("Program complete!")

def singleRunMode():
	print()
	
	inputImageString = input("File name (including the file extension): ")
	imageName, sep, imageFileType = inputImageString.partition(".")
	ABD.imgPath = inputImageString
	ABD.imgName = imageName
	
	print()
	ABD.startTime = time.time()
	ABD.main()
	
	
inputChar = input("Do a Multi run? (Y/N):")

if inputChar.lower() == "y":
	ABD.startTime = time.time()
	multiRunMode()
elif inputChar.lower() == "n":
	
	singleRunMode()
else:
	print("Invalid input!")
	






