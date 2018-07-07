## Project: SudokuSolver
## Element: SudokuFunctions -> Contains the Constraint Satisfaction Functions for the solver
## Creator: juanvergaramunoz
## Year: 2018

from ExtraFunctions import *


# ********* WE DEFINE THE REGULAR UNITS (non-diagonal Sudokus) *********
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist_reg = row_units + column_units + square_units

# We create create the dictionaries without the diagonal units
units_reg = extract_units(unitlist_reg, boxes)
peers_reg = extract_peers(units_reg, boxes)


# ********* WE DEFINE THE DIAGONAL UNITS (Diagonal Sudokus) *********
diagonal_units = [[rows[i]+cols[i] for i in range(9)], [rows[i]+cols[8-i] for i in range(9)]]
unitlist_diag = unitlist_reg + diagonal_units

# We create the dictionaries using the diagonal units
units_diag = extract_units(unitlist_diag, boxes)
peers_diag = extract_peers(units_diag, boxes)


# ********* WE DEFINE THE REGULAR UNITS AS THE PREDEFINED SET OF UNITS *********
unitlist = unitlist_reg
units = units_reg
peers = peers_reg


def redefine_units(diagonal=True):
    """Includes the diagonal units and arranges the units and peers dictionaries
    in case we are dealing with a Diagonal Sudoku.

    DIAGONAL SUDOKUS are based on the regular Sudokus. Diagonal Sudokus mantain the
    rule that only one number 1-9 must appear in each row, column and 3x3 square.
    Additionally, Diagonal Sudokus state that each main diagonal (from top-left-corner
    to bottom-right-corner and the other way around) must also have only once each
    number from 1 to 9.

    Parameters
    ----------
    diagonal(bool)
        it indicates if the diagonal units should be added to the unitlists or not,
        depending on the Sudoku type

    CHANGES GLOBALLY
    ----------------
    unitlist
        a sequence of lists, each of them with a different unit from the Sudoku
        (i.e., the first row, the second column or the top-left 3x3 square)
    units
        a new dictionary with a key for each box (string) whose value is a list
        containing the units that the box belongs to (i.e., the "member units")
    peers
        a new dictionary with a key for each box (string) whose value is a set
        containing all boxes that are peers of the key box (boxes that are in a unit
        together with the key box)
    """
    
    global unitlist, units, peers, unitlist_reg, units_reg, peers_reg, unitlist_diag, units_diag, peers_diag
    
    if diagonal:
        # We assign the values to the global variables, so each function can access the proper values
        unitlist, units, peers = unitlist_diag, units_diag, peers_diag
    else:
        # We assign the values to the global variables, so each function can access the proper values
        unitlist, units, peers = unitlist_reg, units_reg, peers_reg


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers
    """
    
    ## We loop over each unit in the unitlist
    for unit in unitlist:
        unit_pairs = [u for u in unit if len(values[u])==2]
        ## We get the boxes that have exactly 2 values only, and THEN check if there is more than one box
        if len(unit_pairs) > 1:
            ## We make pair of boxes that have exactly the 2 same values (and ommit making pairs of the same box two times)
            twin_boxes = [(u,i) for u in unit_pairs for i in unit_pairs[unit_pairs.index(u):] if values[u] == values[i] and unit_pairs.index(u)!=unit_pairs.index(i)]
            ## We loop over the pairs of boxes founded (the pairs of boxes with 2 identical values)
            for pair in twin_boxes:
                ## We define the other boxes from the unit (different from the pair with 2 identical values)
                other_boxes = [u for u in unit if u != pair[0] and u != pair[1]]
                ## We erase those values from the other boxes
                for o_box in other_boxes:
                    values[o_box] = values[o_box].replace(values[pair[0]][0],"")
                    values[o_box] = values[o_box].replace(values[pair[0]][1],"")
    return values
    
    raise NotImplementedError


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    
    # We get the boxes that have already unique value
    boxes_one_value = [u for u in values.keys() if len(values[u]) == 1]
    for box in boxes_one_value:
        digit = values[box]
        #We get the peers for that box, and erase the number (digit) of that box as an option on its peers
        for peer_box in peers[box]:
            values[peer_box] = values[peer_box].replace(digit, "")
    return values
    
    raise NotImplementedError


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    
    # We check each unit, in order to see the values for each of them
    for unit in unitlist:
        # We check each digit
        for digit in '123456789':
            dboxes = [box for box in unit if digit in values[box]]
            if len(dboxes) == 1 and len(values[dboxes[0]])>1:
                values[dboxes[0]] = digit
    return values
    
    raise NotImplementedError


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    
    aux_values = values.copy() # Auxiliar function that will serve to detect when we have reach the end of improvement
    aux_i = True # Auxiliar value that will serve to indicate the end of the reducing algorithm
    while aux_i:
        aux_values = values.copy()
        # We apply the strategies
        values = naked_twins(values)
        values = eliminate(values)
        values = only_choice(values)
        # We check if there have been changes between the new values and the previous values of the sudoku
        differ_boxes = [b for b in values.keys() if values[b] != aux_values[b]]
        # We stop iterating whenever it stops making changes
        if len(differ_boxes)<1:
            aux_i = False
        # We return an error whenever there is a spot without values
        if len([b for b in values.keys() if len(values[b]) == 0]):
            return False
    return values
    
    raise NotImplementedError


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    
    # We start by reducing the puzzle
    values = reduce_puzzle(values)
    # We stop proceding if there is a spot with blank values
    if values is False:
        return False
    if all(len(values[b])==1 for b in values.keys()):
        return values
    
    # Know we look for one box with the fewest digits in order to start with the decision tree
    n,b = min((len(values[b]), b) for b in values.keys() if len(values[b])>1)
    for digit in values[b]:
        new_sudoku = values.copy()
        new_sudoku[b] = digit
        attempt = search(new_sudoku)
        if attempt:
            return attempt
    # We need to include a final return, for the case non of the possibilities above are possible
    return attempt
    
    raise NotImplementedError


def solve(grid, diagonal=False):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    
    redefine_units(diagonal)
    values = grid2values(grid)
    values = search(values)
    if values is False:
        print("Sorry, there is no solution for this Sudoku...") 
        print("Make sure the input has been correctly inserted!  :-)")
        print()
        values = grid2values_changed(grid)
        return values
    return values


def check_boxes(values):
    """This function serves to identify boxes in the same unit (row, column, 3x3 square and diagonal)
    with equal number

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    list
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    
    list_of_boxes=[]
    for unit in unitlist:
        d={}
        for box in unit:
            if values[box]!='_':
                if values[box] in d:
                    list_of_boxes.append([box, d[values[box]]])
                else:
                    d[values[box]]=box
    if len(list_of_boxes)==0:
        list_of_boxes='We have not found any errors!'
    return list_of_boxes


