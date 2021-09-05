from antlr4 import *
from antlr4.tree.Trees import TerminalNode
from antlr4.error.Errors import *
from antlr.DecafLexer import DecafLexer
from antlr.DecafParser import DecafParser
from antlr.DecafListener import DecafListener
from stack import *

class STFiller(DecafListener):
    def __init__(self) -> None:
        self.errorsFound = []
        self.scopeDictionary = {}
        self.structDictionary = {}
        self.primitives = [
            'int', 
            'char', 
            'boolean', 
            'struct', 
            'void'
            ]
        self.mainDeclarated = False
        self.structToUse = None
        self.currentMethodName = ""
        self.currentScope = "program"
        self.previousScope = "None"
        self.scopesCounter = 1
        self.structStack = []
        self.nodeTypes = {}
        

        self.addScopeST(None)
    
    #función para moverse entre scopes, actualiza el scope anterior y guarda el scope en el que estaba dentro de la variable previousScope
    def goToScope(self, scope):
        self.previousScope = self.currentScope
        self.currentScope = scope

    #--------------------------program--------------------------
    def exitProgram(self, ctx: DecafParser.ProgramContext):
        if not self.mainDeclarated:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): metodo main no declarado")

    #--------------------------structDeclaration--------------------------
    def enterStructDeclaration(self, ctx: DecafParser.StructDeclarationContext):
        structId = ctx.getChild(1).getText()
        self.addStructST(structId)
    
    #--------------------------VarDeclaration--------------------------
    def enterVarDeclaration(self, ctx: DecafParser.VarDeclarationContext):
        isArray = False

        #verificamos si hay un literal num dentro del ctx
        if (ctx.NUM() != None):
            value = ctx.getChild(3).getText()
            isArray = True
            #si hay un num dentro del ctx quiere decir que la variable es un array, validamos que el num sea mayor a 0
            if (int(value) <= 0):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): El tamaño del array debe ser mayor a 0")
                return

        parentCtx = ctx.parentCtx
        firstChild = parentCtx.getChild(0).getText()

        varType = ctx.getChild(0).getText()
        varId = ctx.getChild(1).getText()

        flag = False

        #se intenta agregar la variable dentro de su scope
        if firstChild == "struct":
            structId = parentCtx.getChild(1).getText()
            flag = self.addVarS(structId, varType, varId, "blockVar", isArray)
        else:
            flag = self.addVarST(varType, varId, "blockVar", isArray)

        if flag:
            self.nodeTypes[ctx] = 'void'
        else:
            #En caso de que la variable se repita en el scope mandar mensaje de error
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): La variable ya ha sido declarada dentro del mismo contexto")
    
    def exitVarDeclaration(self, ctx: DecafParser.VarDeclarationContext):
        varType = ctx.getChild(0).getText()
        self.nodeTypes[ctx] = varType
    
    #--------------------------MethodDeclaration--------------------------
    def enterMethodDeclaration(self, ctx: DecafParser.MethodDeclarationContext):
        methodType = ctx.getChild(0).getText() 
        methodName = ctx.getChild(1).getText()

        self.currentMethodName = methodName
        self.goToScope(methodName) #switch

        flag = self.addScopeST(self.previousScope, methodType) #guardar

        if flag:
            #no se repite methodcall
            self.nodeTypes[ctx] = 'void'
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): El método ya ha sido declarado")

    def exitMethodDeclaration(self, ctx: DecafParser.MethodDeclarationContext):
        methodName = ctx.getChild(1).getText()
        if (methodName == 'main'):
            self.mainDeclarated = True
        self.scopesCounter = 1
        self.currentMethodName = "program"
        self.goToScope("program")

    #--------------------------Parameter--------------------------
    def enterParameter(self, ctx: DecafParser.ParameterContext):
        paramType = ctx.getChild(0).getText()

        if (len(ctx.children) > 2):
            isArray=True
        else:
            isArray = False
        
        if paramType != 'void':
            paramId = ctx.getChild(1).getText()
            flag = self.addVarST(paramType, paramId, "param", isArray)

            if flag:
                self.nodeTypes[ctx] = 'void'
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): ya existe un parametro con ese nombre")
    
    #--------------------------Location--------------------------
    def enterLocation(self, ctx: DecafParser.LocationContext):
        if (ctx.location()):
            varId = ctx.getChild(0).getText()
            if (self.structStack == []):
                structVarType = self.searchVar(varId, self.currentScope)
                structToUse = self.searchSST(structVarType.varType) #Search symbol table
                self.structStack.append(structToUse)
            else:
                structVarType = self.structStack[-1].symbolTable[varId]
                structToUse = self.searchSST(structVarType.varType) #Search symbol table
                self.structStack.append(structToUse)
    
    def exitLocation(self, ctx: DecafParser.LocationContext):
        varBeingEvaluated = None

        if (ctx.location() != None):
            if self.structStack != []:
                currentTable = self.structStack.pop()
                if (currentTable != None):
                    varBeingEvaluated = currentTable.symbolTable[ctx.getChild(0).getText()]
                    if (varBeingEvaluated != None):
                        self.nodeTypes[ctx] = self.nodeTypes[ctx.location()]
                    else:
                        self.nodeTypes[ctx] = 'error'
                        self.errorsFound.append("No existe tal propiedad dentro del struct")
                else:
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("La propiedad no es un struct")
            else:
                varBeingEvaluated = self.searchVar(ctx.getChild(0).getText(), self.currentScope)

                if (varBeingEvaluated != None):
                    self.nodeTypes[ctx] = self.nodeTypes[ctx.location()]
                else:
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): esta variable no ha sido definida anteriormente")

        elif (type(ctx.parentCtx) == DecafParser.LocationContext and ctx.location() == None):
            if self.structStack != []:
                currentTable = self.structStack.pop()
                if (currentTable != None):
                    varBeingEvaluated = currentTable.symbolTable[ctx.getChild(0).getText()]
                    if (varBeingEvaluated != None):                      
                        self.nodeTypes[ctx] = varBeingEvaluated.varType                                 
                if (currentTable == None or varBeingEvaluated == None):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): el struct no tiene esta propiedad")

        else:
            varBeingEvaluated = self.searchVar(ctx.getChild(0).getText(), self.currentScope)
            if (varBeingEvaluated != None):
                self.nodeTypes[ctx] = varBeingEvaluated.varType
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): la variable no se ha sido definida en este contexto previamente")

        if (ctx.expression()): 
            if (type(ctx.expression()) == DecafParser.Ex_minuContext):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): ya existe un parametro con ese nombre")

            if (varBeingEvaluated != None):
                if(not varBeingEvaluated.isArray):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): " + varBeingEvaluated.varId + " no es un array")
        else:
            if (varBeingEvaluated != None):
                if(varBeingEvaluated.isArray):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): " + varBeingEvaluated.varId + " necesita un indice")

    #--------------------------Block--------------------------
    def enterBlock(self, ctx: DecafParser.BlockContext):
        parentCtx = ctx.parentCtx
        firstChild = parentCtx.getChild(0).getText()
        if firstChild not in self.primitives:
            newScopeName = 'scope ' + str(self.scopesCounter)+ ' dentro de '+ self.currentMethodName 
            self.scopesCounter = self.scopesCounter + 1
            self.goToScope(newScopeName)
        if self.addScopeST(self.previousScope):
            self.nodeTypes[ctx] = 'void'
    
    def exitBlock(self, ctx: DecafParser.BlockContext):
        currentBlockObj = self.searchMethod(self.currentScope)
        self.goToScope(currentBlockObj.parentKey)

    #--------------------------Statement--------------------------
    #------if------
    def exitSt_if(self, ctx: DecafParser.St_ifContext):
        operator = ctx.getChild(2)
        typeOp = self.nodeTypes[operator]
        if(typeOp == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): el statement dentro del if debe ser una expresión booleana")
    
    
    #------while------
    def exitSt_while(self, ctx: DecafParser.St_whileContext): 
        operator = ctx.getChild(2)
        typeOp = self.nodeTypes[operator]
        if(typeOp == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): el statement dentro del while debe ser una expresión booleana")
    
    #------return------
    def exitSt_return(self, ctx: DecafParser.StatementContext):
        parentMethod = self.getMethodType(self.currentScope)
        parentType = parentMethod.returnType
        expressionOom = ctx.getChild(1)
        if (ctx.getChild(1).getText() != ""):
            if (parentType in self.primitives):
                exprType = self.nodeTypes[expressionOom.getChild(0)]
                if (exprType == parentType):
                    self.nodeTypes[ctx] = 'void'
                else:
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): el método es tipo void así que se espera que no retorne ningún valor")  
        else:
            if (parentType == 'void'):
                self.nodeTypes[ctx] = 'void'
            elif(parentType in self.primitives):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): se espera que el método retorne un valor")
    
    #------mtdc------
    def exitSt_mtdc(self, ctx: DecafParser.St_mtdcContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.methodCall()]

    #------assigment------
    def exitSt_assig(self, ctx: DecafParser.St_assigContext):
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]
        if(type1 == type2):
            self.nodeTypes[ctx] = self.nodeTypes[operator1]
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): los operandos deben ser del mismo tipo")

    #------methodcall------
    def exitMethodCall(self, ctx: DecafParser.MethodCallContext):
        methodName = ctx.getChild(0).getText()
        args = ctx.getChild(2).getText()

        methodObj = self.searchMethod(methodName)

        if (methodObj != None):
            methodCallTypes = []

            for i in range(0, len(ctx.children)):
                if i > 1 and i < len(ctx.children)-1:
                    if (ctx.getChild(i).getText() != ","):
                        methodCallTypes.append(self.nodeTypes[ctx.getChild(i)])

            paramsEquality = self.compareParameters(methodObj, methodCallTypes)

            if paramsEquality:
                self.nodeTypes[ctx] = methodObj.returnType
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): los parametros no son correctos")
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): este método no ha sido declarado")

    #--------------------------Expression--------------------------
    #------mtdc------
    def exitEx_mtdc(self, ctx: DecafParser.Ex_mtdcContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]

    #------loc------    
    def exitEx_loc(self, ctx: DecafParser.Ex_locContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]

    #------literal------
    def exitEx_lite(self, ctx: DecafParser.Ex_liteContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]    
    
    #------minus------
    def exitEx_minu(self, ctx: DecafParser.Ex_minuContext):
        operator1 = ctx.getChild(1)
        type1 = self.nodeTypes[operator1]
        if(type1 == 'int'):
            self.nodeTypes[ctx] = 'int'
        else:
            
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): la operación - espera un operando tipo int")
    
    #------not------
    def exitEx_not(self, ctx: DecafParser.Ex_notContext):
        operator1 = ctx.getChild(1)
        type1 = self.nodeTypes[operator1]
        if(type1 == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
        else:
            
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): la operación ! espera un operando tipo boolean")
    
    #------parenthesis------
    def exitEx_par(self, ctx: DecafParser.Ex_parContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.expression()]

    #------aritmetica------
    #----5----
    def exitEx_ar5(self, ctx: DecafParser.Ex_ar5Context):
        # *, /, %
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]
        if(type1 == 'int' and type2 == 'int'):
            self.nodeTypes[ctx] = 'int'
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): ambos operadores deben ser int")
    
    #----4----
    def exitEx_ar4(self, ctx: DecafParser.Ex_ar4Context):
        # +, -
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]
        if(type1 == 'int' and type2 == 'int'):
            self.nodeTypes[ctx] = 'int'
        else:    
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): ambos operadores deben ser int")

    #----3----
    def exitEx_ar3(self, ctx: DecafParser.Ex_ar3Context):
        #operaciones relacionales (<, >, <=, >=, ==, !=)
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]
        symbol = ctx.getChild(1).getText()
        if (symbol in ('<', '<=', '>','>=')):
            if(type1 == 'int' and type2 == 'int'):
                self.nodeTypes[ctx] = 'boolean'
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): ambos operadores deben ser int")
        elif (symbol == "==" or symbol == "!="):
            allowedTypes = ('int', 'char', 'boolean')
            if (type1 in allowedTypes and type2 in allowedTypes):
                if(self.nodeTypes[operator1] == self.nodeTypes[operator2]):
                    self.nodeTypes[ctx] = 'boolean'
                else:
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): se esperaba dos operadores con el mismo tipo")
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): uno de los operadores es de un tipo no permitido")

    #----2----
    def exitArith_op_second(self, ctx: DecafParser.Arith_op_secondContext):
        # &&
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]
        if(type1 == 'boolean' and type2 == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): se esperaban dos operadores booleanos")

    #----1----
    def exitArith_op_first(self, ctx: DecafParser.Arith_op_firstContext):
        # ||
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]
        if(type1 == 'boolean' and type2 == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): se esperaban dos operadores booleanos")

    #------Literales------
    #----int----
    def exitInt_literal(self, ctx: DecafParser.Int_literalContext):
        self.nodeTypes[ctx] = 'int'
    #----char----
    def exitChar_literal(self, ctx: DecafParser.Char_literalContext):
        self.nodeTypes[ctx] = 'char'
    #----bool----
    def exitBool_literal(self, ctx: DecafParser.Bool_literalContext):
        self.nodeTypes[ctx] = 'boolean'
    #----literal----
    def exitLiteral(self, ctx: DecafParser.LiteralContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]
        
    #--------------------------Métodos del symbol table--------------------------
    #----agregar nuevo scope al diccionario----

    def addNewScope(self, previousScope, methodType=None):
        self.scopeDictionary[self.currentScope] = scopeItem(
                previousScope, 
                {}, 
                methodType
                ) #parent, vars, type


    def addScopeST(self, previousScope, methodType=None):
        if self.currentScope not in self.scopeDictionary:
            self.addNewScope(previousScope, methodType)
            return True
        else:
            return False

    #----agregar nueva variable a symboltable----
    def addVarST(self, varType, varId, varContext, isArray):
        #primero conseguimos el symboltable del scope en el que estamos
        temp = self.scopeDictionary.get(self.currentScope).symbolTable
        if varId not in temp:
            #Si no encuentra la variable dentro del symbolTable
            temp[varId] = varItem(varId, varType, varContext, isArray)
            self.scopeDictionary.get(self.currentScope).symbolTable = temp
            return True
        else:
            return False

    #----busqueda de variable dentro de un scope----
    def searchVar(self, varId, scopeName):
        varEv = None
        #buscamos el symboltable del scope solicitado
        tempST = self.scopeDictionary.get(scopeName).symbolTable
        
        if varId in tempST:
            #Si lo encuentra devuelve valor
            varEv = tempST[varId]
        else:
            #Si no lo encuentra, la función se llama a sí misma para buscar dentro del scope padre
            newScope = self.scopeDictionary.get(scopeName).parentKey
            if (newScope != None):
                varEv = self.searchVar(varId, newScope)

        return varEv

    #----busqueda de método dentro de un scope----
    def searchMethod(self, methodId):
        scopeObject = self.scopeDictionary.get(methodId)
        return scopeObject

    #----get de tipo de método----
    def getMethodType(self, scope):
        scopeObject = self.scopeDictionary.get(scope)
        if (scopeObject.parentKey != "program"):
            scopeObject = self.getMethodType(scopeObject.parentKey)
        return scopeObject
        
    #----comparación de parametros----
    #esta función verifica que cuando se llama una función tenga la cantidad y tipo de parametros correctos
    def compareParameters(self, methodObj, methodCallTypes):
        symbolTable = methodObj.symbolTable
        methodDeclarationTypes = []
        for varId, varItem in symbolTable.items():
            if varItem.varContext == "param":
                methodDeclarationTypes.append(varItem.varType)
        if (methodCallTypes == methodDeclarationTypes):
            return True 
        else:
            return False
            
    #--------------------------Métodos del symbol table--------------------------
    #----agregar struct----
    def addStructST(self, structId):
        structId = "struct"+structId
        if structId not in self.structDictionary:
            self.structDictionary[structId] = structItem(structId=structId, symbolTable={})

    #funcion que verifica si una variable no esta ya dentro de un contexto
    #----agregar variable a struct----
    def addVarS(self, structId, varType, varId, varContext, isArray):
        alreadyDeclared = False
        structId = "struct" + structId
        temp = self.structDictionary.get(structId).symbolTable

        if varId not in temp:
            temp[varId] = varItem(varId, varType, varContext, isArray)
            alreadyDeclared = True
        else:
            alreadyDeclared = False

        self.structDictionary.get(structId).symbolTable = temp
        return alreadyDeclared

    #----agregar variable a struct----
    def searchSST(self, structId):
        symbolTable = None
        if structId in self.structDictionary:
            symbolTable = self.structDictionary[structId]
        return symbolTable