import globe

for path in globe.get_globe():
	print ('|'.join( "{:.16f},{:.16f},{:.16f}".format(*p) for p in path))
