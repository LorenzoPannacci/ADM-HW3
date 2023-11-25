import numpy as np

def algorithm(input_string):

    # get first line of input
    input_list = input_string.split("\n")
    d, sumHours = map(int, input_list.pop(0).split(" "))

    # get other lines
    result = True
    minList = np.zeros([d], dtype = int)
    maxList = np.zeros([d], dtype = int)
    minSum = 0
    maxSum = 0
    for i in range(d):
        min, max = map(int, input_list[i].split(" "))
        
        if min > max: # impossible costraint, immediate fail
            result = False
            break

        # append values to lists
        minList[i] = min
        maxList[i] = max

        # update sums
        minSum += min
        maxSum += max

    # total costraints satistaction
    if (sumHours < minSum) or (sumHours > maxSum):
        result = False

    # creating output

    if result == False:
        print("NO")
    else:
        # we start every day as the minimum, check if there are missing hours to reach the total and
        # turn the current day from minimum to maximum if hours are missing. When we reach the point
        # when adding all the hours make us miss the target we add just what we need to reach it
        print("YES")
        outputList = minList
        outputSum = minSum
        diffs = maxList - minList
        for i in range(d):
            if outputSum + diffs[i] < sumHours: # if "far" from objective turn to max
                outputList[i] += diffs[i]
                outputSum += diffs[i]
            else:  # if "near" objective add just what is needed
                outputList[i] += sumHours - outputSum
                break
        
        print(*outputList, sep = " ")

    return