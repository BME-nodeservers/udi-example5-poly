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
    def __init__(self, poly, primary, address, name, init):
        self.poly = poly
        self.name = name
        self.address = address
        super(testNode, self).__init__(poly, primary, address, name)

        self.counter = init

        poly.subscribe(poly.POLL, self.poll)
        poly.subscribe(poly.CUSTOMNS, self.loadConfig)

        # create a custom data key using our node address
        self.Config = Custom(polyglot, address)


    def poll(self, pollType):
        if pollType == 'shortPoll':
            self.counter += 1
            self.setDriver('GV0', self.counter, True, True)

            # Save current count
            self.Config.counter = self.counter

    # The CUSTOMNS event is sent for every custom key as it is a global
    # event type.  This means that we need to skip any events that 
    # have a key that isn't ours.   Since we only create one custom
    # key and that key is based on our address, it's easy to do that.
    def loadConfig(self, key, data):
        # Initialize the counter to the last saved value.
        if key == self.address:  # if our key
            if 'counter' in data: # if there's actual data saved under this key
                # initialize the counter to the saved value and update the driver.
                LOGGER.info('Initializing {}\'s counter to {}'.format(self.name, data['counter']))
                self.counter = data['counter']
                self.setDriver('GV0', self.counter, True, True)

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

# Plug-in configuration data.  We don't actually need any of this info
# for this plug-in.  But we pull the current assigned log level and log
# just to show how we can access this.
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
        based on what we find.  Here, we simply create our nodes.

        The first node gets it's counter initialized to zero when it is first created.
        The second node gets it's counter initialized to 100 when it is first created.
        '''
        LOGGER.info('Creating nodes...')
        node = testNode(polyglot, 'pi_address_01', 'pi_address_01', 'Counter-1', 0)
        polyglot.addNode(node)

        node = testNode(polyglot, 'pi_address_02', 'pi_address_02', 'Counter-2', 100)
        polyglot.addNode(node)

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

