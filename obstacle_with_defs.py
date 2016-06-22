print "Running obstacle avoidance code."
# Import libraries.
import Lobsang, time, random, sys

# Initialise Lobsang.
Lobsang.begin()
# Point the head straight forward.
Lobsang.head.aim(1430, 1430)

# This becomes a map of the distances from the robot's head
# each time turn_optimum_distance() is run. Length 7.
dist_map = [0, 0, 0, 0, 0, 0, 0]

# This becomes a log of the distances from the robot's head
# over a number of cycles. If lots of the measurements are
# similar but the robot is driving forward, then it has
# probably got stuck on something it can't see. Length 10.
dist_log = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Number of loops per second- this is only approximate.
# Real loops per sec = 1 / LPS + time loop takes to complete.
LPS = 10.0

# This is the number of loops before the random direction
# checks begin again, but initially represented in seconds.
loops_before_recheck = 2
loops_before_recheck *= LPS # To get actual number of loops.

# Number of loops done so far.
loops_since_last_check = 0

# Sensitivity of stuckness noticing.
stuck_sensitivity = 8
similar_dists_in_log = 0

def almost_equal(val1, val2, max_difference):
	if (val1 - val2 < max_difference) and (val2 - val1 < max_difference):
		return True
	return False

def update_dist_log(current_ultrasonic_distance):
	global dist_log
	for i in range(len(dist_log) - 1, 0, -1):
		dist_log[i] = dist_log[i - 1]
	dist_log[0] = int(current_ultrasonic_distance)
	#print dist_log

def turn_optimum_direction():
	global dist_map, dist_log
	# Get rid of the old distance data in the log.
	dist_log = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	update_dist_log(Lobsang.sensors.distance())
	# Map the area in front - left to right.
	Lobsang.head.pan(1000)
	time.sleep(0.2)
	dist_count = 0
	# Loop through seven different measurements, each at different angles.
	for angle in range(1002, 2001, 166): # Ought to be (1000, 2001, 166.66...).
		Lobsang.head.pan(angle)
		time.sleep(0.15)
		dist_map[dist_count] = Lobsang.sensors.distance()
		dist_count += 1
	# Re-centre the head.
	Lobsang.head.pan(1430)
	# Print out the range of values
	#print dist_map
	
	# Work out which measurement is the greatest (furthest away)
	# so Lobsang avoids getting stuck in cramped areas.
	#
	# If two or more measurements are equal, the leftmost is
	# favoured purely due to the nature of the code. So turning
	# is slightly left-biased. This is very unlikely however, since
	# the ultrasonic code gives precision to the tenth of a millimetre.
	# Note that this is precision, not accuracy. An accurate tenth of a
	# millimetre measurement is impossible using the system as it is.
	furthest_dist = max(dist_map)
	# $turn_amount varies between 0 and 6 inclusive. So it has 7 possible values.
	turn_amount = 0
	for dist in dist_map:
		if dist == furthest_dist:
			break
		turn_amount += 1
	# $turn_duration varies between -0.6 and 0.6 incluse.
	turn_duration = turn_amount / 5 - 0.6
	print "Turn duration (right is negative):", turn_duration
	# Work out which way to turn from the nature of $turn_duration
	# (positive or negative) and change $turn duration to positive.
	if turn_duration > 0:
		Lobsang.wheels.both(-8, 8)
	elif turn_duration < 0:
		Lobsang.wheels.both(8, -8)
		turn_duration *= -1
	# Wait while Lobsang turns.
	time.sleep(turn_duration)
	# Stop turning.
	Lobsang.wheels.both(0)

print "Running avoidance loop."

try:
	turn_optimum_direction()
	while True: # Loop until told otherwise.
		cm = Lobsang.sensors.distance()
		update_dist_log(cm)
		similar_dists_in_log = 0
		for dist in dist_log[1:]:
			if almost_equal(dist_log[0], dist, stuck_sensitivity):
				similar_dists_in_log += 1
		if cm < 40:
			print "An obstacle is %icm away. Turning away." %int(cm)
			Lobsang.voice.say("There is an obstacle")
			loops_since_last_check = 0
			# Obstacle detected, so move back a bit.
			Lobsang.wheels.both(-9)
			time.sleep(1)
			# Stop moving.
			Lobsang.wheels.both(0)
			# Measure, compare, then turn to face the direction with the most forward movement available.
			turn_optimum_direction()
		
		elif similar_dists_in_log > 5:# (almost_equal(dist_log[0], dist_log[1], stuck_sensitivity)) and (almost_equal(dist_log[0], dist_log[2], stuck_sensitivity)) and (almost_equal(dist_log[0], dist_log[3], stuck_sensitivity)):
			#If there is a lot of similarity between 
			# the measurements over a space of time,
			# then the robot is probably stuck on
			# something low down it doesn't detect,
			# which causes the robot to not move forward.
			print "I think I'm stuck on something."
			print "dist_log =", dist_log
			Lobsang.voice.say("I think I am stuck")
			loops_since_last_check = 0
			# Obstacle detected, so move back a bit.
			Lobsang.wheels.both(-9)
			time.sleep(1)
			# Stop moving.
			Lobsang.wheels.both(0)
			# Measure, compare, then turn to face the direction with the most forward movement available.
			turn_optimum_direction()
		
		# Randomly recheck if the current direction still has the furthest distance.
		if loops_since_last_check > loops_before_recheck:
			if random.randint(0, 10) == 0: # One in ten chance.
				print "Decided to recheck optimum route."
				Lobsang.voice.say("Rechecking route")
				loops_since_last_check = 0
				Lobsang.wheels.both(0)
				turn_optimum_direction()
		
		else:
			loops_since_last_check += 1
			# Drive straight forward.
			Lobsang.wheels.both(12)
		time.sleep(1.0 / LPS)
except:
	# Ctrl+C or error in code.
	print "Halting obstacle avoidance code."
	Lobsang.quit()
