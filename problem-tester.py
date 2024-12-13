import sys
import re
from subprocess import check_output
from os import listdir
from os.path import join, exists

class SolutionValidator:
    def __init__(self, instance_path):
        self.instance_path = instance_path
        
    def validate_solution(self, is_sat, solution):
        if not solution:
            return None if not is_sat else f'{self.instance_path} is satisfiable but your solver returned "unsat"'
            
        with open(self.instance_path, 'r') as f:
            n, m, c = self._parse_header(f)
            
            if len(solution) != n:
                return f'The solution was supposed to assign users to {n} steps but it assigned users to {len(solution)} steps.'
                
            if error := self._validate_user_assignments(solution, m):
                return error
                
            if error := self._validate_constraints(f, solution, c):
                return error
                
        return None
        
    def _parse_header(self, file):
        n = int(re.match(r'#Steps:\s+(\d+)', file.readline(), re.IGNORECASE).group(1))
        m = int(re.match(r'#Users:\s+(\d+)', file.readline(), re.IGNORECASE).group(1))
        c = int(re.match(r'#Constraints:\s+(\d+)', file.readline(), re.IGNORECASE).group(1))
        return n, m, c
        
    def _validate_user_assignments(self, solution, m):
        for s, user in enumerate(solution):
            if user < 0 or user >= m:
                return f'Step s{s+1} is assigned user u{user} whereas only users u1..u{m} exist'
        return None
        
    def _validate_constraints(self, file, solution, constraint_count):
        constraint_validators = {
            'authorisations': self._validate_authorisations,
            'binding-of-duty': self._validate_binding_of_duty,
            'separation-of-duty': self._validate_separation_of_duty,
            'at-most-k': self._validate_at_most_k,
            'one-team': self._validate_one_team
        }
        
        for _ in range(constraint_count):
            line = file.readline().strip().lower()
            values = line.split()
            constraint_type = values[0]
            
            if constraint_type not in constraint_validators:
                print(f'Unknown constraint {constraint_type}')
                sys.exit(1)
                
            if error := constraint_validators[constraint_type](values, solution, line):
                return f'Broken constraint: {line}'
        return None

    def _validate_authorisations(self, values, solution, line):
        u = int(values[1][1:]) - 1
        A = {int(v[1:]) - 1 for v in values[2:]}
        return any(solution[s] == u for s in set(range(len(solution))) - A)

    def _validate_binding_of_duty(self, values, solution, line):
        s1, s2 = int(values[1][1:]) - 1, int(values[2][1:]) - 1
        return solution[s1] != solution[s2]

    def _validate_separation_of_duty(self, values, solution, line):
        s1, s2 = int(values[1][1:]) - 1, int(values[2][1:]) - 1
        return solution[s1] == solution[s2]

    def _validate_at_most_k(self, values, solution, line):
        k = int(values[1])
        T = [int(v[1:]) - 1 for v in values[2:]]
        return len(set(solution[t] for t in T)) > k

    def _validate_one_team(self, values, solution, line):
        steps = [int(step[1:]) - 1 for step in re.findall(r's\d+', line, re.IGNORECASE)]
        teams = [[int(t[1:]) - 1 for t in team[1:-1].split()] 
                for team in re.findall(r'$[u\d\s]+$', line, re.IGNORECASE)]
        
        for team in teams:
            if solution[steps[0]] in team:
                return any(solution[s] not in team for s in steps)
        return False

class SolutionParser:
    @staticmethod
    def parse_output(output):
        if re.match('unsat', output, re.IGNORECASE):
            return False
            
        solution = []
        for line in output.split('\n'):
            if step_match := re.match(r'.*(s|step )(\d+).*', line, re.IGNORECASE):
                if user_match := re.match(r'.*(u|user )(\d+).*', line, re.IGNORECASE):
                    step = int(step_match.group(2)) - 1
                    user = int(user_match.group(2)) - 1
                    
                    while step >= len(solution):
                        solution.append(-1)
                        
                    if solution[step] >= 0:
                        raise Exception(f'Step s{step+1} is assigned twice.')
                    solution[step] = user
                    
        if any(s < 0 for s in solution):
            raise Exception(f'Step s{solution.index(-1) + 1} is not assigned.')
            
        return solution

def run_solver(instance_path, solver_path):
    return check_output(['python', solver_path, instance_path], shell=True).decode("utf-8")

def test_instance(instance_name, solver_name):
    instance_path = join(sys.path[0], f'{instance_name}.txt')
    solution_path = join(sys.path[0], f'{instance_name}-solution.txt')
    
    with open(solution_path, 'r') as f:
        is_sat = not re.match(r'unsat', f.readline(), re.IGNORECASE)
    
    try:
        output = run_solver(instance_path, solver_name)
        solution = SolutionParser.parse_output(output)
        validator = SolutionValidator(instance_path)
        error = validator.validate_solution(is_sat, solution)
    except Exception as e:
        error, solution = e, None
        
    _print_results(instance_name, error, output, solution)

def _print_results(instance_name, error, output, solution):
    if error is None:
        print(f"{instance_name}: everything's correct.")
    else:
        print(f'\n{instance_name}: {error}')
        print('OUTPUT:\n------\n' + output + '------')
        if solution is not None:
            print('Interpreted as:')
            if not solution:
                print('unsat')
            else:
                for i, user in enumerate(solution):
                    print(f's{i+1}: u{user+1}')
            print()

def main():
    if len(sys.argv) not in [2, 3]:
        print_usage()
        sys.exit(1)
        
    solver_file = sys.argv[1]
    if len(sys.argv) > 2:
        test_directory(sys.argv[2], solver_file)
    else:
        for folder in listdir('.'):
            test_directory(folder, solver_file)

def test_directory(dir_path, solver_file):
    i = 0
    while exists(join(dir_path, f'{i}.txt')):
        test_instance(join(dir_path, str(i)), solver_file)
        i += 1

def print_usage():
    print('Usage:\n'
          'python coutsework-tester.py <your solver filename> [<instances folder>]\n'
          'If the second parameter is not supplied, the tool loads the instances from all the subfolders;'
          'you can delete some subfolders, such as 4-constraint-hard, to skip those tests.\n\n'
          'Example 1: To test the test-solver.py solver on all the instances, run\n'
          'python test-solver.py\n\n'
          'Example 2: To test it on 4-constraint-small instances, run\n'
          'python test-solver.py 4-constraint-small')

if __name__ == '__main__':
    main()
