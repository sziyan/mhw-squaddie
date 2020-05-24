import re
session = '```fix\nwosh\n```'
session_id = re.findall("```fix\s([\w\W]+) ```", session)
print(session_id)

