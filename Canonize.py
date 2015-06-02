nautyPath = '/.../nauty25r9/dreadnaut'

#-------------------------------------------------------------------------------
def TableauToLists(SystemString):
    """
    Converts the tableau format for a polynomial system into a list of lists,
    where a system is a list of lists of lists, where each list is the support
    of a monomial, and each list of lists is a polynomial.
    """
    SystemString = SystemString.split('\n')
    NumberOfVars = int(SystemString.pop(0)) 
    System = []
    while len(SystemString)>0:
        Equation = []
        for i in xrange(int(SystemString.pop(0))):
            Monomial = SystemString.pop(0).split(' ')[3:]
            for i in xrange(len(Monomial)):
                Monomial[i] = int(Monomial[i])
            Equation.append(Monomial)
        System.append(Equation)
    return MakeConstIntoVar(System)

#-------------------------------------------------------------------------------
def MakeConstIntoVar(Polys):
    """
    This is a helper function to add the constant term into each monomial list.
    Converting this makes the parsing easier later on.
    """
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

#-------------------------------------------------------------------------------
def CreateCyclicLists(n):
    """
    Create lists of lists of lists in the desired format that represent the
    cyclic n root polynomial system for the given n.
    """
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

#-------------------------------------------------------------------------------
def CreateNautyString(Polys):
    """
    This function takes in the polynomials in the list of lists of lists format
    and converts them into a string that Nauty can read.
    """
    def NautyString(Polys, RootPart, VarPart, MonPart, PolyPart, PowerPart):
    
        def PartString(Partition):
            return str(Partition).replace(',','')[1:-1]
            
        ReturnString = 'c -a -m n=' + str(len(Polys)) + ' g '
        for Poly in Polys:
            for Term in Poly:
                ReturnString += str(Term) + ' '
        
            ReturnString += ';'
        ReturnString = ReturnString[:-1] + '. f = [ 0 | ' + str(RootPart) + ' | ' 
        ReturnString += PartString(VarPart) + ' | ' + PartString(MonPart) 
        ReturnString += ' | ' + PartString(PolyPart) + ' | '
        for Part in PowerPart:
            ReturnString += PartString(Part) + ' | '
        ReturnString +=  '] x @ b'
        #print ""
        #print "This is the string we are giving to nauty to canonize:"
        #print ReturnString 
        #print ""
        return ReturnString
    
    SystemAsLists = []
    n = len(Polys[0][0])

    for i in xrange(n):
        SystemAsLists.append([])
        
    Monomials = []
    Polynomials = []
    Variables = range(n)
    Variables.remove(0)
    NewNodeRef = n
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
    #print "This is the system converted into our pre-graph list format:"
    #print SystemAsLists
    
    PartList = [[]]
    ExponentsToPartition = (TermToNode.keys())
    ExponentsToPartition.sort(key=lambda x: x[1])
    CurrentPower = ExponentsToPartition[0][1]
    global PowerString
    PowerString = str(CurrentPower) + ' '
    for i in xrange(len(ExponentsToPartition)):
        PossiblyNewPower = ExponentsToPartition[i][1]
        if CurrentPower != PossiblyNewPower:
            CurrentPower = PossiblyNewPower
            PowerString += str(CurrentPower) + ' '
    if len(ExponentsToPartition) > 0:
        MinValue = ExponentsToPartition[0][1]
    for Key in ExponentsToPartition:
        if Key[1] != MinValue:
            PartList.append([])
            MinValue = Key[1]
        PartList[-1].append(TermToNode[Key])
    #print PartList
    #print PowerString
    return NautyString(SystemAsLists, SystemNode, Variables, Monomials, Polynomials, PartList)

#-------------------------------------------------------------------------------
def GetUniqueString(CanonizedLists):
    """
    This function takes a polynomial in the desired format, and then it performs
    the nauty call and parses the output to create the unique string.
    """
    from subprocess import Popen, PIPE, STDOUT
    p = Popen([nautyPath], stdout = PIPE, stdin = PIPE, stderr = STDOUT)
    Output = p.communicate(input = CanonizedLists)[0]
    return Output[Output.find(':') - 4:] + PowerString


import sys
try:
    assert len(sys.argv) > 1
    n = int(sys.argv[1])
    print GetUniqueString(CreateNautyString(MakeConstIntoVar(CreateCyclicLists(n))))
except AssertionError:
    Input = sys.stdin.read()
    print GetUniqueString(CreateNautyString(TableauToLists(Input)))
