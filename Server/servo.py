

import time

# Default constants
DEFAULT_FREQ        = 50.0    # Default frequency in Hertz for PWM signal
MIN_PULSE_WIDTH     = 550.0   # The shortest pulse
MAX_PULSE_WIDTH     = 2500.0  # The longest pulse
NEUTRAL_PULSE_WIDTH = 1500.0  # Neutral pulse sent


def changemode():
	global y
	y=0

def mapValue(value, in_min, in_max, out_min, out_max):
    """
    Returns a new value mapped in a desired range.
    Parameters:
        value: value to be mapped
        in_min - in_max: limits of the range where the value is
        out_min - out_max: limits of the range where the value will be mapped
    """

    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

###############
# Servo Class #
###############

class Servo:
    def __init__(self, name = "myServo", minWidth = MIN_PULSE_WIDTH, maxWidth = MAX_PULSE_WIDTH, frequency = DEFAULT_FREQ):
        """
        Initialize a new servo object.
        Parameters:
            name: servo name for future references.
            minWidth: minimum limit for the servo pulse width. By default 550usec.
            maxWidth: maximum limit for the servo pulse width. By default 2500usec.
            frequency: frequency of PWM signal. By default 50Hz.
        """
        self._name = name
        self._pinAttached = None
        self._pwm = None
        self._minWidth = minWidth
        self._maxWidth = maxWidth
        self._frequency = frequency
        self._period = round(1.0/frequency,4)
        self._uSecs = mapValue(90, 0, 180, self._minWidth, self._maxWidth)

    def __str__(self):
        """
        Returns the current servo motor settings.
        """

        return "Servo reference name: " + self.getName() + "\n" \
                + "Pin attached: " + str(self.getPin()) + "\n" \
                + "Range width (uSec): [" + str(self.getPulseWidth()[0]) + ", " + str(self.getPulseWidth()[1]) + "]" + "\n" \
                + "Frequency: " + str(self.getFrequency()) + "Hz" + "\n" \
                + "Period: " + str(self.getPeriod()) + "sec" + "\n" \
                + "Pulse width: " + str(self.readMicroseconds()) + "uSec" + "\n" \
                + "Angle set: " + str(self.read())

    def attach(self, pin):
        """
        Attaches a servo motor to a PWM pin.
        Parameters:
            pin: pin where the servo motor will be attached. Currently only pins 3, 5, 6, and 9 are supported.
        """

        if pin in [3, 5, 6, 9]:
            self._pinAttached = pin
        else:
            while True: # Keep asking for a valid pin.
                print "The pin '" + str(pin) + "' is not a valid input. The valid pins are 3, 5, 6 or 9."
                pin = raw_input("Select a valid pin: ")
                if pin in ["3", "5", "6", "9"]:
                    pin = int(pin)
                    self._pinAttached = pin
                    break

        # Configure the selected pin as PWM output.
        if self._pinAttached != None:
            self._pwm = mraa.Pwm(self._pinAttached)
            self._pwm.period(self._period)
            self._pwm.enable(True)
            self._pwm.write((self._uSecs/1000000.0)/self._period)

    def writeMicroseconds(self, uSecs):
        """
        Sets the servo pulse width in microseconds.
        Parameters:
            uSecs: pulse width in microseconds.
        """

        # Check if the input value is in the valid range.
        if uSecs < self._minWidth:
            uSecs = self._minWidth
        if uSecs > self._maxWidth:
            uSecs = self._maxWidth

        self._uSecs = uSecs

        if self._pwm != None:
            self._pwm.write((self._uSecs/1000000.0)/self._period)

    def write(self, angle):
        """
        Sets the servo angle in degrees.
        Parameters:
            angle: position as an angle in degrees.
        """

        # Check if the angle is between 0 and 180.
        if angle < 0:
            angle = 0
        if angle > 180:
            angle = 180

        self.writeMicroseconds(mapValue(angle, 0, 180, self._minWidth, self._maxWidth))

    def readMicroseconds(self):
        """
        Returns the last written servo pulse width in microseconds.
        """

        return self._uSecs

    def read(self):
        """
        Returns the last written servo pulse width as an angle between 0 and 180.
        """

        return mapValue(self._uSecs, self._minWidth, self._maxWidth, 0, 180)

    def getName(self):
        """
        Returns the reference name of the servo motor.
        """

        return self._name

    def getPin(self):
        """
        Returns the pin where the servo motor is attached.
        """

        return self._pinAttached

    def getPulseWidth(self):
        """
        Returns the current limits for the servo pulse width.
        """

        return [self._minWidth, self._maxWidth]

    def getFrequency(self):
        """
        Returns the current frequency.
        """

        return self._frequency

    def getPeriod(self):
        """
        Returns the current period.
        """

        return self._period

    def setWidth(self, minWidth, maxWidth):
        """
        Sets new values for the limits of the servo pulse width.
        Parameters:
            minWidth: new minimum limit for the servo pulse width.
            maxWidth: new maximum limit for the servo pulse width.
        """

        self._minWidth = minWidth
        self._maxWidth = maxWidth

    def setFrequency(self, frequency):
        """
        Sets a new value for frequency.
        Parameters:
            frequency: new frequency of PWM signal.
        """

        # Sets frequency and then period.
        self._frequency = frequency
        self._period = round(1.0/frequency,4)
        self._pwm.period(self._period)

    def setPeriod(self, period):
        """
        Sets a new value for period.
        Parameters:
            period: new period of PWM signal.
        """

        # Sets period and then frequency
        self._period = period
        self._pwm.period(self._period)
        self._frequency = round(1/period,4)


# Create a new servo object with a reference name
myServo = Servo("First Servo")

	# Attaches the servo to pin 3 in Arduino Expansion board
myServo.attach(3)


def autofanon():
	global myServo
	global y
	y=1
	temp=grove.GroveTemp(0)
	roomtemp=19
	avg=0
	for i in range(0,10):
		celsius = temp.value()
		avg=(celsius+avg*2)/2
		fahrenheit= celsius*9.0/5.0 +32.0;
		print "%d degrees celsius, or %d degrees Fahrenheit " %(celsius, fahrenheit)
		time.sleep(1)
	if avg>roomtemp:
		print "Switch on the AC or increase fan speed"
		try:
			# Sweeps the servo motor until it is turned off
			while y==1:
				# From 0 to 180 degrees
				for angle in range(0,180):
						myServo.write(angle)
						time.sleep(0.005)

				# From 180 to 0 degrees
				for angle in range(180,-1,-1):
						myServo.write(angle)
						time.sleep(0.005)

		except KeyboardInterrupt:
				print "Sweep ended."

	else :
		print "Switch off the AC or decrease fan speed"
	del temp


def fanon():
	changemode()
	print "Fan on"
	global y
	y=1

	while y==1:
				# From 0 to 180 degrees
		for angle in range(0,180):
			myServo.write(angle)
			time.sleep(0.005)

				# From 180 to 0 degrees
		for angle in range(180,-1,-1):
			myServo.write(angle)
			time.sleep(0.005)



def fanoff():
	changemode()
	global myServo
	myServo.write(0)
	print "Fan off"
