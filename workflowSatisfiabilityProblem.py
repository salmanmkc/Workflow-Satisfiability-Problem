# python -m pip install --upgrade --user ortools

# from z3 import *
import re
import sys
from time import time as currenttime
import time
from ortools.sat.python import cp_model
from collections import defaultdict
constraintsDict = defaultdict(list)
seenAuth = defaultdict(int)
seenSep = defaultdict(int)
seenBind = defaultdict(int)
seenAtMostK = defaultdict(int)
seenOneTeam = defaultdict(int)
printOutputGlob = 1

import numpy as np
from random import *




class WSPSolutionPrinter(cp_model.CpSolverSolutionCallback):

    def __init__(self, M, u, s, solver, printOutput=1):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__M = M
        self.__u = u
        self.__s = s
        self.__solver = solver
        self.__solution_count = 0
        self.__start_time = time.time()
        self.__printOutput = printOutput

    def solution_count(self):
        return self.__solution_count

    def on_solution_callback(self):
        current_time = time.time()
        print('Solution %i, time = %f ms' %
              (self.__solution_count, (current_time - self.__start_time) * 1000))
        self.__solution_count += 1
        # self.__printOutput = printOutput

        outputdict = defaultdict(list)
        for y in range(0, self.__u):
            for x in range(0, self.__s):
                set = self.Value(self.__M[y][x])
                if set == 1:
                    outputdict[y+1].append(x+1)
                # if self.Value(self.__M[y][x]) == 1:
                    if printOutputGlob == 1:
                        print(f'u{y+1} s{x+1}')     
        if printOutputGlob == 2:
            for k, v in outputdict.items():
                print(f'\nUser {k} ', end=' ')
                count = 0
                for s in v:
                    if len(str(k)) == 1 and count == 0:
                        print(f' ', end='')
                        count += 1
                    print(f'S{s}', end=' ')
            print('')


def showModelMatrix(M, u, s, solver, printOutput=1):
    outputdict = defaultdict(list)
    for y in range(0, u):
        for x in range(0, s):
            set = solver.Value(M[y][x])
            if set == 1:
                outputdict[y+1].append(x+1)
                if printOutput == 1:
                    print(f'u{y+1} s{x+1}')
    if printOutput == 2:
        for k, v in outputdict.items():
            print(f'\nUser {k} ', end=' ')
            count = 0
            for s in v:
                if len(str(k)) == 1 and count == 0:
                    print(f' ', end='')
                    count += 1
                print(f'S{s}', end=' ')
        print('')
class Instance:
    def __init__(self):
        self.number_of_steps = 0
        self.number_of_users = 0
        self.number_of_constraints = 0
        self.constraints = []


def read_file(filename):
    def read_attribute(name):
        line = f.readline()
        match = re.match(f'{name}:\\s*(\\d+)$', line)
        if match:\
            return int(match.group(1))
        else:
            raise Exception("Could not parse line {line}; expected the {name} attribute")

    instance = Instance()
    with open(filename) as f:
        instance.number_of_steps = read_attribute("#Steps")
        instance.number_of_users = read_attribute("#Users")
        instance.number_of_constraints = read_attribute("#Constraints")    

        for r in range(instance.number_of_constraints):
            instance.constraints.append(f.readline().rstrip('\n'))

        while True:
            l = f.readline()
            if l == "":
                break;
            m = re.match('^\\s*(\\d+)\\s+(\\d+)\\s*$', l)
            if m:
                instance.exams_to_students.append((int(m.group(1)), int(m.group(2))))
            else:
                raise Exception(f'Failed to parse this line: {l}')
        # print(f'Numbers of steps: {instance.number_of_steps}')
        # print(f'Number of users: {instance.number_of_users}')
        # print(f'Number of constraints: {instance.number_of_constraints}')
        # print(f'\nConstraints')

        
        for i in range(len(instance.constraints)):
            # print(instance.constraints[i])
            split = instance.constraints[i].split(" ")
            constraintsDict[split[0]] += [split[1:]]

        
    return instance


def generateConstraints(inst):
    instance = Instance()
    constarintsdict = defaultdict(list)
    seenAuth = defaultdict(int)
    seenSep = defaultdict(int)
    seenBind = defaultdict(int)
    seenAtMostK = defaultdict(int)
    seenOneTeam = defaultdict(int)
    # instance.number_of_steps = randint(1, 50)
    # instance.number_of_users = randint(1, 50)  
    instance.number_of_steps = inst[5]
    instance.number_of_users = inst[6]
    num_auth = inst[0]
    num_bind = inst[1]
    num_sep = inst[2]
    num_atmostk = inst[3]
    num_oneteam = inst[4]
    instance.number_of_constraints = num_auth + num_bind + num_sep + num_atmostk + num_oneteam

    # instance.number_of_constraints = randint(1, num_conststraints)
    # instance.number_of_constraints = num_conststraints
    atmostkcount = 0
    # print('Generated Constraints:\n')
    # for r in range(instance.number_of_constraints):
        # typeConst = randint(1, 5)
    for i in range(num_auth): # append auth constraint
        customAuthStr = 'Authorisations '
        numUser = ''
        count = 0
        while numUser in seenAuth or count == 0:
            numUser = randint(1, instance.number_of_users)
            count += 1
        seenAuth[numUser] += 1
        customAuthStr += f'u{numUser} '

        numStepsAuth = randint(1, instance.number_of_steps)
        lastUser = 0
        seen = defaultdict(int)
        for i in range(numStepsAuth):
            userAuth = randint(lastUser, instance.number_of_steps)
            if userAuth in seen:
                userAuth = randint(0, instance.number_of_steps)
            customAuthStr += f's{userAuth} '
            seen[userAuth] += 1
            lastUser = userAuth
        instance.constraints.append(customAuthStr.rstrip())
        # print(customAuthStr.rstrip())
    
    
    for i in range(num_bind): # Binding-of-duty s1 s4
        customBindStr = 'Binding-of-duty '
        step1, step2, count = '', '', 0
        while f's{step1} s{step2}' in seenBind or f's{step2} s{step1}' in seenBind or count == 0:
            step1 = randint(0, instance.number_of_steps)
            step2 = randint(0, instance.number_of_steps)
            while step2 == step1:
                step2 = randint(0, instance.number_of_steps)
            count += 1
        seenBind[f's{step1} s{step2}'] += 1
        seenBind[f's{step2} s{step1}'] += 1
        customBindStr += f's{step1} s{step2}'
        instance.constraints.append(customBindStr.rstrip())
        # print(customBindStr.rstrip())
    
    for i in range(num_sep): # Separation-of-duty s1 s4
        customSepStr = 'Separation-of-duty '
        step1, step2, count = '', '', 0
        while f's{step1} s{step2}' in seenSep or f's{step2} s{step1}' in seenSep or count == 0:
            step1 = randint(0, instance.number_of_steps)
            step2 = randint(0, instance.number_of_steps)
            while step2 == step1:
                step2 = randint(0, instance.number_of_steps)
            count += 1
        seenSep[f's{step1} s{step2}'] += 1
        seenSep[f's{step2} s{step1}'] += 1
        customSepStr += f's{step1} s{step2}'
        instance.constraints.append(customSepStr.rstrip())
        # print(customSepStr.rstrip())
    
    

    for i in range(num_atmostk): # AtMostK s1 s4
        count = 0
        customAtMostK = ''
        while count == 0 or customAtMostK in seenAtMostK:
            customAtMostK = 'At-most-k '
            k = randint(1, instance.number_of_users)
            while k >= instance.number_of_steps:
                k = randint(1, instance.number_of_users)
            steplimit = randint(k, instance.number_of_steps)
            customAtMostK += f'{k} '
            seenMostKLoc = defaultdict(int)
            # step = ''
            numSteps = randint(1, instance.number_of_steps)
            for i in range(numSteps):
                step = ''
                while f's{step}' in seenMostKLoc or step == '':
                    step = randint(0, instance.number_of_steps)
                    count += 1
                seenMostKLoc[f's{step}'] += 1
                customAtMostK += f's{step} '
            customAtMostK = customAtMostK.rstrip()
            atmostkcount += 1
        seenAtMostK[customAtMostK] += 1
        instance.constraints.append(customAtMostK)
        # print(customAtMostK)
               

            
        # do one team 
        # One-team  s4 s9 s2 (u20 u35 u22 u8) (u16 u11 u5 u27 u19 u41) (u9 u37 u39)
        for i in range(num_oneteam):
            count = 0
            customOneTeam = ''
            while count == 0 or customOneTeam in seenOneTeam:
                customOneTeam = 'One-team  '
                numStepsForTeam = randint(1, instance.number_of_steps)
                stepsSeenForTeam = defaultdict(int)
                for i in range(numStepsForTeam):
                    stepC = 0
                    stepToAdd = ''
                    while stepToAdd in stepsSeenForTeam or stepC == 0:
                        stepToAdd = randint(1, instance.number_of_steps)
                        stepC += 1
                    stepsSeenForTeam[stepToAdd] += 1
                    customOneTeam += f's{stepToAdd} '
                numTeams = randint(2, instance.number_of_users//2)
                userInTeam = defaultdict(int)
                for i in range(numTeams):
                    customOneTeam += f'('
                    numUserInTeam = randint(2, instance.number_of_users//numTeams)
                    for j in range(numUserInTeam):
                        userC = 0
                        # userToAdd = -1
                        userToAdd = ''
                        while userToAdd in userInTeam or userC == 0:
                            userToAdd = randint(1, instance.number_of_users)
                            # userToAdd = 1
                            
                            
                            userC += 1
                        userInTeam[userToAdd] += 1
                        if j == numUserInTeam-1:
                            customOneTeam += f'u{userToAdd}) '
                        else:
                            customOneTeam += f'u{userToAdd} '
                            
                    # customOneTeam  += f')'
                customOneTeam = customOneTeam.rstrip()
                count += 1
            seenOneTeam[customOneTeam] += 1
            instance.constraints.append(customOneTeam)
            # print(customOneTeam)
                


    for i in range(len(instance.constraints)):
        # print(instance.constraints[i])
        split = instance.constraints[i].split(" ")
        constarintsdict[split[0]] += [split[1:]]
    
    # print('Generated Constraints:')
    # for k, v in constarintsdict.items():
    #     print(k)
    #     for indv in v:
    #         print(indv)
        # instance.constraints.append(f.readline().rstrip('\n'))
    return instance

def solve(instance, vars, multiple=0):
    if __name__ == '__main__':
        mintime = float('inf')
        # s = Solver()
        # solver_file = sys.argv[0]
        # 0, 1, 11, 14, 15, 19 sat but unsat in solution

        # file = '5-constraint/0.txt'
       
        # other = [1, 10]
        # other[1] = 10
        
        # print(inst)
        if isinstance(vars, list):
            inst = generateConstraints(vars[2:])
        elif vars == 101:
            file = 'instances/example1.txt'
            inst = read_file(file)
        else:
            inst = vars
        
        starttime = int(currenttime() * 1000)
        model = cp_model.CpModel()
        M = []
        allsteps = np.array([])
        stepdict = defaultdict(list)
        # for u in range(1, inst.number_of_users + 1):
        #     row = []
        #     for s in range(1, inst.number_of_steps + 1):
        #         uS = model.NewBoolVar(f'{u}{s}')
        #         row.append(uS)
        #         stepdict[s] += [uS]
        #     M.append(row)

        # authorisations
        authdidct = defaultdict(list)
        constraintstr = 'Authorisations'
        for i in range(len(constraintsDict[constraintstr])):
            user = str(constraintsDict[constraintstr][i][0])
            authdidct[user] = constraintsDict[constraintstr][i][1:]
        
        boolcount = 0
        for u in range(1, inst.number_of_users + 1):
            row = []
            rowOrTools = []
            for s in range(1, inst.number_of_steps + 1):
                if f'u{u}' in authdidct:
                    if str(f's{s}') in authdidct[f'u{u}']:
                        uS = model.NewBoolVar(f'')
                        row.append(uS)
                        rowOrTools.append(uS)
                        allsteps = np.append(allsteps, uS)
                        stepdict[s] += [uS]
                        boolcount +=1
                    else:
                        row.append(0)
                    if authdidct[f'u{u}'] == [] and s == inst.number_of_steps:
                            model.Add(sum(row) == 0)
                    if authdidct[f'u{u}'] != [] and s == inst.number_of_steps:    
                        model.Add(sum(rowOrTools) <= len(authdidct[f'u{u}']))
                else:
                    uS = model.NewBoolVar(f'{u}{s}')
                    row.append(uS)
                    rowOrTools.append(uS)
                    allsteps = np.append(allsteps, uS)
                    stepdict[s] += [uS]
                    boolcount +=1
            M.append(row)        

        # auth(model, M, authdidct)
        # Binding of duty
        binddict = []
        constraintstr = 'Binding-of-duty'
        for i in range(len(constraintsDict[constraintstr])):
            user = str(constraintsDict[constraintstr][i][0])
            binddict.append((user, str(constraintsDict[constraintstr][i][1])))
        
        # print('Binding')
        # u + 1 since users and steps are 1-indexed rather than 0
        for u in range(1, len(M) + 1):           
            for bind in binddict:
                counterpair = bind[1]
                counterpairmatrix = int(counterpair[1:]) -1
                s = int(bind[0][1:])
                first = M[u-1][s-1] == 1
                second = M[u-1][counterpairmatrix]
                if not isinstance(second, int):
                    model.AddBoolAnd([M[u-1][s-1],M[u-1][counterpairmatrix]]).OnlyEnforceIf(M[u-1][counterpairmatrix])
                if not (first, int):
                    model.AddBoolAnd([M[u-1][s-1],M[u-1][counterpairmatrix]]).OnlyEnforceIf(M[u-1][s-1])
                    # model.Add(M[u-1][s-1] == 1).OnlyEnforceIf(M[u-1][counterpairmatrix])
                    # model.Add(M[u-1][counterpairmatrix] == 1).OnlyEnforceIf(M[u-1][s-1])
                # except:
                    # model.Add(M[u-1][s-1] == 0)
                    # model.Add(M[u-1][counterpairmatrix] == 0)
                # try:
                #     model.Add(M[u-1][counterpairmatrix] == 1).OnlyEnforceIf(M[u-1][s-1])
                # except:


        sepdict = []
        constraintstr = 'Separation-of-duty'
        for i in range(len(constraintsDict[constraintstr])):
            user = str(constraintsDict[constraintstr][i][0])
            sepdict.append((user, str(constraintsDict[constraintstr][i][1])))
        
        # print('Separation')
        # u + 1 since users and steps are 1-indexed rather than 0
        for u in range(1, len(M) + 1):           
            for sep in sepdict:
                counterpair = sep[1]
                counterpairmatrix = int(counterpair[1:]) -1
                s = int(sep[0][1:])
                # counterpair = sepdict[f's{s}']
                # counterpairmatrix = int(counterpair[1]) -1
                # model.AddAllDifferent([M[u-1][s-1], M[u-1][counterpairmatrix]])
                # model.AddImplication(M[u-1][s-1] == 1, M[u-1][counterpairmatrix] == 0)
                # model.Add(M[u-1][counterpairmatrix] == 0).OnlyEnforceIf(M[u-1][s-1])
                first = M[u-1][s-1]
                second = M[u-1][counterpairmatrix]
                # try:
                model.Add(M[u-1][s-1] + M[u-1][counterpairmatrix] < 2)
                # boolcount += 1
                    # print(f'If u{u-1} does s{s-1} cannot, they cannot do step {counterpairmatrix}')
                    # print(f'If u{u-1} does s{counterpairmatrix} cannot, they cannot do step {s-1}')   
                    # model.Add(M[u-1][s-1] == 0).OnlyEnforceIf(M[u-1][counterpairmatrix])
                    # model.Add(M[u-1][counterpairmatrix] == 0).OnlyEnforceIf(M[u-1][s-1])
                # except:
                    # model.Add(M[u-1][s-1] == 0)
                    # model.Add(M[u-1][counterpairmatrix] == 0)
                    # hello = 'hello'a
                    # print('cannot')
        
        # every step needs one user
        for i in range(len(M[0])):
            model.Add(sum(stepdict[i+1]) == 1)
        # boolvar = model.NewBoolVar('')
        # boolcount += 1
        model.Add(sum(allsteps) == inst.number_of_steps)
        # model.Add(sum(allsteps) == inst.number_of_steps).OnlyEnforceIf(boolvar)
        # model.Add(sum(allsteps) != inst.number_of_steps).OnlyEnforceIf(boolvar.Not())
        # stepcount = model.NewIntVar(0, inst.number_of_steps, '')
        # model.Add(stepcount == inst.number_of_steps).OnlyEnforceIf(boolvar)
        # model.Add(stepcount != inst.number_of_steps).OnlyEnforceIf(boolvar.Not())
        # model.AddHint(boolvar, 1)

        # for u in range(len(M)):
        #     for j in range(len(M)):
        #         if u!=j:
        #             for s in range(len(M[0])):
        #                 if not isinstance(M[j-1][s-1], int):
        #                     model.Add(M[u-1][s-1] == 0).OnlyEnforceIf(M[j-1][s-1])


        
                
        atmostkdict = []
        constraintstr = 'At-most-k'
        for i in range(len(constraintsDict[constraintstr])):
            user = constraintsDict[constraintstr][i][0]
            atmostkdict.append((user, constraintsDict[constraintstr][i][1:]))
        # model.Add(sum(stepdict[1]) < 3) 
        
        for kv in atmostkdict:
            setSteps = []
            allUserSets = np.array([])
            for u in range(1, len(M)+1):
                userSet = np.array([])
                for s in kv[1]:
                    usersteptoadd = M[u-1][int(s[1:])-1]
                    if not isinstance(usersteptoadd, int):
                        userSet = np.append(userSet, M[u-1][int(s[1:])-1])
                # x = model.NewIntVar(0, 10, 'x')
                # y = model.NewBoolVar('')
                b = model.NewBoolVar('')
                boolcount += 1
                model.AddBoolOr(userSet).OnlyEnforceIf(b)
                model.Add(sum(userSet) < 1).OnlyEnforceIf(b.Not())
                # model.Add(y == 1).OnlyEnforceIf(b)
                # model.Add(y == 0).OnlyEnforceIf(b.Not())
                allUserSets = np.append(allUserSets,b)
            model.Add(sum(allUserSets) <= int(kv[0]))
            # boolcount += 1
                        # sum of constructed array should be <= k
                        # each element in array should be 1 or 0 depending on if the user has done a task from the task list
                        # for loop controls which task/step we're checking
                    # model.Add(x + 1).OnlyEnforceIf(b)

        
        # one team
        # One-team s1 s2 s3 (u1 u3) (u2 u4 u5)
        # delim by ( and then for those steps mentioned, check if they are only part of one team, Xor(Or(team1), Or(team2), Or(team3)))
        oneteamdict = defaultdict(list)
        constraintstr = 'One-team'
        newoneteam = defaultdict(lambda: defaultdict(dict))
        for i in range(len(constraintsDict[constraintstr])):
            user = constraintsDict[constraintstr][i][0]
            oneteamdict[i] = str(constraintsDict[constraintstr][i]).split('(')
            for j in range(len(oneteamdict[i])):
                newoneteam[i][j] = removebrackets(oneteamdict[i][j])

        teams = defaultdict(int)
        
        for k, v in newoneteam.items():
            setSteps = []
            allUserSets = []

            testdict = defaultdict(list)
            for i in v[0]:
                testdict[i] = [item for sublist in list(v.values())[1:] for item in sublist]
            authrev(model, M, testdict)
            steps = v[0]
            allTeamSets = []
            for teamIdx in range(1, len(v)):
                team = v[teamIdx]
                teamSet = []   
                for user in team:              
                    for st in steps:
                        usersteptoadd = M[int(user[1:]) - 1][int(st[1:]) - 1]
                        if not isinstance(usersteptoadd, int):
                            teamSet.append(M[int(user[1:]) - 1][int(st[1:]) - 1])
                # x = model.NewBoolVar('x')
                c = model.NewBoolVar('c')
                boolcount += 1
                model.AddBoolOr(teamSet).OnlyEnforceIf(c)
                model.Add(sum(teamSet) < 1).OnlyEnforceIf(c.Not())
                # model.Add(x == 1).OnlyEnforceIf(c)
                # model.Add(x == 0).OnlyEnforceIf(c.Not())
                allTeamSets.append(c)
            model.Add(sum(allTeamSets) == 1)
            # f = model.NewBoolVar('f')
            # g = model.NewBoolVar('g')
            # model.Add(sum(allTeamSets) == 1).OnlyEnforceIf(f)
            # model.Add(sum(teamSet) != 1).OnlyEnforceIf(f.Not())
            # model.Add(g == 1).OnlyEnforceIf(f)
            # model.Add(g == 0).OnlyEnforceIf(f.Not())
            # model.AddDecisionStrategy([g], cp_model.CHOOSE_FIRST,
            #                   cp_model.SELECT_MAX_VALUE)
            # model.AddBoolXOr([g, 0])

            
        

        # multiple solution
        # Solve the model.
        if isinstance(vars, list):
            printOutputGlob = vars[0]
        if multiple == 1:
            solver = cp_model.CpSolver()
            solution_printer = WSPSolutionPrinter(M, inst.number_of_users, inst.number_of_steps, solver)
            solver.parameters.enumerate_all_solutions = True
            solver.Solve(model, solution_printer)

            # Statistics.
            print('\nStats')
            print(f'  Conflicts      : {solver.NumConflicts()}')
            print(f'  Branches       : {solver.NumBranches()}')
            print(f'  Wall time      : {solver.WallTime()} s')
            print(f'  Solutions found: {solution_printer.solution_count()}')
            if solution_printer.solution_count() == 0:
                print('unsat')
        else:
            solver = cp_model.CpSolver()
            # solver.parameters.search_branching = cp_model.FIXED_SEARCH
            status = solver.Solve(model)
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                if isinstance(vars, list):
                    showModelMatrix(M, inst.number_of_users, inst.number_of_steps, solver, vars[0])
                else:
                    showModelMatrix(M, inst.number_of_users, inst.number_of_steps, solver)
                print('sat')
                
                # print(f'  Solutions found: {solution_printer.solution_count()}')
            else:
                print('unsat')
            print('\nStats')
            print(f'  Conflicts      : {solver.NumConflicts()}')
            print(f'  Branches       : {solver.NumBranches()}')
            print(f'  Wall time      : {solver.WallTime()} s')

        # Creates a solver and solves the model.
        # The entire process is timed.
        # print('starting solve')
        
        # solver = cp_model.CpSolver()
        # # solver.parameters.search_branching = cp_model.FIXED_SEARCH
        # status = solver.Solve(model)
        endtime = int(currenttime() * 1000)
        
        print(f'It took  + {str(endtime - starttime)} ms to solve')
        # Checks the result of reasoning; OPTIMAL and FEASIBLE correspond to
        # 'sat' whereas anything else corresponds to 'unsat'
       
        print(f'number of variables: {boolcount}')

        return [endtime - starttime, boolcount]
        

def auth(model, M, authdidct):
        for u in range(1, len(M) + 1):
            if str(f'u{u}') not in authdidct:
                continue
            countcan = 0
            for s in range(1, len(M[0]) + 1):
                if str(f's{s}') not in authdidct[f'u{u}']:
                    model.Add(M[u-1][s-1] == 0)

        # model.Add(M[9][1] == 1)

def authrev(model, M, authdidct):
        for u in range(1, len(M) + 1):
            for s in range(1, len(M[0]) + 1):
                if f's{s}' not in authdidct.keys():
                    continue
                if str(f'u{u}') not in authdidct[f's{s}']:
                    model.Add(M[u-1][s-1] == 0)


    

def removebrackets(list1):
    return str(list1).replace('[','').replace(']','').replace('\'','').replace(',','').replace(')','').strip().split(' ')
# solver_file = sys.argv[1]
# print(solver_file)




# print(f'systemin[0] = {systemin[0]}')
# print(f'systemin[1] = {systemin[1]}')
# print(f'systemin[2] = {systemin[2]}')
# print(f'systemin = {systemin}')
if len(sys.argv) < 2:
    i1 = Instance()
    output1 = solve(i1, 101)
elif sys.argv[1] not in '12':  
    systemin = sys.argv[1]
    inst = read_file(systemin)
    i1 = Instance()
    if len(sys.argv) > 2:
        output1 = solve(i1, inst, 1)
    else:
        output1 = solve(i1, inst)
else:
    systemin = sys.argv
    print(systemin)
    typesConstraints = ['Authorisation', 'Binding', 'Separation', 'At most k', 'One team', 'Users', 'Steps']
    printType = ['Standard','Pretty']
    solutionS = ['No', 'Yes']
    # print(f'Generate Custom = {sys.argv[0]}')
    print(f'0: Print type = {sys.argv[1]}: {printType[int(sys.argv[1])-1]}')
    print(f'1: Multiple solutions = {sys.argv[2]}: {solutionS[int(sys.argv[2])]}')
    print(f'2: Authorisation Constraints = {sys.argv[3]}')
    print(f'3: Binding Constraints = {sys.argv[4]}')
    print(f'4: Separation Constraints = {sys.argv[5]}')
    print(f'5: At most k Constraints = {sys.argv[6]}')
    print(f'6: One team Constraints = {sys.argv[7]}')
    print(f'7: Users = {sys.argv[8]}')
    print(f'8: Steps = {sys.argv[9]}')
    print(f'\nVariable to change = {sys.argv[10]}: {typesConstraints[int(sys.argv[10])-1]}')
    print(f'Changed to = {sys.argv[11]}')
    # print(f'systemin = {systemin}')
    print('')
    # other = sys.argv[2:]
    # if other and other[0] == 1:
    #     print(other)
    # num_conststraints = int(sys.argv[2])
    printOutput = int(sys.argv[1])
    multipleSolutions = int(sys.argv[2])
    num_auth = int(sys.argv[3])
    num_bind = int(sys.argv[4])
    num_sep = int(sys.argv[5])
    num_atmostk = int(sys.argv[6])
    num_oneteam = int(sys.argv[7])
    # try:
    num_set_users = int(sys.argv[8])
    num_set_steps = int(sys.argv[9])
    inst = [printOutput, multipleSolutions, num_auth, num_bind, num_sep, num_atmostk, num_oneteam, num_set_users, num_set_steps]
    inst2 = [printOutput, multipleSolutions, num_auth, num_bind, num_sep, num_atmostk, num_oneteam, num_set_users, num_set_steps]
    inst2[int(sys.argv[10])] = int(sys.argv[11])
    # print(f'inst: {inst}')
    # print(f'inst2: {inst2}')
    i1 = Instance()
    print(f'running 1: {inst}')
    output1 = solve(i1, inst)
    time1 = output1[0]
    var1 = output1[1]
    print(f'\nrunning 2: {inst2}')
    i2 = Instance()
    output2 = solve(i2, inst2)
    time2 = output2[0]
    var2 = output2[1]
    percentDiffTime = (time2 - time1)/time1*100
    percentDiffVar = (var2 - var1)/var1*100
    print(f'\nTime Percentage Change (postive means worse, negative means better): {percentDiffTime}%')
    print(f'Variable Percent Change (postive means worse, negative means better): {percentDiffVar}%')
    # except Exception as e:
    #     print(e)
    #     print('No comparison added, add two more command line variables if you want to compare')
    #     inst = (num_auth, num_bind, num_sep, num_atmostk, num_oneteam, num_set_users, num_set_steps)
    #     i1 = Instance()
    #     solve(i1, inst)
    


