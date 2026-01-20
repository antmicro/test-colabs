# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/ls1046ardb_ls1046a_smp_4cores_philosophers.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/ls1046ardb_ls1046a_smp_4cores_philosophers.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/ls1046ardb_ls1046a_smp_4cores_philosophers.py)
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
logFile $ORIGIN/philosophers-renode.log True

$name?="ls1046ardb_ls1046a_smp_4cores"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/caa8079a5362cd0437ec4d74c888077857df1a9c/ls1046ardb_ls1046a_smp_4cores/philosophers/philosophers.elf
$repl?=$ORIGIN/philosophers.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/caa8079a5362cd0437ec4d74c888077857df1a9c/5b03e34050deb983d78c70ca46dc94fee6e45f2a/ls1046ardb_ls1046a_smp_4cores/philosophers/philosophers.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart1

uart1 RecordToAsciinema $ORIGIN/philosophers-asciinema
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
    gic DisabledSecurity true
    cpu0 PSCIEmulationMethod SMC
    cpu1 PSCIEmulationMethod SMC
    cpu1 IsHalted true
    cpu1 EnableZephyrMode
    cpu2 PSCIEmulationMethod SMC
    cpu2 IsHalted true
    cpu2 EnableZephyrMode
    cpu3 PSCIEmulationMethod SMC
    cpu3 IsHalted true
    cpu3 EnableZephyrMode
    cpu0 EnableProfilerCollapsedStack $ORIGIN/philosophers-profile true 62914560 maximumNestedContexts=10
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("ls1046ardb_ls1046a_smp_4cores")
terminalTester = TerminalTester(machine.sysbus.uart1, 10)

terminalTester.WaitFor(String("Philosopher 0.*THINKING"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String("Philosopher 0.*HOLDING"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String("Philosopher 0.*EATING"), treatAsRegex=True, pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('philosophers-asciinema')

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
