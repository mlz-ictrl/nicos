description = 'Switching the Optic tool to different rough positions'

includes = ['virtual_optic_motors']

group = 'lowlevel'

devices = dict(
	optic_tool_switch = device('nicos_tuw.xccm.devices.optic_tool_switch.OpticToolSwitch',
		description = 'change the position of the optics from between beam and sample to between sample and detector (or vice versa)',
		moveables = ['opt_Tx','opt_Ty','opt_Rz'],
		mapping = {
            		1: [10, 10, 0],
            		2: [40, 60, 90],
            		3: [90, 10, 0],
            	},
		precision = [10, 10, 30],
#higher precision values to allow finetuning of position to user
	),
)
