# python -m pip install --upgrade --user ortools

# from z3 import *
import re
import sys
from time import time as currenttime
from ortools.sat.python import cp_model
from collections import defaultdict
constarintsdict = defaultdict(list)

def showModelMatrix(M, u, s, solver):
    # print('Step \t\t', end='')
    # for i in range(len(M[0])):
    #     print(f'{i+1}', end=' ')
    # print('')
    outputdict = defaultdict(list)
    for y in range(0, u):
        # print(f'User {y+1}', end='\t\t')
        for x in range(0, s):
            # Note that we have to extract the value of each CSP variable
            # print(f'{str(solver.Value(M[y][x]))} ', end = '')
            set = solver.Value(M[y][x])
            if set == 1:
                outputdict[y+1].append(x+1)
                # print(f'User {y+1} S{x+1}')
                print(f'u{y+1} s{x+1}')
        # print('')
    # for k, v in outputdict.items():
    #     print(f'\nUser {k} ', end=' ')
    #     count = 0
    #     for s in v:
    #         if len(str(k)) == 1 and count == 0:
    #             print(f' ', end='')
    #             count += 1
    #         print(f'S{s}', end=' ')

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
        if match:
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
            constarintsdict[split[0]] += [split[1:]]

        
    return instance


def solve(instance):
    if __name__ == '__main__':
        # s = Solver()
        solver_file = sys.argv[0]
        # 0, 1, 11, 14, 15, 19 sat but unsat in solution

        # file = sys.argv[1]
        file = 'instances/example19.txt'
        inst = read_file(file)
        model = cp_model.CpModel()
        M = []
        stepdict = defaultdict(list)
        for u in range(1, inst.number_of_users + 1):
            row = []
            for s in range(1, inst.number_of_steps + 1):
                uS = model.NewBoolVar(f'{u}{s}')
                row.append(uS)
                stepdict[s] += [uS]
            M.append(row)
            # model.Add(sum(row) > 0)
        # print('')


        # authorisations
        authdidct = defaultdict(list)
        constraintstr = 'Authorisations'
        for i in range(len(constarintsdict[constraintstr])):
            user = str(constarintsdict[constraintstr][i][0])
            authdidct[user] = constarintsdict[constraintstr][i][1:]
        
        auth(model, M, authdidct)

        sepdict = []
        constraintstr = 'Separation-of-duty'
        for i in range(len(constarintsdict[constraintstr])):
            user = str(constarintsdict[constraintstr][i][0])
            sepdict.append((user, str(constarintsdict[constraintstr][i][1])))
        
        # print('Separation')
        # u + 1 since users and steps are 1-indexed rather than 0
        for u in range(1, len(M) + 1):           
            for sep in sepdict:
                # matrix is always 0 indexed so need u-1 and u-2
                counterpair = sep[1]
                counterpairmatrix = int(counterpair[1:]) -1
                s = int(sep[0][1:])
                # counterpair = sepdict[f's{s}']
                # counterpairmatrix = int(counterpair[1]) -1
                # print(f'If u{u} does s{s} cannot, they cannot do step {counterpairmatrix+1}')
                # print(f'If u{u} does s{counterpairmatrix+1} cannot, they cannot do step {s}')   
                # model.AddAllDifferent([M[u-1][s-1], M[u-1][counterpairmatrix]])
                # model.AddImplication(M[u-1][s-1] == 1, M[u-1][counterpairmatrix] == 0)
                # model.Add(M[u-1][counterpairmatrix] == 0).OnlyEnforceIf(M[u-1][s-1])
                model.Add(M[u-1][s-1] == 0).OnlyEnforceIf(M[u-1][counterpairmatrix])
                model.Add(M[u-1][counterpairmatrix] == 0).OnlyEnforceIf(M[u-1][s-1])
                        # print('')
        # every step needs one user
        for i in range(len(M[0])):
            model.Add(sum(stepdict[i+1]) == 1)

        # Binding of duty
        binddict = []
        constraintstr = 'Binding-of-duty'
        for i in range(len(constarintsdict[constraintstr])):
            user = str(constarintsdict[constraintstr][i][0])
            binddict.append((user, str(constarintsdict[constraintstr][i][1])))
        
        # print('Binding')
        # u + 1 since users and steps are 1-indexed rather than 0
        for u in range(1, len(M) + 1):           
            for bind in binddict:
                # matrix is always 0 indexed so need u-1 and u-2
                counterpair = bind[1]
                counterpairmatrix = int(counterpair[1:]) -1
                s = int(bind[0][1:])

                model.Add(M[u-1][s-1] == 1).OnlyEnforceIf(M[u-1][counterpairmatrix])
                model.Add(M[u-1][counterpairmatrix] == 1).OnlyEnforceIf(M[u-1][s-1])
                
        atmostkdict = []
        constraintstr = 'At-most-k'
        for i in range(len(constarintsdict[constraintstr])):
            user = constarintsdict[constraintstr][i][0]
            atmostkdict.append((user, constarintsdict[constraintstr][i][1:]))
        # model.Add(sum(stepdict[1]) < 3) 
        
        for kv in atmostkdict:
            # print('new at most k')
            setSteps = []
            # x is NUMBER of Users from the Set assigned to the steps in T
            allUserSets = []
            for u in range(1, len(M)+1):
                # print(f'\nUser {u}')
                userSet = []
                for s in kv[1]:
                    userSet.append(M[u-1][int(s[1:])-1])

                x = model.NewIntVar(0, 10, 'x')
                y = model.NewIntVar(0, 10, f'y{u}{s}')

                b = model.NewBoolVar('b')

                model.Add(sum(userSet) > 0).OnlyEnforceIf(b)
                model.Add(sum(userSet) < 1).OnlyEnforceIf(b.Not())
                model.Add(y == 1).OnlyEnforceIf(b)
                model.Add(y == 0).OnlyEnforceIf(b.Not())
                allUserSets.append(y)
            model.Add(sum(allUserSets) <= int(kv[0]))
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
        for i in range(len(constarintsdict[constraintstr])):
            user = constarintsdict[constraintstr][i][0]
            oneteamdict[i] = str(constarintsdict[constraintstr][i]).split('(')
            for j in range(len(oneteamdict[i])):
                newoneteam[i][j] = removebrackets(oneteamdict[i][j])

        teams = defaultdict(int)
        
        for k, v in newoneteam.items():
            # print('new one team')
            setSteps = []
            # x is NUMBER of Users from the Set assigned to the steps in T
            allUserSets = []
  
            testdict = defaultdict(list)
            for i in v[0]:
                testdict[i] = [item for sublist in list(v.values())[1:] for item in sublist]
            authrev(model, M, testdict)
            steps = v[0]
            allTeamSets = []
            for teamIdx in range(1, len(v)):
                team = v[teamIdx]
                # print(team)
                teamSet = []   
                for user in team:              
                    for st in steps:
                        # print(f'{st} {user}')
                        teamSet.append(M[int(user[1:]) - 1][int(st[1:]) - 1])
                x = model.NewIntVar(0, 10, 'x')
                c = model.NewBoolVar('c')
                model.Add(sum(teamSet) > 0).OnlyEnforceIf(c)
                model.Add(sum(teamSet) < 1).OnlyEnforceIf(c.Not())
                model.Add(x == 1).OnlyEnforceIf(c)
                model.Add(x == 0).OnlyEnforceIf(c.Not())
                allTeamSets.append(x)
            model.Add(sum(allTeamSets) <= 1)

            
        

        # Creates a solver and solves the model.
        # The entire process is timed.
        # print('starting solve')
        starttime = int(currenttime() * 1000)
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        endtime = int(currenttime() * 1000)
        
        print(f'It took  + {str(endtime - starttime)} ms to solve')

        # Checks the result of reasoning; OPTIMAL and FEASIBLE correspond to
        # 'sat' whereas anything else corresponds to 'unsat'
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            showModelMatrix(M, inst.number_of_users, inst.number_of_steps, solver)
            # print('sat')
        else:
            print('unsat')

def auth(model, M, authdidct):
    # u + 1 since users and steps are 1-indexed rather than 0
        for u in range(1, len(M) + 1):
            if str(f'u{u}') not in authdidct:
                continue
            # print(f'user{u} has certain steps it can do')
            # print(f'M U{u} ', end='')
            countcan = 0
            # if dict value is empty then continue
            for s in range(1, len(M[0]) + 1):
                # if authdidct[f'u{u}'] == []:
                #     if countcan == 0:
                #         # print(f'U{u} can do all', end='\n')
                #         countcan = 0
                #     countcan += 1
                #     # continue
                if str(f's{s}') not in authdidct[f'u{u}']:
                    # matrix is always 0 indexed so need u-1 and u-2
                    # print(f'M U{u} S{s} = 0')
                    model.Add(M[u-1][s-1] == 0)
                    # print(f'u{u} cannot do step {s}')
                # else:
                #     print(f' S{s} ', end='')
            # print('')
        # model.Add(M[9][1] == 1)

def authrev(model, M, authdidct):
    # u + 1 since users and steps are 1-indexed rather than 0
        for u in range(1, len(M) + 1):
            
            for s in range(1, len(M[0]) + 1):
                if f's{s}' not in authdidct.keys():
                    continue
                if str(f'u{u}') not in authdidct[f's{s}']:
                    # matrix is always 0 indexed so need u-1 and u-2
                    # print(f'M U{u} S{s} = 0')
                    model.Add(M[u-1][s-1] == 0)
                    # print(f'u{u} cannot do step {s}')
                # else:
                #     print(f' S{s} ', end='')

    

def removebrackets(list1):
    return str(list1).replace('[','').replace(']','').replace('\'','').replace(',','').replace(')','').strip().split(' ')
# solver_file = sys.argv[1]
# print(solver_file)
i1 = Instance()
solve(i1)


