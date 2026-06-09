import ctypes  # TODO-debug
from enum import Enum, auto
import struct

import numpy as np
import numba

import xxhash

TOTAL_OBJECTS = 773

##########
### use ssc::codegen::ELIGIBLE_OBJECTS;
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

##########
### use ssc::tm::{gen_stock, Platform};
# uses max, BTreeSet, serde, prng, internal classes

#####
# PRNG
class JKiss:
    def __init__(self, seed):
        self.x = np.uint32(seed),
        self.y = np.uint32(987654321),
        self.z = np.uint32(43219876),
        self.c = np.uint32(6543217)

    @numba.njit(parallel=True)
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
        while True:
            random = self.gen()
            if random == INT_MIN:
                continue;
            mask = random >> np.uint32(31);
            yield (random ^ mask) + (mask & np.uint32(1));

    def next_max(self, max):
        if max <= 0:
            yield 0;
        yield self.gen() % np.uint32(max)

    def next_min_max(self, range):
        difference = range[1] - range[0]
        return np.uint32(range[0]) if difference <= 1 else np.uint32(range[0]) + (self.gen() % np.uint32(difference))

    def next_double(self):
        a = self.gen() >> np.uint32(6)
        b = self.gen() >> np.uint32(5)

        return np.float(np.uint64(a) * np.uint64(134217728) + b) / np.float(9007199254740992)


def get_prng(seed):
    return JKiss(seed)

class GenStock:
    def __init__(self, items):
        self.items = items

class GenItem:
    def __init__(self, eligible_index, price, quantity):
        self.eligible_index = eligible_index
        self.price = price
        self.quantity = quantity

# Forward-simulate stock for a given platform and RNG seed
def gen_stock(seed):
    prng = get_prng(seed)

    # Phase A: assign a Next() key to every eligible object, take the 10 smallest.
    keyed = []
    for pos in range(TOTAL_OBJECTS):
        key = prng.next()
        #if OBJECT_ENUMERATION[pos] is ObjectClass.FULLY_ELIGIBLE:  # (@ idx):  # TODO???
        #    keyed.push((key, idx));
    keyed.sort()  # TODO: sort by key using lambda

    # Phase B: price and quantity rolls, one per slot in sort-key (= UI slot) order.
    items = []
    for k, v in keyed:
        set_idx = prng.next_max(10)
        mult_idx = prng.next_max(3)
        qty_roll = prng.next_double()

        #elig_idx = keyed[slot].1;  # TODO
        base_price = ELIGIBLE_OBJECTS[elig_idx].price
        set_price = (set_idx + 1) * 100
        multiplied = base_price * {0:3, 1:4, 2:5}[mult_idx]
        price = max(set_price, multiplied)
        quantity = 5 if qty_roll < 0.1 else 1

        items.append(GenItem(elig_idx, price, quantity))

    return GenStock(items)

STOCK_QUANTITY = 10

class Item:
    eligible_index = None
    price = None
    quantity = None

class TM:
    stock = None
    # precomputed: observed_slots[eligible_index] = Some(ui_slot) if stocked
    observed_slots = None

    def __init__(self, stock):
        observed_slots = [None] * TOTAL_ELIGIBLE
        for slot, item in enumerate(stock):
            observed_slots[item.eligible_index] = Some(slot);
        self.stock = stock
        self.observed_slots = observed_slots

    def seed_valid(self, seed):
        prng = get_prng(seed);

        # Phase A: Object shuffle with early rejection (807 next() calls)
        min_non_obs_eligible_key = INT_MAX;
        obs_keys = [0] * STOCK_QUANTITY
        obs_seen = [False] * STOCK_QUANTITY
        obs_count = 0
        max_obs_key = 0

        for pos in range(TOTAL_OBJECTS):
            key = prng.next()
###             match OBJECT_ENUMERATION[pos].class {  # TODO-hi: continue port from here!
###                 ObjectClass::FullyEligible(elig_idx) => {
###                     if let Some(slot) = self.observed_slots[elig_idx as usize] {
###                         let s = slot as usize;
### 
###                         // Check against non-observed items
###                         if min_non_obs_eligible_key < key {
###                             return false;
###                         }
### 
###                         // Check ordering against previously-seen observed items
###                         for t in 0..STOCK_QUANTITY {
###                             if obs_seen[t] {
###                                 if t < s && obs_keys[t] > key {
###                                     return false; // earlier UI slot has larger key
###                                 }
###                                 if t > s && obs_keys[t] < key {
###                                     return false; // later UI slot has smaller key
###                                 }
###                             }
###                         }
### 
###                         obs_keys[s] = key;
###                         obs_seen[s] = true;
###                         obs_count += 1;
###                         if key > max_obs_key {
###                             max_obs_key = key;
###                         }
###                     } else {
###                         // Non-observed fully eligible item
###                         if key < min_non_obs_eligible_key {
###                             min_non_obs_eligible_key = key;
###                         }
###                         if key < max_obs_key {
###                             return false;
###                         }
###                     }
###                 }
###                 ObjectClass::Intermediate | ObjectClass::Ineligible => {
###                     // Just advance RNG, no checks needed
###                 }
###             }
###         }
### 
###         // Verify all 10 observed items were encountered
###         if obs_count != STOCK_QUANTITY as u8 {
###             return false;
###         }
### 
###         // Final check: no non-observed eligible item beat the largest observed key
###         // (already checked incrementally, but verify min_non_obs > max_obs)
###         if min_non_obs_eligible_key < max_obs_key {
###             return false;
###         }
### 
###         // Phase B: Price and quantity verification (10 items x 3 RNG calls)
###         // Items are processed in sort-key order (ascending), which matches UI slot order 0..9
###         for slot in 0..STOCK_QUANTITY {
###             let set_idx = prng.next_max(10);
###             let mult_idx = prng.next_max(3);
###             let qty_roll = prng.next_double();
### 
###             let item = &self.stock[slot];
###             let base_price = ELIGIBLE_OBJECTS[item.eligible_index as usize].price;
### 
###             let set_price = (set_idx as u16 + 1) * 100; // [100, 200, ..., 1000]
###             let multiplied = base_price * [3u16, 4u16, 5u16][mult_idx as usize];
###             let expected_price = max(set_price, multiplied);
###             let expected_qty: u8 = if qty_roll < 0.1 { 5 } else { 1 };
### 
###             if expected_price != item.price || expected_qty != item.quantity {
###                 return False;
###             }
###         }
### 
###         return True
###     }
### }
### 
### pub fn possible_prices(eligible_index: u16) -> Vec<u16> {
###     let base_price = ELIGIBLE_OBJECTS[eligible_index as usize].price;
###     let mut prices: BTreeSet<u16> = BTreeSet::new();
### 
###     for set_idx in 0..10u16 {
###         for mult_idx in 0..3usize {
###             let set_price = (set_idx + 1) * 100;
###             let multiplied = base_price * [3u16, 4u16, 5u16][mult_idx];
###             prices.insert(max(set_price, multiplied));
###         }
###     }
### 
###     prices.into_iter().collect()
### }

##########
### use ssc::xxhash::s_seed;
#use xxhash_rust::xxh32::xxh32;

# Compute the shop RNG seed for a given days_played and uid.
# `xxHash32(pack_le_bytes([days_played % 2147483647, (uid/2) % 2147483647, 0, 0, 0]))`
### def shop_seed(days_played, uid):
###     dp = (days_played as f64 % 2147483647.0) as i32;
###     k = ((uid / 2) as f64 % 2147483647.0) as i32;
###     buf = [0u8; 20];
###     buf[0..4].copy_from_slice(&dp.to_le_bytes());
###     buf[4..8].copy_from_slice(&k.to_le_bytes());
###     // bytes 8..20 are already zero
###     xxh32(&buf, 0) as i32
### }
### 
### /// Compute the SYNCED_RANDOM seed for a given key hash, uid, and days_played.
### ///
### /// Matches the games `CreateRandom(key_hash, uniqueIDForThisGame, DaysPlayed)`:
### /// `xxHash32(pack_le_bytes([key_hash % 2147483647, uid % 2147483647, days_played % 2147483647, 0, 0]))`
### ///
### /// Note: uses full uid (NOT uid/2), unlike shop_seed.
### def synced_random_seed(key_hash, uid, days_played: i32) -> i32 {
###     let kh = (key_hash as f64 % 2147483647.0) as i32;
###     let u = (uid as f64 % 2147483647.0) as i32;
###     let dp = (days_played as f64 % 2147483647.0) as i32;
###     let mut buf = [0u8; 20];
###     buf[0..4].copy_from_slice(&kh.to_le_bytes());
###     buf[4..8].copy_from_slice(&u.to_le_bytes());
###     buf[8..12].copy_from_slice(&dp.to_le_bytes());
###     // bytes 12..20 are already zero
###     xxh32(&buf, 0) as i32
### }

##########

def main():
    uid = 0
    day = 1
    season = 0  # caution: 0-index!
    year = 2

    # TODO: argparse
    ###         "--seed"
    ###             uid = args[i].parse().expect("--seed must be a non-negative integer")
    ###         "--day"
    ###             (check range)
    ###         "--season"
    ###             (get as string, check range!!)
    ###         "--year"
    ###             (check range)
    ###         other? error("unknown argument")

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
    print("{:<4}  {:<32}  {:>7}  {:>3}".format("Slot", "Item", "Price", "Qty"))
    print("{}".format("-"*55))

    for slot, item in enumerate(stock.items):
        obj = eligible_objects[item.eligible_index]
        print("{:<4}  {:<32}  {:>6}g  {:>3}x".format(slot, obj.name, item.price, item.quantity))

if __name__ == "__main__":
    main()
