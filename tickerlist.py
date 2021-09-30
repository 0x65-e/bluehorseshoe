from aiohttp import ClientSession

class TickerList:

    def __init__(self, name, iterable=None):
        self._name = name
        if iterable != None:
            self._list = set(iterable)
        else:
            self._list = set()

    def add_symbols(self, symbols):
        """Add the given symbols to the list. All instances of '$' are stripped out, and empty strings are never added to the list."""
        for s in symbols:
            s = s.strip("$").upper()
            if s: # Ignore empty strings silently
                self._list.add(s)
    
    def remove_symbols(self, symbols):
        for s in symbols:
            s = s.strip("$").upper()
            if s: # Ignore empty strings
                if s in self._list:
                    self._list.remove(s)
                else:
                    print(s + " not in list " + self._name)

    def __iter__(self):
        return iter(self._list)