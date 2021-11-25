import sys
from antlr4 import *
from antlr4.tree.Trees import TerminalNode
from antlr4.error.Errors import *
from antlr.DecafLexer import DecafLexer
from antlr.DecafParser import DecafParser
from customDecaf import *
from objectiveCodeTranslator import *

def executeWalker(file):
    input_stream = FileStream(file)
    lexer = DecafLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = DecafParser(stream)
    tree = parser.program()  
    treeInfo = STFiller()
    walker = ParseTreeWalker()
    walker.walk(treeInfo, tree)

    with open("nombreFunciones.txt", "w") as text_file: 
        actualFunct = None
        previousFunct = None
        size = 0
        for c, v in treeInfo.scopeDictionary.items():
            if c.upper() == "PROGRAM":
                globalSize = 0
                for var, varItem in v.varItems.items():
                    if varItem.isArray:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            globalSize += 4 * int(varItem.arrayLen)
                        elif (varType in ["char","boolean"]):
                            globalSize += 1 * int(varItem.arrayLen)
                    else:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            globalSize += 4
                        elif (varType in ["char","boolean"]):
                            globalSize += 1   
                text_file.write("%s" % (str(c).upper()+" -> " + str(globalSize) + "\n"))
            elif not "SCOPE" in c.upper() and not "INSIDE" in c.upper():
                actualFunct = c.upper()

                if previousFunct == None:
                    previousFunct = c.upper()
                elif previousFunct != actualFunct:
                    text_file.write("%s" % (previousFunct.upper()+" -> " + str(size) + "\n"))
                    previousFunct = actualFunct
                    size=0
                else:
                    text_file.write("%s" % (previousFunct.upper()+" -> " + str(size) + "\n"))
                    previousFunct = actualFunct
                    size=0
                for var, varItem in v.varItems.items():
                    if varItem.isArray:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            size += 4 * int(varItem.arrayLen)
                        elif (varType in ["char","boolean"]):
                            size += 1 * int(varItem.arrayLen)
                    else:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            size += 4
                        elif (varType in ["char","boolean"]):
                            size += 1
            elif actualFunct in c.upper():
                for var, varItem in v.varItems.items():
                    if varItem.isArray:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            size += 4 * int(varItem.arrayLen)
                        elif (varType in ["char","boolean"]):
                            size += 1 * int(varItem.arrayLen)
                    else:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            size += 4
                        elif (varType in ["char","boolean"]):
                            size += 1
        text_file.write("%s" % (actualFunct.upper()+" -> " + str(size) + "\n"))                      
    text_file.close()

    with open("nombrevariables.txt", "w") as text_file:
        actualFunct = None
        previousFunct = None
        size = 0
        for c, v in treeInfo.scopeDictionary.items():
            """
            if c.upper() == "PROGRAM":
                globalSize = 0
                for var, varItem in v.varItems.items():
                    if varItem.isArray:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            globalSize += 4 * int(varItem.arrayLen)
                        elif (varType in ["char","boolean"]):
                            globalSize += 1 * int(varItem.arrayLen)
                    else:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            globalSize += 4
                        elif (varType in ["char","boolean"]):
                            globalSize += 1   
                text_file.write("%s" % (str(c).upper()+" -> " + str(globalSize) + "\n"))
            """
            if not "SCOPE" in c.upper() and not "INSIDE" in c.upper():
                count = 0
                for var, varItem in v.varItems.items():
                    size = 0
                    if varItem.isArray:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            size += 4 * int(varItem.arrayLen)
                        elif (varType in ["char","boolean"]):
                            size += 1 * int(varItem.arrayLen)
                    else:
                        if (varItem.varType == None):
                            varType = 'None'
                        else:
                            varType = varItem.varType
                        if (varType == "int"):
                            size += 4
                        elif (varType in ["char","boolean"]):
                            size += 1
                    count += 1
                    text_file.write("%s" % (str(c).upper()+" -> " + var + " -> " + str(varItem.offset) + " -> " + str(count) + " -> " + str(varItem.size) + "\n"))
    text_file.close() 
    
    with open("scopes.txt", "w") as text_file:
        text_file.write("Fucniones")
        info = "Scopes" 
        for c, v in treeInfo.scopeDictionary.items():
            if (v.parentKey == None):
                parent = 'None'
            else:
                parent = v.parentKey

            if (v.returnType == None):
                returnType = 'None'
            else:
                returnType = v.returnType

            info += "\nEl scope "+c+ " tiene como padre a "+ parent+ " y retorna " + returnType + " su offset es " + str(treeInfo.scopeDictionary.get(c).offset) + " code " + treeInfo.scopeDictionary.get(c).code
            text_file.write("%s" % ("\nEl scope "+c +" retorna " + returnType + " su offset es " + str(treeInfo.scopeDictionary.get(c).offset) + " code " + treeInfo.scopeDictionary.get(c).code))
            info +="\nSus variables son:"
            text_file.write("%s" % ("\nSus variables son:"))
            for var, varItem in v.varItems.items():
                if (varItem.varType == None):
                    varType = 'None'
                    text_file.write("%s" % ("\nNinguna"))
                else:
                    varType = varItem.varType
                info += "\n\tla variable con id " + var + " es tipo " + varType + " (isArray: " + str(varItem.isArray) +")" + " su context es " + varItem.varContext + " su offset es " + str(varItem.offset) + " su label es " + str(varItem.label)
                text_file.write("%s" % ("\n\tla variable con id " + var + " es tipo " + varType + " (isArray: " + str(varItem.isArray) +")" + " su context es " + varItem.varContext + " su offset es " + str(varItem.offset) + " su label es " + str(varItem.label)))
    text_file.close()

    info += '\nStructs'

    for c, v in treeInfo.structDictionary.items():
        info += "\nEl struct con ID "+ c + " offset "+str(treeInfo.structDictionary.get(c).offset) + " size "+str(treeInfo.structDictionary.get(c).size)
        info +="\nTiene los siguientes atributos: "
        for var, varItem in v.varItems.items():
            if (varItem.varType == None):
                varType = 'None'
            else:
                varType = varItem.varType
            info +="\n\tAtributo con nombre " + var + " es tipo " + varType + " (isArray: " + str(varItem.isArray) +")" + " su context es " + varItem.varContext + " su offset es " + str(varItem.offset) + " su label es " + str(varItem.label)
    
    with open("info.txt", "w") as text_file:
        text_file.write("%s" % info)
        text_file.close()

    
    with open("ic.txt", "w") as text_file:
        text_file.write("%s" % treeInfo.intCode)
        text_file.close()

    newTrans = codeTranslator(treeInfo.scopeDictionary, treeInfo.structDictionary)
    newTrans.createCode()
    #print(newTrans.getObejectiveCode())
    

    return treeInfo.errorsFound, newTrans.getObejectiveCode()