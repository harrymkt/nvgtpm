class version:
	"""A class to compare version"""
	def __init__(self, input_str: str):
		"""Initializes the class with a given version, parsing as it is necessary."""
		self._vers = []
		self._ver = ""
		self.version = input_str
	
	def _setup(self, inp: str):
		"""Parse and set up the version."""
		self._vers = [part.strip() for part in inp.split(".")]
	
	def __getitem__(self, n: int) -> str:
		return self._vers[n]
	
	def __len__(self) -> int:
		return len(self._vers)
	
	def _compare(self, other: "version") -> int:
		"""Compare against another version instance.
		Returns a positive value if the current version is greater than the other. Returns a negative value if the current is less than the other. Otherwise, returns 0."""
		
		max_len = max(len(self), len(other))
		for i in range(max_len):
			a = self[i] if i < len(self) else "0"
			b = other[i] if i < len(other) else "0"
			scale = max(len(a), len(b))
			norm_a = a.ljust(scale, "0")
			norm_b = b.ljust(scale, "0")
			if norm_a > norm_b:
				return 1
			elif norm_a < norm_b:
				return -1
		return 0
	
	def __eq__(self, other: "version") -> bool:
		return self._compare(other) == 0
	
	def __lt__(self, other: "version") -> bool:
		return self._compare(other) == -1
	
	def __gt__(self, other: "version") -> bool:
		return self._compare(other) == 1
	
	@property
	def version(self) -> str:
		return self._ver
	@version.setter
	def version(self, value: str):
		value = value.strip()
		self._ver = value
		self._setup(value)
