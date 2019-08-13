'''
Created on Jul 3, 2019

@author: Owner
'''

def solution(numbers, k):
    numbers.sort()
    print("sorted {}\n".format(numbers))
    return numbers[k-1]

print("Start:\n")
s = solution([1,4,3,4,2,5],3)
print("return {}\n".format(s))
    