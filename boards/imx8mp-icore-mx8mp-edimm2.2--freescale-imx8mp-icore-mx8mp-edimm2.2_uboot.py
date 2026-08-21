# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2_uboot.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2_uboot.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2_uboot.py)
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git
! pip install -q git+https://github.com/antmicro/pyrenode3.git
! renode-run download --renode-variant dotnet-portable

# %% [markdown]
"""## Start Renode"""

# %%
import os
from renode_run import get_default_renode_path
from renode_run.utils import RenodeVariant

os.environ['PYRENODE_RUNTIME'] = 'coreclr'
os.environ['PYRENODE_PATH'] = str(get_default_renode_path(variant=RenodeVariant.DOTNET_PORTABLE))

from pyrenode3.wrappers import Emulation, Monitor, TerminalTester, LEDTester
from Antmicro.Renode.Peripherals.UART import UARTBackend
from Antmicro.Renode.Analyzers import LoggingUartAnalyzer
from System import String

currentDirectory = os.getcwd()
emulation = Emulation()
monitor = Monitor()
emulation.BackendManager.SetPreferredAnalyzer(UARTBackend, LoggingUartAnalyzer)

# %% [markdown]
"""## Setup a script"""

# %%
%%writefile script.resc
logFile $ORIGIN/uboot-renode.log True

$name?="imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2"
$bin?=@https://zephyr-dashboard.renode.io/uboot/527115ef6783cec49e5610c523c124b399011361/imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2/uboot/uboot.elf
$repl?=$ORIGIN/uboot.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/uboot_sim/527115ef6783cec49e5610c523c124b399011361/06854d4d1def596a9a88aa841030c600df2249d3/imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2/uboot/uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump



showAnalyzer uart2

uart2 RecordToAsciinema $ORIGIN/uboot-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "hang" $osPanicHook
cpu0 AddSymbolHook "panic" $osPanicHook


# Spoof the i.MX8M boot ROM: get_boot_device() calls query_boot_infor() through
# the ROM function table at 0x980 (arch/arm/mach-imx/romapi.c).
machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/uboot_sim/527115ef6783cec49e5610c523c124b399011361/06854d4d1def596a9a88aa841030c600df2249d3/imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2/uboot/uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump

# query_boot_infor(info_type=w0, info=x1, xor=w2); w2 is unused, so use it as scratch.
cpu0 AssembleBlock 0x800 """
  movz w2, #1, lsl #16;   // boot_type = BT_DEV_TYPE_SD, boot_instance = 0
  str  w2, [x1];          // *info = boot
  movz w0, #0xf0;         // return ROM_API_OKAY
  ret
"""

# download_image() is SPL-only, but keep the pointer valid.
cpu0 AssembleBlock 0x900 """
  movz w0, #0xf0;
  ret
"""

sysbus WriteQuadWord 0x988 0x900   # struct rom_api.download_image
sysbus WriteQuadWord 0x990 0x800   # struct rom_api.query_boot_infor

cpu0 AddCustomPSCIHandler 0xbf00ff01 # OPTEE_SMC_CALLS_UID
"""
self.SetRegisterUlong(0, 0x0)
"""

macro reset
"""
    cpu0 PSCIEmulationMethod SMC
    # i2c probes of absent PMICs/expanders otherwise burn the host timeout
    cpu0 EnableTimeSkip "mxc_i2c_xfer" 0
    cpu0 EnableTimeSkip "mxc_i2c_probe_chip" 0
    sysbus LoadELF $bin 
    cpu0 EnableUbootMode
    cpu1 EnableUbootMode
    cpu2 EnableUbootMode
    cpu3 EnableUbootMode
    cpu1 IsHalted true
    cpu2 IsHalted true
    cpu3 IsHalted true
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/uboot/527115ef6783cec49e5610c523c124b399011361/imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2/uboot/uboot.dtb 0x00000000402b6b78
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("imx8mp-icore-mx8mp-edimm2.2--freescale-imx8mp-icore-mx8mp-edimm2.2")
terminalTester = TerminalTester(machine.sysbus.uart2, 5)

terminalTester.WaitFor(String("Hit any key to stop autoboot"), includeUnfinishedLine=True, pauseEmulation=True)
terminalTester.Write("\n")
terminalTester.WaitFor(String(">"), includeUnfinishedLine=True, pauseEmulation=True)
terminalTester.WriteLine("version")
terminalTester.WaitFor(String("U-Boot"), pauseEmulation=True)
terminalTester.WaitFor(String(">"), includeUnfinishedLine=True, pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('uboot-asciinema')

# %% [markdown]
"""## Renode metrics analysis"""

# %%
import sys
from pathlib import Path
from renode_run import get_default_renode_path
sys.path.append(str(Path(get_default_renode_path()).parent))

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

metrics.display_metrics(parser)
