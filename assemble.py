import re

label = re.compile('[a-zA-Z][0-9a-zA-Z]*')
hexadecimal = re.compile('x-?[0-9a-fA-F]+')
decimal = re.compile('#?-?[0-9]+')
binary = re.compile('b-?[0-1]+')
reg = re.compile('[Rr][0-9]+')

Opcode = {'ADD': '0001', 'AND': '0101', 'BRN': '0000100', 'BRZ': '0000010',
          'BRP': '0000001', 'BR': '0000111', 'BRZP': '0000011', 'BRNP': '0000101',
          'BRNZ': '0000110', 'BRNZP': '0000111', 'JMP': '1100', 'RET': '1000000111000000',
          'JSRR': '0100', 'LD': '0010', 'LDI': '1010', 'LDR': '0110', 'LEA': '1110',
          'NOT': '1001', 'RTI': '1000000000000000', 'ST': '0011', 'STI': '1011', 'STR': '0111',
          'TRAP': '1111', 'GETC': '1111000000100000', 'OUT': '1111000000100001',
          'PUTS': '1111000000100010', 'IN': '1111000000100011',
          'PUTSP': '1111000000100100', 'HALT': '1111000000100101'}

Pseudo_ops = {'.ORIG', '.FILL', '.BLKW', '.STRINGZ', '.END'}


def parse_line(line):
    line = line.split(';')[0]
    line = line.strip()
    if not line:
        return None
    line = line.replace(',', ' ')
    elements = line.split()
    return elements


def is_number(element):
    if hexadecimal.fullmatch(element) \
            or decimal.fullmatch(element) \
            or binary.fullmatch(element):
        return True
    else:
        return False


def is_string(string):
    if string[0] != '"' or string[-1] != '"':
        return False
    string = string[1:-1]
    char_map = {'0': '\0', 'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t', 'v': '\v'}
    true_string = ''
    need = False
    for char in string:
        if not need and char == '\\':
            need = True
        elif need:
            need = False
            if char in char_map:
                true_string += char_map[char]
            else:
                true_string += char
        elif char == '"':
            return False
        else:
            true_string += char
    return true_string


def str2num(element):
    if element.startswith('x'):
        return int(element[1:], base=16)
    elif element.startswith('b'):
        return int(element[1:], base=2)
    elif element.startswith('#'):
        return int(element[1:], base=10)
    else:
        return int(element, base=10)


def num2bin(num, bits, signed=True):
    if num < 0 and not signed:
        return ''
    bins = bin(num)[2:] if num > 0 else bin(num)[3:]
    if not signed:
        return '0' * (bits - len(bins)) + bins
    else:
        if num >= 0:
            return '0' * (bits - len(bins)) + bins
        else:
            tc = bin(2 ** len(bins) + num)[2:]
            return '1' * (bits - len(bins)) + '0' * (len(bins) - len(tc)) + tc


def is_label(element):
    if element.upper() not in Opcode \
            and element.upper() not in Pseudo_ops \
            and not is_number(element) \
            and not reg.fullmatch(element):
        return True
    else:
        return False


def valid_label(l, line_no, error):
    if not label.fullmatch(l):
        error.append('Line {}:Invalid label \'{}\''
                     .format(line_no, l))
        return False
    else:
        return True


# check if operands satisfy need
def valid_operands(operands, need, line_no, error):
    if operands and not need:
        error.append('Line {}:\'{}...\' is redundant'
                     .format(line_no, operands[0]))
        return False
    if not operands and need:
        error.append('Line {}:Expected more operand(s)'
                     .format(line_no))
        return False
    return True


def is_value_operand(operand, line_no, error):
    if not is_number(operand):
        error.append('Line {}:Expected 16 bit value, but found \'{}\' instead'
                     .format(line_no, operand))
        return False
    else:
        value = str2num(operand)
        if value < -32768 or value > 65535:
            error.append('Line {}:{} can not be represented as an unsigned number in 16 bits'
                         .format(line_no, value))
            return False
        else:
            return True


def is_reg_operand(operand, line_no, error):
    if not reg.fullmatch(operand):
        error.append('Line {}:Expected register operand, but found \'{}\' instead'
                     .format(line_no, operand))
        return False
    else:
        reg_no = int(operand[1:], base=10)
        if reg_no > 7:
            error.append('Line {}:Register {} does not exist'
                         .format(line_no, reg_no))
            return False
        else:
            return True


def is_label_or_offset_operand(operand, pcoffset, line_no, error):
    if is_number(operand):
        offset = str2num(operand)
        if offset > 2 ** (pcoffset - 1) - 1 or offset < -2 ** (pcoffset - 1):
            error.append('Line {}:{} can not be represented as a signed number in {} bits'
                         .format(line_no, offset, pcoffset))
            return False
        return True
    elif is_label(operand):
        if not valid_label(operand, line_no, error):
            return False
        return True
    else:
        error.append('Line {}:Expected label or {} bit signed PC offset, but found \'{}\' instead'
                     .format(line_no, pcoffset, operand))
        return False


def parse_po(po, operands, LC, line_no, error):
    if po.upper() == '.ORIG':
        if LC[0] != -1:
            error.append('Line {}:Duplicate pseudo_op \'.ORIG\''
                         .format(line_no))
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            if is_value_operand(operands[0], line_no, error):
                LC[0] = str2num(operands[0])
        valid_operands(operands[1:], False, line_no, error)

    if po.upper() == '.FILL':
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            if is_label(operands[0]):
                valid_label(operands[0], line_no, error)
            elif is_value_operand(operands[0], line_no, error):
                LC[0] += 1
        valid_operands(operands[1:], False, line_no, error)

    if po.upper() == '.BLKW':
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            if is_value_operand(operands[0], line_no, error):
                LC[0] += str2num(operands[0])
        valid_operands(operands[1:], False, line_no, error)

    if po.upper() == '.STRINGZ':
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            if not is_string(operands[0]):
                error.append('Line {}:Expected string constant, but found \'{}\' instead'
                             .format(line_no, operands[0]))
            else:
                LC[0] += len(is_string(operands[0])) + 1
        valid_operands(operands[1:], False, line_no, error)


def parse_op(op, operands, line_no, error):
    if op.upper() in {'ADD', 'AND'}:
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            is_reg_operand(operands[0], line_no, error)
        if not valid_operands(operands[1:], True, line_no, error):
            return
        else:
            is_reg_operand(operands[1], line_no, error)
        if not valid_operands(operands[2:], True, line_no, error):
            return
        else:
            if is_number(operands[2]):
                imm = str2num(operands[2])
                if imm > 15 or imm < -16:
                    error.append('Line {}:{} can not be represented as a signed number in 5 bits'
                                 .format(line_no, imm))
            elif reg.fullmatch(operands[2]):
                is_reg_operand(operands[2], line_no, error)
            else:
                error.append('Line {}:Expected register or immediate value, but found \'{}\' instead'
                             .format(line_no, operands[2]))
        valid_operands(operands[3:], False, line_no, error)

    if op.upper() == 'NOT':
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            is_reg_operand(operands[0], line_no, error)
        if not valid_operands(operands[1:], True, line_no, error):
            return
        else:
            is_reg_operand(operands[1], line_no, error)
        valid_operands(operands[2:], False, line_no, error)

    if op.upper() in {'LD', 'LDI', 'LEA', 'ST', 'STI'}:
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            is_reg_operand(operands[0], line_no, error)
        if not valid_operands(operands[1:], True, line_no, error):
            return
        else:
            is_label_or_offset_operand(operands[1], 9, line_no, error)
        valid_operands(operands[2:], False, line_no, error)

    if op.upper() in {'LDR', 'STR'}:
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            is_reg_operand(operands[0], line_no, error)
        if not valid_operands(operands[1:], True, line_no, error):
            return
        else:
            is_reg_operand(operands[1], line_no, error)
        if not valid_operands(operands[2:], True, line_no, error):
            return
        else:
            if is_number(operands[2]):
                offset6 = str2num(operands[2])
                if offset6 > 31 or offset6 < -32:
                    error.append('Line {}:{} can not be represented as a signed number in 6 bits'
                                 .format(line_no, offset6))
            else:
                error.append('Line {}:Expected 6 bit signed number, but found \'{}\' instead'
                             .format(line_no, operands[2]))
        valid_operands(operands[3:], False, line_no, error)

    if op.upper() in {'BRN', 'BRZ', 'BRP', 'BR', 'BRZP', 'BRNP',
                      'BRNZ', 'BRNZP', 'JSR'}:
        if op.upper() == 'JSR':
            is_label_or_offset_operand(operands[0], 11, line_no, error)
        else:
            is_label_or_offset_operand(operands[0], 9, line_no, error)
        valid_operands(operands[1:], False, line_no, error)

    if op.upper() in {'JSRR', 'JMP'}:
        if not valid_operands(operands, True, line_no, error):
            return
        else:
            is_reg_operand(operands[0], line_no, error)
        valid_operands(operands[1:], False, line_no, error)

    if op.upper() == 'TRAP':
        if is_number(operands[0]):
            vector8 = str2num(operands[0])
            if vector8 > 255 or vector8 < 0:
                error.append('Line {}:{} can not be represented as an 8 bit trap vector'
                             .format(line_no, vector8))
        else:
            error.append('Line {}:Expected 8 bit non-negative trap vector, but found \'{}\' instead'
                         .format(line_no, operands[0]))
        valid_operands(operands[1:], False, line_no, error)

    if op.upper() in {'RET', 'RTI', 'GETC', 'OUT', 'PUTS', 'IN',
                      'PUTSP', 'HALT'}:
        valid_operands(operands, False, line_no, error)


def valid_refer(refer, pcoffset, LC, line_no, error, symbol_table):
    if refer not in symbol_table:
        error.append('Line {}:Instruction references undefined label \'{}\''
                     .format(line_no, refer))
        return False
    else:
        offset = symbol_table[refer]['loc'] - (LC + 1)
        if offset > 2 ** (pcoffset - 1) - 1 or offset < -2 ** (pcoffset - 1):
            error.append('Line {}:Instruction references label \'{}\' that '
                         'cannot be represented in a {} bit signed PC offset'
                         .format(line_no, refer, pcoffset))
            return False
        else:
            return True


def convert(instrcution, LC, line_no, error, symbol_table):
    head = instrcution[0].upper()
    if head == '.ORIG':
        return [num2bin(str2num(instrcution[1]), 16, True)]
    if head == '.FILL':
        if is_label(instrcution[1]):
            if instrcution[1] not in symbol_table:
                error.append('Line {}:Instruction references undefined label \'{}\''
                             .format(line_no, instrcution[1]))
                return ['']
            else:
                return [num2bin(symbol_table[instrcution[1]['loc']], 16, False)]
        else:
            return [num2bin(str2num(instrcution[1]), 16, True)]
    if head == '.BLKW':
        loc_num = str2num(instrcution[1])
        return ['0' * 16] * (loc_num if loc_num >= 0 else 65536 + loc_num)
    if head == '.STRINGZ':
        return [num2bin(ord(char), 16, False) for char in is_string(instrcution[1])] + ['0' * 16]
    if head == 'ADD' or head.upper() == 'AND':
        return [Opcode[head] + num2bin(str2num(instrcution[1][1:]), 3, False) + \
                num2bin(str2num(instrcution[2][1:]), 3, False) + \
                ('1' + num2bin(str2num(instrcution[3]), 5, True) if is_number(instrcution[3])
                 else ('000' + num2bin(str2num(instrcution[3][1:]), 3, False)))]
    if head == 'NOT':
        return [Opcode[head] + num2bin(str2num(instrcution[1][1:]), 3, False) + \
                num2bin(str2num(instrcution[2][1:]), 3, False) + '1' * 6]
    if head in {'LD', 'LDI', 'LEA', 'ST', 'STI'}:
        if is_label(instrcution[2]):
            if not valid_refer(instrcution[2], 9, LC, line_no, error, symbol_table):
                return ''
            else:
                return [Opcode[head] + num2bin(str2num(instrcution[1][1:]), 3, False) + \
                        num2bin(symbol_table[instrcution[2]]['loc'] - (LC + 1), 9, True)]
        return [Opcode[head] + num2bin(str2num(instrcution[1][1:]), 3, False) + \
                num2bin(str2num(instrcution[2]), 9, True)]
    if head in {'LDR', 'STR'}:
        return [Opcode[head] + num2bin(str2num(instrcution[1][1:]), 3, False) + \
                num2bin(str2num(instrcution[2][1:]), 3, False) + \
                num2bin(str2num(instrcution[3]), 6, True)]
    if head in {'BRN', 'BRZ', 'BRP', 'BR', 'BRZP', 'BRNP', 'BRNZ', 'BRNZP'}:
        if is_label(instrcution[1]):
            if not valid_refer(instrcution[1], 9, LC, line_no, error, symbol_table):
                return ''
            else:
                return [Opcode[head] + num2bin(symbol_table[instrcution[1]]['loc'] - (LC + 1), 9, True)]
        else:
            return [Opcode[head] + num2bin(str2num(instrcution[1]), 9, True)]
    if head == 'JSR':
        if is_label(instrcution[1]):
            if not valid_refer(instrcution[1], 11, LC, line_no, error, symbol_table):
                return ''
            else:
                return [Opcode[head] + '1' + num2bin(symbol_table[instrcution[1]]['loc'] - (LC + 1), 11, True)]
        else:
            return [Opcode[head] + '1' + num2bin(str2num(instrcution[1]), 11, True)]
    if head in {'JSRR', 'JMP'}:
        return [Opcode[head] + '0' * 3 + num2bin(str2num(instrcution[1][1:]), 3, False) + '0' * 6]
    if head == 'TRAP':
        return [Opcode[head] + '0' * 4 + num2bin(str2num(instrcution[1]), 8, False)]
    if head in {'RET', 'RTI', 'GETC', 'OUT', 'PUTS', 'IN',
                'PUTSP', 'HALT'}:
        return [Opcode[head]]


def pass1(file):
    LC = [-1]  # Location Counter
    error = []
    symbol_table = dict()
    beyond_memory = False
    start = False
    instructions = []
    line_no = 0
    for idx, line in enumerate(file):
        line_no = idx + 1
        parse_result = parse_line(line)
        if parse_result is None:
            continue
        if LC[0] > 65535 and not beyond_memory:
            error.append('Line {}:Instruction uses memory beyond memory location xFFFF'
                         .format(line_no))
            beyond_memory = True
        leader = parse_result[0]
        if LC[0] == -1 and leader.upper() != '.ORIG' and not start:
            error.append('Line {}:Expected .ORIG, but found \'{}\' instead'
                         .format(line_no, leader))
            start = True
        if is_label(leader):
            valid_label(leader, line_no, error)
            if leader in symbol_table:
                error.append('Line {}:Duplicate label \'{}\' with label on line {}'
                             .format(line_no, leader, symbol_table[leader]['line']))
            symbol_table[leader] = {'loc': LC[0], 'line': line_no}
            instruction_part = parse_result[1:]
        else:
            instruction_part = parse_result
        if not instruction_part:
            error.append('Line {}:Expected opcode or pseudo_op after \'{}\', but found nothing'
                         .format(line_no, leader))
            continue
        instructions.append((line_no, LC[0], instruction_part))
        temp = instruction_part[0]
        if temp.upper() not in Opcode and temp not in Pseudo_ops:
            error.append('Line {}:Unrecognized opcode or pseudo_op at \'{}\''
                         .format(line_no, temp))
            continue
        if temp.upper() == '.END':
            return error, instructions, symbol_table
        operands = instruction_part[1:]
        if temp.upper() in Pseudo_ops:
            parse_po(temp, operands, LC, line_no, error)
        if temp.upper() in Opcode:
            parse_op(temp, operands, line_no, error)
            LC[0] += 1
    error.append('Line {}:Expected \'.END\' at end of file'.format(line_no))
    return error, instructions, symbol_table


def pass2(instructions, symbol_table):
    error = []
    results = []
    for line_no, LC, instrcution in instructions:
        result = convert(instrcution, LC, line_no, error, symbol_table)
        if result:
            results.extend(result)
    return error, results


def assemble(input_text):
    success = False
    results = []
    assemble_infos = ["Assembling...", "Starting Pass 1..."]
    error1, instructions, symbol_table = pass1(input_text)
    assemble_infos.extend(error1)
    assemble_infos.append('Pass 1 - {} error(s)'.format(len(error1)))
    if not error1:
        assemble_infos.append("Starting Pass 2...")
        error2, results = pass2(instructions, symbol_table)
        assemble_infos.extend(error2)
        assemble_infos.append('Pass 2 - {} error(s)'.format(len(error2)))
        if not error2:
            success = True
    return success, assemble_infos, results


def open_file(path):
    with open(path, 'r', encoding='utf-8') as asmfile:
        file = [line for line in asmfile]
    return file


def save_result(results, path):
    result_file = open(path, 'w', encoding='utf-8')
    for result in results:
        result_file.write(result + '\n')


if __name__ == "__main__":
    file_path = 'test/test.asm'
    input_text = open_file(file_path)
    no_error, infos, output_text = assemble(input_text)
    for info in infos:
        print(info)
    if no_error:
        save_result(output_text, 'test.bin')
