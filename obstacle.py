# Import libraries.
import Lobsang
import time

# Initialise Lobsang.
Lobsang.begin()
# Point the head straight forward.
Lobsang.head.aim(1430, 1430)

# This becomes a map of the distances from the robot's head.
dist_map = [0, 0, 0, 0, 0, 0, 0]

try:
	while True:
		# Loop until told otherwise.
		cm = Lobsang.sensors.distance()
		if cm < 40:
			# Obstacle detected, so move back a bit.
			Lobsang.wheels.both(-9)
			time.sleep(1)
			# Stop moving.
			Lobsang.wheels.both(0)
			# Map the area in front - left to right.
			Lobsang.head.pan(1000)
			time.sleep(0.2)
			dist_count = 0
			# Loop through seven different measurements, each at different angles.
			for angle in range(1000, 2001, 142):
				Lobsang.head.pan(angle)
				time.sleep(0.1)
				dist_map[dist_count] = Lobsang.sensors.distance()
				dist_count += 1
			# Re-centre the head.
			Lobsang.head.pan(1430)
			# Print out the range of values
			print dist_map
			
			# Work out which measurement is the greatest (furthest away)
			# so Lobsang avoids getting stuck in cramped areas.
			# If two or more measurements are equal, the leftmost is
			# favoured purely due to the nature of the code. So turning
			# is slightly left-biased.
			furthest_dist = max(dist_map)
			# $turn_amount varies between 0 and 6 inclusive. So it has 7 possible values.
			turn_amount = 0
			for dist in dist_map:
				if dist == furthest_dist:
					break
				turn_amount += 1
			# $turn_duration varies between -0.7 and 0.7 incluse. It has 13 possible values.
			turn_duration = turn_amount / 4.285 - 0.7
			# Work out which way to turn from the nature of $turn_duration
			# (positive or negative) and then change $turn duration to positive.
			if turn_duration > 0:
				Lobsang.wheels.both(-8, 8)
			elif turn_duration < 0:
				Lobsang.wheels.both(8, -8)
				turn_duration *= -1
			# Wait while Lobsang turns.
			time.sleep(turn_duration)
			# Ready to loop obstacle avoidance again.
			Lobsang.wheels.both(0)
		else:
			# All clear ahead. Drive forward.
			Lobsang.wheels.both(12)
except:
	# Ctrl+C or error in code.
	Lobsang.quit()
