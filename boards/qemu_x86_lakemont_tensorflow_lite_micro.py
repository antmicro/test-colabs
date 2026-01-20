# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/qemu_x86_lakemont_tensorflow_lite_micro.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/qemu_x86_lakemont_tensorflow_lite_micro.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/qemu_x86_lakemont_tensorflow_lite_micro.py)
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

$name?="qemu_x86_lakemont"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/caa8079a5362cd0437ec4d74c888077857df1a9c/qemu_x86_lakemont/tensorflow_lite_micro/tensorflow_lite_micro.elf
$repl?=$ORIGIN/tensorflow_lite_micro.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/caa8079a5362cd0437ec4d74c888077857df1a9c/5b03e34050deb983d78c70ca46dc94fee6e45f2a/qemu_x86_lakemont/tensorflow_lite_micro/tensorflow_lite_micro.repl
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
    
    # set the D flag for Executable code segment
    cpu0 SetDescriptor CS 0x0 0x0 0x0 0x400000
    # enable protected mode
    cpu0 CR0 0x60000011
    cpu0 EnableZephyrMode
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("qemu_x86_lakemont")
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
