import re

input_string = "Let's cut this date 10/10/2011 from string"
#result = re.sub('([0-2]\d|3[01])\/(0\d|1[012])\/(\d{4})', '', s)


date_pattern= '\\d{1,2}/\d\d/\d\d{2,4}' #11/22/3333


input_words = re.split(r' ', input_string)
date = re.search(date_pattern, input_string)

match_date = re.search(date_pattern, input_string)
input_string = re.sub(date_pattern, '', input_string)
print(match_date[0] if match_date else 'Not found')


