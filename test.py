# %% [markdown]
"""
![Renode](https://dl.antmicro.com/projects/renode/renode.png)
<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/antmicro/test-colabs/blob/master/test.ipynb"><img src="https://raw.githubusercontent.com/antmicro/tensorflow-arduino-examples/master/examples/.static/view-in-colab.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/master/test.ipynb"><img src="https://raw.githubusercontent.com/antmicro/tensorflow-arduino-examples/master/examples/.static/view-ipynb.png" />View ipynb on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/master/test.py"><img src="https://raw.githubusercontent.com/antmicro/tensorflow-arduino-examples/master/examples/.static/view-source.png" />View Python source on GitHub</a>
  </td>
</table>
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
!pip install -q git+https://github.com/antmicro/pyrenode.git git+https://github.com/antmicro/renode-colab-tools.git git+https://github.com/antmicro/renode-run.git
!pip install -q -r renode/tests/requirements.txt

import os
from renode_colab_tools import metrics
os.environ['PATH'] = os.getcwd()+"/renode:"+os.environ['PATH']

# %%
!mkdir -p binaries
!cd binaries
!wget https://zephyr-dashboard.renode.io/hifive1_revb-philosophers.zip
!unzip hifive1_revb-philosophers.zip

# %% [markdown]
"""## Run the philosophers example in Renode"""

# %%
!renode-run test -- artifacts/hifive1_revb-philosophers.robot

# %% [markdown]
"""## Renode metrics analysis"""

# %%
from renode.tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('renode/metrics.dump')

# %%
metrics.configure_plotly_browser_state()
metrics.show_executed_instructions(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_memory_access(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_exceptions(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_peripheral_access(parser)
