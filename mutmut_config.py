def pre_mutation(context):
    line = context.current_source_line.strip()

    # Skip the self._description.
    if line.startswith("self._description"):
        context.skip = True

    # Skip all the multi line strings
    if line.startswith('"') and (line.endswith('"') or line.endswith("\\")):
        context.skip = True

    # Ignore shit that is printed.
    if line.startswith("print("):
        context.skip = True

    # Modifying the dbus stuff makes little sense
    if line.startswith("@dbus.service.method("):
        context.skip = True

    # It's just a human readable label. Changing it doesn't matter...
    if line.startswith("self._name"):
        context.skip = True

