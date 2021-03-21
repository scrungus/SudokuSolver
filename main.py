import numpy as np
import scipy.stats as s
# Load sudokus
sudoku = np.load("data/very_easy_puzzle.npy")
print("very_easy_puzzle.npy has been loaded into the variable sudoku")
print(f"sudoku.shape: {sudoku.shape}, sudoku[0].shape: {sudoku[0].shape}, sudoku.dtype: {sudoku.dtype}")

# Load solutions for demonstration
solutions = np.load("data/very_easy_solution.npy")
print()

# Print the first 9x9 sudoku...
print("First sudoku:")
print(sudoku[0], "\n")

# ...and its solution
print("Solution of first sudoku:")
print(solutions[0])

import random
import xxhash


def findSquares(sudoku):
    sqrs = []
    sqrSize = [int(x/3) for x in sudoku.shape]
    for i in range(0,sudoku.shape[0],3):
        for j in range(0,sudoku.shape[1],3):   
            sqr = sudoku[i:i+sqrSize[0],j:j+sqrSize[1]]
            sqrs.append((sqr,[[i,i+sqrSize[0]-1],[j,j+sqrSize[1]-1]]))
    #print([x for x,_ in sqrs])
    return sqrs

def locateSquareOfPos(new_pos,sudoku):
    sqrs = findSquares(sudoku)
    for i,sqr in enumerate(sqrs):
        if new_pos[0] >= sqr[1][0][0] and new_pos[0] <= sqr[1][0][1]:
            if new_pos[1] >= sqr[1][1][0] and new_pos[1] <= sqr[1][1][1]:
                return i
    return -1

    
def isSolved(sudoku):
    if 0 in sudoku:
        return False
    for i in range(sudoku.shape[1]):
        if np.unique(sudoku[:, i]).size < sudoku.shape[1]:
            return False
        if np.unique(sudoku[i,:]).size < sudoku.shape[0]:
            return False
    for sqr in findSquares(sudoku):
        if np.unique(sqr[0]).size < sqr[0].size:
            return False
    return True
    
def findRemaining(sudoku):
    sqrs = [x[0] for x in findSquares(sudoku)]
    cols = [sudoku[:,i] for i in range(sudoku.shape[1])]
    rows = [sudoku[i,:] for i in range(sudoku.shape[0])]
    ctrs = [sqrs,cols,rows] 
    remaining_numbers=[]
    for c in ctrs:
        cons_area = []
        for a in c:
            cons_area.append(list(filter(\
            lambda x : not x in a.ravel(),list(range(1,10)))))
        remaining_numbers.append(cons_area)
    return remaining_numbers
    

def pickValAndProp(new_pos,sudoku,r,ste_Hsh):
    try:
        val = 0
        tried = set()
        x = xxhash.xxh32()
        noOfStates = len(ste_Hsh)
        i = 0
        if(new_pos == [-1,-1]):
            return (-1,-1)
        common = np.intersect1d(r[0][locateSquareOfPos([new_pos[0],new_pos[1]],sudoku)]\
                    ,np.intersect1d(r[2][new_pos[0]],r[1][new_pos[1]]))
            
        for val in common:
            sudoku[new_pos[0]][new_pos[1]] = val
            x.update(sudoku)
            ste_Hsh.add(x.digest())
            x.reset()
            if(noOfStates < len(ste_Hsh)):
                break
        if(noOfStates == len(ste_Hsh)):
            return (-1,-1)

        #remove from square
        r[0][locateSquareOfPos(new_pos,sudoku)].remove(val)
        #remove from col 
        r[1][new_pos[1]].remove(val)
        #remove from row
        r[2][new_pos[0]].remove(val)
        #print("no of states",noOfStates)       
        return (sudoku,r)
    except:
        return (-1,-1)

def findNewPos(sudoku,r):
    new_pos = [-1,-1]
    no_r = 10
    deg_h = 0
    for i in range(sudoku.shape[0]):
        for j in range(sudoku.shape[1]):
            if sudoku[i][j] == 0:
                common = np.intersect1d(r[0][locateSquareOfPos([i,j],sudoku)]\
                    ,np.intersect1d(r[2][i],r[1][j]))
                if len(common) == 0:
                    return [-1,-1]
                if len(common) < no_r:
                    no_r = len(common)

                    deg_h = len(r[0][locateSquareOfPos(new_pos,sudoku)])\
                    +len(r[1][j]) + len(r[2][i])

                    new_pos = [i,j]
                    
                elif len(common) == no_r:

                    rmng = len(r[0][locateSquareOfPos(new_pos,sudoku)])\
                    +len(r[1][j]) + len(r[2][i])

                    if rmng > deg_h:
                        deg_h = rmng
                        new_pos = [i,j]

    return new_pos

def possible(sudoku):
    for i in range(sudoku.shape[1]):
        if any(x>1 for x in np.unique(sudoku[:, i],return_counts=True)[1][1:]):
            return False
        if any(x>1 for x in np.unique(sudoku[i,:],return_counts=True)[1][1:]):
            return False
    for sqr in findSquares(sudoku):
        if any(x>1 for x in np.unique(sqr[0],return_counts=True)[1][1:]):
            return False
    return True

def sudoku_solver(sudoku):
    states = []
    ste_Hsh = set()
    x = xxhash.xxh32()
    visited = []
    novisited = 0
    states.append(sudoku)
    ste_Hsh.add(str(sudoku))
    visited.append(False)
    r = findRemaining(sudoku)
    if possible(sudoku):      
        while not all(visited):
            if isSolved(sudoku):
                    return sudoku
            if not visited[novisited]:
                sudoku, r  = pickValAndProp(findNewPos(sudoku,r),sudoku.copy(),r,ste_Hsh) 
            else:
                try:
                    visited[novisited] = True
                    novisited = len(visited) - visited[::-1].index(False) -1
                    sudoku = states[novisited]
                    r = findRemaining(sudoku)
                except:
                    break
                
            if isinstance(sudoku,int):
                visited[novisited] = True
                try:
                    novisited = len(visited) - visited[::-1].index(False) -1
                except:
                    break
                sudoku = states[novisited]
                r = findRemaining(sudoku)
                continue
            x.update(sudoku)
            ste_Hsh.add(x.digest())
            x.reset()
            if len(ste_Hsh) > len(states):
                if novisited == len(states)-1:
                    states.append(sudoku)
                    visited.append(False)
                else:
                    states[novisited+1] = sudoku
                    visited[novisited+1] = False
                novisited += 1
                
            
    return np.full((9,9),-1,dtype=int)

SKIP_TESTS = False

if not SKIP_TESTS:
    import time
    difficulties = ['very_easy', 'easy','medium',\
     'hard']
    total = 0
    totalcor = 0
    times = []
    for difficulty in difficulties:
        print(f"Testing {difficulty} sudokus")
        
        sudokus = np.load(f"data/{difficulty}_puzzle.npy")
        solutions = np.load(f"data/{difficulty}_solution.npy")
        
        count = 0
        
        for i in range(len(sudokus)):
            sudoku = sudokus[i].copy()
            print(f"This is {difficulty} sudoku number", i)
            print(sudoku)
            
            start_time = time.process_time()
            your_solution = sudoku_solver(sudoku)
            end_time = time.process_time()
            
            print(f"This is your solution for {difficulty} sudoku number", i)
            print(your_solution)
            
            print("Is your solution correct?")
            if np.array_equal(your_solution, solutions[i]):
                print("Yes! Correct solution.")
                count += 1
            else:
                print("No, the correct solution is:")
                print(solutions[i])
            
            print("This sudoku took", end_time-start_time, "seconds to solve.\n")
            times.append(end_time-start_time)
        total += len(sudokus)
        totalcor += count
        print(f"{count}/{len(sudokus)} {difficulty} sudokus correct")
        print("Average Time : ",s.trim_mean(times,0.1))
        print("Max : ", max(times) )
        print("Min : ",min(times))
        if count < len(sudokus):
            break