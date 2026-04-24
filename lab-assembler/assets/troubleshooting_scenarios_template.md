# Troubleshooting Scenarios Template

This template provides a complete example of the required troubleshooting scenarios section for lab workbooks. Each workbook MUST include at least 3 scenarios following this format.

---

## 8. Troubleshooting Scenarios

> 🔧 **Practice Makes Perfect**: These scenarios test your ability to diagnose and resolve common [PROTOCOL] misconfigurations. Try to solve them WITHOUT looking at the solutions first!

---

### Scenario 1: Autonomous System / Protocol Instance Mismatch

**Problem Statement:**
After a recent configuration change by a junior administrator, R2 is no longer forming an adjacency with R1. When you run `show ip eigrp neighbors` on R1, there is no neighbor entry for the Fa1/0 interface. Upon reviewing R2's configuration, you notice that it shows `router eigrp 200` instead of the expected AS 100.

**Mission:**
1. Identify why the adjacency failed using appropriate show or debug commands (e.g., `show ip protocols`, `debug eigrp packets hello`)
2. Correct the misconfiguration on R2 to align with the network design standard (AS 100)
3. Verify that the EIGRP adjacency is successfully re-established
4. Confirm that routes are being properly exchanged between routers

**Success Criteria:**
- [ ] `show ip eigrp neighbors` on R1 displays R2 (10.0.12.2) as a neighbor on interface Fa1/0
- [ ] `show ip protocols` on R2 confirms "Routing Protocol is eigrp 100"
- [ ] `show ip route eigrp` on R1 displays routes learned from R2
- [ ] Ping test from R1's Loopback0 (1.1.1.1) to R2's Loopback0 (2.2.2.2) succeeds with 100% success rate

**Solution:**

<details>
<summary>⚠️ SPOILER ALERT - Click to reveal solution</summary>

**Root Cause:** 
EIGRP routers only form adjacencies when they are configured with **matching Autonomous System (AS) numbers**. In this scenario, R2 was configured with AS 200 while R1 uses AS 100. The mismatch prevents the Hello packets from being processed, and the adjacency cannot form.

**Fix Configuration:**
```bash
R2# configure terminal
R2(config)# no router eigrp 200
R2(config)# router eigrp 100
R2(config-router)# eigrp router-id 2.2.2.2
R2(config-router)# network 2.2.2.2 0.0.0.0
R2(config-router)# network 10.0.12.0 0.0.0.3
R2(config-router)# network 10.0.23.0 0.0.0.3
R2(config-router)# passive-interface Loopback0
R2(config-router)# no auto-summary
R2(config-router)# end
R2# write memory
```

**Verification Output:**
```bash
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:00:25   25   200  0  3

R1# ping 2.2.2.2 source 1.1.1.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2.2.2.2, timeout is 2 seconds:
Packet sent with a source address of 1.1.1.1
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms
```

**Why This Works:**
Once both routers are configured with the same AS number (100), they can properly process each other's Hello packets, establish the neighbor relationship, and exchange routing information.

</details>

---

### Scenario 2: Passive Interface Misconfiguration

**Problem Statement:**
R3 has been configured with EIGRP AS 100 and all network statements look correct. However, R2 cannot see R3 as a neighbor on the Fa0/1 interface. When checking R3's configuration, you notice that `passive-interface default` has been configured, along with a `no passive-interface Loopback0` command.

**Mission:**
1. Determine which interfaces on R3 are passive using `show ip protocols`
2. Identify why the adjacency with R2 is not forming
3. Correct the passive interface configuration to allow adjacencies on transit links while suppressing EIGRP Hellos on Loopback0
4. Verify the adjacency is established

**Success Criteria:**
- [ ] `show ip eigrp neighbors` on R2 displays R3 (10.0.23.2) as a neighbor on Fa0/1
- [ ] `show ip protocols` on R3 shows Loopback0 as passive, but Fa0/0 is NOT passive
- [ ] `show ip eigrp interfaces` confirms that Fa0/0 is actively sending/receiving EIGRP packets
- [ ] End-to-end ping from R2 to R3's Loopback0 succeeds

**Solution:**

<details>
<summary>⚠️ SPOILER ALERT - Click to reveal solution</summary>

**Root Cause:**
The `passive-interface default` command makes ALL interfaces passive by default. The administrator then used `no passive-interface Loopback0` intending to activate it, but this is backwards logic. Loopback interfaces SHOULD be passive (to prevent unnecessary EIGRP Hellos), while transit interfaces like FastEthernet0/0 should be ACTIVE to form adjacencies.

**Fix Configuration:**
```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# no passive-interface default
R3(config-router)# passive-interface Loopback0
R3(config-router)# end
R3# write memory
```

**Verification Output:**
```bash
R3# show ip protocols
*** IP Routing is NSF aware ***

Routing Protocol is "eigrp 100"
  ...
  Passive Interface(s):
    Loopback0
  ...

R2# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
1   10.0.23.2               Fa0/1                    12 00:00:08   40   240  0  5
0   10.0.12.1               Fa0/0                    13 00:05:22   25   200  0  3

R2# ping 3.3.3.3 source 2.2.2.2
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 3.3.3.3, timeout is 2 seconds:
Packet sent with a source address of 2.2.2.2
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/3/8 ms
```

**Why This Works:**
Removing `passive-interface default` allows all interfaces to send EIGRP Hellos by default. Then explicitly configuring `passive-interface Loopback0` suppresses Hellos only on the loopback interface, which is the desired behavior.

</details>

---

### Scenario 3: Missing Network Statement

**Problem Statement:**
R1 has been configured with EIGRP AS 100, and you can see that R2 is appearing as a neighbor. However, when you check R2's routing table, you notice that R1's Loopback0 (1.1.1.1/32) is NOT being advertised into EIGRP. R1's configuration shows the following network statements:
- `network 10.0.12.0 0.0.0.3`

The Loopback0 network statement is missing.

**Mission:**
1. Verify which networks are being advertised by R1 using `show ip protocols`
2. Identify why the Loopback0 network is not being advertised
3. Add the appropriate network statement to advertise R1's Loopback0 (1.1.1.1/32) into EIGRP
4. Verify that R2 and R3 now have a route to 1.1.1.1/32

**Success Criteria:**
- [ ] `show ip protocols` on R1 lists both 1.1.1.1/32 and 10.0.12.0/30 as advertised networks
- [ ] `show ip route eigrp` on R2 displays an entry for 1.1.1.1/32 learned via EIGRP
- [ ] `show ip route eigrp` on R3 displays an entry for 1.1.1.1/32 learned via EIGRP
- [ ] Ping from R3's Loopback0 (3.3.3.3) to R1's Loopback0 (1.1.1.1) succeeds

**Solution:**

<details>
<summary>⚠️ SPOILER ALERT - Click to reveal solution</summary>

**Root Cause:**
EIGRP only advertises networks that are explicitly included in a `network` statement under the EIGRP configuration. Since R1's configuration was missing the `network 1.1.1.1 0.0.0.0` statement, the Loopback0 interface was never enabled for EIGRP, and its route was not advertised to neighbors.

**Fix Configuration:**
```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# network 1.1.1.1 0.0.0.0
R1(config-router)# end
R1# write memory
```

**Verification Output:**
```bash
R1# show ip protocols
*** IP Routing is NSF aware ***

Routing Protocol is "eigrp 100"
  ...
  Routing for Networks:
    1.1.1.1/32
    10.0.12.0/30
  Passive Interface(s):
    Loopback0
  ...

R2# show ip route eigrp
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       ...

      1.0.0.0/32 is subnetted, 1 subnets
D        1.1.1.1 [90/130560] via 10.0.12.1, 00:00:15, FastEthernet0/0
      2.0.0.0/32 is subnetted, 1 subnets
C        2.2.2.2 is directly connected, Loopback0
      3.0.0.0/32 is subnetted, 1 subnets
D        3.3.3.3 [90/158720] via 10.0.23.2, 00:05:45, FastEthernet0/1
      10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks
C        10.0.12.0/30 is directly connected, FastEthernet0/0
...

R3# ping 1.1.1.1 source 3.3.3.3
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 1.1.1.1, timeout is 2 seconds:
Packet sent with a source address of 3.3.3.3
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 4/6/12 ms
```

**Why This Works:**
Adding the `network 1.1.1.1 0.0.0.0` statement enables EIGRP on the Loopback0 interface. The wildcard mask `0.0.0.0` creates an exact match, ensuring only the specific /32 address is included. Once enabled, EIGRP advertises this connected route to all neighbors (R2), which in turn advertises it to R3.

</details>

---

## Best Practices for Scenario Creation

When creating troubleshooting scenarios for your labs:

1. **Make them realistic**: Base scenarios on actual mistakes that students commonly make
2. **Progressive difficulty**: Start with simpler issues (AS mismatch) and progress to more subtle problems (wrong wildcard masks)
3. **Diverse categories**: Cover different aspects of the protocol (neighbor formation, route advertisement, optimization)
4. **Clear symptoms**: Describe observable symptoms rather than immediately pointing to the solution
5. **Guided discovery**: Mission steps should guide students through proper troubleshooting methodology
6. **Measurable success**: Acceptance criteria should be objective and verifiable
7. **Educational solutions**: Explanations should teach the "why" not just the "how"
8. **Include verification**: Always show the commands and outputs that prove the fix worked

## Additional Scenario Ideas by Protocol

### EIGRP:
- K-value mismatch preventing adjacency
- Incorrect stub configuration blocking routes
- Wrong wildcard mask matching unintended interfaces
- Authentication key mismatch
- Split-horizon blocking route propagation in DMVPN

### OSPF:
- Area ID mismatch
- Network type mismatch (broadcast vs point-to-point)
- MTU mismatch preventing database synchronization
- Stub area configuration blocking external routes
- Missing virtual link between non-backbone areas

### BGP:
- AS number mismatch (eBGP vs iBGP)
- Missing neighbor update-source loopback
- Route filtering blocking necessary prefixes
- Next-hop reachability issues
- Maximum prefix limit triggering shutdown

### Spanning Tree:
- Root bridge priority misconfiguration
- PortFast on trunk ports causing loops
- BPDU Guard disabling ports unnecessarily
- Incorrect path cost causing suboptimal forwarding

### VLANs/Trunking:
- Native VLAN mismatch
- Allowed VLAN list blocking necessary VLANs
- Wrong encapsulation type (ISL vs 802.1Q)
- Access port configured on trunk link
