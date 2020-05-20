import re
session = '```fix\nwosh\n```'
session_id = re.findall("```fix\W+(\w+)\W```", session)[0]
print(session_id)

