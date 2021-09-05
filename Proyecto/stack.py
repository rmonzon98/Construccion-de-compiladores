class scopeItem():
    def __init__(self, parentKey, symbolTable, returnType):
        self.parentKey = parentKey
        self.returnType = returnType
        self.symbolTable = symbolTable

class structItem():
    def __init__(self, structId, symbolTable):
        self.structId = structId
        self.symbolTable = symbolTable

class varItem():
    def __init__(self, varId, varType, varContext, isArray):
        self.varId = varId 
        self.varType = varType
        self.varContext = varContext
        self.isArray = isArray