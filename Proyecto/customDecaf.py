from typing import Dict, Sized
from antlr4 import *
import antlr4
from antlr4.atn.LexerATNSimulator import SimState
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
        self.offsetByScope = {}
        self.tempCounter = 0
        self.blockCounter = 0
        self.whileCounter = 0
        self.intCode = ''
        self.currentCode = ""

        self.addScopeST(None)
    
    #función para moverse entre scopes, actualiza el scope anterior y guarda el scope en el que estaba dentro de la variable previousScope
    def goToScope(self, scope):
        self.previousScope = self.currentScope
        self.currentScope = scope
        if ( "Inside" in self.currentScope):
            pass
        else:
            self.currentCode = self.currentScope

    #--------------------------program--------------------------
    def exitProgram(self, ctx: DecafParser.ProgramContext):
        if not self.mainDeclarated:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): metodo main no declarado")

        #------Se traducen todos los quaditems dentro de la tabla------
        ic = ''
        #---Se recorre toda la tabla---
        for quad in self.quadTable:
            #If y whiles
            if (quad.operator in ['<', '<=', '>', '>=', '==', '!=']):
                ic += '\n\tif ' + str(quad.argument1.get('address')) + quad.operator + str(quad.argument2.get('address')) + ' goto ' + quad.result.get('lblTrue')
            
            #Impresion de etiqueta de Inicio de metodo o bloque
            elif (quad.operator == "label"):
                if (quad.argument1 != None):
                    ic += "\n" +str(quad.argument1.get('address')) + ":"
            
            #Etiqueta para fin de metodo
            elif (quad.operator == "labelEndMeth"):
                if (quad.argument1 != None):
                    ic += "\n" +str(quad.argument1.get('address'))
            
            #Impresion de return y su valor que retorna
            elif (quad.operator == "return"):
                argument1 = quad.argument1.get('address')
                while (type(argument1) == dict):
                    argument1 = argument1.get('address')
                if (quad.argument1 != None):
                    ic += "\n\treturn " + argument1 +" "
            
            #Impresion de etiqueta de verdadero
            elif (quad.operator == "labelTrue"):
                ic += "\n\t" +quad.argument1.get('lblTrue') + ":"
            
            #Impresion de etiqueta de falso
            elif (quad.operator == "labelFalse"):
                ic += "\n\t" +quad.argument1.get('lblFalse') + ":"

            #Impresion de etiqueta de siguiente bloque
            elif (quad.operator == "labelNext"):
                ic += "\n\t" + str(quad.argument1.get('lblNext')) + ":"

            #Impresion de etiqueta para ir a siguiente etiqueta
            elif (quad.operator == "goToNext"):
                ic += "\n\tgoto " + str(quad.argument1.get('lblNext'))

            #Asignaciones (sin operaciones dentro)
            elif (quad.operator == "="):
                argument1 = quad.argument1.get('address')
                result = quad.result.get('address')
                while (type(argument1) == dict):
                    argument1 = argument1.get('address')
                while (type(result) == dict):
                    result = result.get('address')
                ic += "\n\t" + argument1 + " " + quad.operator + " " + result

            #Impresión de etiqueta de false
            elif (quad.operator == "goToFalse"):
                ic += "\n\tgoto " + quad.argument1.get('lblFalse')
            
            #Cuando no tiene operador es porque solo deseo poner la etiqueta del address (p.e. methodcall)
            elif (quad.operator == ""):
                ic += "\n\t" + str(quad.argument1.get('address'))

            #Cuando se desea imprimir una variable de algún scope
            elif (quad.result == None):
                argument1 = quad.argument1.get('address')
                while type(argument1) == dict:
                    argument1 = argument1.get('address')
                ic += "\n\t" + quad.operator + " " + str(argument1)

            #Asignaciones (con operaciones dentro)
            elif (quad.argument2 != None):
                argument1 = quad.argument1.get('address')
                argument2 = quad.argument2.get('address')
                result = quad.result.get('address')
                while (type(argument1) == dict):
                    argument1 = argument1.get('address')
                while (type(argument2) == dict):
                    argument2 = argument2.get('address')
                while (type(result) == dict):
                    result = result.get('address')
                ic += "\n\t" + str(result) + "=" + str(argument1)  + quad.operator + str(argument2)

            #Este no afecta realmente (pruebas)
            elif (quad.argument2 == None):
                ic += "\n\t" + str(quad.result.get('address')) + "=" + quad.operator + str(quad.argument1.get('address'))
        
        self.intCode=ic


    #--------------------------structDeclaration--------------------------
    def enterStructDeclaration(self, ctx: DecafParser.StructDeclarationContext):
        structId = ctx.getChild(1).getText()
        structId = "struct"+structId
        if structId not in self.structDictionary:
            self.structDictionary[structId] = structItem(structId=structId, varItems={}, offset = self.offset)
            self.currentCode = structId
    
    def exitStructDeclaration(self, ctx: DecafParser.StructDeclarationContext):
        structId = ctx.getChild(1).getText()
        struct = self.structDictionary.get("struct"+structId)
        struct.size = self.offset - struct.size 
        self.structDictionary[struct.structId] = struct

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
        self.quadTable.append(quadrupleItem("labelEndMeth",newAdd, None, None))
    
    #--------------------------Parameter--------------------------
    def exitExpressionOom(self, ctx: DecafParser.ExpressionOomContext):
        self.addresses[ctx] = ctx

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
                        if (ctx.expression):
                            expAdd = self.addresses[ctx.expression]
                            try:
                                offsetVar = self.addresses[ctx.expression].get("address")
                            except:
                                offsetVar = self.addresses[ctx.expression]
                            firstArg = varBeingEvaluated.label 
                            self.addresses[ctx] = self.newInputInfo(4,addVarLabel=firstArg, addVarOffset=offsetVar)
                        if (ctx.location()):
                            self.nodeTypes[ctx] = self.nodeTypes[ctx.location()]
                            temp1 = self.getTemp()
                            tempAdd = self.newInputInfo(1, AddLit=temp1)
                            firstArgAdd = self.newInputInfo(1, AddLit=currentStruct.size)
                            secondArgAdd = self.newInputInfo(1, AddLit=0)
                            self.quadTable.append(quadrupleItem("+", firstArgAdd, secondArgAdd, tempAdd))
                            temp2 = self.getTemp()
                            temp2Add = self.newInputInfo(1, AddLit=temp2)
                            self.quadTable.append(quadrupleItem("+", secondArgAdd, tempAdd, temp2Add))
                            self.addresses[ctx] = self.newInputInfo(1, AddLit=temp2Add)
                            print(ctx.getText())
                            print("caso 1 "+str(self.addresses[ctx]))
                            print()
                    else:
                        self.nodeTypes[ctx] = 'error'
                        self.errorsFound.append("No existe tal propiedad dentro del struct")
                else:
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("La propiedad no es un struct")
            else:
                varBeingEvaluated = self.searchVar(ctx.getChild(0).getText(), self.currentScope)

                if (varBeingEvaluated != None):
                    if (ctx.expression):
                        try:
                            expAdd = self.addresses[ctx.getChild(2)]
                            try:
                                offsetVar = self.addresses[ctx.expression].get("address")
                                
                            except:
                                offsetVar = self.addresses[ctx.getChild(2)]
                            firstArg = varBeingEvaluated.label 
                            self.addresses[ctx] = self.newInputInfo(4,addVarLabel=firstArg, addVarOffset=offsetVar)
                        except:
                            self.addresses[ctx] = self.newInputInfo(4, addVarLabel= varBeingEvaluated.label, addVarOffset= varBeingEvaluated.offset)
                    else:
                        self.nodeTypes[ctx] = self.nodeTypes[ctx.location()]
                        childAdd = self.addresses[ctx.getChild(2)].get('address')
                        while type(childAdd) == dict:
                            childAdd = childAdd.get('address')
                        self.addresses[ctx] = self.newInputInfo(4, addVarLabel= varBeingEvaluated.label, addVarOffset= childAdd)
                    print(ctx.getText())
                    print("caso 2 "+str(self.addresses[ctx]))
                    print()
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
                        if (ctx.expression):
                            try:
                                expAdd = self.addresses[ctx.getChild(2)]
                                try:
                                    offsetVar = self.addresses[ctx.expression].get("address")
                                    
                                except:
                                    offsetVar = self.addresses[ctx.getChild(2)]
                                firstArg = varBeingEvaluated.label 
                                self.addresses[ctx] = self.newInputInfo(4,addVarLabel=firstArg, addVarOffset=offsetVar)
                            except:
                                self.addresses[ctx] = self.newInputInfo(4, addVarLabel= varBeingEvaluated.label, addVarOffset= varBeingEvaluated.offset)
                        else:                      
                            self.nodeTypes[ctx] = varBeingEvaluated.varType 
                            tempRest = self.getTemp()
                            firstArg = self.newInputInfo(1, AddLit= 0) 
                            tempAdd = self.newInputInfo(1, AddLit= tempRest) 
                            secondArg = self.newInputInfo(1, AddLit= varBeingEvaluated.offset)
                            self.addresses[ctx] = tempAdd
                            grandGrandParent = ctx.parentCtx.parentCtx
                            if (type(grandGrandParent) == DecafParser.St_assigContext) or (type(grandGrandParent) == DecafParser.Ex_locContext) :
                                self.quadTable.append(quadrupleItem("+", firstArg, secondArg, tempAdd))
                            else:
                                pass                            
                        print(ctx.getText())
                        #print(type(grandGrandParent))
                        #print(type(grandGrandParent) == DecafParser.St_assigContext)
                        print("caso 3 "+str(self.addresses[ctx]))
                        print()
                if (currentStruct == None or varBeingEvaluated == None):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): el struct no tiene esta propiedad")
        
        else:
            varBeingEvaluated = self.searchVar(ctx.getChild(0).getText(), self.currentScope)
            if (varBeingEvaluated != None):
                self.nodeTypes[ctx] = varBeingEvaluated.varType
                if (ctx.expression):
                    try:
                        expAdd = self.addresses[ctx.getChild(2)]
                        try:
                            offsetVar = self.addresses[ctx.expression].get("address")
                            
                        except:
                            offsetVar = self.addresses[ctx.getChild(2)]
                        firstArg = varBeingEvaluated.label 
                        self.addresses[ctx] = self.newInputInfo(4,addVarLabel=firstArg, addVarOffset=offsetVar)
                    except:
                        self.addresses[ctx] = self.newInputInfo(4, addVarLabel= varBeingEvaluated.label, addVarOffset= varBeingEvaluated.offset)
                else:
                    self.addresses[ctx] = self.newInputInfo(4, addVarLabel= varBeingEvaluated.label, addVarOffset= varBeingEvaluated.offset)
                #YA FUNCIONA CON VARIABLES QUE MULTIPLICA EN RETURN PERO AÚN SE PUEDE MEJORAR EL MANEJO DE ARRAYS
                print(ctx.getText())
                print("caso 4 "+str(self.addresses[ctx]))
                print()
                
            else:
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): la variable no se ha sido definida en este contexto previamente")

        #------Validación de la parte del expression------
        if (ctx.expression()):
            if (ctx.expression):
                expAdd = self.addresses[ctx.getChild(2)]
                try:
                    offsetVar = self.addresses[ctx.expression].get("address")
                except:
                    offsetVar = self.addresses[ctx.getChild(2)]
                firstArg = varBeingEvaluated.label 
                self.addresses[ctx] = self.newInputInfo(4,addVarLabel=firstArg, addVarOffset=offsetVar)
            else:
                print(ctx.getText())
                print("caso 5 "+str(self.addresses[ctx]))
                print()
            if(self.nodeTypes[ctx.expression()] != 'int'):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): se necesita un indice entero")
                return
            elif (type(ctx.expression()) == DecafParser.Ex_minuContext):
                self.nodeTypes[ctx] = 'error'
                self.errorsFound.append("linea (" + str(ctx.start.line) + "): se necesita un indice natural")
                return
            elif (varBeingEvaluated != None):
                if(not varBeingEvaluated.isArray):
                    self.nodeTypes[ctx] = 'error'
                    self.errorsFound.append("linea (" + str(ctx.start.line) + "): " + varBeingEvaluated.varId + " no es un array")
                    return
                    
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
                self.quadTable.append(quadrupleItem("labelTrue", exprAddr, None, None))
                self.ifFlag = True
            else:
                next = self.addresses[parentCtx.getChild(4)]
                self.quadTable.append(quadrupleItem("goToNext", next, None, None))
                self.quadTable.append(quadrupleItem("labelFalse", exprAddr, None, None))

        #En caso de que el padre sea un while
        if (type(parentCtx) == DecafParser.St_whileContext):
            exprAddr = self.addresses[parentCtx.getChild(2)]
            self.quadTable.append(quadrupleItem("labelTrue", exprAddr, None, None))

    
    def exitBlock(self, ctx: DecafParser.BlockContext):
        currentBlockObj = self.scopeDictionary.get(self.currentScope)
        self.goToScope(currentBlockObj.parentKey)


    #--------------------------Statement--------------------------
    #------if------
    #------Codigo intermedio------
    def enterSt_if(self, ctx: DecafParser.St_ifContext):
        #If
        self.blockCounter += 1
        self.ifFlag = False
        trueL = "block"+str(self.blockCounter)+"T"
        nextL = "block"+str(self.blockCounter)+"N"
        nextA = self.newInputInfo(3, addNext= nextL)

        #Else
        lenCtx = len(ctx.children)
        if (lenCtx > 5):
            falseL = "block"+str(self.blockCounter)+"F"
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
            self.quadTable.append(quadrupleItem("labelNext", self.addresses[ctx.getChild(4)], None, None))
            
        else:
            self.nodeTypes[ctx] = 'error'
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): el statement dentro del if debe ser una expresión booleana")
    
    
    #------while------
    def enterSt_while(self, ctx: DecafParser.St_whileContext):
        self.addresses[ctx.getChild(2)] = self.newInputInfo(2, addLabelTrue="blockWhile" + str(self.whileCounter) + "T", addLabelFalse="blockWhile" + str(self.whileCounter) + "N")
        self.addresses[ctx.getChild(4)] = self.newInputInfo(3, addNext = "while" + str(self.whileCounter))
        self.quadTable.append(quadrupleItem("labelNext", self.addresses[ctx.getChild(4)], None, None))


    def exitSt_while(self, ctx: DecafParser.St_whileContext): 
        operator = ctx.getChild(2)
        typeOp = self.nodeTypes[operator]
        if(typeOp == 'boolean'):
            self.nodeTypes[ctx] = 'boolean'
            #------Codigo intermedio------
            self.addresses[ctx.getChild(2)] = self.newInputInfo(2, addLabelTrue="blockWhile" + str(self.whileCounter) + "T", addLabelFalse="blockWhile" + str(self.whileCounter) + "N")
            self.exitEx_ar3(ctx.getChild(2))
            self.quadTable.append(quadrupleItem("labelNext", {'lblNext' : "blockWhile" + str(self.whileCounter) + "N"}, None, None))
            self.whileCounter += 1
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
                    try:
                        child = ctx.getChild(1)
                        grandChild = child.getChild(0)
                        newAdd = self.newInputInfo(1, AddLit = self.addresses[grandChild])
                        self.quadTable.append(quadrupleItem("return",newAdd, None, None))
                    except:
                        newAdd = self.newInputInfo(1, AddLit = self.addresses[ctx.getChild(1)])
                        self.quadTable.append(quadrupleItem("return",newAdd, None, None))
                    
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
            try:
                #print(self.addresses[operator1])
                #print(self.addresses[operator2])
                #print(self.nodeTypes[ctx.getChild(0)])
                #print(ctx.getChild(0).getText()+" "+ctx.getChild(1).getText()+" "+ctx.getChild(2).getText())
                self.quadTable.append(quadrupleItem("=", self.addresses[operator1], None, self.addresses[operator2]))
            except:
                #print(self.addresses[operator1])
                #print(self.addresses[operator2])
                pass
            
            
        else:
            self.errorsFound.append("linea (" + str(ctx.start.line) + "): los operandos deben ser del mismo tipo")

    #------methodcall------
    #def enterMethodCall(self, ctx: DecafParser.MethodCallContext):


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

                #------codigo intermedio------
                #---se establecen los parametros---
                lenChildren = len(ctx.children)
                for child in range(0,lenChildren):
                    if ((child > 1) and (child < lenChildren-1) and ctx.getChild(child) != ","):
                        try:
                            self.quadTable.append(quadrupleItem("param", self.addresses[ctx.getChild(child)], None, None))
                        except:
                            pass
                
                #---se llama a la función---
                parent = ctx.parentCtx
                grandParent = parent.parentCtx
                if(type(grandParent)  != DecafParser.St_returnContext):
                    labelMeth = "Call "+methName
                    methAdd = self.newInputInfo(5,addvar=labelMeth)
                    self.quadTable.append(quadrupleItem("", methAdd, None, None))
                    self.addresses[ctx] = self.newInputInfo(1, AddLit= methAdd)
                else:
                    labelMeth = "Call "+methName
                    methAdd = self.newInputInfo(5,addvar=labelMeth)
                    self.addresses[ctx] = self.newInputInfo(1, AddLit= methAdd)
                

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
        self.addresses[ctx] = self.addresses[ctx.getChild(0)]

    #--------------------------Expression--------------------------
    #------mtdc------
    def exitEx_mtdc(self, ctx: DecafParser.Ex_mtdcContext):
        self.nodeTypes[ctx] = self.nodeTypes[ctx.getChild(0)]
        try:
            self.addresses[ctx] = self.addresses[ctx.getChild(0)]
        except:
            pass

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
        try:
            self.addresses[ctx] = self.addresses[ctx.getChild(0)]
        except:
            pass

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
        try:
            self.addresses[ctx] = self.addresses[ctx.expression()]
        except:
            #print('error con parentesis')
            pass

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
            try:
                self.quadTable.append(quadrupleItem(operator, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))
            except:
                pass

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
            try:
                self.quadTable.append(quadrupleItem(operator, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))
            except:
                pass

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
                try:
                    self.quadTable.append(quadrupleItem(symbol, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))
                    self.quadTable.append(quadrupleItem("goToFalse", self.addresses[ctx], None, None))
                except:
                    pass
                                
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
                    try:
                        self.quadTable.append(quadrupleItem(symbol, self.addresses[operator1], self.addresses[operator2], self.addresses[ctx]))
                        self.quadTable.append(quadrupleItem("goToFalse", self.addresses[ctx], None, None))
                    except:
                        pass

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
        if varType in self.validVarTypes:
            try:
                size = int(int(self.sizeDict.get(varType))*int(value))
            except:
                size = 0
        elif varType in self.structDictionary:
            try:
                size = self.structDictionary.get(varType).size*int(value)
            except:
                size = 0
        
        #primero conseguimos el symboltable del scope en el que estamos
        temp = self.scopeDictionary.get(self.currentScope).varItems
        if (self.currentScope == 'program'):
            code = 'program'
        else:
            code = self.currentScope.upper()
            while ("INSIDE" in code):
                index = code.find("INSIDE")
                code = code[index+6:]
        try:
            labelVar = code
        except:
            labelVar = code

        try:
            currentoffset = self.offset - self.scopeDictionary.get(labelVar.capitalize()).offset
        except:
            currentoffset = self.offset - self.scopeDictionary.get(self.currentScope).offset

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
            offset= currentoffset)
            self.offset += size
            self.scopeDictionary.get(self.currentScope).varItems = temp
            return True
        else:
            return False

    #----agregar nuevo scope al diccionario----
    def addScopeST(self, previousScope, methodType=None):
        if self.currentScope not in self.scopeDictionary:
            if(self.currentScope == "program"):
                self.currentCode = "Program"
                self.scopeDictionary[self.currentScope] = scopeItem(
                    previousScope, 
                    {}, 
                    methodType,
                    offset = self.offset,
                    code = self.currentCode
                    )
                
            else:
                if (not "Inside" in previousScope):
                    self.currentCode = previousScope
                self.scopeDictionary[self.currentScope] = scopeItem(
                    previousScope, 
                    {}, 
                    methodType,
                    offset = self.offset,
                    code = self.currentCode
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
        
        if varType in self.validVarTypes:
            try:
                size = int(int(self.sizeDict.get(varType))*int(num))
            except:
                size = 0
        elif varType in self.structDictionary:
            try:
                size = self.structDictionary.get(varType).size*int(num)
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
            label=structId,
            offset= self.offset - self.structDictionary.get(structId).offset)
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
    def newInputInfo(self,  inputType, addLabelTrue = None, addLabelFalse = None, AddLit = None, addNext = None, addvar = None, addVarLabel = None, addVarOffset = None):
        
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
        elif (inputType == 4):
            while (type(addVarOffset) == dict):
                addVarOffset = addVarOffset.get("address")
            address = addVarLabel+"["+ str(addVarOffset) +"]"
            return {'address' : address}
        
        #---Información de cuando se llama un metodo---
        elif (inputType == 5):
            return{'address': addvar}

        else:
            pass