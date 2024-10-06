import file_parser as fp
import numpy as np
import wave_types as wt

patterns = {}
controllers = {'TIME':1}
DEBUG = False

def generate(file,SAMPLE_RATE):
    #define variables used throughout
    inst = fp.file_parser(file)
    generate.SAMPLE_RATE = SAMPLE_RATE
    generate.audio = [np.empty(0),np.empty(0)]
    generate.vol_sum = [np.empty(0),np.empty(0)]
    generate.vol_max = [np.empty(0),np.empty(0)]
    generate.channels = 0
    #call function that reads instructions
    execute_statements(inst)
    #mix
    generate.audio[0] /= generate.vol_sum[0]/generate.vol_max[0]
    generate.audio[1] /= generate.vol_sum[1]/generate.vol_max[1]
    return np.array(generate.audio).T,generate.channels #returns the audio in stereo form

def execute_statements(inst):
    while (inst.bounded()):
        statement = inst.next_arg()
        if (statement == '$'):
            #get name and type of statement
            type = inst.next_arg()
            name = inst.next_arg()
            if (DEBUG): print(f"checking statement \"{name}\" of type {type}")
            if (type == 'C'):
                if (DEBUG): print(f"creating new channel \"{name}\"")
                create_channel(inst)
            elif (type == 'P'):
                if (DEBUG): print(f"creating new pattern \"{name}\"")
                patterns[name] = inst.get_index()
                inst.next_statement()
            elif (type == 'W'):
                if (DEBUG): print(f"creating new wave \"{name}\"")
                create_wave(inst,name)
            else: print(f"UNEXPECTED TYPE {statement} (expected C,P,W).")
        else: print(f"UNEXPECTED CHARACTER {statement} (expected $).")

def create_wave(inst,name):
    commands = []
    while (inst.bounded_statement()):
        commands.append(inst.next_arg())
    wt.create_custom_wave(name,commands)

def set_controller(name,value):
    controllers[name] = value

def get_controller(name,single_value):
    val = controllers[name]
    if (type(val) is np.ndarray and single_value): val = val[0]
    return val

def create_channel(inst):
    curr_stack = [] #stack of breakpoints
    wave_type = 'NONE' #wave type, initialized to none
    create_channel.old_pos = 0 #keeps track of a wave's final value, used to prevent clicks
    create_channel.audio = [np.empty(0),np.empty(0)] #audio data for the current channel
    create_channel.vol_sum = [np.empty(0),np.empty(0)] #sum data for the current channel
    create_channel.vol_max = [np.empty(0),np.empty(0)] #max data for the current channel
    controllers['FREQ'] = 440
    controllers['LVOL'] = 0
    controllers['RVOL'] = 0
    while(inst.bounded_statement() or curr_stack):
        command = inst.next_arg()
        if (command == '~'):
            #set the wave type to the next argument
            create_channel.old_pos = 0
            wave_type = inst.next_arg()
            if (DEBUG): print(f"set wave to {wave_type}")
        elif (command == '>'):
            set_controller('FREQ',inst.next_note())
            if (DEBUG): print(f"set frequency to {controllers['FREQ']}")
        elif (command == '|'):
            volume_type = inst.next_arg()
            amp= inst.next_num()
            if ('L' in volume_type): set_controller('LVOL',amp)
            if ('R' in volume_type): set_controller('RVOL',amp)
            if (DEBUG): print(f"set {volume_type} volume to {amp}")
        elif (command == ','):
            #write audio using the specified duration
            time = inst.next_duration()
            write_audio(wave_type,time)
            if (DEBUG): print(f"wrote {time} seconds of audio")
        elif (command == '='):
            name = inst.next_arg()
            val = inst.next_any()
            set_controller(name,val)
            if (DEBUG): print(f"set {name} to {val}")
        elif (command == '"'):
            name = inst.next_arg()
            start_val = get_controller(name,True)
            end_val = inst.next_any()
            duration = inst.next_duration()
            set_controller(name,np.linspace(start_val,end_val,int(generate.SAMPLE_RATE*duration)))
            if (DEBUG): print(f"sliding {name} from {start_val} to {end_val} in {duration} seconds")
        elif (command == '&'):
            #append the current index to the stack
            index = inst.get_index()-1
            curr_stack.append(index)
            name = inst.next_arg()
            #go to the new breakpoint
            inst.set_index(patterns[name])
            if (DEBUG): print(f"jumping to pattern {name} (program will resume at breakpoint {index})")
        elif (command == '!'):
            address = inst.next_arg()
            wave = inst.next_arg()
            duration = inst.next_duration()
            set_controller(address,wt.generate_audio(wave,np.linspace(0,duration,int(duration*generate.SAMPLE_RATE))))
            if (DEBUG): print(f"applying wave {wave} to {address} for {duration} seconds")
        elif (command == '['):
            #create a new breakpoint, using the next number to determine how many iterations
            curr_stack.append([inst.get_index()-1,inst.next_num()])
        elif (command == ']'):
            #decrement the repeat value
            curr_stack[-1][1] -= 1
            #if that value is now 0, exit the loop
            if (curr_stack[-1][1] == 0): curr_stack.pop()
            #otherwise, go back to the previous breakpoint
            else: inst.set_index(curr_stack[-1][0])
        elif (command == '$'):
            #if we are no longer in the bounds of a statement, we have to jump to a breakpoint
            index = curr_stack.pop()
            inst.set_index(index)
            if (DEBUG): print(f"end of statement reached, jumping back to {index}")
    if (DEBUG): print('appending channel audio')
    if (generate.channels>0):
        channel_length = len(create_channel.audio[0])-len(generate.audio[0]) #get the length of the current audio data and the current channel
        if (channel_length != 0): #if the length isn't 0 then the lengths are uneven and we have a problem.
            if (channel_length>0): #the current channel is longer
                generate.audio = extend_channel(generate.audio,channel_length)
                generate.vol_sum = extend_channel(generate.vol_sum,channel_length)
                generate.vol_max = extend_channel(generate.vol_max,channel_length)
            else: #the current channel is shorter
                create_channel.audio = extend_channel(create_channel.audio,-channel_length)
                create_channel.vol_sum = extend_channel(create_channel.vol_sum,-channel_length)
                create_channel.vol_max = extend_channel(create_channel.vol_max,-channel_length)
        generate.audio += create_channel.audio
        generate.vol_sum += create_channel.vol_sum
        generate.vol_max = np.maximum(generate.vol_max,create_channel.vol_max)
    else:
        generate.audio = create_channel.audio
        generate.vol_sum = create_channel.vol_sum
        generate.vol_max = create_channel.vol_max
    generate.channels += 1
    if (DEBUG): 
        print('appending finished')
        if(inst.get_index()<0): print('index is negative, should terminate here.')
        else: print('resuming statements')

def extend_channel(channel,length):
    return [np.append(channel[0],np.full(shape=length,fill_value=0)),np.append(channel[1],np.full(shape=length,fill_value=0))]

def get_controller_snippet(name,time):
    if (DEBUG): print(f"getting controller \"{name}\"")
    value = get_controller(name,False) #get the controller
    if (type(value) == np.ndarray): #check if the controller is a range of values
        val_length = len(value) #get the length of values
        if (DEBUG): print(f"controller is range with length {val_length}")
        if (time<val_length): #check if the controller is longer than the expected size
            if (DEBUG): print('controller length is longer than anticipated')
            new_value = value[:time] #slide the value to the expected size
            set_controller(name,value[time:]) #save the remaining data to the controller
            return new_value #return the new value
        elif(time>val_length): #check if the value is less than the expected time
            if (DEBUG): print('controller length is shorter than anticipated')
            value = np.append(value,np.full(shape=time-val_length,fill_value=value[-1]))
        new_value = value
        set_controller(name,value[-1])
    else: 
        if (DEBUG): print('controller is single value')
        value = np.full(shape=time,fill_value=value)
    return value #if it's not a range return the constant, that'll be fine

def apply_frequency(sample_time,t):
    freq = get_controller('FREQ',False)
    if (type(freq) is np.ndarray):
        slide_end = len(freq) #get the length of the slide
        time_diff = sample_time - slide_end #determine if the slide is longer or shorter than the sample time
        start_freq = freq[0] #get start frequency
        end_freq = freq[-1] #get end frequency
        freq = get_controller_snippet('FREQ',sample_time) #correct the length of the slide
        
        if (time_diff<0): 
            end_freq = freq[-1] #get end frequency
            slide_end = sample_time
        slide_fix = np.append(np.linspace(0,(start_freq-end_freq)/2,slide_end),np.full(shape=sample_time-slide_end,fill_value=0))
        freq += slide_fix
        t *= freq
        
        if (time_diff>0):
            t_fix = np.append(np.full(shape=slide_end,fill_value=0),np.full(shape=sample_time-slide_end,fill_value=t[slide_end-1]-t[slide_end]))
            t += t_fix
    else: t *= freq
    return t

def get_noise_frequency(sample_time):
    freq = get_controller_snippet('FREQ',sample_time) #get the controller
    freq /= 15804.2656402
    return freq

def write_audio(wave_type,time):
    sample_time = int(generate.SAMPLE_RATE*time)
    if (wave_type=='NONE'):
        wave_data = np.full(shape=sample_time,fill_value=0)
    elif (wave_type=='NOISE'):
        wave_data = wt.noise(get_noise_frequency(sample_time),sample_time)
    else:
        t = apply_frequency(sample_time,np.linspace(0,time,sample_time))
        t += create_channel.old_pos #add the offset to prevent clicks
        create_channel.old_pos = t[-1]%1 #save the offset for the next note
        wave_data = wt.generate_audio(wave_type,t) #generate audio
    left_volume = get_controller_snippet('LVOL',sample_time)
    right_volume = get_controller_snippet('RVOL',sample_time)
    create_channel.audio[0] = np.append(create_channel.audio[0],left_volume*wave_data) #append audio to left channel
    create_channel.audio[1] = np.append(create_channel.audio[1],right_volume*wave_data) #append audio to right channel
    create_channel.vol_sum[0] = np.append(create_channel.vol_sum[0],left_volume)
    create_channel.vol_sum[1] = np.append(create_channel.vol_sum[1],right_volume)
    create_channel.vol_max[0] = np.append(create_channel.vol_max[0],left_volume)
    create_channel.vol_max[1] = np.append(create_channel.vol_max[1],right_volume)