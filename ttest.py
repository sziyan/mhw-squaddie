test = [2,3,5,6]

for i in range(1, len(test)):
    if i not in test:
        print('Missing number is {}'.format(i))
    else:
        print(i)