from os import X_OK


class codeTranslator():

    """
    Constructor
    """
    def __init__(self, scopeDict, structDict):
        self.intCodePath = 'ic.txt'
        self.objCode = '.global main\n\n'
        self.scopeDict = scopeDict
        self.structDict = structDict
        self.actualFunct = 'program'
        self.variablesNames = []
        self.actualRegister = ''
        f = open('nombreVariables.txt')
        for line in f:
            line = line.replace("\t", "").replace("\n","").replace(" ","")
            self.variablesNames.append(line)
        self.functDict ={}
        f = open('nombreFunciones.txt')
        for line in f:
            line = line.replace("\t", "").replace("\n","").replace(" ","").split("->")
            self.functDict[line[0]] = line[1]
        self.address = {}
        self.registersDict = {}
        self.registers = ["R10", "R9", "R8", "R7", "R6", "R5", "R4", "R3", "R2", "R1", "R0"]
        
    """
    Función para generar el código objetivo
    """
    def createCode(self):
        tabCount = 1
        f = open(self.intCodePath)
        for line in f:
            if(line != "\n"):
                tmp = self.identifyLineType(line)
                
                """
                Asignaciones
                """
                if (tmp['type'] == 'asignation'):
                    if tmp['operation']:
                        rx, ry, rz = self.getRegister(tmp['result'], tmp['operand1'], tmp['operand2'], "operation")
                        if tmp['operator'] == "+":
                            self.objCode += "\tadd    " + rx + ", " +  ry + ", " + rz + "\n"
                        elif tmp['operator'] == "-":
                            self.objCode += "\tsub    " + rx + ", " +  ry + ", " + rz + "\n"
                        elif tmp['operator'] == "*":
                            self.objCode += "\tmul    " + rx + ", " +  ry + ", " + rz + "\n"
                        self.objCode += "\tstr    " + rx + ", [sp]\n"
                    elif not tmp['callMethod']:
                        rx, ry, rz = self.getRegister(tmp['result'], tmp['operand1'])
                        self.objCode += "\tmov    " + rx + ", " + ry +"\n"
                        self.objCode += "\tstr    " + rx + ", " + self.registersDict[rx] +"\n"

                
                """
                return
                """
                if (tmp['type'] == 'return'):
                    if self.isNumericCustom(tmp['returnValue']):
                        self.objCode += "\tmov    R0, #" + tmp['returnValue'] + "\n"
                        self.objCode += "\tbx    lr\n"
                    if self.checkIfHasRegister(tmp['returnValue']):
                        self.objCode += "\tldr    " + self.address[tmp['returnValue']] + ", " +  self.registersDict[self.address[tmp['returnValue']]] + "\n"

                """
                param
                """

                """
                methodCall
                """
                if (tmp['type'] == 'methodCall'):
                    self.objCode += "\tbl    ."+tmp['method']
                    
                """
                Declaración de funciones
                """
                if (tmp['type'] == 'function declaration'):
                    self.actualRegister = ""
                    #self.objCode +="\tpush    {r11, lr}\n"
                    #self.objCode +="\tmov     r11, sp\n"
                    index = tmp['line'].find("_")
                    self.objCode += tmp['line'][index+1:]
                    self.actualFunct = tmp['line'][tmp['line'].find("_")+1:len(tmp['line'])-2]
                    self.objCode += "\tsub sp, sp, #" + self.functDict[self.actualFunct.upper()][:len(self.functDict[self.actualFunct.upper()])] +"\n"
                    variablesList = self.getVariablesByContext(self.actualFunct.upper())
                    for i in range (0,len(variablesList)):
                        temp = variablesList[i].replace(" ","").split("->")
                        self.actualRegister = self.registers.pop()
                        self.objCode += "\tstr    " + self.actualRegister + ", [sp, #" + str(int(temp[2])+int(temp[4])) + "]\n"
                        self.address[self.actualFunct.upper() + "[" + temp[2] + "]"] = self.actualRegister
                        self.registersDict[self.actualRegister] = "[sp, #" + str(int(temp[2])+int(temp[4])) + "]"

                elif (tmp['type'] == 'endLabel'):
                    if (tmp['line'] != 'end label_main'):
                        #self.objCode += "\tpop    {r11, lr}\n"
                        #self.objCode += "\tbx    lr\n"
                        self.objCode += '\n'
                    self.actualFunct = 'program'
                    self.registers = ["R10", "R9", "R8", "R7", "R6", "R5", "R4", "R3", "R2", "R1", "R0"]
                    self.address = {}

                """
                Comparaciones
                """
                if  (tmp['type'] == 'comparation'):
                    #print(tmp)
                    if "==" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split("==")
                        operand1 = self.getValue(tmpComp[0])
                        operand2 = self.getValue(tmpComp[1])
                        
                        self.objCode += "\tcmp    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tb    ."+tmp['trueBlock']
                    elif "<" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split("<")
                        operand1 = self.getValue(tmpComp[0])
                        operand2 = self.getValue(tmpComp[1])
                        self.objCode += "\tcmp    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tbgt    ."+tmp['trueBlock']
                    elif "<=" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split("<")
                        operand1 = self.getValue(tmpComp[0])
                        operand2 = self.getValue(tmpComp[1])
                        self.objCode += "\tcmp    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tbge    ."+tmp['trueBlock']
                    elif ">" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split(">")
                        operand1 = tmpComp[0]
                        operand2 = tmpComp[1]
                        operand1 = self.getValue(tmpComp[0])
                        operand2 = self.getValue(tmpComp[1])
                        self.objCode += "\tcmn    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tblt    ."+tmp['trueBlock']
                    elif ">=" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split(">")
                        operand1 = tmpComp[0]
                        operand2 = tmpComp[1]
                        operand1 = self.getValue(tmpComp[0])
                        operand2 = self.getValue(tmpComp[1])
                        self.objCode += "\tcmn    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tble    ."+tmp['trueBlock']
                    else:
                        tmpComp = tmp['comparation'].split("!=")
                        operand1 = tmpComp[0]
                        operand2 = tmpComp[1]
                        operand1 = self.getValue(tmpComp[0])
                        operand2 = self.getValue(tmpComp[1])
                        self.objCode += "\tcmp    "+operand1+", "+operand2+"\n"
                        self.objCode += "\bne    ."+tmp['trueBlock']
                        pass
                
                """
                goto
                """
                if(tmp['type'] == 'gotoBlock'):
                    self.objCode += "\tb    ."+tmp['blockObjective']+"\n"
                    
                """
                Etiquetas
                """
                if(tmp['type'] == 'blockCodeLabel'):
                    self.objCode += "."+tmp['line'].split("\t")[1]

        f.close()

    """
    Función para analizar linea del código intermedio
    """
    def identifyLineType(self,line):
        if (" = " in line):
            lineInfo = line.split(" ")
            if ("Call" in line):
                #print("caso 1: "+line)
                return {'type':'asignation', 'line': line, 'result': lineInfo[0].replace("\t","").replace("\n",""), 'assignSign':'=', 'operand1': lineInfo[2].replace("\t","").replace("\n","") +" "+ lineInfo[3].replace("\t","").replace("\n",""), 'callMethod':True, 'operation': False}
            elif ("+" in line or "*" in line or "-" in line or "/" in line):
                #print("caso 2: "+line)
                return {'type':'asignation', 'line': line, 'result': lineInfo[0].replace("\t","").replace("\n",""), 'assignSign':'=', 'operand1': lineInfo[2].replace("\t","").replace("\n",""), 'operator': lineInfo[3], 'operand2':lineInfo[4].replace("\t","").replace("\n",""), 'callMethod':False, 'operation': True}
            else:
                #print("caso 3: "+line)
                return {'type':'asignation', 'line': line, 'result': lineInfo[0].replace("\t","").replace("\n",""), 'assignSign':'=', 'operand1': lineInfo[2].replace("\t","").replace("\n",""), 'callMethod':False, 'operation': False}
        elif ("return" in line):
            return {'type': 'return', 'line': line, 'returnValue': line.split(" ")[1]}
        elif ("param" in line):
            return {'type': 'param', 'line': line, 'param': line.split(" ")[1]}
        #LISTO
        elif ("Call" in line):
            return {'type': 'methodCall', 'line': line, 'method': line.split(" ")[1]}
        #LISTO
        elif ("label" in line):
            if("end" not in line):
                return {'type':'function declaration', 'line': line}
            else:
                return {'type': 'endLabel', 'line': line,}
        #LISTO
        elif ("if" in line):
            return {'type': 'comparation', 'line': line, 'comparation': line.split(" ")[1], 'trueBlock': line.split(" ")[3]}
        #LISTO
        elif ("goto" in line):
            return {'type': 'gotoBlock', 'line': line, 'blockObjective': line.split(" ")[1]}
        #LISTO
        elif ("block" in line):
            return {'type': 'blockCodeLabel', 'line': line}
        #IGNORAR
        else:
            return {'type': 'None', 'line': line,}
    
    """
    getValue
    """
    def getValue(self, variable):
        if self.isNumericCustom(variable):
            return "#"+variable
        else:
            self.objCode += "\tldr    " + self.address[variable] + ", " + self.registersDict[self.address[variable]] + "\n"
            return self.address[variable]
            return self.findVar(variable)
    
    """
    findVar
    """
    def findVar(self, variable):
        return variable

    """
    Función para verificar que una variable es numerica
    """
    def isNumericCustom(self, variable):
        try:
            float(variable)
            return True
        except:
            return False
    
    """
    getInfoInside []
    """
    def getInfoInside(self, variable):
        if ("[" in variable):
            inside = variable[variable.find("["):]
            tmpVar = variable[:variable.find("[")]
        if tmpVar.upper() in self.functDict:  # es una variable Local
            if self.isNumericCustom(inside[1:-1]):
                return "[sp, #" + inside + "]"
            else:
                return variable
        else:
            return ""    
    
    

    """
    get Register
    """
    def getRegister(self, x, y, z = None, asignType = None):
        Rx, Ry, Rz = None, None, None
        if asignType == "operation": #Operaciones
            indexRegister = self.actualRegister[1:]
            if self.checkIfHasRegister(y):
                Ry = self.address[y]
                self.objCode += "\tldr    " + Ry + ", " +self.registersDict[Ry] +"\n"
            elif self.actualRegister != "R10" and int(indexRegister) + 1 <= 10:
                self.actualRegister = self.registers.pop()
                Ry = self.actualRegister
                self.address[y] = Ry
                self.registersDict[Ry] = y
                self.objCode += "\tldr    " + Ry + ", " +self.registersDict[Ry] +"\n"
            else: 
                self.actualRegister = "R0"
                Ry = self.actualRegister
                self.address[y] = Ry
                self.registersDict[Ry] = y
                self.objCode += "\tldr    " + Ry + ", " +self.registersDict[Ry] +"\n"

            indexRegister = self.actualRegister[1:]
            if (self.isNumericCustom(z)):
                Rz = "#"+z
            else:
                if self.checkIfHasRegister(z):
                    Rz = self.address[z]
                    self.objCode += "\tldr    " + Rz + ", " +self.registersDict[Rz] +"\n"
                elif self.actualRegister != "R10" and int(indexRegister) + 1 <= 10:
                    self.actualRegister = self.registers.pop()
                    Rz = self.actualRegister
                    self.address[z] = Rz
                    self.registersDict[Rz] = z
                    self.objCode += "\tldr    " + Rz + ", " +self.registersDict[Rz] +"\n"
                else: 
                    self.actualRegister = "R0"
                    Rz = self.actualRegister
                    self.address[z] = Rz 
                    self.registersDict[Rz] = z  
                    self.objCode += "\tldr    " + Rz + ", " +self.registersDict[Rz] +"\n"    
            
            if self.checkIfHasRegister(x):
                Rx = self.address[x]
            else:
                self.address[x] = Ry
                self.registersDict[Ry] = x
                Rx = Ry
        else: #Asignaciones sin methodCalls
            if y:
                indexRegister = self.actualRegister[1:]
                if (self.isNumericCustom(y)):
                    Ry = "#"+y
                else:
                    if self.checkIfHasRegister(y):
                        Ry = self.address[y]
                    elif self.actualRegister != "R10" and int(indexRegister) + 1 <= 10:
                        self.actualRegister = self.registers.pop()
                        Ry = self.actualRegister
                        self.address[y] = Ry
                        self.registersDict[self.actualRegister] = y
                    else: 
                        self.actualRegister = "R0"
                        Ry = self.actualRegister
                        self.address[y] = Ry
                        self.registersDict[self.actualRegister] = y
            
            if x:
                if self.checkIfHasRegister(x):
                    Rx = self.address[x]
                elif self.actualRegister != "R10" and int(indexRegister) + 1 <= 10:
                    self.actualRegister = self.registers.pop()
                    Rx = self.actualRegister
                    self.address[x] = Rx
                    self.registersDict[self.actualRegister] = x
                else: 
                    self.actualRegister = "R0"
                    Rx= self.actualRegister
                    self.address[x] = Rx
                    self.registersDict[self.actualRegister] = x

                
            
        return Rx, Ry, Rz

    """
    check if a variable has a register
    """
    def checkIfHasRegister(self, value):
        flag = False
        for i in list(self.address.keys()):
            if value in i:
                return True
        return flag

    """
    get Variables from Function
    """
    def getVariablesByContext(self, variableContext):
        variablesList = []
        for i in self.variablesNames:
            if variableContext in i:
                variablesList.append(i)

        return variablesList

    """
    getObejectiveCode
    """
    def getObejectiveCode(self):
        return self.objCode

    """
    get addresses
    """
    def getAddresses(self):
        return self.address
