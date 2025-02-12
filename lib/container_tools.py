from collections.abc import Sequence

def is_sequence(obj):
	"""
	Check if the object is a sequence but not a string, bytes, or bytearray.

	Args:
	obj (object): The object to be checked.

	Returns:
	bool: True if the object is a sequence but not a string, bytes, or bytearray. False otherwise.
	"""
	return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray))

def as_list(x):
	"""
	Return the parameter as a list. If it was one before, return a clone.
	:param x: None, a list or a value
	:return: a new list - None results in an empty list.
	"""
	if x is None:
		return []
	if is_sequence(x):
		return list(x)          # create a new list
	return [x]
