# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/ls1046ardb_synchronization.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/ls1046ardb_synchronization.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/ls1046ardb_synchronization.py)
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
logFile $ORIGIN/synchronization-renode.log True

$name?="ls1046ardb"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/ad3df1d0f240f29e07b1620992e2b1aa91e5cf15/ls1046ardb/synchronization/synchronization.elf
$repl?=$ORIGIN/synchronization.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/ad3df1d0f240f29e07b1620992e2b1aa91e5cf15/fe1dfb0df6239f9ed91fb6d119215c5018586d46/ls1046ardb/synchronization/synchronization.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart1

uart1 RecordToAsciinema $ORIGIN/synchronization-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin
    cpu0 EnableZephyrMode
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("ls1046ardb")
terminalTester = TerminalTester(machine.sysbus.uart1, 5)

terminalTester.WaitFor(String(r"thread_a: Hello World from cpu \d on ls1046ardb"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String(r"thread_b: Hello World from cpu \d on ls1046ardb"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String(r"thread_a: Hello World from cpu \d on ls1046ardb"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String(r"thread_b: Hello World from cpu \d on ls1046ardb"), treatAsRegex=True, pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('synchronization-asciinema')

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
