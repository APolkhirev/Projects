# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
#def print_hi(name):
#    # Use a breakpoint in the code line below to debug your script.
#    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

with open('ne_list.txt', 'r') as reader:
    # Read & print the entire file
    line = reader.readline()
    while line != '':  # The EOF char is an empty string
        print(line, end='')
        line = reader.readline()
