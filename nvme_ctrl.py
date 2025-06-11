import subprocess
import json
import os
from random import *
import nvme_simulation as nv_simul

def get_ctrl_regs(device_path):
    if nv_simul.NVME_SIMULATION == 0:
        cmd = "nvme show-regs %s -o json" % device_path
        
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
                print(f"ERROR: nvme show-regs command failed for device {device_path}")
                print(f"Exit code: {err}")
                print(f"Stderr: {stderr}")
            else:
                print(f"Warning: Controller registers unavailable for {device_path}, using defaults")
            # Return default values
            json_data = {'cc': 1, 'csts': 1}  # Default to enabled/ready
        else:
            json_data = json.loads(stdout)
    else:
        json_data = nv_simul.gen_simulation_ctrl(int(device_path[9:]))

    return json_data
