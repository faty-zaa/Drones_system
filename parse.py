from typing import List, Dict, Union, Tuple, Any
from collections import Counter
from zone import Zone
from connection import Connection


class ParsingError(Exception):
    """Creating my own error with line number"""

    def __init__(self, message: str, line: int = 0) -> None:
        self.line = line
        super().__init__(f"line {line}: {message}" if line else message)


class GlobalValidation:
    """Class of parsing methods"""

    def __init__(self, lines: List) -> None:
        self.lines: List[str] = lines
        self.current_line: int = 0
        self.config: Dict[str, Any] = self.check_keys()
        self._parsed: Any = None

    def find_line(self, keyword: str) -> int:
        """Find line number containing a keyword."""
        for i, line in enumerate(self.lines, start=1):
            if keyword in line:
                return i
        return 0

    def check_first_line(self) -> bool:
        """validation that the first line containe nb_drones"""
        mp = False
        for line_num, line in enumerate(self.lines, start=1):
            self.current_line = line_num
            line = line.strip()
            """check the empty and comments lines"""
            if not line or line.startswith("#"):
                continue
            if not mp:
                try:
                    lst = line.split(":", 1)
                    key = lst[0].strip()
                    value = lst[1].strip()
                    # must raise key value error
                except Exception:
                    raise ParsingError(
                        "Error: line must containe key:value", line_num)
                if "nb_drones" not in lst:
                    raise ParsingError(
                        "Error: 1st line must containe number of drones",
                        line_num
                    )
                val: int = 0
                if key != "nb_drones" or not value:
                    raise ParsingError(
                        "Error: 1st line must containe number of drones",
                        line_num
                    )
                try:
                    val = int(value)
                except ValueError:
                    raise ParsingError(
                        "nb_drones must be integer", line_num)
                if val < 0:
                    raise ParsingError(
                        "Error: nb_drones must be a positive integer", line_num
                    )
                mp = True
            else:
                continue
        return True

    def check_keys(self) -> Dict[str, List[str]]:
        """check if there is dupliucated variables"""
        self.check_first_line()
        data: Dict[str, List[str]] = {}
        lst_hub: List[str] = []
        lst_cnx: List[str] = []
        lst_drone: List[str] = []
        lst_start: List[str] = []
        lst_end: List[str] = []
        for line_num, line in enumerate(self.lines, start=1):
            self.current_line = line_num
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lst: List[str] = line.split(":", 1)
            if len(lst) != 2 or lst[1] == "":
                raise ParsingError(
                    f"Error: ({line}) must respect key=value format", line_num
                )
            key: str = lst[0].strip()
            value: str = lst[1].strip()

            if key == "hub":
                lst_hub.append(value)

            elif key == "connection":
                lst_cnx.append(value)

            elif key == "nb_drones":
                lst_drone.append(value)

            elif key == "start_hub":
                lst_start.append(value)

            elif key == "end_hub":
                lst_end.append(value)

            else:
                raise ParsingError(
                    f"Error: Invalid key ({key})", line_num)

        data["hub"] = lst_hub
        data["connection"] = lst_cnx
        data["nb_drones"] = lst_drone
        data["end_hub"] = lst_end
        data["start_hub"] = lst_start

        return data

    def check_duplicates(self) -> None:
        data: Dict[str, list[str]] = self.config
        """Check if the keys that must be one per file are duplicated"""
        dct: Dict[str, int] = {
            "hub": 0,
            "connection": 0,
            "nb_drones": 0,
            "end_hub": 0,
            "start_hub": 0,
        }
        for i in data:
            dct[i] = len(data[i])
        lst = ["nb_drones", "end_hub", "start_hub"]
        for key in dct:
            if (key == "connection" or key == "hub") and dct[key] < 1:
                raise ParsingError(
                    f"Error: {key} must be defined in the file",
                    self.current_line
                )

            if key in lst and dct[key] != 1:
                raise ParsingError(
                    f"Error: {key} must be defined once per file",
                    self.current_line
                )

    def add_defaults(self, i: str, default: str) -> str:
        if "#" in i:
            i = i.split("#", 1)[0].rstrip()
        if "[" not in i and "]" not in i:
            i = i + " " + default

        elif i.count("[") != i.count("]"):
            raise ParsingError(
                f"Error: invalid data format in {i}",
                self.find_line(i.split()[0])
            )

        elif i.count("[") != 1:
            raise ParsingError(
                f"Error: invalid data format in {i}",
                self.find_line(i.split()[0])
            )

        else:
            v1: int = i.find("[")
            v2: int = i.find("]")

            if v1 > 0 and i[v1 - 1] != " " and i[v1 - 1] != "#":
                raise ParsingError(
                    f"Error: Invalid metadata format in {i}",
                    self.find_line(i.split()[0]),
                )

            if i[v1 + 1: v2].strip() == "":
                i = i[:v1] + default

        i = " ".join(i.split())
        return i

    def data_format(self, default: str, new_lst: List[str]) -> List[List[str]]:
        lst: List[List[str]] = []
        for i in new_lst:
            i = self.add_defaults(i, default)
            """
                removing extra whitespace and keeping
                single space between words"""
            new: str = ""
            names: List[str] = []

            j: int = 0
            """check data inside []"""
            while j < len(i):
                if i[j] == "[":
                    if j > 0 and i[j - 1] != " ":
                        raise ParsingError(
                            f"Error: Invalid metadata format in {i}")
                    j += 1
                    while j < len(i) and i[j] != "]":
                        new += i[j]
                        j += 1
                    k = j + 1
                    while k < len(i) and i[k] == " ":
                        k += 1
                    if k < len(i) and i[k] != "#":
                        raise ParsingError(
                            f"invalid metadata format in {i}",
                            self.find_line(i.split()[0]),
                        )
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
        """check zones unique names"""
        data: Dict[str, List[str]] = self.config
        lst1: List[str] = ["end_hub", "start_hub", "hub"]
        lst_data: List[List[str]] = [data[i] for i in data if i in lst1]
        new_lst: List[str] = [i for j in lst_data for i in j]
        """add default values"""
        default: str = "[zone=normal color=none max_drones=1]"
        """check data format []"""
        lst: List[List[str]] = self.data_format(default, new_lst)
        names: List[str] = []
        for idx, i in enumerate(lst):
            for j in i:
                if "#" in j:
                    lst[idx] = i[: i.index(j)]
                    break
            if "-" in i[0] or " " in i[0]:
                raise ParsingError(
                    "Error: Zone name cannot contain"
                    f" dashes or spaces -> ({i[0]})",
                    self.find_line(i[0]),
                )
            names.append(i[0].strip())
        for i in lst:
            if len(i) != 4:
                raise ParsingError(
                    "Error: Zone data must respect the format:"
                    f" <name> <x> <y> [metadata] (in {i[0]})",
                    self.find_line(i[0]),
                )
        count = Counter(names)
        """check hubes names if duplicated"""
        for hub, n in count.items():
            if n != 1:
                raise ParsingError(
                    f"Error: Found duplicated hub: {hub}", self.find_line(hub)
                )
        return lst, names

    def meta_data_check(self) -> Dict[str, Any]:
        """validating hubs meta data"""
        data = self.zone_data_check()
        dct: Dict[str, List[Any]] = {}
        for i in data[0]:
            try:
                int(i[1])
                int(i[2])
            except Exception:
                raise ParsingError(
                    "Error: coordinates must be "
                    f"valid integers (x, y) in hub: {i[0]}",
                    self.find_line(i[0]),
                )
            i[3] = "=".join(x.strip() for x in i[3].split("="))

            coords = (int(i[1]), int(i[2]))
            metadata = [x for x in i[3].split(" ") if x != ""]

            entry: List[Any] = [coords] + metadata
            dct[i[0]] = entry
        default_meta = {"zone": "normal", "color": "none", "max_drones": "1"}
        zval: List[str] = ["normal", "blocked", "restricted", "priority"]
        for h in dct:
            new_dct: Dict[str, str] = {}
            for j in range(len(dct[h])):
                if j < 1:
                    continue
                try:
                    lest: List[str] = dct[h][j].split("=")
                    key, value = lest
                except Exception:
                    raise ParsingError(
                        f"metadata in {h} must follow the "
                        "following format: zone=<type> color=<value> "
                        "max_drones=<number>"
                    )
                if key.strip() not in default_meta.keys():
                    raise ParsingError(
                        f'Invalid metadata key: "{key}" in {h}'
                        f". Expected one of: {list(default_meta.keys())}"
                    )
                elif key.strip() == "zone" and value.strip() not in zval:
                    raise ParsingError(
                        f'Invalid zone type: "{value}" in {h}.'
                        f" Expected one of: {zval}"
                    )
                elif key.strip() == "color" and not value.strip().isalpha():
                    raise ParsingError(
                        f"Error: color in {h} must be a valid single-word "
                        f"strings (e.g., red, blue...)"
                    )
                elif key.strip() == "max_drones":
                    try:
                        v = int(value.strip())
                    except Exception:
                        raise ParsingError(
                            f"Error: {key} in {h} must be a valid integer"
                        )
                    if v < 1:
                        raise ParsingError(
                            f"Error: {key} in {h} must be > than 0")
                if key in new_dct:
                    raise ParsingError(
                        f"Duplicate metadata key ({key}) in {h}")
                new_dct[key] = value
            dct[h] = dct[h][:2]
            merged: Dict[str, str] = default_meta.copy()
            merged.update(new_dct)
            dct[h][1] = merged
        lst: List[Any] = []
        for i in dct.values():
            lst.append(i[0])
        count = Counter(lst)
        for k, v in count.items():
            if v != 1:
                raise ParsingError(
                    f"Error: Duplicated hub position -> {k}",
                    self.find_line(str(k))
                )
        return dct

    def connection_check(
        self,
    ) -> Tuple[
        Dict[str, List[Union[Tuple[int, int], Dict[str, str]]]],
        Dict[Tuple[str, str], int],
    ]:
        data = self.config
        self.check_duplicates()
        hubs = self.meta_data_check()
        nlst = data["connection"]
        for i in nlst:
            if "#" in i:
                nlst[nlst.index(i)] = i.split("#")[0]
        parsed = self.data_format("max_link_capacity=1", nlst)
        for i in parsed:
            if len(i) != 2:
                raise ParsingError(
                    "Error: invalid connection format:"
                    f"<name1>-<name2> [metadata] in ->  {i[0]}",
                    self.find_line(i[0]),
                )
        conn_str: Dict[str, str] = {}
        _, h_name = self.zone_data_check()
        for x in parsed:
            conn_name = x[0]
            metadata = x[1]
            if "=" not in metadata:
                raise ParsingError(f"Invalid metadata format: {metadata}")
            key, _ = metadata.split("=", 1)
            if key != "max_link_capacity":
                raise ParsingError(f"Error: Invalid metadata in ({x[0]})")
            conn_str[conn_name] = metadata

        connect = conn_str.keys()
        pairs: List[List[str]] = []
        for i in connect:
            if len(i.split("-")) != 2:
                raise ParsingError(
                    f"Error: invalid connection: {i}", self.find_line(i))
            elif len(i.split("-")) == 2:
                pairs.append(i.split("-"))
        start = self.config["start_hub"][0].strip().split()[0]
        end = self.config["end_hub"][0].strip().split()[0]
        s = 0
        e = 0
        for i in pairs:
            for j in i:
                if j not in h_name:
                    raise ParsingError(
                        f"Error: connection name must exist"
                        f" in hub names ({j})",
                        self.find_line(j),
                    )
                elif j == start:
                    s += 1
                elif j == end:
                    e += 1
        if s < 1:
            raise ParsingError(
                "Error: start point must have at least one connection",
                self.current_line,
            )
        if e < 1:
            raise ParsingError(
                "Error: end point must have at least one connection",
                self.current_line
            )
        idx = 0
        while idx < len(pairs):
            jdx = idx + 1
            if pairs[idx][0] == pairs[idx][1]:
                raise ParsingError(
                    f"Error: connection names must be different {pairs[idx]}",
                    self.find_line(pairs[idx][0]),
                )
            while jdx < len(pairs):
                if Counter(pairs[idx]) == Counter(pairs[jdx]):
                    raise ParsingError(
                        f"Error: Duplicated connection -> {pairs[idx]}",
                        self.find_line(pairs[idx][0]),
                    )
                jdx += 1
            idx += 1
        result: Dict[Tuple[str, str], str] = {
            (k.split("-")[0], k.split("-")[1]): v for k, v in conn_str.items()
        }
        for value in result.values():
            try:
                key, val = value.split("=")
            except Exception:
                raise ParsingError(
                    f"Error: Invalid data format in {value}"
                    f", it must be max_link_capacity=<number>"
                )
            if key != "max_link_capacity":
                raise ParsingError(f"Error: Invalid key in {key}")
            if not val:
                raise ParsingError(
                    f"Error: Invalid data format in {value}"
                    f", it must be max_link_capacity=<number>"
                )
            if not val.isdigit():
                raise ParsingError(
                    f"Error: Capacity must be a positive number in ({val})"
                )
            elif val.isdigit() and int(val) < 1:
                raise ParsingError(
                    f"Error: Capacity must be > than 0 in ({val})")
        final: Dict[Tuple[str, str], int] = {
            k: int(v.split("=")[1]) for k, v in result.items()
        }
        return hubs, final

    def _get_parsed(
        self,
    ) -> Any:
        if self._parsed is None:
            self._parsed = self.connection_check()
        return self._parsed

    def creat_zone_obj(self) -> List[Zone]:
        hubs, _ = self._get_parsed()
        start = self.config["start_hub"][0].strip().split()[0]
        end = self.config["end_hub"][0].strip().split()[0]
        zones: List[Zone] = []
        for name, value in hubs.items():
            zone = Zone(name, value)
            if name == start:
                zone.place = "start"
                zone.max_drones = int(self.config["nb_drones"][0])
            elif name == end:
                zone.place = "end"
                zone.max_drones = int(self.config["nb_drones"][0])
            else:
                zone.place = "hub"
            zones.append(zone)

        return zones

    def creat_conx_obj(self) -> List[Connection]:
        _, con = self._get_parsed()
        conx_lst: List[Connection] = []
        for i, j in con.items():
            conx_lst.append(Connection(i, j))
        return conx_lst

    def start_end_nbdrone(self) -> Tuple[int, str, str]:
        nb: int = int(self.config["nb_drones"][0].strip())
        st: str = self.config["start_hub"][0].strip().split()[0]
        end: str = self.config["end_hub"][0].strip().split()[0]
        return nb, st, end
