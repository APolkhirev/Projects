# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
ne_counter = 0
with open('./ne_list.txt', 'r') as reader:
    line = reader.readline()
    while line != '':
        print(line, end='')
        line = reader.readline()
        ne_counter += 1
print("\n\nЗавершено. обследовано устройств:", ne_counter, "\nПрограмму можно закрыть.")
input()
