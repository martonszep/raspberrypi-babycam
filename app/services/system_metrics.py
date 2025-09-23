import psutil
import subprocess

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except:
        return None
    
def get_cpu_load():
    # Returns percentage (aggregate across all cores)
    return psutil.cpu_percent(interval=0.5)

def get_ram_usage():
    mem = psutil.virtual_memory()
    return {
        "total": round(mem.total / (1024 ** 2), 1),  # MB
        "used": round(mem.used / (1024 ** 2), 1),
        "percent": mem.percent,
    }

def get_throttle_status():
    """
    Returns a dictionary of all Raspberry Pi throttling bits.
    Only bits that are set will be marked True.
    """
    ISSUES_MAP = {
        0: "Under-voltage detected",
        1: "Arm frequency capped",
        2: "Currently throttled",
        3: "Soft temperature limit active",
        16: "Under-voltage has occurred",
        17: "Arm frequency capping has occurred",
        18: "Throttling has occurred",
        19: "Soft temperature limit has occurred"
    }

    try:
        output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode().strip()
        val = int(output.split("=")[1], 16)
        # return only the bits that are set
        active_issues = [ISSUES_MAP[b] for b in ISSUES_MAP if val & (1 << b)]
        return {
            "raw": hex(val),
            "active_issues": active_issues
        }
    except Exception as e:
        return {"error": str(e)}