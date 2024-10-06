import numpy as np
import wave_constructor as wc

custom_waves = {}

def create_custom_wave(name,commands):
    custom_waves[name] = commands

def noise(f,t):
    vals = np.empty(shape=t)
    pos = 1
    for i in range(t):
        if (pos>=1):
            amp = np.random.uniform(-1,1)
            pos -= 1
        vals[i] = amp
        pos += f[i]
    return vals

def sine(x):
    return np.sin(2*np.pi*x)

def sawtooth(x):
    return 1-x%1*2

def triangle(x):
    return 1-abs(2-(4*x+1)%4)

def square(x):
    return np.sign(0.5-x%1)

def generate_audio(wave_type,t):
    if (wave_type=='SINE'): 
        if (wc.DEBUG): print('generating sine wave')
        return sine(t)
    elif (wave_type=='SQR'): 
        if (wc.DEBUG): print('generating square wave')
        return square(t)
    elif (wave_type=='TRIG'):
        if (wc.DEBUG): print('generating triangle wave')
        return triangle(t)
    elif (wave_type=='SAW'): 
        if (wc.DEBUG): print('generating sawtooth wave')
        return sawtooth(t)
    else: 
        if (wc.DEBUG): print(f"generating custom wave type \"{wave_type}\"")
        return generate_custom_audio(wave_type,t)

def generate_custom_audio(wave_type,t):
    commands = custom_waves[wave_type]
    num_stack = []
    for c in commands:
        if (c=='T'): 
            if (wc.DEBUG): print('adding T to the stack')
            num_stack.append(np.copy(t))
        elif (c[0]=='@'): 
            if (wc.DEBUG): print(f"adding controller {c} to the stack")
            num_stack.append(wc.get_controller_snippet(c[1:],len(t)))
        elif (c.replace('.','').replace('-','').isdigit()): 
            if (wc.DEBUG): print(f"adding {float(c)} to the stack")
            num_stack.append(float(c))
        elif (c=='ADD'):
            op2 = num_stack.pop()
            op1 = num_stack.pop()
            if (wc.DEBUG): print(f"adding {op2} to {op1}")
            num_stack.append(op1+op2)
        elif (c=='SUB'):
            op2 = num_stack.pop()
            op1 = num_stack.pop()
            if (wc.DEBUG): print(f"subtracting {op2} from {op1}")
            num_stack.append(op1-op2)
        elif (c=='DIV'):
            op2 = num_stack.pop()
            op1 = num_stack.pop()
            if (wc.DEBUG): print(f"dividing {op1} by {op2}")
            num_stack.append(op1/op2)
        elif (c=='PROD'):
            op2 = num_stack.pop()
            op1 = num_stack.pop()
            if (wc.DEBUG): print(f"multiplying {op1} by {op2}")
            num_stack.append(op1*op2)
        elif (c=='MOD'):
            op2 = num_stack.pop()
            op1 = num_stack.pop()
            if (wc.DEBUG): print(f"getting the modulus of {op1} and {op2}")
            num_stack.append(op1%op2)
        elif (c=='ABS'):
            if (wc.DEBUG): print(f"adding absolute value to {num_stack[-1]}")
            num_stack[-1] = abs(num_stack[-1])
        elif (c=='SIGN'):
            if (wc.DEBUG): print(f"applying sign to {num_stack[-1]}")
            num_stack[-1] = np.sign(num_stack[-1])
        else:
            if (wc.DEBUG): print(f"unknown command, interpreting {c} as wave")
            num_stack[-1] = generate_audio(c,num_stack[-1])
    return num_stack[0]
        
        
    