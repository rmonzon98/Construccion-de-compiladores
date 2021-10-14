import sys
from antlr4 import *
from antlr4.tree.Trees import TerminalNode
from antlr4.error.Errors import *
from antlr.DecafLexer import DecafLexer
from antlr.DecafParser import DecafParser
from customDecaf import *

def executeWalker(file):
    input_stream = FileStream(file)
    lexer = DecafLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = DecafParser(stream)
    tree = parser.program()  
    treeInfo = STFiller()
    walker = ParseTreeWalker()
    walker.walk(treeInfo, tree)
    
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

        info += "\nEl scope "+c+ " tiene como padre a "+ parent+ " y retorna " + returnType + " su offset es " + str(treeInfo.scopeDictionary.get(c).offset)
        info +="\nSus variables son:"
        for var, varItem in v.varItems.items():
            if (varItem.varType == None):
                varType = 'None'
            else:
                varType = varItem.varType
            info += "\n\tla variable con id " + var + " es tipo " + varType + " (isArray: " + str(varItem.isArray) +")" + " su context es " + varItem.varContext + " su offset es " + str(varItem.offset)

    info += '\nStructs'

    for c, v in treeInfo.structDictionary.items():
        info += "\nEl struct con ID "+ c
        info +="\nTiene los siguientes atributos: "
        for var, varItem in v.varItems.items():
            if (varItem.varType == None):
                varType = 'None'
            else:
                varType = varItem.varType
            info +="\n\tAtributo con nombre " + var + " es tipo VarType " + varType + " (isArray: " + str(varItem.isArray) +")" + " su context es " + varItem.varContext + " su offset es " + varItem.offset
    
    with open("info.txt", "w") as text_file:
        text_file.write("%s" % info)
        text_file.close()

    
    with open("ic.txt", "w") as text_file:
        text_file.write("%s" % treeInfo.intCode)
        text_file.close()
    

    return treeInfo.errorsFound