# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/beaglev_fire_polarfire_u54_smp_tensorflow_lite_micro.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/beaglev_fire_polarfire_u54_smp_tensorflow_lite_micro.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/beaglev_fire_polarfire_u54_smp_tensorflow_lite_micro.py)
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
logFile $ORIGIN/tensorflow_lite_micro-renode.log True

$name?="beaglev_fire_polarfire_u54_smp"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/9463d9a51d9cb1094bf98ef437a39850a7b5705d/beaglev_fire_polarfire_u54_smp/tensorflow_lite_micro/tensorflow_lite_micro.elf
$repl?=$ORIGIN/tensorflow_lite_micro.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/9463d9a51d9cb1094bf98ef437a39850a7b5705d/f0b6003e9e203d0c86b802628142a51df66eed1c/beaglev_fire_polarfire_u54_smp/tensorflow_lite_micro/tensorflow_lite_micro.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart0

uart0 RecordToAsciinema $ORIGIN/tensorflow_lite_micro-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin 
    cpu0 EnableZephyrMode
    emulation SetGlobalSerialExecution true
    cpu0 EnableProfilerCollapsedStack $ORIGIN/tensorflow_lite_micro-profile true 62914560 maximumNestedContexts=10
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("beaglev_fire_polarfire_u54_smp")
terminalTester = TerminalTester(machine.sysbus.uart0, 15)

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
