# CellStat

CellStat is an open-source electrochemical measurement platform designed for flexible, multi-mode potentiostat/galvanostat experiments. It is built for use with Teensy microcontrollers (specifically the Teensy 3.6) and provides a Python-based GUI for controlling experiments, data acquisition, and analysis.

CellStat is based on the PassStat board design, with additional features and expanded functionality for research and educational use. The system leverages the PassStat hardware as its core, but adds new experiment modes, improved data handling, and a modern user interface.

## Background and Reference
CellStat and PassStat are described and validated in the following thesis:

- Purohit, Dharik (2025) [Optimizing and Validating the Performance of a Low-cost Potentiostat for In-Situ Flow Battery Testing](https://spectrum.library.concordia.ca/id/eprint/995495/). Masters thesis, Concordia University.

This work details the design, optimization, and validation of a low-cost potentiostat tailored for flow battery and general electrochemical testing. The potentiostat features:
- Expanded compliance voltage (±2.5V)
- Dynamic current range selection using a multiplexer
- Enhanced noise filtering for accurate operation in aqueous systems and microelectrode setups
- Two-way pulse testing and battery charge-discharge testing over multiple cycles
- Open-source software and affordable, accessible hardware

The thesis demonstrates that CellStat/PassStat can deliver high-performance, reliable electrochemical measurements, supporting research in renewable energy and battery technology. The design is validated through cyclic voltammetry and other experiments, showing accuracy and flexibility across a range of conditions.

> **Note:** The CellStat project is intended for educational and research use. Users are encouraged to review the thesis and hardware documentation for safety, calibration, and best practices before use in critical applications.

## Project Overview
- **Purpose:** CellStat enables users to perform cyclic voltammetry (CV), square wave voltammetry (SWV), battery testing, and other electrochemical techniques with customizable parameters and real-time data visualization.
- **Architecture:** The system consists of firmware for the Teensy 3.6 board (Arduino-compatible), a Python GUI (using PyQt5 and matplotlib), and calibration/data management utilities.

## Folder Structure

```
CellStat/
├── BATtab.py           # Battery test tab for the GUI
├── cailbration.py      # Calibration constants and functions
├── CVTab.py            # Cyclic Voltammetry tab for the GUI
├── CVtesting.py        # Additional CV testing scripts used for exmaple code given by sorbonne-universite
├── function.py         # Utility functions
├── Main.py             # Main entry point for the GUI application
├── ping.py             # Teensy device detection and communication
├── PULTab.py           # Pulse tab for the GUI
├── Firmware/           # Firmware for Teensy microcontroller
│   └── Cellstat_Firmware/
│       └── Cellstat_Firmware.ino
├── debugging code/     # Experimental and legacy code for debugging
│   ├── CV_SWV_new.ino
│   ├── CV_SWV/
│   ├── CV_SWV_new/
│   ├── motor_board_test/
│   └── old code/
├── Teensy_DAC_ADC/     # Teensy DAC/ADC test firmware
│   ├── Teensy_DAC_ADC.ino
│   ├── sketch_nov13a/
│   └── Teensy_DAC_ADC_new/
├── Dharik_PassStat (2024-05-19 11-17-21 PM)/ # PCB and project files
│   ├── CAMtastic1.Cam
│   ├── ...
│   └── PassStat.SchDoc
├── LICENSE.txt         # License file
└── OCV.py              # Open Circuit Voltage script
```

## Key Folders and Files

- **CellStat/**: Main source code for the GUI and experiment logic.
- **Firmware/Cellstat_Firmware/**: Arduino/Teensy firmware for controlling the potentiostat hardware.
- **debugging code/**: Contains experimental, legacy, and test scripts for development and troubleshooting.
- **Teensy_DAC_ADC/**: Firmware and test code for DAC/ADC features on Teensy boards.
- **Dharik_PassStat .../**: PCB design files and project documentation.
- **cailbration.py**: Calibration constants and routines for accurate measurements.
- **CVTab.py, PULTab.py, SWVTab.py, BATtab.py**: GUI tabs for different experiment types.
- **Main.py**: Main application launcher for the CellStat GUI.
- **ping.py**: Device detection and communication utilities.

## Getting Started
1. **Install dependencies:**
   - Python 3.x
   - PyQt5
   - matplotlib
   - pyserial
2. **Upload firmware:**
   - Flash the appropriate firmware to your Teensy board from the `Firmware/Cellstat_Firmware/` folder.
3. **Run the GUI:**
   - Execute `python Main.py` to launch the CellStat application.
4. **Connect your hardware:**
   - Plug in your Teensy-based potentiostat and select the appropriate port when prompted.

## Community and Contributions

Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request on GitHub. For questions or collaboration, see the contact information in the thesis or open an issue in this repository.

## Citation
If you use CellStat or PassStat in your research, please cite the thesis above and reference this repository.

## License
See `LICENSE.txt` for details.

---

