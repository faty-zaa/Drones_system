from typing import List, Dict, Union, Tuple
from collections import Counter


class ParsingError(Exception):
    """Creating my own error"""
    pass


class GlobalValidation:
    """Class of parsing methods"""

    def __init__(self, lines: List):
        self.lines = lines
        self.config = self.check_keys()

    def check_first_line(self) -> bool:
        """validation that the first line containe nb_drones"""
        mp = False
        for line in self.lines:
            line = line.strip()
            """check the empty and comments lines"""
            if not line or line.startswith("#"):
                continue
            if not mp:
                lst = line.split(":", 1)
                if "nb_drones" not in lst:
                    raise ParsingError(
                        "Error: 1st line must containe number of drones")
                key = lst[0].strip()
                value = lst[1].strip()
                val = 0
                if key != "nb_drones" or not value:
                    raise ParsingError(
                        "Error: 1st line must containe number of drones")
                try:
                    val = int(value)
                except ValueError:
                    raise ParsingError("nb_drones must be integer")
                if val < 0:
                    raise ParsingError(
                        "Error: nb_drones must be a positive integer")
                mp = True
            else:
                continue
        return True

    def check_keys(self) -> Dict[str, str | list[str]]:
        """check if there is dupliucated variables"""
        self.check_first_line()
        data: Dict[str, Union[str, List[str]]] = {}
        lst_hub = []
        lst_cnx = []
        lst_drone = []
        lst_start = []
        lst_end = []
        for line in self.lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lst = line.split(":")
            if len(lst) != 2 or lst[1] == '':
                raise ParsingError(
                    f"Error: ({line}) must respect key=value format")
            if lst[0].strip() == "hub":
                lst_hub.append(lst[1].strip())
            elif lst[0].strip() == "connection":
                lst_cnx.append(lst[1].strip())
            elif lst[0].strip() == "nb_drones":
                lst_drone.append(lst[1].strip())
            elif lst[0].strip() == "start_hub":
                lst_start.append(lst[1].strip())
            elif lst[0].strip() == "end_hub":
                lst_end.append(lst[1].strip())
            else:
                raise ParsingError(f"Error: Invalid key ({lst[0]})")
        data["hub"] = lst_hub
        data["connection"] = lst_cnx
        data["nb_drones"] = lst_drone
        data["end_hub"] = lst_end
        data["start_hub"] = lst_start
        return data

    def check_duplicates(self) -> None:
        data = self.config
        """Check if the keys that must be one per file are duplicated"""
        dct = {
            "hub": 0, "connection": 0, "nb_drones": 0,
            "end_hub": 0, "start_hub": 0
            }
        for i in data:
            dct[i] = len(data[i])
        lst = ['nb_drones', 'end_hub', 'start_hub']
        for i in dct:
            if (i == 'connection' or i == 'hub') and dct[i] < 1:
                raise ParsingError(f"Error: {i} must be defined in the file")
            if i in lst and dct[i] != 1:
                raise ParsingError(f"Error: {i} must be defined once per file")

    def add_defaults(self, i: str, default: str) -> str:
        if '#' in i:
            i = i.split('#', 1)[0].rstrip()
        if '[' not in i and ']' not in i:
            i = i + " " + default
        elif i.count('[') != i.count(']'):
            raise ParsingError(f"Error: invalid data format in {i}")
        elif i.count('[') != 1:
            raise ParsingError(f"Error: invalid data format in {i}")
        else:
            v1 = i.find('[')
            v2 = i.find(']')
            if v1 > 0 and i[v1 - 1] != " " and i[v1 - 1] != '#':
                raise ParsingError(f"Error: Invalid metadata format in {i}")
            if i[v1+1:v2].strip() == '':
                i = i[:v1] + default
        i = ' '.join(i.split())
        return i

    def data_format(self, default: str, new_lst: List[str]) -> List[List[str]]:
        lst = []
        for i in new_lst:
            i = self.add_defaults(i, default)
            """
                removing extra whitespace and keeping
                single space between words"""
            new = ""
            names = []
            j = 0
            """check data inside []"""
            while j < len(i):
                if i[j] == "[":
                    if j > 0 and i[j - 1] != " ":
                        raise ParsingError(
                            f"Error: Invalid metadata format in {i}"
                        )
                    j += 1
                    while j < len(i) and i[j] != "]":
                        new += i[j]
                        j += 1
                    k = j + 1
                    while k < len(i) and i[k] == " ":
                        k += 1
                    if k < len(i) and i[k] != "#":
                        raise ParsingError(f"invalid metadata format in {i}")
                    names.append(new.strip())
                    new = ""
                    j += 1
                elif i[j] != " ":
                    new += i[j]
                elif i[j] == " " and new != "":
                    names.append(new.strip())
                    new = ""
                j += 1
            if new != "":
                names.append(new.strip())
            lst.append(names)
        return lst

    def zone_data_check(self) -> Tuple[list[list[str]], list[str]]:
        """check zones unique names """
        data = self.config
        lst1 = ['end_hub', 'start_hub', 'hub']
        lst_data = [data[i] for i in data if i in lst1]
        new_lst = [i for j in lst_data for i in j]
        """add default values"""
        default = "[zone=normal color=none max_drones=1]"
        """check data format []"""
        lst = self.data_format(default, new_lst)
        names = []
        for idx, i in enumerate(lst):
            for j in i:
                if '#' in j:
                    lst[idx] = i[:i.index(j)]
                    break
            if "-" in i[0] or " " in i[0]:
                raise ParsingError(
                    "Error: Zone name cannot contain"
                    f" dashes or spaces -> ({i[0]})")
            names.append(i[0].strip())
        for i in lst:
            if len(i) != 4:
                raise ParsingError(
                    "Error: Zone data must respect the format:"
                    f" <name> <x> <y> [metadata] (in {i[0]})")
        count = Counter(names)
        val: Dict[str, int] = {i: j for i, j in count.items()}
        """check hubes names if duplicated"""
        for hub, n in count.items():
            if n != 1:
                raise ParsingError(f"Error: Found duplicated hub: {hub}")
        return lst, names
    
    def meta_data_check(self) -> Dict:
        """validating hubs meta data"""
        data = self.zone_data_check()
        dct: Dict[str, List[Union[str, Tuple[int, int]]]] = {}
        for i in data[0]:
            try:
                int(i[1])
                int(i[2])
            except Exception:
                raise ParsingError(
                        "Error: coordinates must be "
                        f"valid integers (x, y) in hub: {i[0]}")
            i[3] = "=".join(x.strip() for x in i[3].split("="))
           
            coords = (int(i[1]), int(i[2]))
            metadata = [x for x in i[3].split(" ") if x != ""]

            entry: List[Union[Tuple[int, int], str]] = [coords] + metadata
            dct[i[0]] = entry
        default_meta = {
            "zone": "normal",
            "color": "none",
            "max_drones": "1"
        }
        zval = ["normal", "blocked", "restricted", "priority"]
        for h in dct:
            new_dct = {}
            for j in range(len(dct[h])):
                if j < 1:
                    continue
                try:
                    lst = dct[h][j].split("=")
                    key, value = lst
                except Exception:
                    raise ParsingError(
                        f"metadata in {h} must follow the "
                        "following format: zone=<type> color=<value> "
                        "max_drones=<number>")
                if key.strip() not in default_meta.keys():
                    raise ParsingError(
                        f"Invalid metadata key: \"{key}\" in {h}"
                        f". Expected one of: {list(default_meta.keys())}")
                elif key.strip() == "zone" and value.strip() not in zval:
                    raise ParsingError(
                        f"Invalid zone type: \"{value}\" in {h}."
                        f" Expected one of: {zval}"
                    )
                elif key.strip() == 'color' and not value.strip().isalpha():
                    raise ParsingError(
                        f"Error: color in {h} must be a valid single-word "
                        f"strings (e.g., red, blue...)")
                elif key.strip() == 'max_drones':
                    try:
                        v = int(value.strip())
                    except Exception:
                        raise ParsingError(
                            f"Error: {key} in {h} must be a valid integer")
                    if v < 1:
                        raise ParsingError(
                            f"Error: {key} in {h} must be > than 0")
                if key in new_dct:
                    raise ParsingError(
                        f"Duplicate metadata key ({key}) in {h}")
                new_dct[key] = value
            dct[h] = dct[h][:2]
            merged = default_meta.copy()
            merged.update(new_dct)
            dct[h][1] = merged
        lst = []
        for i in  dct.values():
            lst.append(i[0])
        count = Counter(lst)
        for j, i in count.items():
            if i != 1:
                raise ParsingError(f"Error: Duplicated hub position -> {j}")
        return dct

    def connection_check(self) -> Dict:
        self.check_first_line()
        self.check_duplicates()
        hubs = self.meta_data_check()
        data = self.config
        nlst = data["connection"]
        for i in nlst:
            if '#' in i:
                nlst[nlst.index(i)] = i.split("#")[0]
        lst = self.data_format("max_link_capacity=1", nlst)
        for i in lst:
            if len(i) != 2:
                raise ParsingError(
                    "Error: invalid connection format:"
                    f"<name1>-<name2> [metadata] in ->  {i[0]}")
        dct = {}
        _, h_name = self.zone_data_check()
        for x in lst:
            conn_name = x[0]
            metadata = x[1]
            if '=' not in metadata:
                raise ParsingError(f"Invalid metadata format: {metadata}")
            key, _ = metadata.split('=', 1)

            if key != "max_link_capacity":
                raise ParsingError(f"Error: Invalid metadata in ({x[0]})")
            dct[conn_name] = metadata

        connect = dct.keys()
        lst = []
        for i in connect:
            if len(i.split("-")) != 2:
                raise ParsingError(f"Error: invalid connection: {i}")
            elif len(i.split("-")) == 2:
                lst.append(i.split("-"))
        hubs = self.meta_data_check()
        start = self.config["start_hub"][0].strip().split()[0]
        end = self.config["end_hub"][0].strip().split()[0]
        s = 0
        e = 0
        for i in lst:
            for j in i:
                if j not in h_name:
                    raise ParsingError(
                            f"Error: connection name must exist"
                            f" in hubes names ({j})")
                elif j == start:
                    s += 1
                    if s != 1:
                        raise ParsingError(
                            "Error: start point can't be "
                            "connected more then once")
                elif j == end:
                    e += 1
                    if e != 1:
                        raise ParsingError(
                            "Error: end point can't be connected"
                            " more then once")
        i = 0
        while i < len(lst):
            j = i + 1
            if lst[i][0] == lst[i][1]:
                raise ParsingError(
                    f"Error: connection names must be different {lst[i]}")
            while j < len(lst):
                if Counter(lst[i]) == Counter(lst[j]):
                    raise ParsingError(
                        f"Error: Duplicated connection -> {lst[i]}")
                j += 1
            i += 1
        dct = {
            tuple(k.split('-')): v
            for k, v in dct.items()
        }
        for value in dct.values():
            try:
                key, val = value.split("=")
            except Exception:
                raise ParsingError(
                    f"Error: Invalid data format in {value}"
                    f", it must be max_link_capacity=<number>")
            if key != "max_link_capacity":
                raise ParsingError(f"Error: Invalid key in {key}")
            if not val:
                raise ParsingError(
                    f"Error: Invalid data format in {value}"
                    f", it must be max_link_capacity=<number>")
            if not val.isdigit():
                raise ParsingError(
                    f"Error: Capacity must be a positive number in ({val})")
            elif val.isdigit() and int(val) < 1:
                raise ParsingError(
                    f"Error: Capacity must be > than 0 in ({val})")
        for k, v in dct.items():
            dct[k] = int(v.split("=")[1])
        return hubs, dct
