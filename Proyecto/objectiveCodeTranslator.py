class codeTranslator():

    """
    Constructor
    """
    def __init__(self):
        self.intCodePath = 'ic.txt'
        self.objCode = '.global main\n'
        self.varCount = 1

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
                Declaración de funciones
                """
                if (tmp['type'] == 'function declaration'):
                    self.objCode += tmp['line'][tmp['line'].find("_")+1:]
                elif (tmp['type'] == 'endLabel'):
                    if (tmp['line'] != 'end label_main'):
                        self.objCode += '\n'
                
                """
                Asignaciones
                """
                if (tmp['type'] == 'asignation'):
                    asignLine = ''
                    register = self.getReg(tmp['operand1'], tmp['type'])
                    asignLine += register

                """
                Comparaciones
                """
                if  (tmp['type'] == 'comparation'):
                    if "==" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split("==")
                        operand1 = tmpComp[0]
                        operand2 = tmpComp[1]
                        if self.isNumericCustom(operand1):
                            operand1 = "#"+operand1
                            #print(operand1)
                        else:
                            operand1 = self.getReg(operand1, tmp['type'])
                        if self.isNumericCustom(operand2):
                            operand2 = "#"+operand2
                            #print(operand2)
                        else:
                            operand2 = self.getReg(operand2, tmp['type'])
                        self.objCode += "\tcmp    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tbe    ."+tmp['trueBlock']
                    elif "<" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split("<")
                        operand1 = tmpComp[0]
                        operand2 = tmpComp[1]
                        if self.isNumericCustom(operand1):
                            operand1 = "#"+operand1
                            #print(operand1)
                        else:
                            operand1 = self.getReg(operand1, tmp['type'])
                        if self.isNumericCustom(operand2):
                            operand2 = "#"+operand2
                            #print(operand2)
                        else:
                            operand2 = self.getReg(operand2, tmp['type'])
                        self.objCode += "\tcmn    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tbgt    ."+tmp['trueBlock']
                    elif ">" in tmp['comparation']:
                        tmpComp = tmp['comparation'].split(">")
                        operand1 = tmpComp[0]
                        operand2 = tmpComp[1]
                        if self.isNumericCustom(operand1):
                            operand1 = "#"+operand1
                            #print(operand1)
                        else:
                            operand1 = self.getReg(operand1, tmp['type'])
                        if self.isNumericCustom(operand2):
                            operand2 = "#"+operand2
                            #print(operand2)
                        else:
                            operand2 = self.getReg(operand2, tmp['type'])
                        self.objCode += "\tcmn    "+operand1+", "+operand2+"\n"
                        self.objCode += "\tblt    ."+tmp['trueBlock']
                    elif "<=" in tmp['comparation']:
                        pass
                    elif ">=" in tmp['comparation']:
                        pass
                    else:
                        #print("!=")
                        pass

                """
                Etiquetas
                """
                if(tmp['type'] == 'blockCodeLabel'):
                    self.objCode += "."+tmp['line'].split("\t")[1]

                """
                goto
                """
                if(tmp['type'] == 'gotoBlock'):
                    self.objCode += "\tb    ."+tmp['blockObjective']+"\n"
                
                """
                methodCall
                """
                if (tmp['type'] == 'methodCall'):
                    self.objCode += "\tbl    ."+tmp['method']

        print(self.objCode)
        f.close()

    """
    Función para analizar linea del código intermedio
    """
    def identifyLineType(self,line):
        if (" = " in line):
            lineInfo = line.split(" ")
            if ("Call" in line):
                #print("caso 1: "+line)
                return {'type':'asignation', 'line': line, 'result': lineInfo[0], 'assignSign':'=', 'operand1': lineInfo[2] +" "+ lineInfo[3], 'callMethod':True}
            elif ("+" in line or "*" in line or "-" in line or "/" in line):
                #print("caso 2: "+line)
                return {'type':'asignation', 'line': line, 'result': lineInfo[0], 'assignSign':'=', 'operand1': lineInfo[2], 'operator': lineInfo[3], 'operand2':lineInfo[4], 'callMethod':False}
            else:
                #print("caso 3: "+line)
                return {'type':'asignation', 'line': line, 'result': lineInfo[0], 'assignSign':'=', 'operand1': lineInfo[2], 'callMethod':False}
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
    Función para verificar que una variable es numerica
    """
    def isNumericCustom(self, variable):
        try:
            float(variable)
            return True
        except:
            return False
    
    """
    GetReg
    """
    def getReg(self,variable, senderType):
        """
        if self.varCount > 8:
            self.varCount += 1
            return self.varCount -1
        else:
            self.varCount = 1
            return self.varCount
        """
        return variable






newTrans = codeTranslator()
newTrans.createCode()