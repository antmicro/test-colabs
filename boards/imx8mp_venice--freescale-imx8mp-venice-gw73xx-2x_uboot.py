# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x_uboot.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x_uboot.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x_uboot.py)
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
$name?="imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x"
mach create $name

machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/uboot_sim/93905ab6e7564089f5d7b703b660464d675e5ab0/ffd339dd25d1b077a39f348685017e28dfc48d1b/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x/uboot/uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart2

uart2 RecordToAsciinema $ORIGIN/uboot-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "hang" $osPanicHook
cpu0 AddSymbolHook "panic" $osPanicHook


sysbus LoadSymbolsFrom @https://zephyr-dashboard.renode.io/uboot/93905ab6e7564089f5d7b703b660464d675e5ab0/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x/uboot/uboot.elf
set hook
"""
self.SetRegisterUlong(0, 6) # SD1_BOOT
self.PC = self.GetRegisterUlong(30)
"""
cpu0 AddSymbolHook "get_boot_device" $hook # romapi.c:get_boot_device

macro reset
"""
    cpu0 EnableTimeSkip "mxc_i2c_xfer" 0
    cpu0 EnableTimeSkip "mxc_i2c_probe_chip" 0
    sysbus LoadELF @https://zephyr-dashboard.renode.io/uboot/93905ab6e7564089f5d7b703b660464d675e5ab0/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x/uboot/uboot.elf
    cpu0 EnableUbootMode
    cpu0 EnableZephyrMode
    cpu1 IsHalted true
    cpu2 IsHalted true
    cpu3 IsHalted true
    sysbus LoadSymbolsFrom @https://zephyr-dashboard.renode.io/uboot/93905ab6e7564089f5d7b703b660464d675e5ab0/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x/uboot/uboot.elf textAddress=0x00000000ffeef000
    cpu0 EnableProfilerCollapsedStack $ORIGIN/uboot-profile true 62914560 maximumNestedContexts=10
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/uboot/93905ab6e7564089f5d7b703b660464d675e5ab0/imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x/uboot/uboot.dtb 0x00000000402f38b8
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("imx8mp_venice--freescale-imx8mp-venice-gw73xx-2x")
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
