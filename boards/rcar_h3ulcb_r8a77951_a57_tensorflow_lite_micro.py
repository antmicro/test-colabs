# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/rcar_h3ulcb_r8a77951_a57_tensorflow_lite_micro.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/rcar_h3ulcb_r8a77951_a57_tensorflow_lite_micro.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/rcar_h3ulcb_r8a77951_a57_tensorflow_lite_micro.py)
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
$name?="rcar_h3ulcb_r8a77951_a57"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/a70bf0e488c5327ad67512c2854987d113318c79/39825dfac1127ddb969d5fea99613f72ad37c639/rcar_h3ulcb_r8a77951_a57/tensorflow_lite_micro/tensorflow_lite_micro.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.scif2
sysbus.scif2 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/zephyr/a70bf0e488c5327ad67512c2854987d113318c79/rcar_h3ulcb_r8a77951_a57/tensorflow_lite_micro/tensorflow_lite_micro.elf
    
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.scif2", timeout=15)
StartEmulation()

WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)
WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)
WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)
WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)

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
from renode_run import get_default_renode_path
sys.path.append(str(Path(get_default_renode_path()).parent))

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

metrics.display_metrics(parser)
