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
        print("YES")
        outputList = minList
        outputSum = minSum
        diffs = maxList - minList
        for i in range(d):
            if outputSum + diffs[i] < sumHours:
                outputList[i] += diffs[i]
                outputSum += diffs[i]
            else:
                outputList[i] += sumHours - outputSum
                break
        
        print(*outputList, sep = " ")

    return