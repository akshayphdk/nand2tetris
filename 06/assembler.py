#!/usr/bin/env python

import sys
import os.path

# function to initialize a symbol table with the pre-defined symbols

def create_symbol_table():

    sym_table = dict()

    # generate table entries for registers. ex: R0 -> 0
    for i in range(16):
        key = 'R'+str(i)
        value = i
        sym_table[key] = value

    # add remaining table entries manually
    sym_table['SCREEN'] = 16384 
    sym_table['KBD']    = 24576
    sym_table['SP']     = 0
    sym_table['LCL']    = 1
    sym_table['ARG']    = 2
    sym_table['THIS']   = 3
    sym_table['THAT']   = 4

    return sym_table

# function to perform first-pass on input file

def first_pass(input_file,sym_table):

    # the first-pass involves two steps:
    # 1. remove whitespace and comments
    # 2. add label symbols to symbol table

    line_num = 0
    first_pass = list()

    with open(input_file,'rb') as file_in:
        for instr in file_in:
            instr = instr.strip()
            instr = instr.split('//')[0].strip()
            if len(instr) > 0:
                if instr[0] == '(':
                    label = instr[1:-1]
                    sym_table[label] = line_num
                else:
                    first_pass.append(instr)
                    line_num += 1
    return first_pass

def is_Ainstruction(instr):

    return instr[0] == '@'

def process_Ainstruction(instr,sym_table,addr_loc):

    addr = instr.split('@')[1]
    if addr.isdigit():
        bin_addr = '{0:016b}'.format(int(addr))
    else:
        if addr in sym_table:
            bin_addr = '{0:016b}'.format(sym_table[addr])
        else:
            bin_addr = '{0:016b}'.format(addr_loc)
            sym_table[addr] = addr_loc
            addr_loc += 1
    return bin_addr,addr_loc

def process_jump(jump):

    if jump == '':
        return '000'
    if jump == 'JGT':
        return '001'
    if jump == 'JEQ':
        return '010'
    if jump == 'JGE':
        return '011'
    if jump == 'JLT':
        return '100'
    if jump == 'JNE':
        return '101'
    if jump == 'JLE':
        return '110'
    if jump == 'JMP':
        return '111'

def process_dest(dest):

    bin_dest = ['0','0','0']
    if 'M' in dest:
        bin_dest[2] = '1'
    if 'D' in dest:
        bin_dest[1] = '1'
    if 'A' in dest:
        bin_dest[0] = '1'
    return ''.join(bin_dest)

def process_comp(comp):

    if 'M' in comp:
        a = '1'
    else:
        a = '0'

    comp_lookup = {'0'   : '101010',
                   '1'   : '111111',
                   '-1'  : '111010',
                   'D'   : '001100',
                   'A'   : '110000',
                   'M'   : '110000',
                   '!D'  : '001101',
                   '!A'  : '110001',
                   '!M'  : '110001',
                   '-D'  : '001111',
                   '-A'  : '110011',
                   '-M'  : '110011',
                   'D+1' : '011111',
                   'A+1' : '110111',
                   'M+1' : '110111',
                   'D-1' : '001110',
                   'A-1' : '110010',
                   'M-1' : '110010',
                   'D+A' : '000010',
                   'D+M' : '000010',
                   'D-A' : '010011',
                   'D-M' : '010011',
                   'A-D' : '000111',
                   'M-D' : '000111',
                   'D&A' : '000000',
                   'D&M' : '000000',
                   'D|A' : '010101',
                   'D|M' : '010101'}

    return a+comp_lookup[comp]

def process_Cinstruction(instr):

    header = '111'
    jump = ''
    dest = ''
    comp = ''

    first_split = instr.split(';')
    prefix = first_split[0]
    if len(first_split) == 2:
        jump = first_split[1].strip()

    second_split = prefix.split('=')
    if len(second_split) == 2:
        dest = second_split[0].strip()
        comp = second_split[1].strip()
    else:
        comp = second_split[0].strip()

    return header+process_comp(comp)+process_dest(dest)+process_jump(jump)


def second_pass(instruction_list,sym_table):

    second_pass = list()
    addr_loc = 16

    for instr in instruction_list:
        if is_Ainstruction(instr):
            bin_addr,addr_loc = process_Ainstruction(instr,sym_table,addr_loc)
            second_pass.append(bin_addr)
        else:
            second_pass.append(process_Cinstruction(instr))

    return second_pass

if __name__ == '__main__':

    if len(sys.argv) < 2:
        exit('Error: No input file defined. Exiting...')

    if len(sys.argv) > 2:
        exit('Error: Specify only one input file. Exiting...')

    input_file = sys.argv[1].strip()
    if not os.path.isfile(input_file):
        exit('Error: Invalid input file. Exiting..')

    # generate output file with .hack extension
    output_file = input_file.split('.')[0]+'.hack'

    sym_table = create_symbol_table()
    instruction_list_1 = first_pass(input_file,sym_table)
    instruction_list_2 = second_pass(instruction_list_1,sym_table)

    with open(output_file,'wb') as file_out:
        for instruction in instruction_list_2:
            file_out.write(instruction+'\n')
