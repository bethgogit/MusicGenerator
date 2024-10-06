import wave_constructor as wc
#this class is used to read through a set of instructions from a given file
class file_parser:
    inst = ['']
    
    #defines the instruction list
    def __init__(self,file):
        #get instructions
        inst_string = ""
        #open the file containing the instructions
        file = open("song.sn","r")
        for l in file.readlines():
            #add each line to the instruction variable, removing any newline characters
            inst_string += l.rstrip()
        file.close()
        #remove spaces in file
        inst_string = inst_string.replace(" ","")
        #set of valid instructions
        OPERATORS = ['~','>','|',',','=','"','&','[',']','$',':','!']
        for c in inst_string:
            #if the character is an operator...
            if c in OPERATORS:
                #if the instruction isn't empty, append a new item to the list
                if (self.inst[0]): self.inst.insert(0,'')
                if (c != ':'):
                    #if the character isn't a delimiter, append the instruction and add a new blank
                    self.inst[0] = c
                    self.inst.insert(0,'')
            else:
                #otherwise append the character to the current instruction
                self.inst[0] += c
        if (self.inst[0] == ''): self.inst.pop(0)
        self.curr = len(self.inst)-1
    
    #ensures the current index isn't out of bounds
    def bounded(self):
        return self.curr >= 0
    
    #similar to bounded except it also checks the current character is not a $
    def bounded_statement(self):
        return self.bounded() and self.inst[self.curr] != '$'
    
    #returns the current index
    def get_index(self):
        return self.curr
    
    #sets the current index
    def set_index(self,index):
        self.curr = index
    
    #returns the next character available
    def next_arg(self):
        self.curr -= 1
        return self.inst[self.curr+1]
    
    #returns the position of the next statement, or -1 if the end of the file is reached
    def next_statement(self):
        while (self.inst[self.curr] != '$' and self.bounded()): self.curr -= 1
    
    def next_num(self):
        return get_type(self.next_arg(),('ADDR','FLOAT'))
    
    def next_note(self):
        return get_type(self.next_arg(),('TRNSP','NOTE','FLOAT'))
        
    def next_duration(self):
        return get_type(self.next_arg(),('FRAC','ADDR','FLOAT'))
    
    def next_any(self):
        return get_type(self.next_arg(),('FRAC','TRNSP','ADDR','NOTE','FLOAT'))

def get_type(val,types):
    if ('FRAC' in types and '/' in val):
        #returns a fraction given two values multiplied by the time
        delim_index = val.index('/')
        num = get_type(val[:delim_index],('FLOAT','ADDR'))
        denom = get_type(val[delim_index+1:],('FLOAT','ADDR'))
        return wc.controllers['TIME']*num/denom
    elif ('TRNSP' in types and '^' in val):
        #returns a note transposed by some value
        delim_index = val.index('^')
        note = val[:delim_index]
        shift = get_type(val[delim_index+1:],('FLOAT','ADDR'))
        return get_freq(note,shift)
    #returns the value from some address
    elif ('ADDR' in types and val[0]=='@'): 
        return wc.controllers[val[1:]]
    #returns a float. note that this crashes if the value isn't a note
    elif ('FLOAT' in types and val.replace('.','').replace('-','').isdigit()): return float(val)
    #returns the frequency of a given note
    elif ('NOTE' in types): return get_freq(val,0)

def get_freq(note,shift):
    num = 2*ord(note[0])
    if (num>138): num -= 1
    num = (num-4)%13
    octave_index = 1
    if (note[1]=='#'): 
        num += 1
        octave_index += 1
    num += shift
    num = num/12+int(note[octave_index])
    return 2**num*16.3515978313
  