# test = [1,2,3,4]
#
# test.remove(3)
# print(test)


# text = '123456789900'
# mac = ""
# for i in range(0, len(text), 2):
#     mac+='{}{}-'.format(text[i],text[i+1])
#
# mac = mac[:-1]
# print(mac)

text = '9pm'

from datetime import datetime

time = datetime.strptime(text,'%I%M%p')
print(time)