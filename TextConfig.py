# Here are the main variables for a text editor

font = ('courser', 9, 'normal')  # Initial font and size

# Initial color
bg = 'white'
fg = 'black'

# Initial size
height = 20
width = 80

# Case sensitivity
caseinses = True  # Start included

open_ask_user = True  # If true, then creature the request
open_encoding = ''  # If empty, then the encoding will be 'latin-1' or 'cp500'
save_use_know_encoding = 1  # If > 0, then trying made to apply
# Encoding known from the last operation
save_ask_user = True  # If it's true, last made request user
save_encoding = ''  # If it's not empty, then will be 'utf-8'
