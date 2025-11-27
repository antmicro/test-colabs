# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/stm32373c_eval_philosophers.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/stm32373c_eval_philosophers.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/stm32373c_eval_philosophers.py)
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

$name?="stm32373c_eval"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/9463d9a51d9cb1094bf98ef437a39850a7b5705d/stm32373c_eval/philosophers/philosophers.elf
$repl?=$ORIGIN/philosophers.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/9463d9a51d9cb1094bf98ef437a39850a7b5705d/f0b6003e9e203d0c86b802628142a51df66eed1c/stm32373c_eval/philosophers/philosophers.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer usart2

usart2 RecordToAsciinema $ORIGIN/philosophers-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin 
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
    cpu0 EnableZephyrMode
    cpu0 EnableProfilerCollapsedStack $ORIGIN/philosophers-profile true 62914560 maximumNestedContexts=10
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("stm32373c_eval")
terminalTester = TerminalTester(machine.sysbus.usart2, 10)

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
