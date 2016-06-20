from numpy import *
import operator
import matplotlib
import matplotlib.pyplot as plt
import os

def createDataSet():
    group = array([[1.0,1.1], [1.0,1.0], [0,0], [0,0.1]])
    labels = ['A','A','B','B']
    return group, labels

def classify(inputArr, trainArr, labels, k):
    dataSetSize = trainArr.shape[0]
    diffMat = tile(inputArr,(dataSetSize,1)) - trainArr
    sqrtMat = diffMat**2
    sqDistance = sqrtMat.sum(axis=1)
    distance = sqDistance**0.5
    sortedDistanceIdx = distance.argsort()
    classCount = {}

    for i in range(k):
        voteClass = labels[sortedDistanceIdx[i]]
        classCount[voteClass] = classCount.get(voteClass,0)+1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1),reverse=True)
    return sortedClassCount[0][0]

def file2matrix(filename):
    fr = open(filename)
    arrayOLines = fr.readlines()
    numOLines = len(arrayOLines)
    returnMat = zeros((numOLines,3))
    classLabelVec = []
    index = 0
    for line in arrayOLines:
        line = line.strip()
        listFromLine = line.split('\t')
        returnMat[index,:] = listFromLine[:3]
        classLabelVec.append(int(listFromLine[-1]))
        index += 1
    return returnMat, classLabelVec

def autoNorm(dataSet):
    minVals = dataSet.min(0)
    maxVals = dataSet.max(0)
    ranges = maxVals - minVals
    normDataSet = zeros(shape(dataSet))
    m = dataSet.shape[0]
    normDataSet = dataSet - tile(minVals,(m,1))
    normDataSet = normDataSet/tile(ranges,(m,1))
    return normDataSet, ranges, minVals

def datingClassTest():
    hoRatio = 0.10
    datingDataMat, datingLabels = file2matrix('datingTestSet2.txt')
    normMat, ranges, minVals = autoNorm(datingDataMat)
    m = normMat.shape[0]
    numTestVecs = int(m*hoRatio)
    errorCount = 0.0

    for i in range(numTestVecs):
        classifierResult = classify(normMat[i,:], normMat[numTestVecs:m,:],\
                datingLabels[numTestVecs:], 10)
        print 'result is: %d, the real label is: %d' % (classifierResult, \
                datingLabels[i])
        if classifierResult != datingLabels[i]:
            errorCount += 1.0
    print 'total error is: %f' % (errorCount/float(numTestVecs))

def img2vector(filename):
    returnVect = zeros((1,1024))
    fr = open(filename)
    for i in range(32):
        lineStr = fr.readline()
        for j in range(32):
            returnVect[0,32*i+j] = int(lineStr[j])
    return returnVect

def handwritingClassTest():
    labels = []
    errorCount = 0
    trainDir = 'digits/trainingDigits/'
    testDir = 'digits/testDigits/'
    trainFileList = os.listdir(trainDir)
    m = len(trainFileList)
    trainMat = zeros((m,1024))
    for i in range(m):
        fileName = trainFileList[i].split('.')[0]
        labels.append(int(fileName.split('_')[0]))
        trainMat[i,:] = img2vector(trainDir + trainFileList[i])

    testFileList = os.listdir(testDir)
    n = len(testFileList)
    for i in range(n):
        fileName = testFileList[i].split('.')[0]
        testLabel = int(fileName.split('_')[0])
        testVec = img2vector(trainDir + testFileList[i])
        classifiedLabel = classify(testVec, trainMat, labels, 3)
        if classifiedLabel != testLabel:
            errorCount += 1
            print fileName, classifiedLabel, testLabel
    print errorCount/float(n)

if __name__=='__main__':
    group, labels = createDataSet()
    '''
    print group
    print labels
    print classify([1,1],group,labels,3)

    datingDataMat, datingLabels = file2matrix('datingTestSet2.txt')
    print datingDataMat
    print datingLabels[0:20]
    '''
    #datingClassTest()
    
    handwritingClassTest()

    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #ax.scatter(datingDataMat[:,0],datingDataMat[:,1],
    #        15.0*array(datingLabels), 15.0*array(datingLabels))
    #plt.show()

    #normMat, ranges, minVals = autoNorm(datingDataMat)
    #print normMat, ranges, minVals
