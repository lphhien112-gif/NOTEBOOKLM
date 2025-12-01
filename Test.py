#!/usr/bin/env python3
"""
hw_audit.py
Ghi lại thông tin phần cứng và so sánh với snapshot trước đó.
Chạy trên Windows / Linux. Một số phần (serial RAM, disk serial) cần quyền admin/root.
"""

import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime
from pprint import pprint

try:
    import psutil
except ImportError:
    print("Missing psutil. Install with: pip install psutil")
    sys.exit(1)

# Optional libs
try:
    import cpuinfo
except Exception:
    cpuinfo = None

# Helper: run command and return stdout
def run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return out.decode(errors="ignore").strip()
    except Exception:
        return ""

def get_basic_info():
    info = {}
    info["timestamp"] = datetime.utcnow().isoformat() + "Z"
    info["hostname"] = socket.gethostname()
    try:
        info["ip"] = socket.gethostbyname(info["hostname"])
    except Exception:
        info["ip"] = None
    info["platform"] = platform.system()
    info["platform_release"] = platform.release()
    info["platform_version"] = platform.version()
    return info

def get_cpu_info():
    ci = {}
    if cpuinfo:
        try:
            data = cpuinfo.get_cpu_info()
            ci["brand_raw"] = data.get("brand_raw")
            ci["arch"] = data.get("arch_string_raw") or platform.machine()
        except Exception:
            ci["arch"] = platform.machine()
    else:
        ci["arch"] = platform.machine()
    ci["logical_cpus"] = psutil.cpu_count(logical=True)
    ci["physical_cores"] = psutil.cpu_count(logical=False)
    return ci

def get_ram_info():
    vm = psutil.virtual_memory()
    ram = {
        "total_bytes": vm.total,
        "total_gb": round(vm.total / (1024**3), 2)
    }
    # Try to get serials: Windows via wmic, Linux via dmidecode (root)
    serials = []
    if platform.system() == "Windows":
        out = run_cmd('wmic memorychip get banklabel, capacity, manufacturer, partnumber, serialnumber /format:csv')
        if out:
            serials = [line for line in out.splitlines() if line.strip() and not line.startswith("Node")]
    else:
        # need sudo dmidecode -t memory
        out = run_cmd('sudo dmidecode -t memory')  # may fail without root
        if out:
            # crude parse for "Serial Number:"
            for block in out.split("\n\n"):
                for line in block.splitlines():
                    if line.strip().startswith("Serial Number:"):
                        serials.append(line.split(":",1)[1].strip())
    ram["modules_info"] = serials
    return ram

def get_disks_info():
    disks = []
    # psutil.disk_partitions gives mount points; for disk devices metadata use platform-specific commands
    if platform.system() == "Windows":
        # use wmic to list model, size, serial
        out = run_cmd('wmic diskdrive get model, size, serialnumber /format:csv')
        if out:
            lines = [l for l in out.splitlines() if l.strip() and not l.startswith("Node")]
            for l in lines:
                parts = [p.strip() for p in l.split(",") if p.strip()!='']
                # format: Node,Model,SerialNumber,Size  (order may vary); do naive mapping
                disks.append({"raw": l})
    else:
        # Linux: lsblk for model,size,name, and udevadm or /sys for serial
        out = run_cmd("lsblk -o NAME,MODEL,SIZE,TYPE -dn")
        if out:
            for line in out.splitlines():
                cols = line.split(None, 3)
                if len(cols) >= 3:
                    name = cols[0]
                    model = cols[1]
                    size = cols[2]
                    dev = "/dev/" + name
                    serial = ""
                    # try /sys/block/<name>/device/serial
                    try:
                        p = f"/sys/block/{name}/device/serial"
                        if os.path.exists(p):
                            with open(p, "r", errors="ignore") as f:
                                serial = f.read().strip()
                    except Exception:
                        serial = ""
                    # fallback to udevadm
                    if not serial:
                        u = run_cmd(f"udevadm info --query=property --name={dev} 2>/dev/null | grep ID_SERIAL=")
                        if u:
                            serial = u.split("=",1)[1].strip()
                    disks.append({"name": dev, "model": model, "size": size, "serial": serial})
    return disks

def get_gpu_info():
    gpus = []
    # Try GPUtil (if installed), else nvidia-smi, else lspci
    try:
        import GPUtil
        devs = GPUtil.getGPUs()
        for d in devs:
            gpus.append({"id": d.id, "name": d.name, "memoryTotalMB": d.memoryTotal})
    except Exception:
        # try nvidia-smi
        out = run_cmd("nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader,nounits")
        if out:
            for line in out.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    gpus.append({"index": parts[0], "name": parts[1], "memoryMB": parts[2]})
        else:
            # fallback lspci (linux)
            if platform.system() != "Windows":
                out = run_cmd("lspci | grep -i 'vga\\|3d\\|display'")
                for line in out.splitlines():
                    gpus.append({"raw": line})
            else:
                # windows fallback: wmic path win32_videocontroller get name
                out = run_cmd("wmic path win32_videocontroller get name /format:csv")
                for line in out.splitlines():
                    if line.strip() and not line.startswith("Node"):
                        gpus.append({"raw": line})
    return gpus

def collect_all():
    data = {}
    data.update(get_basic_info())
    data["cpu"] = get_cpu_info()
    data["ram"] = get_ram_info()
    data["disks"] = get_disks_info()
    data["gpus"] = get_gpu_info()
    return data

def save_snapshot(data, outdir="hw_snapshots"):
    os.makedirs(outdir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = os.path.join(outdir, f"hw_snapshot_{ts}.json")
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return fname

def latest_snapshot(outdir="hw_snapshots"):
    if not os.path.exists(outdir):
        return None
    files = [f for f in os.listdir(outdir) if f.startswith("hw_snapshot_") and f.endswith(".json")]
    if not files:
        return None
    files.sort()
    return os.path.join(outdir, files[-1])

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compare_snapshots(old, new):
    diffs = []
    # simple compares for disks count/serials, ram module serials, cpu core counts
    if old.get("cpu",{}).get("physical_cores") != new.get("cpu",{}).get("physical_cores"):
        diffs.append(f"CPU physical cores changed: {old.get('cpu',{}).get('physical_cores')} -> {new.get('cpu',{}).get('physical_cores')}")
    old_ram = old.get("ram",{}).get("modules_info", [])
    new_ram = new.get("ram",{}).get("modules_info", [])
    if old_ram != new_ram:
        diffs.append(f"RAM modules info changed: {old_ram} -> {new_ram}")
    # disks: compare list of serials/names
    old_disks = {(d.get("serial") or d.get("name") or d.get("raw")) for d in old.get("disks",[])}
    new_disks = {(d.get("serial") or d.get("name") or d.get("raw")) for d in new.get("disks",[])}
    if old_disks != new_disks:
        diffs.append(f"Disks changed: old={sorted(list(old_disks))} new={sorted(list(new_disks))}")
    # gpu count / names
    old_gpus = [g.get("name") or g.get("raw") for g in old.get("gpus",[])]
    new_gpus = [g.get("name") or g.get("raw") for g in new.get("gpus",[])]
    if old_gpus != new_gpus:
        diffs.append(f"GPU list changed: {old_gpus} -> {new_gpus}")
    return diffs

def main():
    print("Collecting hardware information... (may need sudo/admin for full details)")
    data = collect_all()
    pprint(data)
    outdir = "hw_snapshots"
    prev = latest_snapshot(outdir)
    if prev:
        print(f"\nComparing with previous snapshot: {prev}")
        old = load_json(prev)
        diffs = compare_snapshots(old, data)
        if diffs:
            print("\n***** Differences detected *****")
            for d in diffs:
                print("- " + d)
        else:
            print("\nNo differences detected vs last snapshot.")
    else:
        print("\nNo previous snapshot found.")
    saved = save_snapshot(data, outdir=outdir)
    print(f"\nSaved current snapshot to: {saved}")

if __name__ == "__main__":
    main()
