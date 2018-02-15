def read_file():
    with open("categories.dot") as f:
        lines = f.readlines()
    beginning = ""
    groups = {}
    key_flag = False
    previous_key = None
    for line in lines:
        if line.startswith('}'):
            pass
        elif line.startswith('"'):
            key = line[1:line.index('"', 1)]
            if key == previous_key:
                key_flag = True
            elif key_flag:
                key = previous_key
                key_flag = False
            else:
                key_flag = True
            if key in groups:
                groups[key] += line
            else:
                groups[key] = line
            previous_key = key
        else:
            beginning += line
    for key, value in groups.iteritems():
        filename = "category_{}.dot".format(key)
        text = beginning + value + "}"
        with open(filename, 'w') as f:
            f.write(text)

read_file()


