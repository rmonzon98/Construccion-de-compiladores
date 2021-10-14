#--------------------------Segunda entrega--------------------------
#Clase para definir un item de la tabla de quadruple
#Entre sus atributos encontramos su operador (se espera un string)
#Además 2 argumentos
#Y por último 1 resultado
#El operador 2 ocasiones puede faltar, pero siempre se 
#Espera un argumento y un operador
class quadrupleItem():
    def __init__(self, operator, argument1, argument2, result):
        self.operator = operator
        self.argument1 = argument1
        self.argument2 = argument2
        self.result = result