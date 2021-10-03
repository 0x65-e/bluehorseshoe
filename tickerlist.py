from aiohttp import ClientSession
import asyncio
from decimal import Decimal
from typing import List, Tuple
from settings import get_setting
from HTMLTableParser import HTMLTableParser

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

    async def _fetch_contract(self, symbol: str, month: str, type: str, session: ClientSession) -> Tuple[Decimal, List[Tuple[Decimal, Decimal, Decimal, int]]]:
        """Gets the contracts for a symbol at a particular month of one type (call or put).
        Returns (price, [contracts]) where each contract is (strike, bid, ask, odds)
        """
        target = "https://www.stockoptionschannel.com/symbol/?symbol=%s&month=%s&type=%s" % (symbol.strip("$"), month, type)
        
        # Asynchronous Request
        if(get_setting("DEBUG")): print(target)
        response = await session.get(target, cookies={'slogin' : get_setting("SLOGIN")})
        xhtml = await response.text()

        # Decode
        parser = HTMLTableParser()
        parser.feed(xhtml)
        
        # TODO: Check if no options available (raise exception or print error, schedule contract reload)

        # Modify list - [strike, bid, ask, odds]
        tables = parser.tables[6:-5]
        contracts = [ ( Decimal(tables[i-1][1][0].split(" ")[0]), Decimal(tables[i-1][1][1]), Decimal(tables[i][0][1]), int(tables[i][0][5][:-1]) ) for i in range(1, len(tables)) ]
        
        # Grab header with price and change
        header = tables[0][0][2].split("\n")[-1]
        start_index = header.find("(")
        end_index = header.find(",  V")
        header = header[start_index:end_index]
        
        # Grab price
        price = Decimal(header[header.find("Last:")+6:header.find(" , ")])
        
        return (price, contracts)

    async def fetch_contracts(self, month: str) -> List[Tuple[Decimal, List[Tuple[Decimal, Decimal, Decimal, int]]]]:
        async with ClientSession() as session:
            fetches = [ self._fetch_contract(symbol, month, t, session) for t in ("call", "put") for symbol in self._list ]
            results = await asyncio.gather(*fetches)

        return results

    def __iter__(self):
        return iter(self._list)