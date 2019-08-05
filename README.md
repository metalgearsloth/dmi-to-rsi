# Summary #
This is a quick util to convert a byond .dmi file into an .rsi file (format use in [SS14](https://github.com/space-wizards/space-station-14))
This is provided *as is* and is currently broken due to removing external images that were used for initial testing.

## How to use ##
~~~
git clone https://github.com/this-is-the-bard/dmi_to_rsi.git
from dmi_to_rsi.src.utils import convert_dmi_to_rsi
dmi_source = ""
rsi_target = ""
convert_dmi_to_rsi(dmi_source, rsi_target)
~~~

### What could be better ###
This isn't so much of a todo list
* Add generic tests (current ones will fail)
* Make tests check outputs and not just instantiation
* Add additional utils for bulk converting
* Add async and await (particularly to the individual frame splicer for dmi but also for any potential bulk dmi converters) though this is overkill for this kind of library.