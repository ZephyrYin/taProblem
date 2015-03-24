__author__ = 'zephyryin'
from taAssignment import taAssignment
import time
#

fileName = 'testData'
fileName = 'dataset_AI_CSP'
fileName = 'dataset_AI_CSP_correct'
fileName = 'testData1'

taAssign = taAssignment(fileName)
taAssign.initialize()

for c in taAssign.courseList:
    c.printDetails()

# for t in taAssign.taList:
#     t.printDetails()

cur0 = time.clock()
taAssign.backtrackingSearch()
cur1 = time.clock()
print(cur1 - cur0)

taAssign.forwardChecking()
cur3 = time.clock()
print(cur3 - cur1)

taAssign.constraintPropagation()
print(time.clock() - cur3)






