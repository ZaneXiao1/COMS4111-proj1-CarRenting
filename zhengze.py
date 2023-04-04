import re

s = "3415123"

print(re.search("[A-Z]", s) != None and re.search("[0-9]", s) != None)
print(re.search("[0-9]", "df12") != None)
