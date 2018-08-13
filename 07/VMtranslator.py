import sys
import os.path

class Parser:

    def __init__(self,inputFile):
        self._inputFile = inputFile
        self._commandType = {'add'  : 'C_ARITH',
                             'sub'  : 'C_ARITH',
                             'neg'  : 'C_ARITH',
                             'eq'   : 'C_ARITH',
                             'gt'   : 'C_ARITH',
                             'lt'   : 'C_ARITH',
                             'and'  : 'C_ARITH',
                             'or'   : 'C_ARITH',
                             'not'  : 'C_ARITH',
                             'pop'  : 'C_POP',
                             'push' : 'C_PUSH'}
        self._numArgument = {'C_ARITH' : 1,
                             'C_PUSH'  : 2,
                             'C_POP'   : 2}
        self._parsedCommands = list()

    def removeComments(self,instr):
        instr = instr.split('//')[0].strip()
        if len(instr) > 0:
            return instr

    def getCommandType(self,instr):
        comm = instr.split(' ')[0].strip()
        if comm in self._commandType:
            return self._commandType[comm]

    def getNumArgument(self,instrType):
        if instrType in self._numArgument:
            return self._numArgument[instrType]

    def getArgument1(self,instr):
        if instr is not None:
            tokens = instr.split(' ')
            argCount = self.getNumArgument(self.getCommandType(tokens[0]))
            if argCount is not None:
                if argCount == 1:
                    return tokens[0]
                if argCount == 2:
                    return tokens[1]

    def getArgument2(self,instr):
        if instr is not None:
            tokens = instr.split(' ')
            argCount = self.getNumArgument(self.getCommandType(tokens[0]))
            if argCount is not None:
                if argCount == 2:
                    return tokens[2]
        
    def parseFile(self):
        with open(self._inputFile,'rb') as inFile:
            for instr in inFile:
                uncommented = self.removeComments(instr)
                if uncommented is not None and len(uncommented) > 0:
                    commType = self.getCommandType(uncommented)
                    if commType is not None:
                        args = list()
                        args.append(self.getArgument1(uncommented))
                        if self._numArgument[commType] >= 2:
                            args.append(self.getArgument2(uncommented))
                        self._parsedCommands.append((commType,args))
        return self._parsedCommands

class CodeWriter:

    def __init__(self,parsedCommands,outputFile):
        self._parsedCommands = parsedCommands
        self._outputFile = outputFile
        self._lineNumber = 0

    def getCommandType(self,parsedInstr):
        return parsedInstr[0]

    def getArguments(self,parsedInstr):
        return parsedInstr[1]

    def processArith(self,command):
        asmCode = list()

        if command == 'add':
            # take top element from stack, store in D, and decrement SP
            asmCode.extend(['@SP','A=M-1','D=M','@SP','M=M-1'])
            # add contents of D with stack element
            asmCode.extend(['A=M-1','M=D+M'])

        elif command == 'sub':
            # take top element from stack, store in D, and decrement SP
            asmCode.extend(['@SP','A=M-1','D=M','@SP','M=M-1'])
            # subtract contents of D from stack element, and increment SP
            asmCode.extend(['A=M-1','M=M-D'])

        elif command == 'neg':
            # find top element of stack and negate
            asmCode.extend(['@SP','A=M-1','M=-M'])

        elif command == 'and':
            # take top element from stack, store in D, and decrement SP
            asmCode.extend(['@SP','A=M-1','D=M','@SP','M=M-1'])
            # and contents of D with stack element
            asmCode.extend(['A=M-1','M=D&M'])

        elif command == 'or':
            # take top element from stack, store in D, and decrement SP
            asmCode.extend(['@SP','A=M-1','D=M','@SP','M=M-1'])
            # or contents of D with stack element
            asmCode.extend(['A=M-1','M=D|M'])

        elif command == 'not':
            # find top element of stack and negate logically
            asmCode.extend(['@SP','A=M-1','M=!M'])

        elif command == 'gt':
            # get top of stack, store in D, decrement SP, get new top
            asmCode.extend(['@SP','A=M-1','D=M','@SP','M=M-1','A=M-1'])
            # compare D with new top, jump to TRUE branch if new top > D
            asmCode.extend(['D=M-D','@GT_'+str(self._lineNumber),'D;JGT'])
            # if new top !> D, set new top to FALSE
            asmCode.extend(['@SP','A=M-1','M=0'])
            # unconditional jump to end of evaluation to avoid TRUE branch
            asmCode.extend(['@END_GT_'+str(self._lineNumber),'0;JMP'])
            # label for the TRUE branch
            asmCode.extend(['(GT_'+str(self._lineNumber)+')'])
            # new top > D, thus set new top to TRUE
            asmCode.extend(['@SP','A=M-1','M=-1'])
            # label for end of evaluation of gt command
            asmCode.extend(['(END_GT_'+str(self._lineNumber)+')'])

        elif command == 'lt':
            # get top of stack, store in D, decrement SP, get new top
            asmCode.extend(['@SP','A=M-1','D=M','@SP','M=M-1','A=M-1'])
            # compare D with new top, jump to TRUE branch if new top < D
            asmCode.extend(['D=M-D','@LT_'+str(self._lineNumber),'D;JLT'])
            # if new top !< D, set new top to FALSE
            asmCode.extend(['@SP','A=M-1','M=0'])
            # unconditional jump to end of evaluation to avoid TRUE branch
            asmCode.extend(['@END_LT_'+str(self._lineNumber),'0;JMP'])
            # label for the TRUE branch
            asmCode.extend(['(LT_'+str(self._lineNumber)+')'])
            # new top < D, thus set new top to TRUE
            asmCode.extend(['@SP','A=M-1','M=-1'])
            # label for end of evaluation of lt command
            asmCode.extend(['(END_LT_'+str(self._lineNumber)+')'])

        elif command == 'eq':
            # get top of stack, store in D, decrement SP, get new top
            asmCode.extend(['@SP','A=M-1','D=M','@SP','M=M-1','A=M-1'])
            # compare D with new top, jump to TRUE branch if new top == D
            asmCode.extend(['D=M-D','@EQ_'+str(self._lineNumber),'D;JEQ'])
            # if new top != D, set new top to FALSE
            asmCode.extend(['@SP','A=M-1','M=0'])
            # unconditional jump to end of evaluation to avoid TRUE branch
            asmCode.extend(['@END_EQ_'+str(self._lineNumber),'0;JMP'])
            # label for the TRUE branch
            asmCode.extend(['(EQ_'+str(self._lineNumber)+')'])
            # new top == D, thus set new top to TRUE
            asmCode.extend(['@SP','A=M-1','M=-1'])
            # label for end of evaluation of eq command
            asmCode.extend(['(END_EQ_'+str(self._lineNumber)+')'])

        return asmCode

    def getSegmentMap(self,argNumeric):

        staticValue = '_'.join(self._outputFile.split('.')[0].split('/'))
        staticValue += '.'+argNumeric

        segmentMap = {'local'    : 'LCL',
                      'argument' : 'ARG',
                      'this'     : 'THIS',
                      'that'     : 'THAT',
                      'constant' : argNumeric,
                      'temp'     : '5',
                      'pointer'  : 'THIS' if argNumeric == '0' else 'THAT',
                      'static'   : staticValue}
        return segmentMap

    def processPush(self,args):
        segment,argNumeric = args
        segmentMap = self.getSegmentMap(argNumeric)
        asmCode = list()

        if segment in ['local','argument','this','that']:
            # store the numeric offset in D register
            asmCode.extend(['@'+argNumeric,'D=A'])
            # access contents of register pointed by (base_address+offset)
            # and store in D register
            asmCode.extend(['@'+segmentMap[segment],'A=M+D','D=M'])

        elif segment == 'constant':
            # put numeric argument in A register, then copy it to D register
            asmCode.extend(['@'+argNumeric,'D=A'])

        elif segment == 'temp':
            # store the numeric offset in D register
            asmCode.extend(['@'+argNumeric,'D=A'])
            # access contents of register pointed by (base_address+offset)
            # and store in D register
            asmCode.extend(['@'+segmentMap[segment],'A=A+D','D=M'])

        elif segment in ['pointer','static']:
            # store contents of register and store them in D
            asmCode.extend(['@'+segmentMap[segment],'D=M']) 

        # push contents of D register onto stack and increment SP
        asmCode.extend(['@SP','M=M+1','A=M-1','M=D'])
        return asmCode

    def processPop(self,args): 
        segment,argNumeric = args
        segmentMap = self.getSegmentMap(argNumeric)
        asmCode = list()

        if segment in ['local','argument','this','that']:
            # store the numeric offset in D register
            asmCode.extend(['@'+argNumeric,'D=A'])
            # calculate target address (base_address+offset) and store in D
            asmCode.extend(['@'+segmentMap[segment],'A=M+D','D=A'])
            # store the target address of pop in R15
            asmCode.extend(['@R15','M=D'])

        elif segment == 'temp':
            # store the numeric offset in D register
            asmCode.extend(['@'+argNumeric,'D=A'])
            # calculate target address (base_address+offset) and store in D
            asmCode.extend(['@'+segmentMap[segment],'A=A+D','D=A'])
            # store the target address of pop in R15
            asmCode.extend(['@R15','M=D'])

        elif segment in ['pointer','static']:
            # store target location in D
            asmCode.extend(['@'+segmentMap[segment],'D=A']) 
            # store the target address of pop in R15
            asmCode.extend(['@R15','M=D'])

        # get contents from top of stack, store them in D, decrement SP
        # access target address from R15, redirect to target address, and load it with D
        asmCode.extend(['@SP','M=M-1','A=M','D=M','@R15','A=M','M=D'])
        return asmCode

    def processFile(self):
        with open(self._outputFile,'wb') as outFile:
            for command in self._parsedCommands:
                commandType = self.getCommandType(command)
                args = self.getArguments(command)

                if commandType == 'C_ARITH':
                    asmCode = '\n'.join(self.processArith(args[0]))
                    outFile.write('// '+' '.join(args)+'\n')
                    outFile.write(asmCode+'\n')

                if commandType == 'C_PUSH':
                    asmCode = '\n'.join(self.processPush(args))
                    outFile.write('// push '+' '.join(args)+'\n')
                    outFile.write(asmCode+'\n')

                if commandType == 'C_POP':
                    asmCode = '\n'.join(self.processPop(args))
                    outFile.write('// pop '+' '.join(args)+'\n')
                    outFile.write(asmCode+'\n')

                self._lineNumber += 1

if __name__ == '__main__':

    if len(sys.argv) < 2:
        exit('Error: No input file defined. Exiting...')
    if len(sys.argv) > 2:
        exit('Error: Specify only one input file. Exiting...')
    inputFile = sys.argv[1].strip()
    if not os.path.isfile(inputFile):
        exit('Error: Invalid input file. Exiting...')

    # generate output file with .asm extension
    outputFile = inputFile.split('.')[0]+'.asm'

    parser = Parser(inputFile)
    parsed = parser.parseFile()

    codewriter = CodeWriter(parsed,outputFile)
    codewriter.processFile()
