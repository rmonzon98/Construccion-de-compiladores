class varItem():
    def __init__(self, varId, varType,  isArray, arrayLen = None, varContext = None, size = None, offset = None):
        self.varId = varId 
        self.varType = varType
        self.varContext = varContext
        self.isArray = isArray
        self.offset = offset
        self.size = size
        self.arrayLen = arrayLen

class scopeItem():
    def __init__(self, parentKey, varItems, returnType):
        self.parentKey = parentKey
        self.returnType = returnType
        self.varItems = varItems

class structItem():
    def __init__(self, structId, varItems):
        self.structId = structId
        self.varItems = varItems

