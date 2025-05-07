# 🛰️ Shadytel SIM Tools — Enhanced Fork for OTA & BIP-enabled SIMs

## 📌 Overview

This repository is a **modernized and enhanced fork** of the original [Shadytel SIM Tools](https://git.osmocom.org/sim/sim-tools/), adapted specifically for working with **secure SIM cards** such as the [sysmoUSIM-SJS1](https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoUSIM-SJS1), which require **KIC/KID authentication and encryption** for Remote Application Management (RAM) operations.

This project was developed as part of a **Final Degree Project (TFG)** in Computer Engineering, focusing on SIM Toolkit interaction, OTA secure messaging, and BIP (Bearer Independent Protocol) communication in embedded telecom systems.

> ℹ️ The original project by the Osmocom community is the foundation for this fork. All credits and licensing are preserved.

---
## 🔧 Key Features and Enhancements

- ✅ Fully updated to **Python 3 (3.12+)** — The original `shadysim` codebase has been ported from legacy Python 2.7 to Python 3, ensuring compatibility with modern interpreters and dependency management via an updated `requirements.txt`.
  
- 🔁 **Proactive Command Handling (FETCH/ENVELOPE)** — Introduced complete support for proactive SIM interactions by implementing a dedicated `FetchProactiveHandler` class, which dynamically parses `FETCH` commands and interprets their TLV contents according to [ETSI TS 102 223](https://www.etsi.org/deliver/etsi_ts/102200_102299/102223/16.00.00_60/ts_102223v160000p.pdf). This enables real-time processing of commands such as `Send Short Message`, `Open Channel`, and `Display Text`.

- 📡 **Advanced OTA Padding Strategy** — OTA command encryption now uses a **dynamic padding algorithm** in compliance with [ETSI TS 102 225](https://www.etsi.org/deliver/etsi_ts/102200_102299/102225/15.00.00_60/ts_102225v150000p.pdf) Section 4.4.3. The padding length is automatically calculated to meet the block size requirements of **Triple DES in outer-CBC mode**, depending on the length of the encrypted payload, CNTR, and SPI configuration. This ensures compliance with secure OTA message standards.

- 🧱 Optimized applet upload via **adjustable chunk/block size** — Resolved issues with `6A86 (Incorrect parameters P1-P2)` errors during CAP installation by tuning the upload block size from `0xB0` to `0xBC`, accommodating payload boundaries more accurately based on actual card buffer capacity and response parsing feedback.

- 🧩 Enhanced INSTALL [Install] command customization — Support for extended toolkit parameters including `--max-bip-channel` has been added following the **Trusted Connectivity Alliance StepStones v6** guidelines (Section 17.2.3). The command is now capable of injecting BIP configuration settings dynamically into the `INSTALL` command, improving runtime BIP session management and compatibility.

- 🧰 CLI Tools Refactored — The command-line interface has been restructured for better modularity and support for runtime options such as APDU wrapping, encrypted/envelope construction, custom AIDs, and toolkit configuration overrides.

- 🧪 Proactive Command Simulation Suite — Added test hooks for triggering and observing `FETCH`, `TERMINAL RESPONSE`, and `ENVELOPE` behaviors within the STK runtime, useful for debugging applet logic and OTA provisioning workflows.

> 📘 These enhancements ensure full compliance with JavaCard 2.2.1, TS 102 223/225/226, and StepStones OTA deployment architecture. The loader is now capable of managing complex proactive interactions, security layers, and robust applet installation workflows on compliant UICCs.

---

## 📁 Project Structure

```
.
├── sim-tools/                          # Root directory for SIM applet tooling
│   ├── javacard/                       # JavaCard STK applet source code (HelloSTK3 or custom)
│   │   └── build/                      # Output folder for CAP files and EXP exports
│   └── shadysim/                       # Updated APDU deployment tool (Python 3)
│       ├── shadysim.py                 # Main CLI script for interacting with the SIM/UICC
│       ├── FetchProactiveHandler.py   # Proactive SIM command handler (FETCH/ENVELOPE interpreter)
│       └── pysim/                      # Updated PySim transport layer and utility libraries
└── README.md                           # Project documentation and usage guide
```

---

## 🚀 Quickstart Guide

To get started with deploying a SIM Toolkit applet using the updated `shadysim` tool, follow the steps below:

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/sim-tools.git
cd sim-tools/shadysim
```

### 2. Create and Activate a Python 3 Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. List Existing Applets on the SIM

This command connects to the card via PC/SC and shows currently installed applets:

```bash
python3 shadysim.py \
  --pcsc \
  --kic <YOUR_KIC_HEX> \
  --kid <YOUR_KID_HEX> \
  --list-applets
```

> Replace `<YOUR_KIC_HEX>` and `<YOUR_KID_HEX>` with your secure OTA keys.

### 5. Install a JavaCard Applet with STK and BIP Support

Use the following command to load your compiled `.cap` file and install the applet with full SIM Toolkit capabilities including BIP:

```bash
  python3 shadysim.py \
  --pcsc \
  -l /path/to/your/build/my-applet.cap \
  -i /path/to/your/build/my-applet.cap \
  --enable-sim-toolkit \
  --module-aid <YOUR_MODULE_AID_HEX> \
  --instance-aid <YOUR_INSTANCE_AID_HEX> \
  --nonvolatile-memory-required 0100 \
  --volatile-memory-for-install 0100 \
  --max-menu-entry-text 15 \
  --max-menu-entries 05 \
  --max-bip-channel 4 \
  --access-domain 00 \
  --max-timers 2 \
  --kic <YOUR_KIC_HEX> \
  --kid <YOUR_KID_HEX>
```

### 6. Verify Installed Applets

```bash
  python3 shadysim.py \
  --pcsc \
  --kic <YOUR_KIC_HEX> \
  --kid <YOUR_KID_HEX> \
  --list-applets
```

### 7. Delete a Previously Installed Applet

To delete an applet by its AID:

```bash
  python3 shadysim.py \
  --pcsc \
  --kic <YOUR_KIC_HEX> \
  --kid <YOUR_KID_HEX> \
  --delete <APPLET_AID_PREFIX>
```

> Example: `--delete 177002ca41` will match any applet whose AID starts with that prefix.

---

With this setup, you can list, install, test, and remove applets from any JavaCard-compliant SIM using the modernized Python 3 toolchain.

---

## 🛠️ Technologies and Specs

- **JavaCard API 2.2.1**
- **UICC/STK APIs** (`uicc.toolkit`, `uicc.access`)
- **OTA Secure Messaging (RAM over SMS)** with KIC/KID
- **ETSI TS 102 221 / 223 / 241**
- **3GPP TS 31.101 / 31.102 / 31.111**
- **Python 3.x**, PC/SC libraries
- **Custom JavaCard build via ant-javacard**
- **CAP deployment tools** from Osmocom + custom extensions

---
## 🛠️ Troubleshooting and Important Considerations

During the development and deployment process using `shadysim` with `pysim` and a JavaCard applet, several critical issues were identified and resolved:

### 1. Block Size Issue During CAP File Installation

Initially, the script failed while loading the CAP file at block 37 with the following error:

```
RX DATA: 027100000e0a00000000000000000000016a86
RuntimeError: SW match failed! Expected 9000 and got 6a86.
```

It was identified that this was **not due to another APDU failing**, but rather the `6A86` status word (Incorrect P1/P2) was returned within the same `RX DATA` of the last `LOAD` block. The block was shorter than usual, leading to internal padding or encoding issues.

**Solution applied**:
- The CAP loader's block size was reduced from `0xd0` (208 bytes) to `0xbc` (188 bytes), ensuring all blocks respect maximum allowable APDU size.
- This change fixed the `6A86` error and allowed full applet installation.

---

### 2. Automatic FETCH Handling for SIM Toolkit Responses

After upgrading `pysim`, proactive commands such as `SendShortMessage` began triggering automatic `FETCH` sequences. However, `shadysim` originally performed manual handling of `SW=91XX` and `SW=9FXX`.

**Problem**:
- New versions of `pysim` expect applications to handle `FETCH` and envelope responses via `send_apdu_checksw`.
- The previous implementation caused command parsing errors and lost state across commands.

**Solution applied**:
- A new `FetchProactiveHandler` class was implemented, replacing the manual FETCH logic.
- This handler manages:
  - Intercepting `91XX` and `9FXX` status words
  - Issuing the correct `FETCH` or `GET RESPONSE` commands
  - Delegating parsing to modular functions (`parse_responsedata`, `parse_envelope_responsedata`)

This allows flexible decoding of proactive commands and reusability across multiple toolkit events.

---

### 3. 🧠 SMS TPDU Structure Interpretation

Parsing the `SendShortMessage` proactive command required full understanding of the **GSM 03.40 SMS-TPDU format**, especially for analyzing embedded SMS headers.

#### Fields Parsed:
| Field      | Description                                                        |
|------------|--------------------------------------------------------------------|
| `TP-MTI`   | Message Type Indicator (e.g., 01 = SMS-SUBMIT)                    |
| `TP-RP`    | Reply Path                                                        |
| `TP-UDHI`  | User Data Header Indicator                                        |
| `TP-VPF`   | Validity Period Format                                            |
| `TP-DA`    | Destination Address (BCD encoded)                                 |
| `TP-PID`   | Protocol Identifier                                                |
| `TP-DCS`   | Data Coding Scheme                                                |
| `TP-UDL`   | User Data Length                                                  |
| `TP-UD`    | User Data                                                         |

For example, an SMS TPDU like `1100...` is parsed as:
- `TP-MTI = 01` (SMS-SUBMIT)
- `TP-RD = 0` (Reject Duplicates)
- `TP-VPF = 0` (no validity period)
- Destination number and payload encoded in semi-octet format

> 📌 **Note**: The decoding logic and structural understanding were based on:
> • [ETSI TS 123 140 – SIM Toolkit for UICC](https://www.etsi.org/deliver/etsi_ts/123000_123099/123040/18.00.00_60/ts_123040v180000p.pdf)  
> • [3GPP TS 23.040 – Technical realization of SMS (GSM 03.40)](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=749)  
> • [pysim source code](https://github.com/osmocom/pysim)

### 4. OTA Ciphering & Padding Handling (Triple DES, SPI, TAR)

The OTA message building logic was enhanced to support padding and cryptographic constraints described in **ETSI TS 102 225** and **TS 102 226**.

**Improvements included**:
- SPI first octet parsed to determine integrity and ciphering modes:
  - `00`: No integrity
  - `01`: Redundancy Check (RC, 4 bytes)
  - `02`: Cryptographic Checksum (CC, 8 bytes)
- Proper calculation of padding based on DES3 block size.
- Support for ciphering using:
  - **Triple DES in outer-CBC mode with two different keys** (as required for CC)
- Dynamic adjustment of KIC and KID fields based on SPI bits.

This ensured the envelope complied with real-world OTA formats, especially for secure remote provisioning.

---

### 5. BIP Channel Initialization

After installation of the applet, the BIP (Bearer Independent Protocol) channel was not initialized correctly.

**Issue**:
- The JavaCard applet did not expose any BIP channels because the install parameters lacked this configuration.

**Solution applied**:
- `--max-bip-channel` flag was added to the CLI tool, and its logic was integrated into the install parameters.

```python
toolkit_params = ...
toolkit_params += ('%02x' % args.max_bip_channel)
```

This allowed the applet to support up to 4 concurrent BIP channels (or more, if configured), enabling commands like `Open Channel`, `Send Data`, and `Close Channel`.
> **📘 Reference**: *Interoperability Stepping Stones Release 6*,  
> Section **17.2.3 – INSTALL(Install) Command**,  
> Table: **Toolkit application specific parameters**  
> [Click here to view the document](https://trustedconnectivityalliance.org/wp-content/uploads/2020/01/StepStonesRelease6_v100.pdf)

These enhancements ensure compatibility with OTA provisioning protocols, full toolkit event handling, and secure applet deployment within JavaCard 2.2.1 environments.

---

## 📚 References and Credits

The development and debugging process of this SIM Toolkit loader and installer has been guided by the following standards, open-source tools, and community contributions:

- **Trusted Connectivity Alliance (for erly SIM Alliance)**:
  - [*Interoperability Stepping Stones Release 6*](https://trustedconnectivityalliance.org/wp-content/uploads/2020/01/StepStonesRelease6_v100.pdf) — Especially section 17.2.3 `INSTALL [Install]` was used to understand and inject extended parameters such as `max-bip-channel` during toolkit applet installation via the INSTALL command structure.

- **ETSI (European Telecommunications Standards Institute)**:
  - [TS 102 221 — UICC-Terminal Interface](https://www.etsi.org/deliver/etsi_ts/102200_102299/102221/16.02.00_60/ts_102221v160200p.pdf)
  - [TS 102 223 — SIM Application Toolkit (STK)](https://www.etsi.org/deliver/etsi_ts/102200_102299/102223/16.00.00_60/ts_102223v160000p.pdf)
  - [TS 102 225 — OTA Security Mechanisms](https://www.etsi.org/deliver/etsi_ts/102200_102299/102225/15.00.00_60/ts_102225v150000p.pdf)
  - [TS 102 226 — OTA Application Download](https://www.etsi.org/deliver/etsi_ts/102200_102299/102226/15.00.00_60/ts_102226v150000p.pdf)

- **3GPP (3rd Generation Partnership Project)**:
  - [TS 31.101 — UICC-Terminal Physical/Logical Interface](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=1525)
  - [TS 31.102 — USIM Application Characteristics](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=1526)
  - [TS 31.111 — USIM Application Toolkit (USAT)](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=1586)

- **Osmocom Project**:
  - [Osmocom SIM Tools](https://git.osmocom.org/sim/sim-tools/) — Base project forked and extended for proactive command handling, with support for Python 3 and custom proactive handlers.
  - [Osmocom HelloSTK](https://git.osmocom.org/sim/hello-stk/) — Minimal applet template and STK command handling logic.

- **pySim (modernized version)**:
  - [https://github.com/osmocom/pysim](https://github.com/osmocom/pysim) — Used as base for integrating `send_apdu_checksw` behavior, proactive command handling via `ProactiveHandler`, and internal APDU flow with `FETCH` and `TERMINAL RESPONSE` structures.

- **Protocol Implementation Notes**:
  - Proactive command responses are parsed using internal handlers (`ProactiveHandler`) by decoding `FETCH` APDU contents including `SMS_TPDU`, `TP-MTI`, `TP-VPF`, and User Data Headers (UDHL).
  - Response parsing logic references TPDU structure as described in ETSI TS 102 223 and the format outlined by `StepStones Release 6`, including `RPL`, `RHL`, and status bytes for OTA.

- **Smart Card Readers Tested**:
  - HID Omnikey 6121 ([hidglobal.com](https://www.hidglobal.com/products/readers/omnikey/6121))

> **Note:** All parameter encoding, APDU wrapping, and proactive response parsing were implemented in accordance with the above standards and specifications. This ensures proper interoperability with JavaCard 2.2.1 environments and STK-compliant UICCs.

---

## ⚖️ License and Usage

This project is open for **educational and research use only**. Please respect the original licenses from Osmocom and cite both the original and modified works when reusing code or structures.

- **Original Authors**: Osmocom Community  
- **Enhanced by**: Rafael Moreno Campos
- **GitHub**: [https://github.com/ramosaurio](https://github.com/ramosaurio)

---

## 📜 Changelog

### v1.0 — Initial Release

- Migrated entire `shadysim` toolset from Python 2.7 to Python 3.12 with updated syntax, UTF-8 support, and improved compatibility.
- Refactored and modularized the CLI logic into `shadysim.py` and `FetchProactiveHandler.py` to support modern SIM Toolkit workflows.
- Integrated proactive command handling (`FETCH`, `ENVELOPE`, `TERMINAL RESPONSE`) using a custom `FetchProactiveHandler` class.
- Implemented full support for parsing complex OTA SMS structures:
  - TPDU decoding (TP-UDL, TP-MTI, TP-VPF)
  - RPL (Response Payload Length), RHL (Response Header Length), TAR, CNTR, PCNTR
- Dynamically calculated padding based on encryption (3DES-CBC) and SPI configuration according to ETSI TS 102 225 & 226.
- Added support for `--max-bip-channel` in the `INSTALL [for install]` command using StepStones Release 6 (Section 17.2.3) as reference.
- Improved handling of APDU `6A86` errors during CAP loading by adjusting block sizes (`LOAD` block size set to `0xBC`).
- Modernized and cleaned `requirements.txt` for compatibility with `venv` + pip-based environments.
- Project structure reorganization:
  - `shadysim/` → contains updated CLI, proactive handler and embedded `pysim` fork.
  - `javacard/` → JavaCard STK applet source and CAP builds.
- Enhanced logging and debug trace to visualize SIM proactive responses and fetch flow during OTA interaction.
- Verified working deployment with real hardware:
  - `sysmoUSIM-SJS1` cards
  - NOX and HID Omnikey 6121 PCSC-compatible readers
---

## 👨‍💻 Author

- **Name**: Rafael Moreno Campos
- **Email**: rmoreno.morcam@gmail.com
- **Project**: Final Degree Project (TFG) - Computer Engineering

---

