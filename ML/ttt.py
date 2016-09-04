#import kNN
from numpy import *

def classify(inputArr, trainArr, labels, k):
    dataSetSize = trainArr.shape[0]
    diffMat = tile(inputArr,(dataSetSize,1)) - trainArr
    sqrtMat = diffMat**2
    sqDistance = sqrtMat.sum(axis=1)
    distance = sqDistance**0.5
    sortedDistance = distance.argsort()




if __name__=='__main__':
    arr = array([3,1,2])
    order = argsort(arr)
    print order
