# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/xiao_esp32s3_esp32s3_procpu_hello_world.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/xiao_esp32s3_esp32s3_procpu_hello_world.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/xiao_esp32s3_esp32s3_procpu_hello_world.py)
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
logFile $ORIGIN/hello_world-renode.log True

$name?="xiao_esp32s3_esp32s3_procpu"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/f78c4deb4523a58eca057cc59b33532b80c20843/xiao_esp32s3_esp32s3_procpu/hello_world/hello_world.elf
$repl?=$ORIGIN/hello_world.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/f78c4deb4523a58eca057cc59b33532b80c20843/bdd0eb0b0fb313502b3ecf587e2b25a184959e60/xiao_esp32s3_esp32s3_procpu/hello_world/hello_world.repl
machine EnableProfiler $ORIGIN/metrics.dump



showAnalyzer usbserial

usbserial RecordToAsciinema $ORIGIN/hello_world-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin useVirtualAddress=true
    cpu0 EnableZephyrMode
    sysbus LoadBinary @https://dl.antmicro.com/projects/renode/esp32s3_rev0_rom.bin-s_393216-d5d2d95ffbd551d79b82b923ef597b4730835d60 0x40000000
    sysbus LoadBinary @https://dl.antmicro.com/projects/renode/esp32s3_rev0_rom.bin-s_393216-d5d2d95ffbd551d79b82b923ef597b4730835d60 0x3ff00000 offset=0x40000
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/zephyr/f78c4deb4523a58eca057cc59b33532b80c20843/xiao_esp32s3_esp32s3_procpu/hello_world/hello_world.bin 0x3dff0000
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/zephyr/f78c4deb4523a58eca057cc59b33532b80c20843/xiao_esp32s3_esp32s3_procpu/hello_world/hello_world.bin 0x3c800000
    cpu0 PC 0x40000400
    cpu1 IsHalted true
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("xiao_esp32s3_esp32s3_procpu")
terminalTester = TerminalTester(machine.sysbus.usbserial, 5)

terminalTester.WaitFor(String("Hello World! xiao_esp32s3/esp32s3/procpu"), pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('hello_world-asciinema')

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
