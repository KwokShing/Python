from numpy import *
import operator

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
        line = line.strtip()
        listFromLine = line.split('\t')
        returnMat[index,:] = listFromLine[:3]
        classLabelVec.append(int(listFromLine[-1]))
        index += 1
    return returnMat, classLabelVec

if __name__=='__main__':
    group, labels = createDataSet()
    print group
    print labels
    print classify([1,1],group,labels,3)

    datingDataMat, datingLabels = file2matrix('datingTestSet.txt')
