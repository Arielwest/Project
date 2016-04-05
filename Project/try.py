data = raw_input("...")
to_add = len(data) % 16
print to_add
data += '\x00' * to_add
print len(data)