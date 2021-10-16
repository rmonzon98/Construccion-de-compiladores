class varItem():

    def __init__(self, varId, varType,  isArray, insideScope, arrayLen = None, varContext = None, size = None, offset = None, label = None):
        self.varId = varId 
        self.varType = varType
        self.varContext = varContext
        self.isArray = isArray
        self.offset = offset
        self.size = size
        self.arrayLen = arrayLen
        self.addres = None
        self.insideScope = insideScope
        self.label = label
        

class scopeItem():
    def __init__(self, parentKey, varItems, returnType, offset = 0, code = "Ninguno"):
        self.parentKey = parentKey
        self.returnType = returnType
        self.varItems = varItems
        self.offset = offset
        self.code = code

class structItem():
    def __init__(self, structId, varItems,offset = 0,size=0):
        self.structId = structId
        self.varItems = varItems
        self.offset = offset
        self.size = offset  

