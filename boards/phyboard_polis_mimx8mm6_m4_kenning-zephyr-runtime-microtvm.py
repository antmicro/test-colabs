# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/phyboard_polis_mimx8mm6_m4_kenning-zephyr-runtime-microtvm.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/phyboard_polis_mimx8mm6_m4_kenning-zephyr-runtime-microtvm.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/phyboard_polis_mimx8mm6_m4_kenning-zephyr-runtime-microtvm.py)
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
logFile $ORIGIN/kenning-zephyr-runtime-microtvm-renode.log True

$name?="phyboard_polis_mimx8mm6_m4"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/ad320ee4f25130af333f7c8d177ab73b7f584fe8/phyboard_polis_mimx8mm6_m4/kenning-zephyr-runtime-microtvm/kenning-zephyr-runtime-microtvm.elf
$repl?=$ORIGIN/kenning-zephyr-runtime-microtvm.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/ad320ee4f25130af333f7c8d177ab73b7f584fe8/fb29ee41fe3f2756a261758f8e89be1fceb15237/phyboard_polis_mimx8mm6_m4/kenning-zephyr-runtime-microtvm/kenning-zephyr-runtime-microtvm.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart4

uart4 RecordToAsciinema $ORIGIN/kenning-zephyr-runtime-microtvm-asciinema
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
    cpu0 EnableProfilerCollapsedStack $ORIGIN/kenning-zephyr-runtime-microtvm-profile true 62914560 maximumNestedContexts=10
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("phyboard_polis_mimx8mm6_m4")
terminalTester = TerminalTester(machine.sysbus.uart4, 5)

terminalTester.WaitFor(String("\*\*\* Booting Zephyr OS build.+ad320ee4f251 \*\*\*"), treatAsRegex=True, pauseEmulation=True)

terminalTester.WaitFor(String("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 0.000000, ring: 0.000000, slope: 0.000000, negative: 1.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 0.000000, ring: 0.000000, slope: 1.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 0.000000, ring: 0.997465, slope: 0.000000, negative: 0.002535]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 0.000000, ring: 0.000000, slope: 1.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 0.000000, ring: 0.000000, slope: 1.000000, negative: 0.000000]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: inference done"), pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('kenning-zephyr-runtime-microtvm-asciinema')

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
