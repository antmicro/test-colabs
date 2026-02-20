# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev_uboot.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev_uboot.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev_uboot.py)
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

$name?="verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev"
$bin?=@https://zephyr-dashboard.renode.io/uboot/f9ffeec4bdcf1da655a0ffea482062adde78fee8/verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev/uboot/uboot.elf
$repl?=$ORIGIN/uboot.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/uboot_sim/f9ffeec4bdcf1da655a0ffea482062adde78fee8/7f0af423ad652a8a5c6fe5b28d0606e7a294ef55/verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev/uboot/uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart1

uart1 RecordToAsciinema $ORIGIN/uboot-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "hang" $osPanicHook
cpu0 AddSymbolHook "panic" $osPanicHook


cpu0 AddCustomPSCIHandler 0xbf00ff01 # OPTEE_SMC_CALLS_UID
"""
self.SetRegisterUlong(0, 0x0)
"""

macro reset
"""
    cpu0 PSCIEmulationMethod SMC
    sysbus LoadELF $bin 
    cpu0 EnableUbootMode
    cpu0 EnableZephyrMode
    cpu1 IsHalted true
    cpu2 IsHalted true
    cpu3 IsHalted true
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/uboot/f9ffeec4bdcf1da655a0ffea482062adde78fee8/verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev/uboot/uboot.dtb 0x00000000402d8710
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("verdin-imx8mm--freescale-imx8mm-verdin-wifi-dev")
terminalTester = TerminalTester(machine.sysbus.uart1, 5)

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
