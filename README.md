Code reads a "song.sn" file and generates a "thesound.wav" file.

.sn file format:
```
All spaces and newline characters are ignored.

Files consist of a series of statements. Statements take the following form:
$STATEMENT_TYPE:STATEMENT_NAME:...
Where the statement type affects the following syntax.

There are 3 supported statement types:
C - channel statement: Contains instructions that generate audio.
P - pattern statement: Constains a reusable set of instructions for generating audio that can be referenced using the statement name.
W - wave statement: Contains an expression for a custom wave type that can be referenced using the statement name.

Channel and pattern statements use the same set of instructions.
~NAME - Sets the current wave type. Can be a predefined wave type or a custom wave defined in a previous statement. The default wave types are:
  - NONE (default)
  - SINE
  - TRIG
  - SQR
  - SAW
  - NOISE
>NOTE - Sets the current frequency for the channel.
  A NOTE consists of a letter (C-B), an optional # symbol and the octave.
  A NOTE can also be appended with a ^ symbol followed by an integer or controller, which can be used to transpose notes.
  Frequency can also be set with a float
|CHANNELS:AMP - Sets the volume of the specified channels (L for left channel, R for right channel, LR for both) to the AMP specified.
,DURATION - Generates audio for the time specified.
  A DURATION can either be a float or an INTERVAL.
  An INTERVAL consists of 2 integers on either side of a / symbol.
=NAME:VALUE - sets the value of a specified controller. Predefined controllers include:
  - TIME: The length of a 1/1 interval in seconds
  - FREQ: The frequency of the channel
  - LVOL: The volume of the left channel
  - RVOL: The volume of the right channel
"NAME:END_VAL:DURATION - Linearly interpolates the value of a controller from its current value to a new value over a given duration.
&NAME - Jumps to the instructions defined by the pattern name specified before resuming the rest of the instructions.
!ADDRESS:WAVE:DURATION - Applies a wave to an address for a given duration.
  Addresses begin with a @ symbol followed by a name. Seemingly another way to reference controllers.
[NUMBER ...] - Repeat the instructions inside for the specified number of iterations.


Wave statements define expressions using a series of operations and numbers seperated by the delimiter :. The expression is postfix.

The following values are pushed onto a stack:
T - special input variable, represents the position within a wave. 
@NAME - references a controller value
float - numerical value

The remaining are operations that remove values from the stack and push their results on top:
ADD - adds the top two values on the stack
SUB - subtracts the top value from the second top value
DIV - divides the second top value by the top value
PROD - multiplies the top two values on the stack
MOD - gets the remainder using the top value as the dividend and the second top value as the divisor
ABS - gets the absolute value of the top value
SIGN - gets the sign of the top value

Waves can also be referenced by name, in which case the top stack value is used as the T value for the wave and the resulting amplitude is pushed onto the stack.
```
