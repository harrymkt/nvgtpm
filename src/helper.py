def convert_size(size, round_place=2):
	import math
	sizeunits = ["B", "KB", "MB", "GB", "TB"]
	if size < 1:
		return f"0 {sizeunits[0]}"
	# Determine unit index using logarithm
	i = min(int(math.log(size, 1024)), len(sizeunits) - 1)
	rsize = round(size / (1024 ** i), round_place)
	return f"{rsize} {sizeunits[i]}"
