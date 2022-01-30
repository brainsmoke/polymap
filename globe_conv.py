import globe

for path in globe.get_globe():
    print('|'.join("%.16f,%.16f,%.16f" % p for p in path))
