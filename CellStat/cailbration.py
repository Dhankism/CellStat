#cailbration
# place all cailbration resistance and ressitance and capcitor values here 

KOHM=1000

CurrentRange= ["±2.5mA", "±.25mA", "±25uA", "±2.5uA", "±.25uA", "±72uA", "±25nA", "±2.5nA"]
ResistorValues = [value*KOHM for value in [1, 10, 100, 1000, 10000, 30000, 100000, 1000000]]
CapacitorLabels = ["2p", "20p", "50p", "100p", "200p", "1n", "50n", "100n"]
CapacitorValues = [2e-9, 20e-9,  50e-9, 100e-9, 200e-9, 1e-6, 50e-6, 100e-6]

ADC_OFFSET = [2050,       2044,       2045,       2044,       2043,       2043,       2044,       2041      ]
ADC_QUANT =  [0.00000254, 0.00001368, 0.00001292, 0.00002118, 0.00001449, 0.00007420, 0.00001234, 0.00022089]

DAC_QUANT = 1./828.33
DAC_OFFSET = 2069.6
ADC_QUANT = 3.3 / 4095
CONV_COEFF = 1.51  # Inverse of the output voltage divider
GAIN = -1.0 

