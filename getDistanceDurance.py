# ограничение размерности входного списка в N=50 
# (?) сервис старается соотнести координаты с реальным адресом. Если он адреса не находит, запрос выполняется с ошибкой или выдает значение null

import re
import csv
from urllib2 import Request, urlopen

datastore = []
makeitastring = ''
apiKey = '' # ключ API openrouteservice.org

# чтение файла
with open('Input.csv') as csvfile:
	reader = csv.reader(csvfile)
	next(reader, None)
	for row in reader: 
		datastore.append(row)

# преобразование в строку
for row in datastore:
	for index in row:
		makeitastring +=''.join(map(str, index))
		makeitastring +=''.join('%7C') # разделение строки символом "|" между latitude и longitude

makeitastring = makeitastring.replace(';', '%2C') # разделение строки между координатами символом ";"
makeitastring = makeitastring[:-3] # удаление кода последнего символа ";"

# формирование тела зопроса
headers = {
  'Accept': 'text/json; charset=utf-8'
}

requeststring = 'https://api.openrouteservice.org/matrix?api_key='+ apiKey +'&profile=driving-hgv&locations='+ makeitastring +'&sources=all&destinations=all&metrics=distance%7Cduration&units=km&optimized=true'

# выполнение запроса
request = Request(requeststring, headers=headers)
body = urlopen(request).read()

# парсинг строк дистанций и времени в пути
ReRes = re.findall(r'(?<=distances\":).*\]\](?=\,\"durations)|(?<=durations\":).*\]\](?=\,\"destinations)', body)

# замена значений null для формата csv
ReRes[0] = ReRes[0].replace('null', 'nan')
ReRes[1] = ReRes[1].replace('null', 'nan')

# парсинг значений
regex = r"\d*\.\d*|(?<=\,)\d*(?=\,)|0|nan|(?<=\,)\d*(?=\])|(?<=\[)\d*(?=\,)"
Dist = re.findall(regex, ReRes[0])
Dura = re.findall(regex, ReRes[1])

# преобразование в float и объединение списков
Dist = map(float, Dist)
Dura = map(float, Dura)

zip = zip(Dist, Dura)

# запись в файл
with open('Result.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(zip)