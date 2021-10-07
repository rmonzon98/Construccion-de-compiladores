grammar Decaf;

// definimos letras y digitos de primero
fragment LETTER: ('a'..'z'|'A'..'Z'|'_');
fragment DIGIT: '0'..'9';

// definimos id y numeros (enteros)
ID: LETTER (LETTER|DIGIT)*;
NUM: DIGIT(DIGIT)*;

// definimos comentarios y caracteres
CHAR: '\'' ( ~['\r\n\\] | '\\' ['\\] ) '\'';
WS : [ \t\r\n\f]+  -> channel(HIDDEN);

COMMENT:    '/*' .*? '*/' -> channel(2);

LINE_COMMENT:   '//' ~[\r\n]* -> channel(2);

// Reglas 
program:    'class' 'Program' '{' (declaration)* '}';

declaration:    structDeclaration | varDeclaration | methodDeclaration;

varDeclaration:     varType ID ';' | varType ID '[' NUM ']' ';';

structDeclaration:      'struct' ID '{' (varDeclaration)* '}' (';')?;

varType:    'int' | 'char' | 'boolean' | 'struct' ID | structDeclaration;

methodDeclaration:      methodType ID '(' (parameter (',' parameter)*)* ')' block;

methodType:     'int' | 'char' | 'boolean' | 'void';

parameter:      parameterType ID | parameterType ID '[' ']' | 'void';

parameterType:      'int' | 'char' | 'boolean';

block: '{' (varDeclaration)* (statement)* '}';

statement: 
        'if' '(' expression ')' block ( 'else' block )? #st_if
        | 'while' '('expression')' block #st_while
        | 'return' expressionOom ';' #st_return
        | methodCall ';' #st_mtdc
        | block #st_block
        | location '=' expression #st_assig
        | (expression)? ';' #st_line
        ;


expressionOom:  expression |;

location:       (ID|ID '[' expression ']') ('.' location)?;

expression: 
        methodCall #ex_mtdc
        | location #ex_loc
        | literal #ex_lite
        | '-' expression #ex_minu
        | '!' expression #ex_not
        | '('expression')' #ex_par
        | expression arith_op_fifth expression #ex_ar5
        | expression arith_op_fourth expression #ex_ar4
        | expression arith_op_third expression #ex_ar3
        | expression arith_op_second expression #ex_ar2
        | expression arith_op_first expression #ex_ar1
        ;

methodCall: ID '(' (expression (',' expression)*)? ')';

// operaciones de relación y aritmeticas
// se dividen las operaciones para poder tener mejor control de la precedencia
rel_op : '<' | '>' | '<=' | '>=';
eq_op : '==' | '!=' ;
arith_op_fifth: '*' | '/' | '%';
arith_op_fourth: '+' | '-';
arith_op_third: rel_op | eq_op;
arith_op_second: '&&';
arith_op_first: '||';

// literales
literal : int_literal | char_literal | bool_literal ;
int_literal : NUM ;
char_literal : '\'' CHAR '\'' ;
bool_literal : 'true' | 'false' ;