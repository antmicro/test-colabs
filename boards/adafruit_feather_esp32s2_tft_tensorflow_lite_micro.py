# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/adafruit_feather_esp32s2_tft_tensorflow_lite_micro.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/adafruit_feather_esp32s2_tft_tensorflow_lite_micro.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/adafruit_feather_esp32s2_tft_tensorflow_lite_micro.py)
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
logFile $ORIGIN/tensorflow_lite_micro-renode.log True

$name?="adafruit_feather_esp32s2_tft"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/29d3d75b7ef638a5323815fa94f78af54c96d1a5/adafruit_feather_esp32s2_tft/tensorflow_lite_micro/tensorflow_lite_micro.elf
$repl?=$ORIGIN/tensorflow_lite_micro.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/29d3d75b7ef638a5323815fa94f78af54c96d1a5/fa0dba5a67963a6fbb9125a82a3b376616630ddb/adafruit_feather_esp32s2_tft/tensorflow_lite_micro/tensorflow_lite_micro.repl
machine EnableProfiler $ORIGIN/metrics.dump



showAnalyzer uart1

uart1 RecordToAsciinema $ORIGIN/tensorflow_lite_micro-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin useVirtualAddress=true
    cpu0 EnableZephyrMode
    sysbus LoadELF @https://dl.antmicro.com/projects/renode/esp32s2_rom.elf-s_292128-c7d210c90d927c2a787363077029bf2854bd3200 useVirtualAddress=true
    sysbus LoadBinary @https://dl.antmicro.com/projects/renode/esp32s2_romdata.bin-s_1696-5c05f62c50d2f4c1cfbab35b5a5b760ce5962b09 0x4001bed4
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/zephyr/29d3d75b7ef638a5323815fa94f78af54c96d1a5/adafruit_feather_esp32s2_tft/tensorflow_lite_micro/tensorflow_lite_micro.bin 0x1000
    sysbus LoadBinary @https://zephyr-dashboard.renode.io/zephyr/29d3d75b7ef638a5323815fa94f78af54c96d1a5/adafruit_feather_esp32s2_tft/tensorflow_lite_micro/tensorflow_lite_micro.bin 0x3f371000
    cpu0 PC 0x40000400
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("adafruit_feather_esp32s2_tft")
terminalTester = TerminalTester(machine.sysbus.uart1, 15)

terminalTester.WaitFor(String("x_value: .* y_value: .*"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String("x_value: .* y_value: .*"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String("x_value: .* y_value: .*"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String("x_value: .* y_value: .*"), treatAsRegex=True, pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('tensorflow_lite_micro-asciinema')

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
