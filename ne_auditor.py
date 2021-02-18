# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
ne_counter = 0
with open('./ne_list.txt', 'r') as reader:
    line = reader.readline()
    while line != '':
        ne_counter += 1
        print('NE', ne_counter, ':', line, end='')
        line = reader.readline()
print("\n\nЗавершено. Обследовано устройств:", ne_counter)
input()
