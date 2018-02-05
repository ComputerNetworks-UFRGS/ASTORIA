import itertools
import random

from mosaik.util import connect_randomly, connect_many_to_one
import mosaik
import ns3topo as ns3Topo
import json


sim_config = {
    'CSV': {
        'python': 'mosaik_csv:CSV',
    },
    'DB': {
        'cmd': 'mosaik-hdf5 %(addr)s',
    },
    'HouseholdSim': {
        'python': 'householdsim.mosaik:HouseholdSim',
        # 'cmd': 'mosaik-householdsim %(addr)s',
    },
    'PyPower': {
        'python': 'mosaik_pypower.mosaik:PyPower',
        # 'cmd': 'mosaik-pypower %(addr)s',
    },
    'WebVis': {
        'cmd': 'mosaik-web -s 0.0.0.0:8000 %(addr)s',
    },
    'NS3': {
       'connect': 'localhost:5678',
    },
}

START = '2014-01-01 00:00:00'
END =	1*3600  # (seconds)
PV_DATA = 'data/pv_10kw.csv'
PROFILE_FILE = 'data/profiles.data'
GRID_NAME = 'demo_lv_grid'
GRID_FILE = 'data/%s.json' % GRID_NAME
TOPO_FILE = 'data/ns3topo.xml'
STEP = 60
NUM_PRODUCERS = 2

STATION_SUBSERVER = 10 
PROTOCOL = 'Modbus'  

def main():
    random.seed(23)
    world = mosaik.World(sim_config)
    create_scenario(world)
    world.run(until=END)  # As fast as possilbe
    # world.run(until=END, rt_factor=1/60)  # Real-time 1min -> 1sec


def create_scenario(world):
    # Start simulators
    pypower = world.start('PyPower', step_size=STEP)
    hhsim = world.start('HouseholdSim')
    pvsim = world.start('CSV', sim_start=START, datafile=PV_DATA)
    
    ns3 = world.start('NS3',step_size=STEP,sim_end=END,subserver=STATION_SUBSERVER,protocol=PROTOCOL);

    # Instantiate models
    grid = pypower.Grid(gridfile=GRID_FILE).children
    
    houses = hhsim.ResidentialLoads(sim_start=START,
                                    profile_file=PROFILE_FILE,
                                    grid_name=GRID_NAME).children
    
    pvs = pvsim.PV.create(NUM_PRODUCERS) 
    
    ns3TopoHelper = ns3Topo.Topo(world,houses,GRID_FILE) 
    p2pTopo = ns3TopoHelper.create_p2p_topo()
    ns3TopoHelper.create_file(p2pTopo)
   
    ns3nodes = ns3.Network(topology_file=TOPO_FILE).children
    
    # Connect entities
    connect_buildings_to_grid(world, houses, grid)
    connect_producers(world, pvs, grid)
    connect_to_network(world,houses,pvs,grid,ns3nodes)
    
    # Database
    db = world.start('DB', step_size=STEP, duration=END)
    hdf5 = db.Database(filename='demo.hdf5')
    connect_many_to_one(world, houses, hdf5, 'P_out')
    connect_many_to_one(world, pvs, hdf5, 'P')

    nodes = [e for e in grid if e.type in ('RefBus, PQBus')]
    connect_many_to_one(world, nodes, hdf5, 'P', 'Q', 'Vl', 'Vm', 'Va')

    branches = [e for e in grid if e.type in ('Transformer', 'Branch')]
    connect_many_to_one(world, branches, hdf5,
                        'P_from', 'Q_from', 'P_to', 'P_from')

    # Web visualization
    webvis = world.start('WebVis', start_date=START, step_size=STEP)
    webvis.set_config(ignore_types=['Topology', 'ResidentialLoads', 'Grid',
                                    'Database'])
    vis_topo = webvis.Topology()
    
    connect_many_to_one(world, nodes, vis_topo, 'P', 'Vm')
    webvis.set_etypes({
        'RefBus': {
            'cls': 'refbus',
            'attr': 'P',
            'unit': 'P [W]',
            'default': 0,
            'min': 0,
            'max': 30000,
        },
        'PQBus': {
            'cls': 'pqbus',
            'attr': 'Vm',
            'unit': 'U [V]',
            'default': 230,
            'min': 0.99 * 230,
            'max': 1.01 * 230,
        },
    })

    connect_many_to_one(world, houses, vis_topo, 'P_out')
    webvis.set_etypes({
        'House': {
            'cls': 'load',
            'attr': 'P_out',
            'unit': 'P [W]',
            'default': 0,
            'min': 0,
            'max': 3000,
        },
    })

    connect_many_to_one(world, pvs, vis_topo, 'P')
    webvis.set_etypes({
        'PV': {
            'cls': 'gen',
            'attr': 'P',
            'unit': 'P [W]',
            'default': 0,
            'min': -10000,
            'max': 0,
        },
    })

def connect_to_network(world,houses,pvs,grid,ns3nodes):
	house_data = world.get_data(houses,'num')
	for house in houses:
		ns3_node = get_ns3_node(world,ns3nodes,house.eid)
		world.connect(house,ns3_node,('P_out','P'))
	for pv in pvs:
		ns3_node = get_ns3_node(world,ns3nodes,pv.eid)
		world.connect(pv,ns3_node,('P','P'))
	for node in grid:
		if("branch" not in node.eid):
			ns3_node = get_ns3_node(world,ns3nodes,node.eid.split("-")[1])
			try:
				world.connect(node,ns3_node,('P','P'))
			except mosaik.exceptions.ScenarioError:
				world.connect(node,ns3_node,('P_from','P'))
			except AttributeError:
				pass
			
			
def get_ns3_node(world,ns3nodes,node_id):
	for ns3_node in ns3nodes:
		id_index = ns3_node.eid
		if(id_index == -1):
			id_index = 0
		if(node_id == ns3_node.eid):
			return ns3_node
	
		
def connect_producers(world, pvs, grid):
    with open(GRID_FILE) as data_file:
    	grid_info = json.load(data_file)    

    buses = filter(lambda e: e.type == 'PQBus', grid)
    buses = {b.eid.split('-')[1]: b for b in buses}
		
    for pv in pvs:
    	pv_id = int(pv.eid.split("_")[1])
    	node_id = grid_info["prod"][pv_id][1]
    	world.connect(pv, buses[node_id], ('P', 'P'))
        #world.connect(house, buses[node_id], ('P_out', 'P'))


def connect_buildings_to_grid(world, houses, grid):
    buses = filter(lambda e: e.type == 'PQBus', grid)
    buses = {b.eid.split('-')[1]: b for b in buses}
    house_data = world.get_data(houses, 'node_id')
    for house in houses:
        node_id = house_data[house]['node_id']
        world.connect(house, buses[node_id], ('P_out', 'P'))
       
if __name__ == '__main__':
    main()
