# Fault Injection Scripts - README Template

This directory contains automated fault injection scripts for troubleshooting practice.

## Prerequisites

- **GNS3 project must be running** with all devices started
- All devices must be accessible via their console ports
- Python 3.x installed
- `netmiko` library installed (`pip install netmiko`)

## ⚠️ Important Notes

- These scripts modify live device configurations
- Always save your work before running fault injections
- Use `apply_solution.py` to restore correct configurations
- Scripts connect via console telnet (localhost)

---

## Available Fault Scenarios

### Scenario 1: AS Number Mismatch
**Fault Description**: Changes R2's EIGRP AS from 100 to 200  
**Impact**: Prevents adjacency formation between R1 and R2  
**Target Device**: R2  
**Injection Command**: 
```bash
python3 inject_scenario_01.py
```

**What to Observe**:
- `show ip eigrp neighbors` on R1 shows no neighbor on Fa1/0
- `show ip protocols` on R2 shows "eigrp 200" instead of "eigrp 100"
- No EIGRP routes exchanged between R1 and R2

---

### Scenario 2: Passive Interface Misconfiguration
**Fault Description**: Configures `passive-interface default` on R3  
**Impact**: Blocks all EIGRP adjacencies on R3  
**Target Device**: R3  
**Injection Command**: 
```bash
python3 inject_scenario_02.py
```

**What to Observe**:
- `show ip eigrp neighbors` on R2 shows no neighbor on Fa0/1
- `show ip protocols` on R3 shows all interfaces as passive
- R3 cannot form adjacency with R2

---

### Scenario 3: Missing Network Statement
**Fault Description**: Removes Loopback0 network statement from R1  
**Impact**: R1's Loopback0 not advertised to EIGRP neighbors  
**Target Device**: R1  
**Injection Command**: 
```bash
python3 inject_scenario_03.py
```

**What to Observe**:
- `show ip protocols` on R1 shows network 10.0.12.0/30 but not 1.1.1.1/32
- `show ip route eigrp` on R2 and R3 shows no route to 1.1.1.1/32
- Ping from R2/R3 to 1.1.1.1 fails

---

## Usage Workflow

### 1. Start Your GNS3 Lab
Ensure all routers are running and accessible:
```bash
telnet 127.0.0.1 5001  # Test R1
telnet 127.0.0.1 5002  # Test R2
telnet 127.0.0.1 5003  # Test R3
```

### 2. Apply Initial Configuration
Make sure all devices are configured correctly before injecting faults:
```bash
cd ../../scripts
python3 setup_lab.py
```

### 3. Inject a Fault
Navigate to the fault-injection directory and run a scenario:
```bash
cd scripts/fault-injection
python3 inject_scenario_01.py
```

Expected output:
```
============================================================
Fault Injection: AS Number Mismatch
============================================================
[*] Connecting to R2 on 127.0.0.1:5002...
[+] Connected to R2
[*] Injecting fault configuration...
[*] Changing EIGRP AS from 100 to 200 (FAULT)
    configure terminal
    no router eigrp 100
    router eigrp 200
    ...
[+] Fault injected successfully on R2!
[!] Troubleshooting Scenario 1: AS Number Mismatch is now active.
============================================================
```

### 4. Practice Troubleshooting
Follow the troubleshooting exercises in the workbook:
- Use show commands to identify the problem
- Analyze outputs and logs
- Determine the root cause
- Plan and implement the fix

### 5. Restore Correct Configuration
After completing the troubleshooting exercise:
```bash
python3 apply_solution.py
```

This will restore ALL devices to their correct configuration.

---

## Advanced Usage

### Running Multiple Scenarios
You can inject multiple faults sequentially:
```bash
python3 inject_scenario_01.py
# Practice troubleshooting scenario 1
python3 apply_solution.py

python3 inject_scenario_02.py
# Practice troubleshooting scenario 2
python3 apply_solution.py
```

### Batch Fault Injection
To inject all faults at once (advanced):
```bash
for script in inject_scenario_*.py; do
    python3 "$script"
done
```

---

## Troubleshooting the Scripts

### Connection Refused
**Error**: `Could not connect to 127.0.0.1:5001`

**Solutions**:
- Verify GNS3 project is running
- Check device is started in GNS3
- Verify console port mapping in GNS3 project settings

### Script Hangs
**Symptom**: Script connects but doesn't complete

**Solutions**:
- Check device is responsive (test with manual telnet)
- Ensure device isn't stuck at a prompt
- Verify IOS version compatibility

### Commands Not Applied
**Symptom**: Script completes but configuration unchanged

**Solutions**:
- Manually telnet and verify commands work
- Check for IOS syntax differences
- Review script output for error messages

---

## Script Customization

Each script can be customized by editing:
- `CONSOLE_HOST`: Change if using remote GNS3 server
- `CONSOLE_PORT`: Update if ports differ
- `FAULT_COMMANDS`: Modify to inject different faults
- `TIMEOUT`: Adjust if devices are slow to respond

---

## Safety Features

1. **Connection Validation**: Scripts verify connection before applying commands
2. **Error Handling**: Clear error messages if connection fails
3. **Feedback**: Progress output shows exactly what's happening
4. **Restoration**: `apply_solution.py` provides easy rollback

---

## Instructor Notes

These scripts enable:
- **Reproducible Labs**: Same fault every time
- **Time Savings**: No manual misconfiguration needed
- **Focus on Learning**: Students spend time troubleshooting, not breaking configs
- **Assessment**: Standardized scenarios for testing

---

## Next Steps

1. Review the workbook for detailed troubleshooting methodology
2. Run fault injection scripts one at a time
3. Practice systematic troubleshooting approach
4. Verify solutions using the acceptance criteria
5. Check spoiler solutions only after attempting yourself

Happy troubleshooting! 🔧
