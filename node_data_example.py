#!/usr/bin/env python3
"""
Polyglot v3 node server Example 5
Copyright (C) 2024 Robert Paauwe

MIT License
"""
import udi_interface
import sys
import time

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None

'''
TestNode is the device class.  For this example, testNode extends the 
node class to save and restore persistent data.

In this case, the persistent data is current count, which is updated
every short poll interval.
'''
class testNode(udi_interface.Node):
    id = 'test'
    def __init__(self, poly, primary, address, name):
        super().__init(poly, primary, address, name)
        self.poly = poly
        self.name = name
        self.address = address
        self.counter = 0

        poly.subscribe(poly.POLL, self.poll)
        poly.subscribe(poly.NSCUSTOM, self.loadConfig)

        Config = Custom(polyglot, address)


    def poll(self, pollType):
        LOGGER.error('In poll for node {}'.format(self.name))
        if polltype == 'shortPoll':
            self.counter += 1
            self.setDriver(GV0, self.counter, True, True)

            # TODO: Save current count
            Config.counter = self.counter

    # When we get this event, we pull the saved counter value
    # and restore it.
    def loadConfig(self, data):
        LOGGER.error('NSCUSTOM data looks like {}'.format(data))

    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            ]


'''
Read the user entered custom parameters. In this case there shouldn't
be anything as we don't need any user defined parameters.
'''
def parameterHandler(params):
    LOGGER.info('User config = {}'.format(params))


'''
When we are told to stop, we update the node's status to False.  Since
we don't have a 'controller', we have to do this ourselves.
'''
def stop():
    nodes = polyglot.getNodes()
    for n in nodes:
        nodes[n].setDriver('ST', 0, True, True)
    polyglot.stop()

def config(data):
    loglevel = data['logLevel']
    loglist = data['logLevelList']
    level = udi_interface.LOG_HANDLER.getLevelName(loglevel)
    LOGGER.error('list = {}'.format(loglist))
    LOGGER.error('Current log level {} ({})'.format(loglevel, level))


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.0')  # Version 1.0.0

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.STOP, stop)
        polyglot.subscribe(polyglot.CONFIG, config)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        '''
        Here we create the device node.  In a real node server we may
        want to try and discover the device or devices and create nodes
        based on what we find.  Here, we simply create our node and wait
        for the add to complete.
        '''
        node = testNode(polyglot, 'my_address', 'my_address', 'Counter')
        polyglot.addNode(node)

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

