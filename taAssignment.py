__author__ = 'zephyryin'
from baseClass import Time, Course, TA
import copy
import operator

class taAssignment(object):
    def __init__(self, inputFile):
        self.inputFile = inputFile
        self.courseList = []
        self.courseDict = {}        # save course name and its index in list
        self.courseNames = []
        self.taList = []
        self.taDict = {}                # save ta name and its index in list
        self.taNames = []
        self.graph = {}
        self.domain = {}

    def initialize(self):
        file = open(self.inputFile)
        lines = file.readlines()            # read whole file
        file.close()
        tableCnt = 1

        for l in range(len(lines)):
            if not lines[l]:                    # blank line
                continue

            if lines[l][0:2] == 'TA' or lines[l][0:3] == 'CSE':
                if lines[l][0:3] == 'CSE' and lines[l+1] and lines[l+1][0:3] != 'CSE':
                    lines[l] = lines[l].rstrip('\n') +  lines[l+1]
                words = self.getWords(lines[l])     # turn the line to word list

                if tableCnt == 1:               # course schedule
                    course = Course('', [], [], 0, False, [], [])
                    course.name = words[0]
                    for i in range(1, len(words), 2):
                        time = Time('', '')
                        time.day = words[i]
                        time.hourAndMin = words[i+1]
                        course.scheduleTimes.append(time)
                    if course.name in self.courseDict:                      # remove duplicates
                        self.courseList.remove(self.courseDict[course.name])
                    self.courseList.append(course)
                    self.courseDict[course.name] = self.courseList[len(self.courseList)-1]

                elif tableCnt == 2:             # course recitation
                    self.courseDict[words[0]].recitationTimes = []      # override duplicates
                    for i in range(1, len(words), 2):
                        time = Time('', '')
                        time.day = words[i]
                        time.hourAndMin = words[i+1]
                        self.courseDict[words[0]].recitationTimes.append(time)

                elif tableCnt == 3:             # course detail (student num and if need ta to attend)
                    self.courseDict[words[0]].stuNum = int(words[1])
                    self.courseDict[words[0]].needTaAttend = True if words[2] == 'yes' else False

                elif tableCnt == 4:             # course skill requirement
                    self.courseDict[words[0]].skills = []
                    for i in range(1, len(words)):          # override duplicates
                        self.courseDict[words[0]].skills.append(words[i])

                elif tableCnt == 5:             # TA responsibility
                    ta = TA(' ', [], [])
                    ta.name = words[0]
                    for i in range(1, len(words), 2):
                        time = Time('', '')
                        time.day = words[i]
                        time.hourAndMin = words[i+1]
                        ta.responTimes.append(time)
                    if ta.name in self.taDict:
                        self.taList.remove(self.taDict[ta.name])
                    self.taList.append(ta)
                    self.taDict[ta.name] = self.taList[len(self.taList) - 1]

                elif tableCnt == 6:             # TA skills
                    self.taDict[words[0]].skills = []       # override duplicates
                    for i in range(1, len(words)):
                        self.taDict[words[0]].skills.append(words[i])          # eliminate blank

            else:
                for i in range(1, 7):
                    if lines[l][0] == str(i):
                        tableCnt = i            # table index
                        break
        self.getMatchTA()               # get most match tas after courseList and taList is initialized
        self.courseList.sort(key = lambda c : len(c.candidateTAs))          # handle course with less domain first
        self.courseNames = [course.name for course in self.courseList]
        self.taNames = [ta.name for ta in self.taList]
        self.constructGraph()           # construct graph of courses for forward checking
        self.genDomain()

    def constructGraph(self):
            self.graph = {course.name : [] for course in self.courseList}
            length = len(self.courseList)
            for i in range(length-1):
                courseA = self.courseList[i]
                for j in range(i+1, length):
                    courseB = self.courseList[j]
                    if len(list(set(courseA.candidateTAs)&set(courseB.candidateTAs))) > 0:
                        self.graph[courseA.name].append(courseB)
                        self.graph[courseB.name].append(courseA)


    def genDomain(self):
        for course in self.courseList:
            self.domain[course.name] = []
            for ta in course.candidateTAs:
                self.domain[course.name].append(ta.name)
                self.domain[course.name].append(ta.name)


    def getMatchTA(self):
        for course in self.courseList:
            dic = {}
            for ta in self.taList:
                sameSkillNum = len(list(set(course.skills)&set(ta.skills)))
                dic[ta.name] = sameSkillNum
            sortedDict = sorted(dic.items(), key=operator.itemgetter(1))        # sort course by domain size
            for t in sortedDict:
                course.candidateTAs.append(self.taDict[t[0]])
            course.candidateTAs = self.filterConfilct(course)

    # def getMatchTA(self):
    #     for course in self.courseList:
    #         maxNum = -1
    #         for ta in self.taList:
    #             sameSkillNum = len(list(set(course.skills)&set(ta.skills)))
    #             #print(course.name + ' ' + str(sameSkillNum) + ' ' + str(maxNum) + ' ' + ta.name)
    #             if sameSkillNum > maxNum:
    #                 maxNum = sameSkillNum
    #                 course.candidateTAs.clear()
    #                 course.candidateTAs.append(ta)
    #             elif sameSkillNum == maxNum:
    #                 course.candidateTAs.append(ta)
    #         course.candidateTAs = self.filterConfilct(course)

    def getWords(self, line):
        words = [w.strip() for w in line.split(',')]
        while '' in words:
            words.remove('')
        return words

    def getTALimit(self, num):
        if num >= 60:
            return int(2.0 * 2)
        if num >= 40 and num < 60:
            return int(1.5 * 2)
        if num >= 25 and num < 40:
            return int(0.5 * 2)
        return int(0.0)

    def filterConfilct(self, course):
        candidates = course.candidateTAs
        courseTime = []
        if len(course.recitationTimes) > 0:
            courseTime = course.recitationTimes

        if course.needTaAttend:
            courseTime += course.scheduleTimes
        for ta in candidates:
            found = False
            for responTime in ta.responTimes:
                if found:
                    break
                for cT in courseTime:
                    if responTime.isConflict(cT):
                        candidates.remove(ta)
                        found = True
                        break
        return candidates

    def backtrackingSearch(self):

        taNumDict = {taName : 2 for taName in self.taNames}
        courseTaNumDict = {course.name : self.getTALimit(course.stuNum) for course in self.courseList}

        path = {cName :[] for cName in self.courseNames}
        if self.permuationBS(path, courseTaNumDict, taNumDict, 0,  0):
            for p in path:
                print(p, end = ': ')
                for t in path[p]:
                    print(t.name, end = ' ')
                print('')
        else:
            print('no solution')
    def permuationBS(self, path, courseTaNumDict, taNumDict, index, canIndex):
        if index >= len(courseTaNumDict):
            return True
        course = self.courseList[index]
        courseName = course.name

        if courseTaNumDict[courseName] <= 0:
            return self.permuationBS(path, courseTaNumDict, taNumDict, index + 1,  0)
        else:
            candidates = self.domain[courseName]
            if candidates == []:
                return False

            for i in range(canIndex, len(candidates) - courseTaNumDict[courseName]):
                taName = candidates[i]
                ta = self.taDict[taName]
                if taNumDict[taName] > 0:
                    path[courseName].append(ta)
                    taNumDict[taName] = taNumDict[taName] - 1
                    courseTaNumDict[courseName] = courseTaNumDict[courseName] - 1
                    if self.permuationBS(path, courseTaNumDict, taNumDict, index, i+1):
                        return True
                    path[courseName].pop()
                    courseTaNumDict[courseName] = courseTaNumDict[courseName] + 1
                    taNumDict[taName] = taNumDict[taName] + 1
        return False

    def forwardChecking(self):
        taNumDict = {t : 2 for t in self.taNames}
        courseTaNumDict = {course.name : self.getTALimit(course.stuNum) for course in self.courseList}
        path = {cName : [] for cName in self.courseNames}

        if self.permutationFC(self.domain, path, courseTaNumDict, taNumDict, 0):
            for p in path:
                print(p, end = ': ')
                for t in path[p]:
                    print(t, end = ' ')
                print('')
        else:
            print('no solution')

    def permutationFC(self, avaDict, path, courseTaNumDict, taNumDict, index):
        #print(index)
        if index >= len(courseTaNumDict):
            return True
        course =self.courseList[index]
        courseName = course.name
        if courseTaNumDict[courseName] <= 0:
            return self.permutationFC(avaDict, path, courseTaNumDict, taNumDict, index + 1)
        else:
            if len(avaDict[courseName]) <= 0:
                return False
            for taName in avaDict[courseName]:

                newAvaDict = copy.deepcopy(avaDict)
                newAvaDict[courseName].remove(taName)

                notWork = False
                fG = self.graph[courseName]          # forward checking
                if len(fG) > 0:
                    for c in fG:
                        if self.courseNames.index(courseName) >= self.courseNames.index(c.name):
                            continue
                        if taName in newAvaDict[c.name]:
                            newAvaDict[c.name].remove(taName)
                            if(len(newAvaDict[c.name]) == 0):
                                notWork = True
                                break
                if notWork:
                    continue

                path[courseName].append(taName)
                taNumDict[taName] = taNumDict[taName] - 1
                courseTaNumDict[courseName] = courseTaNumDict[courseName] - 1
                if self.permutationFC(newAvaDict, path, courseTaNumDict, taNumDict, index):
                    return True
                path[courseName].pop()
                taNumDict[taName] = taNumDict[taName] + 1
                courseTaNumDict[courseName] = courseTaNumDict[courseName] + 1
        return False

    def constraintPropagation(self):
        domain = copy.deepcopy(self.domain)
        taNumDict = {t : 2 for t in self.taNames}
        courseTaNumDict = {course.name : self.getTALimit(course.stuNum) for course in self.courseList}
        path = {cName : [] for cName in self.courseNames}

        if self.permutationCP(domain, path, courseTaNumDict, taNumDict, 0):
            for p in path:
                print(p, end = ': ')
                for t in path[p]:
                    print(t, end = ' ')
                print('')
        else:
            print('no solution')

    def permutationCP(self, avaDict, path, courseTaNumDict, taNumDict, index):
        if index >= len(courseTaNumDict):
            return True
        course =self.courseList[index]
        courseName = course.name
        if courseTaNumDict[courseName] <= 0:
            return self.permutationFC(avaDict, path, courseTaNumDict, taNumDict, index + 1)
        else:
            if len(avaDict[courseName]) <= 0:
                return False

            #constraint propagation
            modified = True
            while(modified):
                modified = False
                for courseA in self.courseList:
                    for courseB in self.graph[courseA.name]:
                        if len(courseA.candidateTAs) < len(courseB.candidateTAs):
                            continue
                        for taName in avaDict[courseA.name]:
                            if len(avaDict[courseB.name]) - 1 < courseTaNumDict[courseB.name]:
                                avaDict[courseA.name].remove(taName)            # delete candidate in domain
                                modified = True

            for taName in avaDict[courseName]:

                newAvaDict = copy.deepcopy(avaDict)
                newAvaDict[courseName].remove(taName)

                notWork = False
                fG = self.graph[courseName]          # forward checking
                if len(fG) > 0:
                    for c in fG:
                        if self.courseNames.index(courseName) >= self.courseNames.index(c.name):
                            continue
                        if taName in newAvaDict[c.name]:
                            newAvaDict[c.name].remove(taName)           # delete candidate in domain
                            if(len(newAvaDict[c.name]) == 0):
                                notWork = True
                                break
                if notWork:
                    continue

                path[courseName].append(taName)
                taNumDict[taName] = taNumDict[taName] - 1
                courseTaNumDict[courseName] = courseTaNumDict[courseName] - 1
                if self.permutationFC(newAvaDict, path, courseTaNumDict, taNumDict, index):
                    return True
                path[courseName].pop()
                taNumDict[taName] = taNumDict[taName] + 1
                courseTaNumDict[courseName] = courseTaNumDict[courseName] + 1
        return False
