import Adafruit_GPIO.I2C as I2C
import time
import Image
import ImageFont
import ImageDraw
from types import StringType

# Constants: OLED commands
address = 0x3C
on = 0xAF
off = 0xAE
invert = 0xA7
no_invert = 0xA6
vertical_flip = 0xC8
no_vertical_flip = 0xC0
all_on = 0xA5
no_all_on = 0xA4
set_brightness = 0x81
set_column = 0x21
set_page = 0x22
set_high_column = 0x00
set_low_column = 0x10
set_start_line = 0x40
set_vertical_offset = 0xD3 # the number of pixels to wrap picture down

port = I2C.get_i2c_device(address)

buffer = Image.new('1', (128, 64))
temp_buffer = Image.new('1', (128, 64))
console_buffer = Image.new('1', (128, 64))
draw = ImageDraw.Draw(buffer)
console_draw = ImageDraw.Draw(console_buffer)
font8 = ImageFont.truetype("Minecraftia.ttf", 8)
font16 = ImageFont.truetype("Minecraftia.ttf", 16)
font24 = ImageFont.truetype("Minecraftia.ttf", 24)
font = font8 # font to actually display with. can be changed to font8/16/24
font_size = 8
old_cursor_line = 0

def command(hex):
	'''Sends hexadecimal value to OLED as a command eg. Oled.on.'''
	port.write8(0x00, hex)

def data(hex):
	'''Sends hexadecimal value to OLED as data.'''
	port.write8(0x40, hex)

def brightness(val):
	'''Set screen brightness.'''
	command(set_brightness)
	command(val)

def slide_up(speed):
	'''Takes current buffer and scrolls it up y axis from 100% y offset. Nice smooth animation.'''
	for i in range(64):
		command(0xA8) # offset mode
		command(i)
		time.sleep(speed / 64.0)

def set_cursor(x, y):
	'''Set cursor position.'''
	m_col = x + 2
	m_row = y
	command(0xb0 + m_row)
	command(m_col & 0xf) # set lower column address
	command(0x10 | (m_col >> 4)) # set higher column address

def clear():
	'''Clears buffer and screen.'''
	global buffer, old_cursor_line
	old_cursor_line = 0
	draw.rectangle((0,0,127,63), outline=0, fill=0) # draw black rectangle over whole buffer image
	refresh()

def clear_buffer():
	'''Clears buffer but not screen.'''
	global buffer, old_cursor_line
	old_cursor_line = 0
	draw.rectangle((0,0,127,63), outline=0, fill=0) # draw black rectangle over whole buffer image

def refresh(blackout=True):
	'''Writes buffer to screen. Quite slow.'''
	pix = buffer.load() # load buffer image
	temp_buffer = [] # to store 32 bytes temporarily
	if blackout: command(off) # have a blank (off) screen while it is updated, for smoother transition
	for page in range(8): # for each (128x8) page:
		set_cursor(0, page) # go to beginning of line
		for x in range(128): # for each vertical line of 8 pixels in page:
			bits = 0 # to store a byte temporarily
			for bit in [0, 1, 2, 3, 4, 5, 6, 7]: # find each byte of data from buffer to send to oled
				bits = bits << 1 # prepare for next bit from buffer
				bits |= 0 if pix[(x, page*8+7-bit)] == 0 else 1 # add bit from buffer
			temp_buffer.append(bits)
			if len(temp_buffer) == 32: # ready to send next batch of data to oled (32 bytes)
				port.writeList(0x40, temp_buffer)
				temp_buffer = []
	if blackout: command(on) # after updating, switch screen back on (for smoother transition)

def open(img):
	'''Open an image for writing to screen, but don't do anything with it.'''
	return Image.open(img).convert('1')

def render(img, pos=(0,0)):
	'''Loads and displays an image at coords $pos with filename $img.'''
	if isinstance(img, StringType): # if $img is a string, load then display file. otherwise (image already loaded) go ahead and display
		img = Image.open(img).convert("1")
	else:
		img = img.convert("1")
        draw.bitmap(pos, img, 1)

def screenshot(name=None):
	'''Saves buffer to image file.'''
	if name == None:
		name = "oled_screenshot_"+ str(int(time.time())) +".bmp"
	buffer.save(name)

def _stream():
	'''For debugging. Not for general use. Sends user defined hexadecimal commands through I2C.'''
	while True:
		byte = raw_input()
		byte = int(byte)
		if byte == 256:
			clear()
		else:
			 data(byte)

def set_pixel((x, y), val):
	'''Sets single pixel to $val (1 or 0) but does not refresh screen.'''
        global buffer
        page = int(y) / 8 # which page is the pixel in? 0 to 7
        page_pos = y % 8 # what's left over after dividing by 8? this is the position of the pixel in the page
        if val == 1: # if told to set pixel to on
                buffer[page][x] = 1#buffer[page][x] | (1 << page_pos) # set bit with mask and bitwise OR
        elif val == 0: # if told to set pixel to off
                buffer[page][x] = 0#buffer[page][x] & ~(1 << page_pos) # negative mask: all on except bit to unset

def get_pixel((x, y)):
	'''Gets single pixel value (1 or 0) from buffer (NOT screen!).'''
        global buffer
        page = int(y) / 8 # which page is the pixel in? 0 to 7
        page_pos = y % 8 # what's left over after dividing by 8? this is the position of the pixel in the page
        return(buffer[page][x] & (1 << page_pos))

def set_font_size(size):
	'''Sets font size to 8px, 16px or 24px.'''
	global font_size, font, font8, font16, font24
	if size == 16:
		font = font16
		font_size = 16
	elif size == 24:
		font = font24
		font_size = 24
	else: # catch wrong font sizes and size = 8
		font = font8 # default size
		font_size = 8

def splashscreen():
	command(off)
	clear_buffer()
	render("lobsang_beta.bmp", pos=(6, 9))
	refresh()
	command(on)

def write(string, pos=None, epos=None, size=8):
	'''Writes a string to the buffer. Can position start of string,\r\n
	   create (invisible) box to write into (hit right hand \r\n
	   wall = newline so text stays in box) and set font size.'''
	# TODO: This is very messy and unpythonic. Rework it entirely, and make it much better.
	global font, font_size, font8, font16, font24, old_cursor_line, buffer
	if size == 16:
		font = font16
		font_size = 16
	elif size == 24:
		font = font24
		font_size = 24
	else: # catch wrong font sizes and size = 8
		font = font8 # default size
		font_size = 8
	if pos == None:
		pos = (0, old_cursor_line)
	if epos != None: # max right and bottom values specified
		limit_x, limit_y = epos
	else:
		limit_x, limit_y = 127, 63
	string_x, string_y = pos # top left corner of the text render area
	string_width, string_height = draw.textsize(string, font=font) # width and height of string on screen
	end_x = string_x + string_width # right edge of text render area, using literal screen coords
	end_y = string_y + string_height - 2 # bottom edge of text render area, using literal screen coords
	newline = 0#font_size / 8 + 1 # space between line and line below
	
	if end_x <= limit_x: # string can be written with no problems
		draw.rectangle((string_x, string_y + 1, end_x, end_y), outline=0, fill=0)
		draw.text(pos, string, font=font, fill=255)
		old_cursor_line = string_y + string_height - 2
	else: # string to write would go over the right hand edge of the screen / limit area
		if " " in string: # can you wrap text? or is it only one word?
			words = string.split(" ") # individual words
			for i in range(string.count(" "), 1, -1): # between the number of spaces in text and 1. reverse iteration
				temp_x, temp_y = draw.textsize(" ".join(words[:i]), font=font) # temporary width + height check variables
				temp_y -= 2
				if string_x + temp_x <= limit_x: # if text is no longer too long (x start pos on screen + current string width <= max width)
					string = " ".join(words[:i]) # join the string back together, leaving off the too long bit
					next_string = " ".join(words[i:]) # the too long bit (to be written one line down)
					##############
					draw.rectangle((string_x, string_y + 1, string_x + temp_x, string_y + temp_y), outline = 0, fill = 0)
					draw.text(pos, string, font=font, fill=255) # draw the text to the buffer
					write(next_string, (string_x, end_y), (limit_x, limit_y), font_size) # write the rest- this is the same function again (this one) so it will check again for too long string
					break # don't keep looping, you'll end up writing wrong shorter strings
		else: # one long word
			for i in range(len(string), 1, -1):
				word = string[:i] # cut off the end
				temp_x, temp_y = draw.textsize(word, font=font)
				if temp_x <= limit_x:
					draw.rectangle((string_x, string_y, string_x + x, string_y + y), outline = 0, fill = 0)
					draw.text(pos, word, font=font, fill=255)
					write(string[i:], (string_x, string_y + font_size + newline), (limit_x, limit_y), font_size) # write the rest
					break
