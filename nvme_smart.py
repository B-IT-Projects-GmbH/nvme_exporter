import subprocess
import json
import os
from random import *
import nvme_simulation as nv_simul

def print_smart_log(json_data):
	debug_mode = os.environ.get('DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
	
	if debug_mode:
		print('=== SMART Log Data ===')
		print('critical_warning %d' % json_data.get('critical_warning', 0))
		print('temperature %d' % json_data.get('temperature', 0))
		print('avail_spare %d' % json_data.get('avail_spare', 0))
		print('spare_thresh %d' % json_data.get('spare_thresh', 0))
		print('percent_used %d' % json_data.get('percent_used', 0))
		print('data_units_read %d' % json_data.get('data_units_read', 0))
		print('data_units_written %d' % json_data.get('data_units_written', 0))
		print('host_read_commands %d' % json_data.get('host_read_commands', 0))
		print('host_write_commands %d' % json_data.get('host_write_commands', 0))
		print('controller_busy_time %d' % json_data.get('controller_busy_time', 0))
		print('power_cycles %d' % json_data.get('power_cycles', 0))
		print('power_on_hours %d' % json_data.get('power_on_hours', 0))
		print('unsafe_shutdowns %d' % json_data.get('unsafe_shutdowns', 0))
		print('media_errors %d' % json_data.get('media_errors', 0))
		print('num_err_log_entries %d' % json_data.get('num_err_log_entries', 0))
		print('warning_temp_time %d' % json_data.get('warning_temp_time', 0))
		print('critical_comp_time %d' % json_data.get('critical_comp_time', 0))
		print('thm_temp1_trans_count %d' % json_data.get('thm_temp1_trans_count', 0))
		print('thm_temp2_trans_count %d' % json_data.get('thm_temp2_trans_count', 0))
		print('thm_temp1_total_time %d' % json_data.get('thm_temp1_total_time', 0))
		print('thm_temp2_total_time %d' % json_data.get('thm_temp2_total_time', 0))
	else:
		# In non-debug mode, just show key health indicators
		temp = json_data.get('temperature', 0) - 273  # Convert Kelvin to Celsius
		print(f"SMART data collected: temp={temp}°C, power_hours={json_data.get('power_on_hours', 0)}, cycles={json_data.get('power_cycles', 0)}")


def get_smart_log(device_path):
    if nv_simul.NVME_SIMULATION == 0:
        cmd = "nvme smart-log %s -o json" % device_path
        
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                encoding='utf-8')
        err = proc.wait()

        (stdout, stderr) = proc.communicate()

        if err != 0 or not stdout.strip() or stdout.strip().startswith("Usage:"):
            debug_mode = os.environ.get('DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
            if debug_mode:
                print(f"ERROR: nvme smart-log command failed for device {device_path}")
                print(f"Exit code: {err}")
                print(f"Stderr: {stderr}")
            else:
                print(f"Warning: SMART data unavailable for {device_path}, using defaults")
            # Return empty/default data structure
            json_data = {
                'critical_warning': 0,
                'temperature': 0,
                'avail_spare': 0,
                'spare_thresh': 0,
                'percent_used': 0,
                'data_units_read': 0,
                'data_units_written': 0,
                'host_read_commands': 0,
                'host_write_commands': 0,
                'controller_busy_time': 0,
                'power_cycles': 0,
                'power_on_hours': 0,
                'unsafe_shutdowns': 0,
                'media_errors': 0,
                'num_err_log_entries': 0,
                'warning_temp_time': 0,
                'critical_comp_time': 0,
                'thm_temp1_trans_count': 0,
                'thm_temp2_trans_count': 0,
                'thm_temp1_total_time': 0,
                'thm_temp2_total_time': 0
            }
        else:
            json_data = json.loads(stdout)
    else:
        json_data = nv_simul.gen_simulation_smart_log(int(device_path[9:]))

    print_smart_log(json_data)

    return json_data

if __name__ == '__main__':
	smart_log_json = get_smart_log("/dev/nvme0")
	print('test critical warning %d' %smart_log_json['critical_warning'])
