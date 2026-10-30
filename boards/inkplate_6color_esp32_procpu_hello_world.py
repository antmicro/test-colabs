# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/inkplate_6color_esp32_procpu_hello_world.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/inkplate_6color_esp32_procpu_hello_world.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/inkplate_6color_esp32_procpu_hello_world.py)
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

$name?="inkplate_6color_esp32_procpu"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/bc5d59d1b6657cfeef30124b818c8fbd69da68ac/inkplate_6color_esp32_procpu/hello_world/hello_world.elf
$repl?=$ORIGIN/hello_world.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/bc5d59d1b6657cfeef30124b818c8fbd69da68ac/03e7bf4e259b85bdc1bf5dc63c4053dcc7c54680/inkplate_6color_esp32_procpu/hello_world/hello_world.repl
machine EnableProfiler $ORIGIN/metrics.dump



showAnalyzer uart0

uart0 RecordToAsciinema $ORIGIN/hello_world-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin useVirtualAddress=true
    cpu0 EnableZephyrMode
    sysbus LoadBinary @https://dl.antmicro.com/projects/renode/esp32-v3-rom.bin-s_455722-c76e96d5bbab3cf190dbecd777fe84b75256da9e 0x40000000
    sysbus LoadBinary @https://dl.antmicro.com/projects/renode/esp32-v3-rom.bin-s_455722-c76e96d5bbab3cf190dbecd777fe84b75256da9e 0x3ff90000 offset=0x60000
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/zephyr/bc5d59d1b6657cfeef30124b818c8fbd69da68ac/inkplate_6color_esp32_procpu/hello_world/hello_world.bin 0x3f401000
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/zephyr/bc5d59d1b6657cfeef30124b818c8fbd69da68ac/inkplate_6color_esp32_procpu/hello_world/hello_world.bin 0x1000
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/zephyr/bc5d59d1b6657cfeef30124b818c8fbd69da68ac/inkplate_6color_esp32_procpu/hello_world/hello_world.bin 0x3f721000
    cpu0 PC 0x40000400
    cpu1 IsHalted true
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("inkplate_6color_esp32_procpu")
terminalTester = TerminalTester(machine.sysbus.uart0, 5)

terminalTester.WaitFor(String("Hello World! inkplate_6color/esp32/procpu"), pauseEmulation=True)

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
