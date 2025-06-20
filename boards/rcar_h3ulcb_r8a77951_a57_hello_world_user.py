# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/rcar_h3ulcb_r8a77951_a57_hello_world_user.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/rcar_h3ulcb_r8a77951_a57_hello_world_user.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/rcar_h3ulcb_r8a77951_a57_hello_world_user.py)
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
logFile $ORIGIN/hello_world_user-renode.log True

$name?="rcar_h3ulcb_r8a77951_a57"
$bin?=@https://zephyr-dashboard.renode.io/zephyr/34e47f4040c99d52fe0e5d5eb64b2904e14f8981/rcar_h3ulcb_r8a77951_a57/hello_world_user/hello_world_user.elf
$repl?=$ORIGIN/hello_world_user.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/34e47f4040c99d52fe0e5d5eb64b2904e14f8981/b50237b53ead88c2c8fe98ee9775c75d08813f6b/rcar_h3ulcb_r8a77951_a57/hello_world_user/hello_world_user.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer scif2

scif2 RecordToAsciinema $ORIGIN/hello_world_user-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "z_fatal_error" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin
    cpu0 EnableZephyrMode
    gic DisabledSecurity true
    cpu0 EnableProfilerCollapsedStack $ORIGIN/hello_world_user-profile true 62914560 maximumNestedContexts=10
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("rcar_h3ulcb_r8a77951_a57")
terminalTester = TerminalTester(machine.sysbus.scif2, 5)

terminalTester.WaitFor(String("Hello World from UserSpace! (rcar_h3ulcb_r8a77951_a57)"), pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('hello_world_user-asciinema')

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
