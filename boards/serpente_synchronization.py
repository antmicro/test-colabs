# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/serpente_synchronization.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/serpente_synchronization.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/serpente_synchronization.py)
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

using sysbus
$name?="serpente"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/76e1fc7713a4a3f2b50c497afddec0364a34c10b/234e81a06ec4b68b8091b7a9e595f25a611c1ce5/serpente/synchronization/synchronization.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer sercom2

sercom2 RecordToAsciinema $ORIGIN/synchronization-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/zephyr/76e1fc7713a4a3f2b50c497afddec0364a34c10b/serpente/synchronization/synchronization.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
    cpu0 EnableZephyrMode
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("serpente")
terminalTester = TerminalTester(machine.sysbus.sercom2, 5)

terminalTester.WaitFor(String(r"thread_a: Hello World from cpu \d on serpente"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String(r"thread_b: Hello World from cpu \d on serpente"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String(r"thread_a: Hello World from cpu \d on serpente"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String(r"thread_b: Hello World from cpu \d on serpente"), treatAsRegex=True, pauseEmulation=True)

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
