# import logging
# from mongoengine import *
# from mongoengine import connect
#
# db = connect('test', host="mongodb+srv://ndg:P%40ssw0rd@ndg-3djuk.gcp.mongodb.net/test?retryWrites=true&w=majority") #test
# TOKEN = '180665590:AAGEXQVVWTzpou9TBekb8oq59cjz2Fxp_gY' #Ascension
#
# class Player(Document):
#     username = StringField(max_length=200, required=False)
#     player_name = StringField(max_length=200, required=False)
#
# user = Player.objects(username="test")
# if not user:
#     print("Empty")
# else:
#     print("not none")

value = 4 % 4
print(value)