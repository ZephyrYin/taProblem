__author__ = 'zephyryin'
import copy

class Time(object):
    def __init__(self, day, hourAndMin):
        self.day = day
        self.hourAndMin = hourAndMin

    def timeToMin(self):
        weekDict = {'Mon':0, 'Tue':1, 'Wed':2, 'Thu':3, 'Fri':4, 'Sat':5, 'Sun':6}
        if self.day not in weekDict:
            return -1
        d = weekDict[self.day]
        wholeTime = self.hourAndMin.split()
        hAndMin = wholeTime[0].split(':')
        h = int(hAndMin[0])
        if wholeTime[1] == 'PM':
            h = h%12 + 12
        minutes = d*24*60 + h*60 + int(hAndMin[1])
        return minutes

    def isConflict(self, timeB):                    # check whether
        minutes = self.timeToMin()
        minutesB = timeB.timeToMin()
        if abs(minutes - minutesB) < 90:
            return True
        return False

    def show(self):
        print(self.day + ' ' + self.hourAndMin, end = ' ')


class Course(object):
    def __init__(self, name, scheduleTimes, recitationTimes, stuNum, needTaAttend, skills, canditateTAs):
        self.name = name
        self.scheduleTimes = scheduleTimes
        self.recitationTimes = recitationTimes
        self.stuNum = stuNum
        self.needTaAttend = needTaAttend
        self.skills = skills
        self.candidateTAs = canditateTAs            # ta names

    def printDetails(self):
        print('course name: ' + self.name)
        print('schedule time: ', end = '')
        for time in self.scheduleTimes:
            time.show()

        if(len(self.recitationTimes) > 0):
            print('recitation time:', end = '')
            for time in self.recitationTimes:
                time.show()
        print('')
        print('student number: ' + str(self.stuNum))
        print('need TA attend: ' + str(self.needTaAttend))
        print('skills: ', end = '')
        for s in self.skills:
            print(s, end = ' ')
        print('\n' + 'tas: ', end = '')
        for c in self.candidateTAs:
            print(c.name, end = ' ')
        print('\n')

class TA(object):
    def __init__(self, name, responTimes, skills):
        self.name = name
        self.responTimes = responTimes
        self.skills = skills
    def printDetails(self):
        print('TA name: ' + self.name)
        print('responsible time: ', end = '')
        for time in self.responTimes:
            time.show()
        print('\n' + 'skills: ', end = '')
        for s in self.skills:
            print(s, end = ' ')
        print('\n')

