import numpy as np


stop_arr = np.loadtxt('stop_arr.txt')
walk_arr = np.loadtxt('walk_arr.txt')
run_arr = np.loadtxt('run_arr.txt')

right_arr = np.loadtxt('right_arr.txt')
left_arr = np.loadtxt('left_arr.txt')
fall_arr = np.loadtxt('fall_arr.txt')

array = stop_arr
print("average: ",np.average(array))
print("std: ",np.std(array))
print("max: ",np.max(array))
print()

array = walk_arr
print("average: ",np.average(array))
print("std: ",np.std(array))                                          
print("max: ",np.max(array))
print()

array = run_arr
print("average: ",np.average(array))
print("std: ",np.std(array))                                          
print("max: ",np.max(array))
print()
