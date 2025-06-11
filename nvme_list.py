import subprocess
import json
import os
import nvme_simulation as nv_simul

def print_nvme_list(json_data):
	debug_mode = os.environ.get('DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
	
	if debug_mode:
		print("=== NVMe Device Details ===")
		for device in json_data['Devices']:
			print('DevicePath %s' %device.get('DevicePath', 'N/A'))
			print('Firmware %s' %device.get('Firmware', 'N/A'))
			print('Index %s' %device.get('Index', device.get('NameSpace', 'N/A')))
			print('ModelNumber %s' %device.get('ModelNumber', 'N/A'))
			print('ProductName %s' %device.get('ProductName', 'N/A'))
			print('SerialNumber %s' %device.get('SerialNumber', 'N/A'))
			print('UsedBytes %s' %device.get('UsedBytes', device.get('Size', 'N/A')))
			print('MaximumLBA %s' %device.get('MaximumLBA', 'N/A'))
			print('PhysicalSize %s' %device.get('PhysicalSize', device.get('Size', 'N/A')))
			print('SectorSize %s' %device.get('SectorSize', 'N/A'))
			print("---")
	else:
		device_count = len(json_data['Devices'])
		device_names = [device.get('DevicePath', 'Unknown') for device in json_data['Devices']]
		print(f"Found {device_count} NVMe device(s): {', '.join(device_names)}")

def get_nvme_list():
    if nv_simul.NVME_SIMULATION == 0:

        proc = subprocess.Popen("nvme list -o json",
                                shell=True,
                                stdout=subprocess.PIPE,
                                encoding='utf-8')
        err = proc.wait()

        (stdout, stderr) = proc.communicate()

        json_data = json.loads(stdout)

    else:
        json_data = nv_simul.gen_simulation_nvme_list()

    print_nvme_list(json_data)

    return json_data

if __name__ == '__main__':
	nvme_list_json = get_nvme_list("/dev/nvme0")
	print(nvme_list_json)
