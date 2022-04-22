# %% [markdown]
"""
![Renode](https://dl.antmicro.com/projects/renode/renode.png)
<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/antmicro/test-colabs/blob/master/test.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/master/.static/view-in-colab.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/master/test.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/master/.static/view-ipynb.png" />View ipynb on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/master/test.py"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/master/.static/view-source.png" />View Python source on GitHub</a>
  </td>
</table>
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git@testing

import sys
from pathlib import Path
sys.path.append(Path('~/.config/renode/renode-run.path').read_text())

# %% [markdown]
"""## Run the philosophers example in Renode"""

# %%
! renode-run demo --binary philosophers hifive1_revb -- --console -e "machine EnableProfiler @/tmp/metrics.dump; emulation RunFor 0.3"

# %% [markdown]
"""## Renode metrics analysis"""

# %%
from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('/tmp/metrics.dump')

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
