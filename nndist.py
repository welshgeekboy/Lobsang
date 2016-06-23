print "Importing..."
from pybrain.supervised.trainers	import BackpropTrainer
from pybrain.datasets 			import SupervisedDataSet
from pybrain.tools.shortcuts		import buildNetwork
from pybrain.structure			import TanhLayer
import Lobsang
Lobsang.begin()
#Lobsang.wheels.calibrate_speeds(-0.8)
Lobsang.head.aim(1430, 1430)

print "Setting up..."
'''ds = SupervisedDataSet(1, 2)
ds.addSample((2,), (-6, -6))
ds.addSample((4,), (-4, -4))
ds.addSample((6,), (0, 0))
ds.addSample((8,), (4, 4))
ds.addSample((10,), (6, 6))'''

ds = SupervisedDataSet(1, 1)
ds.loadFromFile("nndist.ds")

ds.addSample((2,), (-9,))
ds.addSample((4,), (-6,))
ds.addSample((6,),  (6,))
ds.addSample((8,),  (9,))
ds.addSample((10,), (12,))

net = buildNetwork(1, 5, 1, bias=True, hiddenclass=TanhLayer)
trainer = BackpropTrainer(net, ds)

loop_count = 0
train_count = 0
try:
	print "Training 1000 times..."
	while train_count < 1000:
		for i in range(100):
			trainer.train()
		train_count += 100
		print "Trains:", train_count
		print "Error:", trainer.train()
		print " "
	
	print "Running movement loop..."
	while True:
		try:
			for i in range(9):
				trainer.train()
				train_count += 1
			print "Error:", trainer.train()
			train_count += 1
		except:
			raise Exception
		cm = round(Lobsang.sensors.distance(), -1) / 10
		right_speed = net.activate([cm])
		print "CM: %i, LS: %f, RS: %f" %(cm * 10, 0.0, right_speed)
		#left_speed = round(left_speed)
		right_speed = round(right_speed)
		print "Speeds to motors (L, R): (", 0, ",", right_speed, ")"
		print " "
		Lobsang.wheels.both(right_speed)
except Exception as e:
	Lobsang.quit()
	print e
	print "Halted after", loop_count, "loops and", train_count, "trainings."
	ds.saveToFile("nndist.ds")
else:
	Lobsang.quit()
