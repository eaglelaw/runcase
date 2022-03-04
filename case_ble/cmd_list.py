
m_cmd = {
	'initBle' : {},
	'stopScan' : {},
	'connectDevice' : {'address': '22:22:22:22:22:22'},
	'disconnectDevice' : {},
	'requestMtu' : {'mtuSize': 512},
	'discoverServices' : {},
	'scanDevice' : {},
	'cancelBondProcess' : {},
	'cancelPairing' : {},
	'connectGatt' : {'context': None, 'autoConnect': False, 'callback': None, 'transport':'TRANSPORT_LE', 'phy': 'PHY_LE_1M_MASK' ,'handler':None},
	'createBond' : {},
	'createInsecureL2capChannel' : {'psm': None},
	'createInsecureRfcommSocketToServiceRecord' : {'uuid' : None},
	'createL2capChannel' : {'psm': None},
	'createRfcommSocketToServiceRecord' : {'uuid': None},
}

m_hook = [
	'BluetoothGattService', 'BleDevice'
]