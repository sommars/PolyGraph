nautyPath = '/.../nauty25r9/dreadnaut'

#-----------------------------------------------------------------------------------------
def MakeConstIntoVar(Polys):
	for Poly in Polys:
		for Monomial in Poly:
			Monomial.insert(0,0)
			IsConstant = True
			for Term in Monomial:
				if Term != 0:
					IsConstant = False
					break
			if IsConstant:
				Monomial[0] = 1
	return Polys

#-----------------------------------------------------------------------------------------
def TableauToLists(systemString):
	systemString = systemString.split('\n')
	numVars = int(systemString.pop(0))
	system = []
	while len(systemString)>0:
		eq = []
		for i in xrange(int(systemString.pop(0))):
			mon = systemString.pop(0).split(' ')[3:]
			for i in xrange(len(mon)):
				mon[i] = int(mon[i])
			eq.append(mon)
		system.append(eq)
	return MakeConstIntoVar(system)

#-----------------------------------------------------------------------------------------
def CreateCyclicLists(n):
	system = []
	for i in xrange(n-1):
		equation = []
		for j in xrange(n):
			mon = [0 for x in xrange(n)]
			for k in xrange(i+1):
				mon[(j+k)%n]=1
			equation.append(mon)
		system.append(equation)
	mon1 = [0 for x in xrange(n)]
	mon2 = [1 for x in xrange(n)]
	system.append([mon1,mon2])
	return system

#-----------------------------------------------------------------------------------------
def Canonize(Polys):

	def NautyString(Polys, VarPart, MonPart, PolyPart, PowerPart):
	
		def PartString(Partition):
			return str(Partition).replace(',','')[1:-1]
			
		ReturnString = 'c -a -m n=' + str(len(Polys)) + ' g '
		for Poly in Polys:
			for Term in Poly:
				ReturnString += str(Term) + ' '
		
			ReturnString += ';'
		ReturnString = ReturnString[:-1] + '. f = [' + PartString(VarPart) + ' | ' 
		ReturnString += PartString(MonPart) + ' | ' + PartString(PolyPart) + ' | '
		for Part in PowerPart:
			ReturnString += PartString(Part) + ' | '
		ReturnString +=  '] x @ b'
		print ""
		print "This is the string we are giving to nauty to canonize:"
		print ReturnString 
		print ""
		return ReturnString
	
	SystemAsLists = []
	n = len(Polys[0][0])

	for n in xrange(n):
		SystemAsLists.append([])
		
	Monomials = []
	Polynomials = []
	Variables = range(n+1)
	NewNodeRef = n + 1
	TermToNode = {}
	SystemNode = NewNodeRef
	SystemAsLists.append([])
	NewNodeRef += 1
	for i in xrange(len(Polys)):
		PolyNode = NewNodeRef
		Polynomials.append(NewNodeRef)
		SystemAsLists.append([SystemNode])
		NewNodeRef += 1
		for j in xrange(len(Polys[i])):
			MonomialNode = NewNodeRef
			Monomials.append(NewNodeRef)
			SystemAsLists[PolyNode].append(MonomialNode)
			SystemAsLists.append([])
			NewNodeRef += 1
			for k in xrange(len(Polys[i][j])):
				if Polys[i][j][k] != 0:
					if (k, Polys[i][j][k]) not in TermToNode:
						TermToNode[(k, Polys[i][j][k])] = NewNodeRef
						SystemAsLists.append([])
						NewNodeRef += 1
						SystemAsLists[k].append(TermToNode[(k, Polys[i][j][k])])
					SystemAsLists[MonomialNode].append(TermToNode[(k, Polys[i][j][k])])
	print "This is the system converted into our pre-graph list format:"
	print SystemAsLists
	
	PartList = [[]]
	ExponentsToPartition = (TermToNode.keys())
	ExponentsToPartition.sort(key=lambda x: x[1])
	if len(ExponentsToPartition) > 0:
		MinValue = ExponentsToPartition[0][1]
	for Key in ExponentsToPartition:
		if Key[1] != MinValue:
			PartList.append([])
			MinValue = Key[1]
		PartList[-1].append(TermToNode[Key])
	print PartList

	return NautyString(SystemAsLists, Variables, Monomials, Polynomials, PartList)

#-----------------------------------------------------------------------------------------
def FindThirdLine(Output):
	Start = Output.find('\n')
	n = 3
	while Start >= 0 and n > 1:
		Start = Output.find('\n', Start+len('\n'))
		n -= 1
	return Start

#-----------------------------------------------------------------------------------------
def CallNauty(CanonizedLists):
	from subprocess import Popen, PIPE, STDOUT
	p = Popen([nautyPath],stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	output = p.communicate(input=CanonizedLists)[0]
	return output[FindThirdLine(output):]


import sys
try:
	if len(sys.argv) > 1:
		n = int(sys.argv[1])
		print CallNauty(Canonize(MakeConstIntoVar(CreateCyclicLists(n))))		
	else:
		int('Raise Error')
except ValueError:
	Input = sys.stdin.read()
	print CallNauty(Canonize(TableauToLists(Input)))
