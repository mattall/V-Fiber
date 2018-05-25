#JSON Seller Data....

Seller =  {
            "ISP": "LabLink",
            "Fiber Strands": 1,
            "Host1": {
              "Name" : "HostA",
              "Address": "192.168.57.200"
            },
            "Host2": {
              "Name" : "HostB",
              "Address": "192.168.57.201"
            },
            "Fiber Details": {
              "Fiber 1": {
                "Lambdas": 4,
                "Capacity Per Lambda (Gb/s)": 1,
                "Amount Per Lambda" : 100,
                "Lambda Details" : {
                  "Lambda 1": {
                    "Host1 Interface": "GigabitEthernet 0/25",
                    "Host2 Interface": "GigabitEthernet 0/25",
                    "Wavelength": 1470,
                    "Status": "Inactive"
                  },
                  "Lambda 2": {
                    "Host1 Interface": "GigabitEthernet 0/26",
                    "Host2 Interface": "GigabitEthernet 0/26",
                    "Wavelength": 1490,
                    "Status": "Inactive"
                  },
                  "Lambda 3": {
                    "Host1 Interface": "GigabitEthernet 0/27",
                    "Host2 Interface": "GigabitEthernet 0/27",
                    "Wavelength": 1510,
                    "Status": "Inactive"
                  },
                  "Lambda 4": {
                    "Host1 Interface": "GigabitEthernet 0/28",
                    "Host2 Interface": "GigabitEthernet 0/28",
                    "Wavelength": 1530,
                    "Status": "Inactive"
                  }
                }
              }
            }
          }

'''
>>> Seller["Fiber Details"]["Fiber 1"]["Lambda Details"]["Lambda 1"]["Wavelength"]
1530

>>> Seller["Fiber Details"]["Fiber 1"]["Lambda Details"]["Lambda 1"]["Host1 Interface"]
'GigabitEthernet 0/28'
'''
