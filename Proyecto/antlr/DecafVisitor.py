# Generated from Decaf.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .DecafParser import DecafParser
else:
    from DecafParser import DecafParser

# This class defines a complete generic visitor for a parse tree produced by DecafParser.

class DecafVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by DecafParser#program.
    def visitProgram(self, ctx:DecafParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#declaration.
    def visitDeclaration(self, ctx:DecafParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#varDeclaration.
    def visitVarDeclaration(self, ctx:DecafParser.VarDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#structDeclaration.
    def visitStructDeclaration(self, ctx:DecafParser.StructDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#varType.
    def visitVarType(self, ctx:DecafParser.VarTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#methodDeclaration.
    def visitMethodDeclaration(self, ctx:DecafParser.MethodDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#methodType.
    def visitMethodType(self, ctx:DecafParser.MethodTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#parameter.
    def visitParameter(self, ctx:DecafParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#parameterType.
    def visitParameterType(self, ctx:DecafParser.ParameterTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#block.
    def visitBlock(self, ctx:DecafParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#st_if.
    def visitSt_if(self, ctx:DecafParser.St_ifContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#st_while.
    def visitSt_while(self, ctx:DecafParser.St_whileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#st_return.
    def visitSt_return(self, ctx:DecafParser.St_returnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#st_mtdc.
    def visitSt_mtdc(self, ctx:DecafParser.St_mtdcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#st_block.
    def visitSt_block(self, ctx:DecafParser.St_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#st_assig.
    def visitSt_assig(self, ctx:DecafParser.St_assigContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#st_line.
    def visitSt_line(self, ctx:DecafParser.St_lineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#expressionOom.
    def visitExpressionOom(self, ctx:DecafParser.ExpressionOomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#location.
    def visitLocation(self, ctx:DecafParser.LocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_lite.
    def visitEx_lite(self, ctx:DecafParser.Ex_liteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_par.
    def visitEx_par(self, ctx:DecafParser.Ex_parContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_ar2.
    def visitEx_ar2(self, ctx:DecafParser.Ex_ar2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_loc.
    def visitEx_loc(self, ctx:DecafParser.Ex_locContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_ar1.
    def visitEx_ar1(self, ctx:DecafParser.Ex_ar1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_not.
    def visitEx_not(self, ctx:DecafParser.Ex_notContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_ar4.
    def visitEx_ar4(self, ctx:DecafParser.Ex_ar4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_minu.
    def visitEx_minu(self, ctx:DecafParser.Ex_minuContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_ar3.
    def visitEx_ar3(self, ctx:DecafParser.Ex_ar3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_ar5.
    def visitEx_ar5(self, ctx:DecafParser.Ex_ar5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#ex_mtdc.
    def visitEx_mtdc(self, ctx:DecafParser.Ex_mtdcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#methodCall.
    def visitMethodCall(self, ctx:DecafParser.MethodCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#rel_op.
    def visitRel_op(self, ctx:DecafParser.Rel_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#eq_op.
    def visitEq_op(self, ctx:DecafParser.Eq_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#arith_op_fifth.
    def visitArith_op_fifth(self, ctx:DecafParser.Arith_op_fifthContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#arith_op_fourth.
    def visitArith_op_fourth(self, ctx:DecafParser.Arith_op_fourthContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#arith_op_third.
    def visitArith_op_third(self, ctx:DecafParser.Arith_op_thirdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#arith_op_second.
    def visitArith_op_second(self, ctx:DecafParser.Arith_op_secondContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#arith_op_first.
    def visitArith_op_first(self, ctx:DecafParser.Arith_op_firstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#literal.
    def visitLiteral(self, ctx:DecafParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#int_literal.
    def visitInt_literal(self, ctx:DecafParser.Int_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#char_literal.
    def visitChar_literal(self, ctx:DecafParser.Char_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DecafParser#bool_literal.
    def visitBool_literal(self, ctx:DecafParser.Bool_literalContext):
        return self.visitChildren(ctx)



del DecafParser