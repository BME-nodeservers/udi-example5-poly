
# Example 5 Plug-in (c) 2024 Robert Paauwe

This example plug-in demonstrates how to use the Custom data class
and the NSCUSTOM event to save and restore persistent data for a
plug-in's node.

This plug-in simply incrents a counter at each shortPoll interval. The
current count is saved.  When the plug-in starts, it restores the last
saved count and continues incrementing the count from there.
