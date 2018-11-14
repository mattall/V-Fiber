# Server bindings
SERVER_BINDING = {
    'address': ['192.168.57.102', 
                '192.168.57.103', 
                '192.168.57.104', 
                '192.168.57.105', 
                '192.168.57.106', 
                '192.168.57.107', 
                '192.168.57.108',
                '192.168.57.109',
                '192.168.57.110', 
                'localhost'],
    'port': '10000',
    'service_alias': 'VirtualFiber'
}

# Contextual settings
CONTEXT = {
    'debug': False,
    'client_socket_buffer': 8192,
    'compressed_content': False,
    'request_size': 1024,
    'meas_format': "d",
    'meas_to_file': True,
    'meas_to_location': '/home/matt/vFiber/V-Fiber/src/experiment'
}

# Useful parameters for test purposes
TEST_PARAMS = {
    'server_path': '../data/',
    'client_path': '/Users/TomNason/Dropbox/VFiber_code/VFiber/data/',
    'buyer_file_name': 'labClient.txt',
    'seller_file_name': 'labSeller.txt',
    'client_request_type': 'BUYER',                 # or SDX
    'client_request_code': 100,                     # or 001
    # change this according to the experiment
    'infra_tested': 'MOCK',                       # or REAL
    #'infra_tested': 'REAL',
    'install_time': 34.29, # mean
    # 'install_time': 34.29, # max
    # 'install_time': 34.29, # mean
}

# Database parameters
DB_PARAMS = {
    'address': '127.0.0.1',
    'username': 'root',
    'password': '',
    'database': 'VirtualFiber',
    'truncate': True,                                # True will truncate the IPAllocation table at the start
}

# Ad Exchange settings
ADEX = {
    # status takes either open or closed
    'status': 'open',
    # auction takes values either gsp or vcg"
    'auction': 'gsp',
    # bids below this reserved price are ignored -- just to ensure that everyone makes money.
    'reserve': 500,
    'port': '7000',
    # server port combinations for distributed adExObject
    'bindings0': ['localhost:7000'],
    'bindings1': ['192.168.60.2:7000', '192.168.60.4:7000', '192.168.60.3:7000'],
    'bindings2': ['192.168.60.3:7000', '192.168.60.2:7000', '192.168.60.4:7000'],
    'bindings3': ['192.168.60.4:7000', '192.168.60.3:7000', '192.168.60.2:7000'],
}

SELLER = {
    'port':'7100',
    # server port combination for distributed seller object
    'bindings0': ['localhost:7100'],
    'bindings1': ['192.168.60.2:7100', '192.168.60.4:7100', '192.168.60.3:7100'],
    'bindings2': ['192.168.60.3:7100', '192.168.60.2:7100', '192.168.60.4:7100'],
    'bindings3': ['192.168.60.4:7100', '192.168.60.3:7100', '192.168.60.2:7100'],
}


