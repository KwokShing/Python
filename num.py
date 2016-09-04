import sys
import copy
import getopt

from numpy import *
import operator

randArr = random.rand(4,4)
print type(randArr)
print randArr
randMat = mat(random.rand(4,4))
print type(randMat)
print randMat
print randMat.I
print eye(4)
