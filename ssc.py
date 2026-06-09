import ctypes  # TODO-debug
from enum import Enum, auto
import struct

import numpy as np
import numba

import xxhash

class ObjectClass(Enum):
    # Passes both Layer 1 and Layer 2 filters.
    FULLY_ELIGIBLE = auto()
    # Passes Layer 1 but fails Layer 2.
    INTERMEDIATE = auto()
    # Fails Layer 1.
    INELIGIBLE = auto()

class EligibleObject:
    def __init__(self, objid, name, price):
        self.id = objid
        self.name = name
        self.price = price

class JKiss:
    def __init__(self, seed):
        np.seterr(over='ignore')
        self.x = np.uint32(seed)
        self.y = np.uint32(987654321)
        self.z = np.uint32(43219876)
        self.c = np.uint32(6543217)

    def gen(self):
        self.x = np.uint32(314527869) * self.x + np.uint32(1234567)

        self.y ^= self.y << np.uint32(5)
        self.y ^= self.y >> np.uint32(7)
        self.y ^= self.y << np.uint32(22)

        t = np.uint64(4294584393) * np.uint64(self.z) + np.uint64(self.c)
        self.z = np.uint32(t & np.uint64(0xFFFFFFFF))
        self.c = np.uint32(t >> np.uint32(32))

        return np.uint32(self.x + self.y + self.z)

    def next(self):
        random = np.int32(self.gen())
        while random == np.int32(-2147483648):
            random = np.int32(self.gen())
        mask = random >> np.int32(31);
        return (random ^ mask) + (mask & np.int32(1));

    def next_max(self, max):
        if max <= 0:
            return 0;
        return np.int32(self.gen() % np.int32(max))

    def next_min_max(self, range):
        difference = range[1] - range[0]
        return np.int32(range[0]) if difference <= 1 else np.int32(range[0]) + (self.gen() % np.uint32(difference))

    def next_double(self):
        a = self.gen() >> np.uint32(6)
        b = self.gen() >> np.uint32(5)
        return np.float64(np.uint64(a) * np.uint64(134217728) + b) / np.float64(9007199254740992)


class GenStock:
    def __init__(self, items):
        self.items = items

class GenItem:
    def __init__(self, eligible_index, price, quantity):
        self.eligible_index = eligible_index
        self.price = price
        self.quantity = quantity

import json
all_objects = []
enumeration_entries = []
eligible_objects = []

with open("Objects.json", "r") as fh:
    obj_data = json.load(fh)
    for i, obj_idx in enumerate(obj_data):
        obj = obj_data[obj_idx]
        all_objects.append(obj)

        name = obj["Name"]
        price = obj["Price"]
        ty = obj["Type"]
        category = obj["Category"]
        exclude = obj["ExcludeFromRandomSale"]
        try:
            oid = int(obj_idx)
        except ValueError:
            oid = -1
        passes_random_items = (oid == -2 or oid >= 2 and oid <= 789) and not exclude and price > 0
        if not passes_random_items:
            enumeration_entries.append(ObjectClass.INELIGIBLE)
            continue

        # Layer 2
        passes_condition = category < 0 \
                and category != -999 \
                and ty != "Quest" \
                and ty != "Minerals" \
                and ty != "Arch"
        if not passes_condition:
            enumeration_entries.append(ObjectClass.INTERMEDIATE)
            continue

        # Fully eligible for travelling cart
        enumeration_entries.append(ObjectClass.FULLY_ELIGIBLE)
        eligible_objects.append(EligibleObject(oid, name, price))

TOTAL_OBJECTS = len(enumeration_entries)
TOTAL_ELIGIBLE = len(eligible_objects)

# Forward-simulate stock for a given platform and RNG seed
def gen_stock(seed):
    prng = JKiss(seed)

    # Phase A: assign a Next() key to every eligible object, take the 10 smallest.
    keyed = []
    for pos in range(TOTAL_OBJECTS):
        key = prng.next()
        if enumeration_entries[pos] == ObjectClass.FULLY_ELIGIBLE:
            keyed.append((int(np.uint32(key)), len(keyed)))
    keyed.sort()

    # Phase B: price and quantity rolls, one per slot in sort-key (= UI slot) order.
    items = []
    for _, elig_idx in keyed[:10]:
        set_idx = prng.next_max(10)
        mult_idx = prng.next_max(3)
        qty_roll = prng.next_double()

        base_price = eligible_objects[elig_idx].price
        set_price = (set_idx + 1) * 100
        multiplied = base_price * {0:3, 1:4, 2:5}[mult_idx]
        price = max(set_price, multiplied)
        quantity = 5 if qty_roll < 0.1 else 1

        items.append(GenItem(elig_idx, price, quantity))

    return GenStock(items)

### /// Compute the SYNCED_RANDOM seed for a given key hash, uid, and days_played.
### ///
### /// Matches the games `CreateRandom(key_hash, uniqueIDForThisGame, DaysPlayed)`:
### /// `xxHash32(pack_le_bytes([key_hash % 2147483647, uid % 2147483647, days_played % 2147483647, 0, 0]))`


def main():
    uid = 0
    day = 1
    season = 0  # caution: 0-index!
    year = 1
    # TODO: argparse
    ###         "--seed"
    ###             uid = args[i].parse().expect("--seed must be a non-negative integer")
    ###         "--day"
    ###             (check range)
    ###         "--season"
    ###             (get as string, check range!!)
    ###         "--year"
    ###             (check range)

    days_played = (year - 1) * 112 + season * 28 + day
    xxHash32 = xxhash.xxh32()
    xxHash32.update(struct.pack("<IIIII", days_played % 2147483647, (uid//2) % 2147483647, 0, 0, 0))
    seed = xxHash32.intdigest()
    stock = gen_stock(seed)

    season_name = ["Spring", "Summer", "Fall", "Winter"]

    print("Platform  : Switch")
    print("Date      : Day {} of {}, Year {} (days_played={})".format(day, season_name[season], year, days_played))
    print("User seed : {}".format(uid))
    print("Shop seed : {}".format(ctypes.c_int32(seed).value))
    print("")
    print("{:<4}  {:<32}  {:>7}   {:>3}".format("Slot", "Item", "Price", "Qty"))
    print("{}".format("-"*55))

    for slot, item in enumerate(stock.items):
        obj = eligible_objects[item.eligible_index]
        print("{:<4}  {:<32}  {:>6}g  {:>3}x".format(slot, obj.name, item.price, item.quantity))

if __name__ == "__main__":
    main()
