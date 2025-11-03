# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/beaglev_fire_polarfire_u54_smp_kenning-zephyr-runtime-iree.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/beaglev_fire_polarfire_u54_smp_kenning-zephyr-runtime-iree.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/beaglev_fire_polarfire_u54_smp_kenning-zephyr-runtime-iree.py)
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
logFile $ORIGIN/kenning-zephyr-runtime-iree-renode.log True

$name?="beaglev_fire_polarfire_u54_smp"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/0f5e03f1fcba4326baf4507c343f3609bf32c524/beaglev_fire_polarfire_u54_smp/kenning-zephyr-runtime-iree/kenning-zephyr-runtime-iree.elf
$repl?=$ORIGIN/kenning-zephyr-runtime-iree.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/0f5e03f1fcba4326baf4507c343f3609bf32c524/34743ba5fd349aed8305c9d44c9822880a59f0f1/beaglev_fire_polarfire_u54_smp/kenning-zephyr-runtime-iree/kenning-zephyr-runtime-iree.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart0

uart0 RecordToAsciinema $ORIGIN/kenning-zephyr-runtime-iree-asciinema
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
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("beaglev_fire_polarfire_u54_smp")
terminalTester = TerminalTester(machine.sysbus.uart0, 5)

terminalTester.WaitFor(String("\*\*\* Booting Zephyr OS build.+0f5e03f1fcba \*\*\*"), treatAsRegex=True, pauseEmulation=True)

terminalTester.WaitFor(String("I: model output: [wing: 213.957657, ring: 80.423126, slope: 113.229385, negative: 158.669312]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 162.148727, ring: 140.959763, slope: 149.957062, negative: 236.156754]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 188.821198, ring: 250.954285, slope: 465.087341, negative: 329.155609]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 338.350342, ring: 124.087769, slope: 176.398407, negative: 253.115158]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: -4.008126, ring: 17.447975, slope: -7.546309, negative: 11.472969]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 92.145882, ring: 120.856918, slope: 199.117325, negative: 148.276291]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 48.781994, ring: -10.816508, slope: 2.117262, negative: 8.108255]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 409.882996, ring: 152.557037, slope: 218.346588, negative: 307.647278]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 131.864792, ring: 56.820179, slope: 77.920105, negative: 98.029961]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: model output: [wing: 111.868904, ring: 157.771606, slope: 303.319824, negative: 198.856445]"), pauseEmulation=True)
terminalTester.WaitFor(String("I: inference done"), pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('kenning-zephyr-runtime-iree-asciinema')

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
