# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/qemu_riscv32_qemu_virt_riscv32_smp_lz4.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/qemu_riscv32_qemu_virt_riscv32_smp_lz4.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/qemu_riscv32_qemu_virt_riscv32_smp_lz4.py)
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
logFile $ORIGIN/lz4-renode.log True

$name?="qemu_riscv32_qemu_virt_riscv32_smp"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/6353ba88b6cd5c2969215d601947bd89f651375d/qemu_riscv32_qemu_virt_riscv32_smp/lz4/lz4.elf
$repl?=$ORIGIN/lz4.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/6353ba88b6cd5c2969215d601947bd89f651375d/7ef505b300bbcc32e104ae2e636d21f7e2fec465/qemu_riscv32_qemu_virt_riscv32_smp/lz4/lz4.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart0

uart0 RecordToAsciinema $ORIGIN/lz4-asciinema
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
    cpu0 EnableProfilerCollapsedStack $ORIGIN/lz4-profile true 62914560 maximumNestedContexts=10
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("qemu_riscv32_qemu_virt_riscv32_smp")
terminalTester = TerminalTester(machine.sysbus.uart0, 5)

terminalTester.WaitFor(String(r"Original Data size: \d+"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String(r"Compressed Data size : \d+"), treatAsRegex=True, pauseEmulation=True)
terminalTester.WaitFor(String("Successfully decompressed some data"), pauseEmulation=True)
terminalTester.WaitFor(String("Validation done. The string we ended up with is:"), pauseEmulation=True)
terminalTester.WaitFor(String(r".*"), treatAsRegex=True, pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('lz4-asciinema')

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
