from antlr4 import *
from antlr4.tree.Trees import TerminalNode
from antlr4.error.Errors import *
from antlr.DecafLexer import DecafLexer
from antlr.DecafParser import DecafParser
from antlr.DecafListener import DecafListener
from stack import *
from quadruples import *

class STFiller(DecafListener):
    def __init__(self) -> None:
        #--------------------------Primera entrega--------------------------
        self.errorsFound = []
        self.scopeDictionary = {}
        self.structDictionary = {}
        self.validVarTypes = [
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

        #--------------------------Segunda entrega--------------------------
        self.sizeDict = {'int' : 4, 'char' : 1, 'boolean' : 1}
        self.offset = 0
        self.ifFlag = False
        self.inputInfo = {}
        self.addresses = {}
        self.quadTable = []
        self.tempCounter = 0
        self.blockCounter = 0
        self.intCode = ''

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
        ic = ''
        for quad in self.quadTable:
            if (quad.operator == "newArray"):
                ic += "\n\t" + quad.result.get('address') + "=" + str(quad.argument1.get('address')) + "*" + str(quad.argument2.get('address'))
            elif (quad.operator == '<' or quad.operator== '<=' or quad.operator == '>' or quad.operator == '>=' or quad.operator == '==' or quad.operator == '!='):
                ic += '\n\tif ' + str(quad.argument1.get('address')) + quad.operator + str(quad.argument2.get('address')) + ' goto ' + quad.result.get('lblTrue')
            elif (quad.operator == "label"):
                if (quad.argument1 != None):
                    ic += "\n" +str(quad.argument1.get('address')) + ":"
            elif (quad.operator == "labelend"):
                if (quad.argument1 != None):
                    ic += "\n" +str(quad.argument1.get('address'))
            elif (quad.operator == "labelt"):
                ic += "\n\t" +quad.argument1.get('lblTrue') + ":"
            elif (quad.operator == "labelf"):
                ic += "\n\t" +quad.argument1.get('lblFalse') + ":"
            elif (quad.operator == "labeln"):
                ic += "\n\t" +quad.argument1.get('lblNext') + ":"
            elif (quad.operator == "GOTON"):
                ic += "\n\tgoto " + str(quad.argument1.get('lblNext'))
            elif (quad.operator == "GOTOF"):
                ic += "\n\tgoto " + quad.argument1.get('lblFalse')
            elif (quad.result == None):
                ic += "\n\t" + quad.operator + " " + str(quad.argument1.get('address'))
            elif (quad.argument2 != None):
                ic += "\n\t" + str(quad.result.get('address')) + "=" + quad.argument1.get('address')  + quad.operator + quad.argument2.get('address') 
            elif (quad.argument2 == None):
                ic += "\n\t" + str(quad.result.get('address')) + "=" + quad.operator + str(quad.argument1.get('address'))
        self.intCode=ic


    #--------------------------structDeclaration--------------------------
    def enterStructDeclaration(self, ctx: DecafParser.StructDeclarationContext):
        structId = ctx.getChild(1).getText()
        structId = "struct"+structId
        if structId not in self.structDictionary:
            self.structDictionary[structId] = structItem(structId=structId, varItems={})
    
    #--------------------------VarDeclaration--------------------------
    def enterVarDeclaration(self, ctx: DecafParser.VarDeclarationContext):
        value = None
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
    
        #se intenta agregar la variable dentro de su scope
        if firstChild == "struct":
            structId = parentCtx.getChild(1).getText()
            flagAdd = self.addVarToStruct(structId, varType, varId, self.currentScope, value, isArray)
            if flagAdd:
                self.nodeTypes[ctx] = 'void'
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): no se logró agregar "+ varId +" al struct ya que ya existía")

        else:
            flagAdd = self.addVarST(varType, varId, self.currentScope, value, isArray)
            #En caso de que la variable se repita en el scope mandar mensaje de error
            if flagAdd:
                self.nodeTypes[ctx] = 'void'
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): no se logró agregar "+ varId +" al scope ya que ya existía")
        
    
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

            #------Codigo intermedio------
            labelMethod = "label_"+methodName
            newAdd = self.newInputInfo(1, AddLit = labelMethod)
            self.quadTable.append(quadrupleItem("label",newAdd, None, None))
            
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
        #------Codigo intermedio------
        labelMethod = "end label_"+methodName
        newAdd = self.newInputInfo(1, AddLit = labelMethod)
        self.quadTable.append(quadrupleItem("labelend",newAdd, None, None))

    #--------------------------Parameter--------------------------
    def enterParameter(self, ctx: DecafParser.ParameterContext):
        varType = ctx.getChild(0).getText()

        if (len(ctx.children) > 2):
            isArray=True
        else:
            isArray = False
        
        if varType != 'void':
            varId = ctx.getChild(1).getText()

            flag = self.addVarST(varType, varId, "param", None, isArray)

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
                temp = None
                if structVarType.varType in self.structDictionary:
                    temp = self.structDictionary[structVarType.varType]
                self.structStack.append(temp)
            else:
                structVarType = self.structStack[-1].varItems[varId]
                temp = None
                if structVarType.varType in self.structDictionary:
                    temp = self.structDictionary[structVarType.varType]
                self.structStack.append(temp)
    
    def exitLocation(self, ctx: DecafParser.LocationContext):
        varBeingEvaluated = None

        #------En caso de que location tenga un location como hijo entra en este bloque------
        if (ctx.location() != None):
            if self.structStack != []:
                currentStruct = self.structStack.pop()
                if (currentStruct != None):
                    varBeingEvaluated = currentStruct.varItems[ctx.getChild(0).getText()]
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
        
        #------En caso de que el ctx evaluado sea hijo de un location y no tenga un location como hijo------
        elif (type(ctx.parentCtx) == DecafParser.LocationContext and ctx.location() == None):
            if self.structStack != []:
                currentStruct = self.structStack.pop()
                if (currentStruct != None):
                    varBeingEvaluated = currentStruct.varItems[ctx.getChild(0).getText()]
                    if (varBeingEvaluated != None):                      
                        self.nodeTypes[ctx] = varBeingEvaluated.varType                                 
                if (currentStruct == None or varBeingEvaluated == None):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): el struct no tiene esta propiedad")
        
        else:
            varBeingEvaluated = self.searchVar(ctx.getChild(0).getText(), self.currentScope)
            if (varBeingEvaluated != None):
                self.nodeTypes[ctx] = varBeingEvaluated.varType
                self.addresses[ctx] = self.newInputInfo(4, addvar = varBeingEvaluated.label)
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): la variable no se ha sido definida en este contexto previamente")

        #------Validación de la parte del expression------
        if (ctx.expression()): 
            if(self.nodeTypes[ctx.expression()] != 'int'):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): se necesita un indice entero")
                return
                
            if (type(ctx.expression()) == DecafParser.Ex_minuContext):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): se necesita un indice natural")
                return

            if (varBeingEvaluated != None):
                if(not varBeingEvaluated.isArray):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): " + varBeingEvaluated.varId + " no es un array")
                    return
                
                #------Codigo intermedio------
                getTemp = self.getTemp()
                tempAdd = self.newInputInfo(1, AddLit = getTemp)
                self.addresses[ctx] = self.newInputInfo(4, addvar = varBeingEvaluated.label)
                expAdd = self.addresses[ctx.expression]
                width = str(self.sizeDict.get(varBeingEvaluated.varType))
                self.quadTable.append(quadrupleItem("newArray", expAdd, self.newInputInfo(1,AddLit= width), tempAdd))

                #self.addresses[ctx] =

        else:
            if (varBeingEvaluated != None):
                if(varBeingEvaluated.isArray):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): " + varBeingEvaluated.varId + " necesita un indice")

    #--------------------------Block--------------------------
    def enterBlock(self, ctx: DecafParser.BlockContext):
        parentCtx = ctx.parentCtx
        firstChild = parentCtx.getChild(0).getText()
        if firstChild not in self.validVarTypes:
            newScopeName = 'Scope' + str(self.scopesCounter)+ 'Inside'+ self.currentMethodName 
            self.scopesCounter = self.scopesCounter + 1
            self.goToScope(newScopeName)
        if self.addScopeST(self.previousScope):
            self.nodeTypes[ctx] = 'void'
        
        #------Codigo intermedio------

        #En caso de que el padre sea un if else
        if (type(parentCtx) == DecafParser.St_ifContext):
            exprAddr = self.addresses[parentCtx.getChild(2)]
            if (not(self.ifFlag)):
                self.quadTable.append(quadrupleItem("labelt", exprAddr, None, None))
                self.ifFlag = True
            else:
                next = self.addresses[parentCtx.getChild(4)]
                self.quadTable.append(quadrupleItem("GOTON", next, None, None))
                self.quadTable.append(quadrupleItem("labelf", exprAddr, None, None))


    
    def exitBlock(self, ctx: DecafParser.BlockContext):
        currentBlockObj = self.scopeDictionary.get(self.currentScope)
        self.goToScope(currentBlockObj.parentKey)


    #--------------------------Statement--------------------------
    #------if------
    #------Codigo intermedio------
    def enterSt_if(self, ctx: DecafParser.St_ifContext):
        #If
        trueL = "blockContext"+str(self.blockCounter)+".true"
        nextL = "blockContext"+str(self.blockCounter)+".next"
        nextA = self.newInputInfo(3, addNext= nextL)

        #Else
        lenCtx = len(ctx.children)
        if (lenCtx > 5):
            falseL = "blockContext"+str(self.blockCounter)+".false"
            expAdd = self.newInputInfo(2, addLabelTrue = trueL, addLabelFalse = falseL)
        else: 
            falseL = nextL
            expAdd = self.newInputInfo(2, addLabelTrue = trueL, addLabelFalse = falseL)

        self.addresses[ctx.getChild(2)] = expAdd
        self.addresses[ctx.getChild(4)] = nextA

    def exitSt_if(self, ctx: DecafParser.St_ifContext):
        operator = ctx.getChild(2)
        typeOp = self.nodeTypes[operator]
        if(typeOp == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
                      
            #------Codigo intermedio------
            self.quadTable.append(quadrupleItem("labeln", self.addresses[ctx.getChild(4)], None, None))
            
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
        if (ctx.getChild(1).getText() == ""):
            if (parentType == 'void'):
                self.nodeTypes[ctx] = 'void'
            elif  (parentType in self.validVarTypes):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): se esperaba que retornara un valor")  
            else: 
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): este tipo de operaciones no se permite en el lenguaje")  
        else: 
            if (parentType in self.validVarTypes):
                exprType = self.nodeTypes[ctx.getChild(1).getChild(0)]
                if (exprType == parentType):
                    self.nodeTypes[ctx] = 'void'
                else:
                    if (parentType == 'void'):
                        self.nodeTypes[ctx] = 'error'
                        self.errorsFound.append("linea (" + str(ctx.start.line) + "): no se esperaba valor de retorno")
                    else:
                        self.nodeTypes[ctx] = 'error'
                        self.errorsFound.append("linea (" + str(ctx.start.line) + "): el valor de retorno no coincide con el valor esperado")
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): este tipo de operaciones no se permite en el lenguaje")
    
    

    #------mtdc------
    def exitSt_mtdc(self, ctx: DecafParser.St_mtdcContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.methodCall()]

    #------assigment------
    def exitSt_assig(self, ctx: DecafParser.St_assigContext):
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        if(self.nodeTypes[operator1] == self.nodeTypes[operator2]):
            self.nodeTypes[ctx] = self.nodeTypes[operator1]

            #------codigo intermedio------
            #self.quadTable.append(quadrupleItem("", self.addresses[operator2], None, self.addresses[operator1]))
            
        else:
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): los operandos deben ser del mismo tipo")

    #------methodcall------
    def exitMethodCall(self, ctx: DecafParser.MethodCallContext):
        methName = ctx.getChild(0).getText()
        methInfo = self.scopeDictionary.get(methName)
        if (methInfo != None):
            methTypes = []
            for i in range(0, len(ctx.children)):
                if i > 1 and i < len(ctx.children)-1:
                    if (ctx.getChild(i).getText() != ","):
                        methTypes.append(self.nodeTypes[ctx.getChild(i)])
            paramsEquality = self.compareParameters(methInfo, methTypes)
            if paramsEquality:
                self.nodeTypes[ctx] = methInfo.returnType
            else:                
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): los parametros no son correctos")
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): este método no ha sido declarado")
    
    #----comparación de parametros----
    #esta función verifica que cuando se llama una función tenga la cantidad y tipo de parametros correctos
    def compareParameters(self, methodObj, methodCallTypes):
        symbolTable = methodObj.varItems
        methodDeclarationTypes = []
        for varId, varItem in symbolTable.items():
            if varItem.varContext == "param":
                methodDeclarationTypes.append(varItem.varType)
        if (methodCallTypes == methodDeclarationTypes):
            return True 
        else:
            return False

    def exitexpressionOom(self, ctx:DecafParser.expressionOom):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.expressionOom]

    #--------------------------Expression--------------------------
    #------mtdc------
    def exitEx_mtdc(self, ctx: DecafParser.Ex_mtdcContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]

    #------loc------    
    def exitEx_loc(self, ctx: DecafParser.Ex_locContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]
        '''
        print("1")
        print(ctx)
        print(type(ctx))
        print("2")
        print(ctx.getChild(0))
        print(type(ctx.getChild(0)))
        print("3")
        print(self.addresses)
        '''
        self.addresses[ctx] = self.addresses[ctx.getChild(0)]

    #------literal------
    def exitEx_lite(self, ctx: DecafParser.Ex_liteContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]
        self.addresses[ctx] = self.addresses[ctx.getChild(0)]
    
    #------minus------
    def exitEx_minu(self, ctx: DecafParser.Ex_minuContext):
        operator1 = ctx.getChild(1)
        type1 = self.nodeTypes[operator1]
        if(type1 == 'int'):
            self.nodeTypes[ctx] = 'int'

            #------codigo intermedio------
            getTemp = self.getTemp()
            self.addresses[ctx] = self.newInputInfo(1, AddLit = getTemp)
            self.quadTable.append(quadrupleItem("minus", self.addresses[operator1], None, self.addresses[ctx]))

        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): la operación - espera un operando tipo int")
    
    #------not------
    def exitEx_not(self, ctx: DecafParser.Ex_notContext):
        operator1 = ctx.getChild(1)
        type1 = self.nodeTypes[operator1]
        if(type1 == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
            #------codigo intermedio------
            self.addresses[operator1] = self.addresses[ctx]

        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): la operación ! espera un operando tipo boolean")
    
    #------parenthesis------
    def exitEx_par(self, ctx: DecafParser.Ex_parContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.expression()]
        #------codigo intermedio------
        self.addresses[ctx] = self.addresses[ctx]

    #------aritmetica------
    #----5----
    def exitEx_ar5(self, ctx: DecafParser.Ex_ar5Context):
        # *, /, %
        operator1 = ctx.getChild(0)
        operator = ctx.getChild(1).getText()
        operator2 = ctx.getChild(2)
        
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]  

        if(type1 == 'int' and type2 == 'int'):
            self.nodeTypes[ctx] = 'int'

            #------codigo intermedio------
            getTemp = self.getTemp()
            self.addresses[ctx] = self.newInputInfo(1, AddLit = getTemp)
            self.quadTable.append(quadrupleItem(operator, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))
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
        operator = ctx.getChild(1).getText()
        if(type1 == 'int' and type2 == 'int'):
            self.nodeTypes[ctx] = 'int'

            #------codigo intermedio------
            getTemp = self.getTemp()
            self.addresses[ctx] = self.newInputInfo(1, AddLit = getTemp)
            self.quadTable.append(quadrupleItem(operator, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))

        else:    
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): ambos operadores deben ser int")

    #----3----
    def exitEx_ar3(self, ctx: DecafParser.Ex_ar3Context):
        #operaciones relacionales (<, >, <=, >=)
        operator1 = ctx.getChild(0)
        operator2 = ctx.getChild(2)
        type1 = self.nodeTypes[operator1]
        type2 = self.nodeTypes[operator2]
        symbol = ctx.getChild(1).getText()
        if (symbol in ('<', '<=', '>','>=')):
            if(type1 == 'int' and type2 == 'int'):
                self.nodeTypes[ctx] = 'boolean'

                #------Codigo intermedio------
                self.quadTable.append(quadrupleItem(symbol, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))
                self.quadTable.append(quadrupleItem("GOTOF", self.addresses[ctx], None, None))
                                
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): ambos operadores deben ser int")
        #operaciones relacionales (==, !=)
        elif (symbol == "==" or symbol == "!="):
            allowedTypes = ('int', 'char', 'boolean')
            if (type1 in allowedTypes and type2 in allowedTypes):
                if(self.nodeTypes[operator1] == self.nodeTypes[operator2]):
                    self.nodeTypes[ctx] = 'boolean'

                    #------Codigo intermedio------
                    self.quadTable.append(quadrupleItem(symbol, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))
                    self.quadTable.append(quadrupleItem("GOTOF", self.addresses[ctx], None, None))

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
        self.addresses[ctx] = self.newInputInfo(1, AddLit = ctx.getText())
    #----char----
    def exitChar_literal(self, ctx: DecafParser.Char_literalContext):
        self.nodeTypes[ctx] = 'char'
        self.addresses[ctx] = self.newInputInfo(1, AddLit = ctx.getText())
    #----bool----
    def exitBool_literal(self, ctx: DecafParser.Bool_literalContext):
        self.nodeTypes[ctx] = 'boolean'
        self.addresses[ctx] = self.newInputInfo(1, AddLit = ctx.getText())

    #----literal----
    def exitLiteral(self, ctx: DecafParser.LiteralContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]
        self.addresses[ctx] = self.addresses[ctx.getChild(0)]

    #--------------------------Métodos del symbol table--------------------------
    #----agregar nueva variable a symboltable----
    def addVarST(self, varType, varId, varContext, value, isArray):
        if (value == None): 
            value = 1
        try:
            size = int(self.sizeDict.get(varType)*value)
        except:
            size = 0
        
        #primero conseguimos el symboltable del scope en el que estamos
        temp = self.scopeDictionary.get(self.currentScope).varItems
        if (self.currentScope == 'program'):
            code = 'G'
        else:
            code = self.currentScope.capitalize()
        labelVar = code+'['+str(self.offset - self.scopeDictionary.get(self.currentScope).offset)+']'

        if varId not in temp:
            #Si no encuentra la variable dentro del symbolTable
            temp[varId] = varItem(varId = varId, 
            varType = varType, 
            isArray = isArray,
            arrayLen= value,
            insideScope = True,
            label = labelVar,
            varContext= varContext, 
            size= size, 
            offset= self.offset - self.scopeDictionary.get(self.currentScope).offset)
            self.offset += size
            self.scopeDictionary.get(self.currentScope).varItems = temp
            return True
        else:
            return False

    #----agregar nuevo scope al diccionario----
    def addScopeST(self, previousScope, methodType=None):
        if self.currentScope not in self.scopeDictionary:
            self.scopeDictionary[self.currentScope] = scopeItem(
                previousScope, 
                {}, 
                methodType,
                offset = self.offset
                )
            return True
        else:
            return False

   #----busqueda de variable dentro de un scope----
    def searchVar(self, varId, scopeName):
        varEv = None
        #buscamos el symboltable del scope solicitado
        tempST = self.scopeDictionary.get(scopeName).varItems
        if varId in tempST:
            #Si lo encuentra devuelve valor
            varEv = tempST[varId]
        else:
            #Si no lo encuentra, la función se llama a sí misma para buscar dentro del scope padre
            newScope = self.scopeDictionary.get(scopeName).parentKey
            if (newScope != None):
                varEv = self.searchVar(varId, newScope)
        return varEv

    #----get de tipo de método----
    def getMethodType(self, scope):
        scopeObject = self.scopeDictionary.get(scope)
        if (scopeObject.parentKey != "program"):
            scopeObject = self.getMethodType(scopeObject.parentKey)
        return scopeObject
        
    

    #----addVarToStruct----
    #Agrega variable a struct
    def addVarToStruct(self, structId, varType, varId, varContext, num, isArray):
        if (num == None): 
            num = 1
        canAdd = False
        
        try:
            size = int(self.sizeDict.get(varType)*num)
        except:
            size = 0

        structId = "struct"+structId
        tempStructMembers = self.structDictionary.get(structId).varItems

        if varId not in tempStructMembers:
            tempStructMembers[varId] = varItem(varId = varId, 
            varType = varType, 
            isArray = isArray,
            insideScope = False,
            arrayLen= num,
            varContext= varContext, 
            size= size, 
            offset= self.offset - self.scopeDictionary.get(self.currentScope).offset)
            self.offset += size
            canAdd = True
        else:
            canAdd = False

        self.structDictionary.get(structId).varItems = tempStructMembers
        
        return canAdd
    
    #--------------------------Procedimientos de generación de código intermedio-------------------------- 
    #------función para obtener un temporal------
    def getTemp(self):
        if self.tempCounter == 16:
            self.tempCounter = 0
        temp = 'r'+str(self.tempCounter)
        self.tempCounter += 1
        self.lastTempUsed = temp
        return temp
    
    #------función para crear una nueva direccion con la informacion que se ingreso------
    def newInputInfo(self,  inputType, addLabelTrue = None, addLabelFalse = None, AddLit = None, addNext = None, addvar = None):
        
        #---Se guarda la dirección de un literal---
        if (inputType == 1):
            return {'address': AddLit}

        #---Se guarda labels de true y false---
        elif (inputType == 2):
            return {'lblTrue' : addLabelTrue, 'lblFalse' : addLabelFalse}
        
        #---Se guarda label Next---
        elif (inputType == 3):
            return {'lblNext' : addNext}

        #---Se guarda direccion de una variable---
        else:
            return {'address' : addvar}