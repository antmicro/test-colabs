# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/b_u585i_iot02a_stm32u585xx_ns_kenning-zephyr-runtime-iree.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/b_u585i_iot02a_stm32u585xx_ns_kenning-zephyr-runtime-iree.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/b_u585i_iot02a_stm32u585xx_ns_kenning-zephyr-runtime-iree.py)
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
$name?="b_u585i_iot02a_stm32u585xx_ns"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/25812289779f471143cf1a2cc34c245c603bd941/a62db5c9be07ce1bc43c383460194ee0fbc9ee72/b_u585i_iot02a_stm32u585xx_ns/kenning-zephyr-runtime-iree/kenning-zephyr-runtime-iree.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.usart1
sysbus.usart1 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/zephyr/25812289779f471143cf1a2cc34c245c603bd941/b_u585i_iot02a_stm32u585xx_ns/kenning-zephyr-runtime-iree/kenning-zephyr-runtime-iree.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.usart1", timeout=5)

WaitForLineOnUart("\*\*\* Booting Zephyr OS build.+25812289779f \*\*\*", treatAsRegex=True)

WaitForLineOnUart("I: model output: [wing: 213.957657, ring: 80.423126, slope: 113.229385, negative: 158.669312]")
WaitForLineOnUart("I: model output: [wing: 162.148727, ring: 140.959763, slope: 149.957062, negative: 236.156754]")
WaitForLineOnUart("I: model output: [wing: 188.821198, ring: 250.954285, slope: 465.087341, negative: 329.155609]")
WaitForLineOnUart("I: model output: [wing: 338.350342, ring: 124.087769, slope: 176.398407, negative: 253.115158]")
WaitForLineOnUart("I: model output: [wing: -4.008126, ring: 17.447975, slope: -7.546309, negative: 11.472969]")
WaitForLineOnUart("I: model output: [wing: 92.145882, ring: 120.856918, slope: 199.117325, negative: 148.276291]")
WaitForLineOnUart("I: model output: [wing: 48.781994, ring: -10.816508, slope: 2.117262, negative: 8.108255]")
WaitForLineOnUart("I: model output: [wing: 409.882996, ring: 152.557037, slope: 218.346588, negative: 307.647278]")
WaitForLineOnUart("I: model output: [wing: 131.864792, ring: 56.820179, slope: 77.920105, negative: 98.029961]")
WaitForLineOnUart("I: model output: [wing: 111.868904, ring: 157.771606, slope: 303.319824, negative: 198.856445]")
WaitForLineOnUart("I: inference done")

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