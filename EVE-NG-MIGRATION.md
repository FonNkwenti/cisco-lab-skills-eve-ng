# EVE-NG Migration Guide

Migrating from GNS3/Apple Silicon to EVE-NG on Dell Latitude 5540 (Windows).

---

## Context

| Item | Old setup | New setup |
|---|---|---|
| Machine | MacBook (Apple Silicon) | Dell Latitude 5540 — i7-1370P, 64 GB RAM |
| Platform | GNS3 + Dynamips | EVE-NG Community/Pro |
| Images | c7200, c3725 only | Full portfolio (IOSv, IOS-XRv, NX-OS, CSR1000v, ASAv, …) |
| Blocker | Apple Silicon has no Intel VT-x | Intel KVM/QEMU unlocked |

---

## Phase 1 — Windows Machine Setup

### 1.1 Install core tools

- [ ] Download and install **Git for Windows**: https://git-scm.com/download/win
- [ ] Download and install **Windows Terminal** (Microsoft Store or winget)
- [ ] Download and install **VS Code**: https://code.visualstudio.com
  - Install extensions: `ms-vscode.powershell`, `yzhang.markdown-all-in-one`
- [ ] Download and install **Node.js LTS** (needed for Claude Code CLI): https://nodejs.org

### 1.2 Install Claude Code

```powershell
npm install -g @anthropic-ai/claude-code
```

Verify:

```powershell
claude --version
```

### 1.3 Clone repos

```powershell
# Create workspace
mkdir C:\Lab
cd C:\Lab

# Reference repo (read-only going forward)
git clone https://github.com/<your-org>/cisco-lab-skills.git

# New EVE-NG repo (active development)
git clone https://github.com/<your-org>/cisco-lab-skills-eveng.git
```

> Replace `<your-org>` with your GitHub username or org.

---

## Phase 2 — EVE-NG Installation

### 2.1 Choose deployment model

EVE-NG runs on Ubuntu Server. Two options:

| Option | Pros | Cons |
|---|---|---|
| **Bare-metal on Dell** | Maximum performance, KVM native | Windows no longer boots natively |
| **Hyper-V VM on Windows** | Keep Windows, nested virt | ~10–15% overhead, nested virt quirks |
| **VMware Workstation VM** | Best nested-virt support | Paid licence |

**Recommended:** Bare-metal Ubuntu dual-boot OR VMware Workstation if you need Windows.

### 2.2 Download EVE-NG

- Community ISO: https://www.eve-ng.net/index.php/download/
- Use **EVE-NG Community** (free) to start; upgrade to Pro for multi-user/iol support.

### 2.3 Bare-metal install (Ubuntu)

```bash
# After booting from ISO, follow Ubuntu Server install wizard
# Then run EVE-NG bootstrap:
wget -O - https://www.eve-ng.net/repo/install-eve.sh | bash -i
```

Reboot, then navigate to `http://<eve-ng-ip>` from your browser (default creds: `admin / eve`).

### 2.4 VMware Workstation install (alternative)

1. Create VM: Ubuntu 22.04 LTS, 8+ vCPUs, 32+ GB RAM, 200+ GB disk.
2. Enable: **Virtualize Intel VT-x/EPT** in VM settings.
3. Run same bootstrap script above after OS install.

---

## Phase 3 — Cisco Images

### 3.1 Source images

Images repository (community-sourced): https://github.com/hegdepavankumar/Cisco-Images-for-GNS3-and-EVE-NG

Priority images to download first:

| Image | Type | Use |
|---|---|---|
| `vios-adventerprisek9-m.vmdk` | IOSv | CCNA/CCNP routing |
| `vios_l2-adventerprisek9-m.vmdk` | IOSvL2 | Switching labs |
| `CSR1000v` | CSR | Advanced IOS-XE |
| `IOS-XRv` | XRv | ENARSI / SP labs |
| `NX-OSv` | NXOS | Data-centre labs |
| `ASAv` | ASAv | Firewall labs |

### 3.2 Upload images to EVE-NG

```bash
# SCP from Windows to EVE-NG server
scp vios-adventerprisek9-m.vmdk root@<eve-ng-ip>:/opt/unetlab/addons/qemu/vios-<version>/
```

Or use **WinSCP** (GUI) for bulk transfers.

### 3.3 Fix permissions

```bash
# Run on EVE-NG after every image upload
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions
```

---

## Phase 4 — New Repo Bootstrap

### 4.1 Create `cisco-lab-skills-eveng` on GitHub

```bash
# On Windows, after cloning cisco-lab-skills:
cd C:\Lab
cp -r cisco-lab-skills cisco-lab-skills-eveng
cd cisco-lab-skills-eveng

git remote remove origin
gh repo create cisco-lab-skills-eveng --public --source=. --push
```

### 4.2 Content to carry over (~70%)

These directories are platform-agnostic and should be copied as-is:

- `lab-workbook-creator/` — workbook generation skill
- `drawio/` — diagram skill
- `spec-creator/` — topic spec generation
- `lab-builder/` — lab generation orchestrator
- `cisco-troubleshooting-1/`
- `fault-injector/`
- `mega-capstone-creator/`
- `LESSONS_LEARNED.md`
- `skills/` — all universal skills

### 4.3 Content to replace (~30%)

| Old (GNS3) | New (EVE-NG) |
|---|---|
| `gns3/` directory | New `eve-ng/` directory |
| GNS3 API calls | EVE-NG REST API (`/api/labs`, `/api/nodes`) |
| Dynamips node types | QEMU node types |
| `.gns3` project files | `.unl` topology files |
| GNS3 SSH connect logic | EVE-NG console/telnet logic |

### 4.4 Remove GNS3 artifacts

```bash
rm -rf gns3/
# Update README.md to reflect EVE-NG
# Update any skill files that reference GNS3
```

---

## Phase 5 — EVE-NG Skill Layer ✓ COMPLETE

`eve-ng/SKILL.md` has been created in this repo. It covers:

- Section 1: Host architecture (Dell i7-1370P, KVM/QEMU)
- Section 2: Platform selection guide (IOSv, IOSvL2, CSR1000v, IOL, XRv 9000, NX-OSv, ASAv)
- Section 3: Hardware templates with interface maps per platform
- Section 4: VPC node reference
- Section 5: Console access (REST API discovery, HTML5, SecureCRT, telnet)
- Section 6: Design rules for lab generation
- Section 7: Common issues and solutions

EVE-NG API base URL: `http://<eve-ng-ip>/api/`

Key endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/login` | POST | Authenticate |
| `/api/labs` | GET/POST | List or create labs |
| `/api/labs/<lab>/nodes` | GET/POST | List or add nodes — returns dynamic telnet ports |
| `/api/labs/<lab>/nodes/<id>/start` | GET | Start a node |
| `/api/labs/<lab>/nodes/<id>/stop` | GET | Stop a node |

---

## Phase 6 — Verification Checklist

Before calling migration complete:

- [ ] EVE-NG web UI loads at `http://<eve-ng-ip>`
- [ ] At least one IOSv node starts and reaches CLI
- [ ] SSH/console from Windows Terminal to a running node works
- [ ] `cisco-lab-skills-eveng` repo cloned on Dell and Claude Code runs
- [ ] One existing lab workbook generates correctly in new repo
- [ ] Drawio skill produces a diagram in the new repo

---

## Reference Links

- EVE-NG documentation: https://www.eve-ng.net/index.php/documentation/
- EVE-NG REST API: https://www.eve-ng.net/index.php/documentation/howtos/how-to-eve-ng-api/
- Cisco images repo: https://github.com/hegdepavankumar/Cisco-Images-for-GNS3-and-EVE-NG
- EVE-NG community forum: https://www.eve-ng.net/index.php/community/
