# Server bindings
SERVER_BINDING = {
    #local test
    #'address': '127.0.0.1',
    #Virtual Box test
    'address': ['192.168.57.104','192.168.56.102','192.168.56.103'],
    'port': '10000',
    'service_alias': 'VirtualFiber'
}

# Contextual settings
CONTEXT = {
    'debug': True,
    'client_socket_buffer': 8192,
    'compressed_content': False,
    'request_size': 1024,
    'meas_format': "d",
    'meas_to_file': True,
    'meas_to_location': '/Users/ram/Desktop/RAM/Project/GreyFiber/ClientServer/src/realdeployment/Outputs/'
}

# Useful parameters for test purposes
TEST_PARAMS = {
    'path': '../data/',
    'buyer_file_name': 'clientRequest.txt',
    #'buyer_file_name': 'clientRequests_10.txt',
    'seller_file_name': 'sellerData.txt',
    'client_request_type': 'BUYER',                 # or SDX
    'client_request_code': 100,                     # or 001
    # change this according to the experiment
    #'infra_tested': 'MININET',                       # or REAL
    'infra_tested': 'REAL',
    'geni_slice_name': 'TestScaling',
    'geni_rspec_location': '/Users/ram/Desktop/RAM/Project/GreyFiber/ClientServer/src/realdeployment/'
}

# Database parameters
DB_PARAMS = {
    'address': '127.0.0.1',
    'username': 'root',
    'password': '',
    'database': 'VirtualFiber',
    'truncate': True                                # True will truncate the IPAllocation table at the start
}

# Ad Exchange settings
ADEX = {
    # status takes either open or closed
    'status': 'open',
    # auction takes values either gsp or vcg"
    'auction': 'gsp',
    # bids below this reserved price are ignored -- just to ensure that everyone makes money.
    'reserve': 500,
    # server port combinations for distributed adExObject
    'bindings': ['127.0.0.1:7000', '127.0.0.1:7001', '127.0.0.1:7002']
    # 'bindings': ['192.168.57.3:7000', '192.168.57.4:7000', '192.168.57.5:7000']
    # 'bindings': ['192.168.57.4:7000', '192.168.57.3:7000', '192.168.57.5:7000']
    # 'bindings': ['192.168.57.5:7000', '192.168.57.3:7000', '192.168.57.4:7000']


}

SELLER = {
    # server port combination for distributed seller object
    'bindings': ['127.0.0.1:7100', '127.0.0.1:7101', '127.0.0.1:7102']
    # 'bindings': ['192.168.57.3:7100', '192.168.57.4:7100', '192.168.57.5:7100']
    # 'bindings': ['192.168.57.4:7100', '192.168.57.3:7100', '192.168.57.5:7100']
    # 'bindings': ['192.168.57.5:7100', '192.168.57.3:7100', '192.168.57.4:7100']

}
