# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/nucleo_f756zg_blinky.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/nucleo_f756zg_blinky.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/nucleo_f756zg_blinky.py)
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git
! pip install -q git+https://github.com/antmicro/pyrenode.git
! pip install -q robotframework==4.0.1
! renode-run download

# %% [markdown]
"""## Start Renode"""

# %%
from pyrenode import connect_renode, get_keywords
connect_renode()
get_keywords()

# %% [markdown]
"""## Setup a script"""

# %%
%%writefile script.resc

using sysbus
$name?="nucleo_f756zg"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/nucleo_f756zg-blinky/nucleo_f756zg-blinky.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.usart3
sysbus.usart3 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/nucleo_f756zg-blinky/nucleo_f756zg-zephyr-blinky.elf
    
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.usart3", timeout=5)
ExecuteCommand('emulation CreateLEDTester "led_tester" "sysbus.gpiob.greenled"')
StartEmulation()

WaitForLineOnUart("Booting Zephyr OS", treatAsRegex=True)
ExecuteCommand("led_tester AssertState true 1")
ExecuteCommand("led_tester AssertState false 1")
ExecuteCommand("led_tester AssertState true 1")
ExecuteCommand("led_tester AssertState false 1")
ExecuteCommand("led_tester AssertState true 1")
ExecuteCommand("led_tester AssertState false 1")

ResetEmulation()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('output.asciinema')

# %% [markdown]
"""## Renode metrics analysis"""

# %%
import sys
from pathlib import Path
sys.path.append(Path('/root/.config/renode/renode-run.path').read_text())

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

metrics.display_metrics(parser)
