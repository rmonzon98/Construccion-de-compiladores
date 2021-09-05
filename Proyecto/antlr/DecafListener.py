# Generated from Decaf.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .DecafParser import DecafParser
else:
    from DecafParser import DecafParser

# This class defines a complete listener for a parse tree produced by DecafParser.
class DecafListener(ParseTreeListener):

    # Enter a parse tree produced by DecafParser#program.
    def enterProgram(self, ctx:DecafParser.ProgramContext):
        pass

    # Exit a parse tree produced by DecafParser#program.
    def exitProgram(self, ctx:DecafParser.ProgramContext):
        pass


    # Enter a parse tree produced by DecafParser#declaration.
    def enterDeclaration(self, ctx:DecafParser.DeclarationContext):
        pass

    # Exit a parse tree produced by DecafParser#declaration.
    def exitDeclaration(self, ctx:DecafParser.DeclarationContext):
        pass


    # Enter a parse tree produced by DecafParser#varDeclaration.
    def enterVarDeclaration(self, ctx:DecafParser.VarDeclarationContext):
        pass

    # Exit a parse tree produced by DecafParser#varDeclaration.
    def exitVarDeclaration(self, ctx:DecafParser.VarDeclarationContext):
        pass


    # Enter a parse tree produced by DecafParser#structDeclaration.
    def enterStructDeclaration(self, ctx:DecafParser.StructDeclarationContext):
        pass

    # Exit a parse tree produced by DecafParser#structDeclaration.
    def exitStructDeclaration(self, ctx:DecafParser.StructDeclarationContext):
        pass


    # Enter a parse tree produced by DecafParser#varType.
    def enterVarType(self, ctx:DecafParser.VarTypeContext):
        pass

    # Exit a parse tree produced by DecafParser#varType.
    def exitVarType(self, ctx:DecafParser.VarTypeContext):
        pass


    # Enter a parse tree produced by DecafParser#methodDeclaration.
    def enterMethodDeclaration(self, ctx:DecafParser.MethodDeclarationContext):
        pass

    # Exit a parse tree produced by DecafParser#methodDeclaration.
    def exitMethodDeclaration(self, ctx:DecafParser.MethodDeclarationContext):
        pass


    # Enter a parse tree produced by DecafParser#methodType.
    def enterMethodType(self, ctx:DecafParser.MethodTypeContext):
        pass

    # Exit a parse tree produced by DecafParser#methodType.
    def exitMethodType(self, ctx:DecafParser.MethodTypeContext):
        pass


    # Enter a parse tree produced by DecafParser#parameter.
    def enterParameter(self, ctx:DecafParser.ParameterContext):
        pass

    # Exit a parse tree produced by DecafParser#parameter.
    def exitParameter(self, ctx:DecafParser.ParameterContext):
        pass


    # Enter a parse tree produced by DecafParser#parameterType.
    def enterParameterType(self, ctx:DecafParser.ParameterTypeContext):
        pass

    # Exit a parse tree produced by DecafParser#parameterType.
    def exitParameterType(self, ctx:DecafParser.ParameterTypeContext):
        pass


    # Enter a parse tree produced by DecafParser#block.
    def enterBlock(self, ctx:DecafParser.BlockContext):
        pass

    # Exit a parse tree produced by DecafParser#block.
    def exitBlock(self, ctx:DecafParser.BlockContext):
        pass


    # Enter a parse tree produced by DecafParser#st_if.
    def enterSt_if(self, ctx:DecafParser.St_ifContext):
        pass

    # Exit a parse tree produced by DecafParser#st_if.
    def exitSt_if(self, ctx:DecafParser.St_ifContext):
        pass


    # Enter a parse tree produced by DecafParser#st_while.
    def enterSt_while(self, ctx:DecafParser.St_whileContext):
        pass

    # Exit a parse tree produced by DecafParser#st_while.
    def exitSt_while(self, ctx:DecafParser.St_whileContext):
        pass


    # Enter a parse tree produced by DecafParser#st_return.
    def enterSt_return(self, ctx:DecafParser.St_returnContext):
        pass

    # Exit a parse tree produced by DecafParser#st_return.
    def exitSt_return(self, ctx:DecafParser.St_returnContext):
        pass


    # Enter a parse tree produced by DecafParser#st_mtdc.
    def enterSt_mtdc(self, ctx:DecafParser.St_mtdcContext):
        pass

    # Exit a parse tree produced by DecafParser#st_mtdc.
    def exitSt_mtdc(self, ctx:DecafParser.St_mtdcContext):
        pass


    # Enter a parse tree produced by DecafParser#st_block.
    def enterSt_block(self, ctx:DecafParser.St_blockContext):
        pass

    # Exit a parse tree produced by DecafParser#st_block.
    def exitSt_block(self, ctx:DecafParser.St_blockContext):
        pass


    # Enter a parse tree produced by DecafParser#st_assig.
    def enterSt_assig(self, ctx:DecafParser.St_assigContext):
        pass

    # Exit a parse tree produced by DecafParser#st_assig.
    def exitSt_assig(self, ctx:DecafParser.St_assigContext):
        pass


    # Enter a parse tree produced by DecafParser#st_line.
    def enterSt_line(self, ctx:DecafParser.St_lineContext):
        pass

    # Exit a parse tree produced by DecafParser#st_line.
    def exitSt_line(self, ctx:DecafParser.St_lineContext):
        pass


    # Enter a parse tree produced by DecafParser#expressionOom.
    def enterExpressionOom(self, ctx:DecafParser.ExpressionOomContext):
        pass

    # Exit a parse tree produced by DecafParser#expressionOom.
    def exitExpressionOom(self, ctx:DecafParser.ExpressionOomContext):
        pass


    # Enter a parse tree produced by DecafParser#location.
    def enterLocation(self, ctx:DecafParser.LocationContext):
        pass

    # Exit a parse tree produced by DecafParser#location.
    def exitLocation(self, ctx:DecafParser.LocationContext):
        pass


    # Enter a parse tree produced by DecafParser#ex_lite.
    def enterEx_lite(self, ctx:DecafParser.Ex_liteContext):
        pass

    # Exit a parse tree produced by DecafParser#ex_lite.
    def exitEx_lite(self, ctx:DecafParser.Ex_liteContext):
        pass


    # Enter a parse tree produced by DecafParser#ex_par.
    def enterEx_par(self, ctx:DecafParser.Ex_parContext):
        pass

    # Exit a parse tree produced by DecafParser#ex_par.
    def exitEx_par(self, ctx:DecafParser.Ex_parContext):
        pass


    # Enter a parse tree produced by DecafParser#ex_ar2.
    def enterEx_ar2(self, ctx:DecafParser.Ex_ar2Context):
        pass

    # Exit a parse tree produced by DecafParser#ex_ar2.
    def exitEx_ar2(self, ctx:DecafParser.Ex_ar2Context):
        pass


    # Enter a parse tree produced by DecafParser#ex_loc.
    def enterEx_loc(self, ctx:DecafParser.Ex_locContext):
        pass

    # Exit a parse tree produced by DecafParser#ex_loc.
    def exitEx_loc(self, ctx:DecafParser.Ex_locContext):
        pass


    # Enter a parse tree produced by DecafParser#ex_ar1.
    def enterEx_ar1(self, ctx:DecafParser.Ex_ar1Context):
        pass

    # Exit a parse tree produced by DecafParser#ex_ar1.
    def exitEx_ar1(self, ctx:DecafParser.Ex_ar1Context):
        pass


    # Enter a parse tree produced by DecafParser#ex_not.
    def enterEx_not(self, ctx:DecafParser.Ex_notContext):
        pass

    # Exit a parse tree produced by DecafParser#ex_not.
    def exitEx_not(self, ctx:DecafParser.Ex_notContext):
        pass


    # Enter a parse tree produced by DecafParser#ex_ar4.
    def enterEx_ar4(self, ctx:DecafParser.Ex_ar4Context):
        pass

    # Exit a parse tree produced by DecafParser#ex_ar4.
    def exitEx_ar4(self, ctx:DecafParser.Ex_ar4Context):
        pass


    # Enter a parse tree produced by DecafParser#ex_minu.
    def enterEx_minu(self, ctx:DecafParser.Ex_minuContext):
        pass

    # Exit a parse tree produced by DecafParser#ex_minu.
    def exitEx_minu(self, ctx:DecafParser.Ex_minuContext):
        pass


    # Enter a parse tree produced by DecafParser#ex_ar3.
    def enterEx_ar3(self, ctx:DecafParser.Ex_ar3Context):
        pass

    # Exit a parse tree produced by DecafParser#ex_ar3.
    def exitEx_ar3(self, ctx:DecafParser.Ex_ar3Context):
        pass


    # Enter a parse tree produced by DecafParser#ex_ar5.
    def enterEx_ar5(self, ctx:DecafParser.Ex_ar5Context):
        pass

    # Exit a parse tree produced by DecafParser#ex_ar5.
    def exitEx_ar5(self, ctx:DecafParser.Ex_ar5Context):
        pass


    # Enter a parse tree produced by DecafParser#ex_mtdc.
    def enterEx_mtdc(self, ctx:DecafParser.Ex_mtdcContext):
        pass

    # Exit a parse tree produced by DecafParser#ex_mtdc.
    def exitEx_mtdc(self, ctx:DecafParser.Ex_mtdcContext):
        pass


    # Enter a parse tree produced by DecafParser#methodCall.
    def enterMethodCall(self, ctx:DecafParser.MethodCallContext):
        pass

    # Exit a parse tree produced by DecafParser#methodCall.
    def exitMethodCall(self, ctx:DecafParser.MethodCallContext):
        pass


    # Enter a parse tree produced by DecafParser#rel_op.
    def enterRel_op(self, ctx:DecafParser.Rel_opContext):
        pass

    # Exit a parse tree produced by DecafParser#rel_op.
    def exitRel_op(self, ctx:DecafParser.Rel_opContext):
        pass


    # Enter a parse tree produced by DecafParser#eq_op.
    def enterEq_op(self, ctx:DecafParser.Eq_opContext):
        pass

    # Exit a parse tree produced by DecafParser#eq_op.
    def exitEq_op(self, ctx:DecafParser.Eq_opContext):
        pass


    # Enter a parse tree produced by DecafParser#arith_op_fifth.
    def enterArith_op_fifth(self, ctx:DecafParser.Arith_op_fifthContext):
        pass

    # Exit a parse tree produced by DecafParser#arith_op_fifth.
    def exitArith_op_fifth(self, ctx:DecafParser.Arith_op_fifthContext):
        pass


    # Enter a parse tree produced by DecafParser#arith_op_fourth.
    def enterArith_op_fourth(self, ctx:DecafParser.Arith_op_fourthContext):
        pass

    # Exit a parse tree produced by DecafParser#arith_op_fourth.
    def exitArith_op_fourth(self, ctx:DecafParser.Arith_op_fourthContext):
        pass


    # Enter a parse tree produced by DecafParser#arith_op_third.
    def enterArith_op_third(self, ctx:DecafParser.Arith_op_thirdContext):
        pass

    # Exit a parse tree produced by DecafParser#arith_op_third.
    def exitArith_op_third(self, ctx:DecafParser.Arith_op_thirdContext):
        pass


    # Enter a parse tree produced by DecafParser#arith_op_second.
    def enterArith_op_second(self, ctx:DecafParser.Arith_op_secondContext):
        pass

    # Exit a parse tree produced by DecafParser#arith_op_second.
    def exitArith_op_second(self, ctx:DecafParser.Arith_op_secondContext):
        pass


    # Enter a parse tree produced by DecafParser#arith_op_first.
    def enterArith_op_first(self, ctx:DecafParser.Arith_op_firstContext):
        pass

    # Exit a parse tree produced by DecafParser#arith_op_first.
    def exitArith_op_first(self, ctx:DecafParser.Arith_op_firstContext):
        pass


    # Enter a parse tree produced by DecafParser#literal.
    def enterLiteral(self, ctx:DecafParser.LiteralContext):
        pass

    # Exit a parse tree produced by DecafParser#literal.
    def exitLiteral(self, ctx:DecafParser.LiteralContext):
        pass


    # Enter a parse tree produced by DecafParser#int_literal.
    def enterInt_literal(self, ctx:DecafParser.Int_literalContext):
        pass

    # Exit a parse tree produced by DecafParser#int_literal.
    def exitInt_literal(self, ctx:DecafParser.Int_literalContext):
        pass


    # Enter a parse tree produced by DecafParser#char_literal.
    def enterChar_literal(self, ctx:DecafParser.Char_literalContext):
        pass

    # Exit a parse tree produced by DecafParser#char_literal.
    def exitChar_literal(self, ctx:DecafParser.Char_literalContext):
        pass


    # Enter a parse tree produced by DecafParser#bool_literal.
    def enterBool_literal(self, ctx:DecafParser.Bool_literalContext):
        pass

    # Exit a parse tree produced by DecafParser#bool_literal.
    def exitBool_literal(self, ctx:DecafParser.Bool_literalContext):
        pass



del DecafParser