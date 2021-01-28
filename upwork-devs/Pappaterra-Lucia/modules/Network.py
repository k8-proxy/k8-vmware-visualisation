import json
import textwrap
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex

BLUE = "#99CDFF"
YELLOW = "#FEEBA7"
PINK = "#FFBBB2"
PURPLE = "#DAADF0"
ORANGE = "#FFC266"
GREEN = "#C6E7B0"
BROWN = "#ADAD85"
RED = "#FF6666"
AQUAMARINE = "#5CD6D6"

SHAPE = "circle"
SHAPE2 = "box"


class Network():

	def __init__(self):
		self.nodes = []
		self.nodesIdsCounter = 0 # id of next node to add
		self.nodesIds = {} # dict with nodes ids by label keys
		self.nodesLabels = {} # dict with nodes labels by id key
		self.groups = []
		self.nodesGroups = {} # dict with nodes' groups by id key if any
		self.groupSettings = lambda *args: args # function to set groups' characteristics
		self.edges = [] # list of groups for nodes
		self.edgesIdsCounter = 0 # id of next edge to add
		self.edgesPairs = [] # list of pairs of edges (a, b), where a and b are the nodes ids
		self.edgesPairsId = {} # dict with pairs of edges (a, b) by edge id key
		self.edgesLabelsId = {} # dict with edge Labels by edge id key


	def ids_from_label(self, label):
		return self.nodesIds[label] 


	def id_from_label(self, label):
		return self.nodesIds[label][0]


	def label_from_id(self, node_id):
		return self.nodesLabels[node_id] 


	def get_labels(self):
		return list(self.nodesIds.keys())


	def add_node(self, label="", group="default", x=-950, y=-950, color="#99CDFF", shape="default", fixed=False, physics=True, repeat_nodes=False):
		"""
		Add nodes to the network
		"""
		d = {}

		d["id"] = self.nodesIdsCounter
		d["label"] = label

		if group == "default":
			d["color"] = color
			d["fixed"] = fixed
			d["physics"] = physics
			if shape != "default":
				d["shape"] = shape
		else:
			d["group"] = group
			d = self.groupSettings(d, group, x, y, color, shape)

		if repeat_nodes == False:
			if label not in self.nodesIds.keys():
				self.nodesIds[label] = [self.nodesIdsCounter]

				self.nodesLabels[self.nodesIdsCounter] = label
				self.nodesGroups[self.nodesIdsCounter] = group

				self.nodes.append(d)
				self.nodesIdsCounter += 1
		else:
			if label not in self.nodesIds.keys():
				self.nodesIds[label] = [self.nodesIdsCounter]
			else:
				self.nodesIds[label].append(self.nodesIdsCounter)

			self.nodesLabels[self.nodesIdsCounter] = label
			self.nodesGroups[self.nodesIdsCounter] = group

			self.nodes.append(d)
			self.nodesIdsCounter += 1


	def add_edge(self, a, b, label="", color="black", length=100, arrows="to"):
		"""
		Add edges to the network. a and b are the nodes ids. If there are more than one edge between "a" and "b",
		use different colors for the arrows.
		"""

		m = self.edgesPairs.count((a, b))

		if m == 0 :
			color = color
		if m == 1:
			color = "red"
		if m == 2:
			color = "blue"

		self.edgesPairs.append((a, b))
		self.edgesPairsId[self.edgesIdsCounter] = (a, b)
		self.edgesLabelsId[self.edgesIdsCounter] = label

		self.edges.append({"id": self.edgesIdsCounter,
						"from": a,
						"to": b,
						"label": label,
						"arrows": arrows,
						"color": color,
						"length": length
						})
		self.edgesIdsCounter += 1


	def save_to_json(self, path):
		nodes_edges = {"nodes": self.nodes, "edges": self.edges}
		with open(path, 'w') as fp:
			json.dump(nodes_edges, fp)


################# Auxiliary functions ###############################################


def wrap_by_word(s, n):
	"""
	Returns a string where \n is inserted between every n words

	:param s: string
	:param n: integer, number of words
	:return:
	"""
	a = s.split()
	ret = ''
	for i in range(0, len(a), n):
		ret += ' '.join(a[i:i+n]) + '\n'
	return ret


def wrap_by_char(s, n):
	return '\n'.join(l for line in s.splitlines() for l in textwrap.wrap(line, width=n))


def is_unique(s):
	"""
	Check if all values in a pandas dataframe column are the same
	"""
	a = s.to_numpy() # s.values (pandas<0.24)
	return (a[0] == a).all()


def group_settings_VM(d, group, x, y, color, shape="default"):

	if group == "Reference":
		d["x"] = x
		d["y"] = y
		d["color"] = color
		d["fixed"] = True
		d["physics"] = False
		if shape != "default":
			d["shape"] = shape

	elif group == "Name":
		d["color"] = BLUE
		d["shape"] = SHAPE2
		d["level"] = 4

	elif group == "GuestId":
		d["color"] = YELLOW
		d["shape"] = SHAPE2
		d["level"] = 0

	elif group == "NumCpu":
		d["color"] = PINK
		d["shape"] = SHAPE
		d["level"] = 1

	elif group == "MemoryMB":
		d["color"] = GREEN
		d["shape"] = SHAPE
		d["level"] = 2

	elif group == "PowerState":
		d["color"] = PURPLE
		d["shape"] = SHAPE2
		d["level"] = 3

	elif group == "Version":
		d["color"] = ORANGE
		d["shape"] = SHAPE
		d["level"] = 5

	elif group == "HardwareVersion":
		d["color"] = RED
		d["shape"] = SHAPE2
		d["level"] = 6

	elif group == "VMResourceConfiguration":
		d["color"] = BROWN
		d["shape"] = SHAPE2
		d["level"] = 7

	return d


def group_settings_R(d, group, x=None, y=None, color=None, shape=None):

	if group == "Repo":
		d["color"] = rgb2hex(plt.cm.Pastel1(0))
		d["shape"] = 'box'

	elif group == "Tag_Id":
		d["color"] = rgb2hex(plt.cm.Pastel1(1))

	elif group == "Description":
		d["color"] = rgb2hex(plt.cm.Pastel1(5))
		d["shape"] = 'box'

	d["fixed"] = False
	d["physics"] = True

	return d

