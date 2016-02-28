for i in xrange(300, 312):
    num = str(i)
    num = "".join([str(j - j) for j in xrange(3 - len(num))]) + num
    print int(num)