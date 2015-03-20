import cPickle

def save_obj(obj, filename ):
    with open(filename, 'wb') as f:
        cPickle.dump(obj, f, cPickle.HIGHEST_PROTOCOL)

def load_obj(filename):
    with open(filename, 'rb') as f:
        return cPickle.load(f)


def printTable(matrix):
	# The input should be a matrix with col,row. E.g. matrix[0] is the first column to print
	matrix = [[x if type(x) == type('a') else str(x) for x in col] for col in matrix]
	rows = len(matrix[0])
	cols = len(matrix)
	colSpacing = [ 3+max([len(x) for x in matrix[i]]) for i in range(cols)]
	table = ''
	for r in range(rows):
		for c in range(cols):
			table = table + matrix[c][r] + ' '*(colSpacing[c]-len(matrix[c][r]))
		table = table + '\n'
	return table
