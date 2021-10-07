class varItem():
    def __init__(self, varId, varType, varContext, isArray):
        self.varId = varId 
        self.varType = varType
        self.varContext = varContext
        self.isArray = isArray

class scopeItem():
    def __init__(self, parentKey, varItems, returnType):
        self.parentKey = parentKey
        self.returnType = returnType
        self.varItems = varItems

class structItem():
    def __init__(self, structId, varItems):
        self.structId = structId
        self.varItems = varItems

