# Workflow Satisfiability Problem (WSP) Solver

This repository contains a Python implementation of a solver for the Workflow Satisfiability Problem (WSP). The solution leverages Google OR-Tools and Constraint Programming (CP) to handle various constraints efficiently.

## Features

- **Flexible Constraint Support**: Includes constraints such as:
  - Authorisation
  - Binding-of-Duty
  - Separation-of-Duty
  - At-most-k Constraints
  - One-team Constraints
- **Efficient Solver**: Built with Google OR-Tools for performance and scalability.
- **Custom Constraint Generation**: Automatically generates constraints for testing.
- **Multiple Solution Modes**: Supports enumeration of all feasible solutions or finding a single optimal solution.

---

## Installation

Ensure you have Python installed and run the following command to install the required dependency:

```bash
python -m pip install --upgrade --user ortools
python -m pip install --upgrade --user numpy
```

---

## Usage

### Command-Line Execution

Run the solver by specifying the input file or constraints directly:

1. **Using Input Files**:

   ```bash
   python workflowSatisfiabilityProblem.py instances/example1.txt
   ```

   The above reads a file containing WSP constraints and solves it.

2. **Generate Custom Constraints**:

   ```bash
   python workflowSatisfiabilityProblem.py <print_type> <multiple_solutions> <num_auth> <num_bind> <num_sep> <num_atmostk> <num_oneteam> <users> <steps>
   ```

   Parameters:
   - `<print_type>`: Output style (`1` for standard, `2` for detailed).
   - `<multiple_solutions>`: Solve for all solutions (`1`) or a single solution (`0`).
   - `<num_auth>`: Number of Authorisation constraints.
   - `<num_bind>`: Number of Binding-of-Duty constraints.
   - `<num_sep>`: Number of Separation-of-Duty constraints.
   - `<num_atmostk>`: Number of At-most-k constraints.
   - `<num_oneteam>`: Number of One-team constraints.
   - `<users>`: Number of users.
   - `<steps>`: Number of steps.

---

## Examples

1. **Solve with a File**:
   ```bash
   python workflowSatisfiabilityProblem.py instances/example1.txt
   ```

## Developer Notes

### Key Files

- **`workflowSatisfiabilityProblem.py`**: Main script for solving the WSP.
- **`problem-tester.py`**: Test the solution against all problems

### Core Dependencies

- **[Google OR-Tools](https://developers.google.com/optimization)**: Used for Constraint Programming.

---

## Performance Metrics

The solver reports:
- **Conflicts**: Number of constraint conflicts encountered.
- **Branches**: Number of branches explored.
- **Wall Time**: Total time taken to solve.
- **Solution Statistics**: Number of solutions found.

---

# License
This project is licensed under the All Rights Reserved. See the LICENSE file for details.