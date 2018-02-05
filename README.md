# ASTORIA

### What is ASTORIA?

ASTORIA is a framework developed to allow the simulation of attacks and the evaluation of their impact on Smart Grid infrastructures, using closely-related real devices and real topologies comprising both power grid elements as well as ICT and networking equipment. ASTORIA can be used by Smart Grid operators not only to analyze the impact of malicious attacks and other security threats in different components, but also to permit the development and evaluation of anomaly detection techniques in a simulation environment.


### Setup Steps

##### Clone source from Github

```
$ git clone https://github.com/ComputerNetworks-UFRGS/ASTORIA.git
```

##### Install dependencies

```
$ sudo apt-get update
$ sudo apt-get install g++ python-libvirt python-dev python-pip
```

1. Download [NS-3](https://www.nsnam.org) simulator source code to your computer and extract the folder ```ns-allinone-<version>/ns-<version> (e.g version=3.27)```.

2. Copy ```scada-application``` folder from this repository to ```ns-allinone-<version>/ns-<version>/src```.

3. Copy the content of ```include``` folder from this repository to ```ns-allinone-<version>/ns-<version>/include```.

4. Copy ```scada-application``` folder from this repository to ```ns-allinone-<version>/ns-<version>/src```.

5. Copy the content of ```scratch``` folder from this repository to ```ns-allinone-<version>/ns-<version>/scratch```.

6. Install [Mosaik 2.4.0](http://mosaik.readthedocs.io/en/latest/installation.html#linux) simulator.

7. Download [Boost 1.66.0](https://dl.bintray.com/boostorg/release/1.66.0/source/) and extract to NS3 root folder.

8. Run the following command lines within Boost folder and wait for a couple of minutes.

```
$ ./bootstrap.sh
$ ./b2 install
```

### Build

1. Access ```ns-allinone-<version>/ns-<version>/``` and run the following commands:

```
$ CXXFLAGS="-std=c++0x" ./waf configure --enable-examples --enable-tests
$ ./waf configure --enable-examples
$ ./waf
```

### Run

1. Open a terminal to run NS3 simulator:

```
$ ./waf --run scratch mosaik-ns3-integration
```

2. In a new terminal access mosaik folder which you have cloned from this repository and execute:

```
$ sudo pip install -U virtualenv
$ virtualenv -p /usr/bin/python3 ~/.virtualenvs/mosaik
$ source ~/.virtualenvs/mosaik/bin/activate
$ (mosaik)$ pip install mosaik
$ (mosaik)$ pip install -r requirements.txt
```

### Referencing and Citation

For academic work referencing and citation please read our [paper](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=7502822) "ASTORIA: A Framework for Attack Simulation and Evaluation in Smart Grids" published at 15th IEEE/IFIP Network Operations and Management Symposium (NOMS 2016), 25-29 April 2016, Istanbul, Turkey, pp. 273-280.


### Acknowledgement

This work is supported by ProSeG - Information Security, Protection and Resilience in Smart Grids, a research project funded by MCTI/CNPq/CT-ENERG # 33/2013.
