# Server bindings
SERVER_BINDING = {
    'address': ['192.168.57.102','192.168.57.103','192.168.57.104'],
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
    'meas_to_location': '~/'
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
    # 'infra_tested': 'MOCK',                       # or REAL
    'infra_tested': 'REAL',
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
    'bindings1': ['192.168.60.2:7000', '192.168.60.4:7000', '192.168.60.3:7000'],
    'bindings2': ['192.168.60.3:7000', '192.168.60.2:7000', '192.168.60.4:7000'],
    'bindings3': ['192.168.60.4:7000', '192.168.60.3:7000', '192.168.60.2:7000'],
}

SELLER = {
    # server port combination for distributed seller object
    'bindings1': ['192.168.60.2:7100', '192.168.60.4:7100', '192.168.60.3:7100'],
    'bindings2': ['192.168.60.3:7100', '192.168.60.2:7100', '192.168.60.4:7100'],
    'bindings3': ['192.168.60.4:7100', '192.168.60.3:7100', '192.168.60.2:7100'],

}
