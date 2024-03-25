# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/db-xc3-24g4xg--armada-xp-db-xc3-24g4xg_uboot.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/db-xc3-24g4xg--armada-xp-db-xc3-24g4xg_uboot.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/db-xc3-24g4xg--armada-xp-db-xc3-24g4xg_uboot.py)
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git
! pip install -q git+https://github.com/antmicro/pyrenode.git
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
$name?="db-xc3-24g4xg--armada-xp-db-xc3-24g4xg"
mach create $name

machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/db-xc3-24g4xg--armada-xp-db-xc3-24g4xg-uboot/db-xc3-24g4xg--armada-xp-db-xc3-24g4xg-uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart0
sysbus.uart0 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://u-boot-dashboard.renode.io/db-xc3-24g4xg--armada-xp-db-xc3-24g4xg-uboot/db-xc3-24g4xg--armada-xp-db-xc3-24g4xg-uboot.elf
    
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.uart0", timeout=5)
StartEmulation()

WaitForPromptOnUart("Hit any key to stop autoboot")
SendKeyToUart(ord('a'))
WaitForPromptOnUart(">")
WriteLineToUart("version")
WaitForLineOnUart("U-Boot")

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
