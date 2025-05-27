# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/lx2160ardb_tfa_stmm--fsl-lx2160a-rdb_uboot.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/lx2160ardb_tfa_stmm--fsl-lx2160a-rdb_uboot.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/lx2160ardb_tfa_stmm--fsl-lx2160a-rdb_uboot.py)
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
os.environ['PYRENODE_BIN'] = get_default_renode_path(variant=RenodeVariant.DOTNET_PORTABLE)

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

using sysbus
$name?="lx2160ardb_tfa_stmm--fsl-lx2160a-rdb"
mach create $name

machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/uboot_sim/2ca1398a5ece8d33d8feb6b410e6e38588b5d2bc/327f86675b49497a02301a95de5220ccc7bab67d/lx2160ardb_tfa_stmm--fsl-lx2160a-rdb/uboot/uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart0

uart0 RecordToAsciinema $ORIGIN/uboot-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "hang" $osPanicHook
cpu0 AddSymbolHook "panic" $osPanicHook


# This handler stubs the `smc` SIP call 0xff12 (SIP_SVC_MEM_BANK)
# atf implementation can be found here:
# https://github.com/Xilinx/arm-trusted-firmware/blob/e4a37b000fb9a708112da1e06da0e8fad939dc86/plat/nxp/common/sip_svc/sip_svc.c#L115
# Basically it returns available dram regions size

cpu0 AddCustomPSCIHandler 0xc200ff12 """
from Antmicro.Renode.Peripherals.CPU import RegisterValue

x1 = self.GetRegisterUlong(1)
if x1 == 0xFFFFFFFFFFFFFFFF:
    self.SetRegisterUlong(1, 0x80002000)
    self.SetRegisterUlong(0, 0x0)
elif x1 == 0:
    self.SetRegisterUlong(1, 0x80000000)
    self.SetRegisterUlong(2, 0x80000000)
    self.SetRegisterUlong(0, 0)
elif x1 == 1:
    self.SetRegisterUlong(1, 0x1080000)
    self.SetRegisterUlong(2, 0x1000)
    self.SetRegisterUlong(0, 0)
elif x1 == 2:
    self.SetRegisterUlong(1, 0x1090000)
    self.SetRegisterUlong(2, 0x1000)
    self.SetRegisterUlong(0, 0)
else:
    self.SetRegisterUlong(0, 0xFFFFFFFFFFFFFFFF)
"""

macro reset
"""
    cpu0 PSCIEmulationMethod SMC
    sysbus LoadELF @https://zephyr-dashboard.renode.io/uboot/2ca1398a5ece8d33d8feb6b410e6e38588b5d2bc/lx2160ardb_tfa_stmm--fsl-lx2160a-rdb/uboot/uboot.elf
    cpu0 EnableUbootMode
    cpu0 EnableZephyrMode
    sysbus LoadSymbolsFrom @https://zephyr-dashboard.renode.io/uboot/2ca1398a5ece8d33d8feb6b410e6e38588b5d2bc/lx2160ardb_tfa_stmm--fsl-lx2160a-rdb/uboot/uboot.elf textAddress=0x00000000fbd42000
    cpu0 EnableProfilerCollapsedStack $ORIGIN/uboot-profile true 62914560 maximumNestedContexts=10
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("lx2160ardb_tfa_stmm--fsl-lx2160a-rdb")
terminalTester = TerminalTester(machine.sysbus.uart0, 5)

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
