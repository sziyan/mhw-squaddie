# from datetime import datetime
# #
# # input = '12.30pm'
# # if "." in input:
# #     new_input = datetime.strptime(input.upper(), '%I.%M%p')
# #     new_input = new_input.strftime('%I.%M%p')
# # else:
# #     new_input = datetime.strptime(input.upper(), '%I%p')
# #     new_input = new_input.strftime('%I%p')
# #
# # print(new_input.lstrip('0'))

from app import Siege
from mongoengine import *
from mongoengine import connect

# siege = Siege.objects(siege_id=2)
# print(siege.siege_id)

# siege = Siege.objects()
# siege.sort()
# for s in siege:
#     print(s.siege_id)


