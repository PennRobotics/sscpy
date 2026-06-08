from enum import Enum

##########
### use ssc::codegen::ELIGIBLE_OBJECTS;
class ObjectClass(Enum):
    # Passes both Layer 1 and Layer 2 filters.
    FULLY_ELIGIBLE
    # Passes Layer 1 but fails Layer 2.
    INTERMEDIATE
    # Fails Layer 1.
    INELIGIBLE

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
from ctypes import c_uint32, c_uint64

class Prng:
    def from_seed(self, seed):
        pass

    def next(self):
        # returns a non-negative i32
        pass

    def next_max(self, max):
        # returns a value in [0, max)
        pass

    def next_min_max(self, range):
        # returns a value in [min, max)
        pass

    def next_double(self):
        # returns a double in [0, 1)
        pass

def from_seed(seed):
    return Jkiss(
            x=c_uint32(seed),
            y=c_uint32(987654321),
            z=c_uint32(43219876),
            c=c_uint32(6543217)
            )

class JKiss:
    def __init__(self, seed):
        self.x = seed
        self.y
        self.z
        self.c

    def gen(self):
        self.x = c_uint32(314527869) * self.x + c_uint32(1234567)
        self.x = c_uint32(self.x)

        self.y = c_uint32(self.y ^ (self.y << 5))
        self.y = c_uint32(self.y ^ (self.y >> 7))
        self.y = c_uint32(self.y ^ (self.y << 22))

        # Should not overflow; max expected is 0xfffa28490005d7b6
        t = c_uint64(4294584393 * c_uint64(self.z) + c_uint64(self.c))
        self.z = c_uint32(t)
        self.c = c_uint32(t >> 32)

        return c_uint32(self.x + self.y + self.z)


    def next(self)
        while True:
            random = self.gen()
            if random == INT_MIN:
                continue;
            mask = random >> 31;
            yield (random ^ mask) + (mask & 1);

    def next_max(self, max):
        if max <= 0:
            yield 0;
        yield (self.gen() % max as u32) as i32  # TODO: continue port from here
    }

    fn next_min_max(&mut self, range: Range<i32>) -> i32 {
        let difference: u32 = (Wrapping(range.end) - Wrapping(range.start)).0 as u32;
        if difference <= 1 {
            range.start
        } else {
            (Wrapping(range.start) + Wrapping((self.gen() % difference) as i32)).0
        }
    }

    fn next_double(&mut self) -> f64 {
        let a: f64 = (self.gen() >> 6) as f64;
        let b: f64 = (self.gen() >> 5) as f64;

        (a * 134217728f64 + b) / 9007199254740992f64
    }
}


def get_prng(platform, seed):
    match(platform):
        case "arm":
            return new JKiss from_seed seed  # TODO
        _:  # TODO: raise error (x86 not supported!)
#####

class GenStock:
    def __init__(self, items):
        self.items = items

class GenItem:
    def __init__(self, eligible_index, price, quantity):
        self.eligible_index = eligible_index
        self.price = price
        self.quantity = quantity

# Forward-simulate stock for a given platform and RNG seed
def gen_stock(platform, seed) -> GeneratedStock {
    prng = get_prng(platform, seed)

    # Phase A: assign a Next() key to every eligible object, take the 10 smallest.
    keyed = [];
    for pos in range(TOTAL_OBJECTS):
        key = prng.next()
        if OBJECT_ENUMERATION[pos] is ObjectClass::FULLY_ELIGIBLE (@ idx):
            keyed.push((key, idx));
    keyed.sort();  # TODO: sort by key using lambda

    # Phase B: price and quantity rolls, one per slot in sort-key (= UI slot) order.
    items = []
    for k, v in keyed:
        set_idx = prng.next_max(10)
        mult_idx = prng.next_max(3)
        qty_roll = prng.next_double()

        elig_idx = keyed[slot].1;
        base_price = ELIGIBLE_OBJECTS[elig_idx as usize].price
        set_price = (set_idx as u16 + 1) * 100;
        multiplied = base_price * [3u16, 4u16, 5u16][mult_idx as usize];
        price = max(set_price, multiplied);
        quantity = if qty_roll < 0.1 { 5 } else { 1 };

        items.push_back(GenItem(eligible_index: elig_idx, price, quantity))

    return GenStock(items)

STOCK_QUANTITY = 10

class Platform(Enum):
    X86
    ARM

class Item:
    self.eligible_index
    self.price
    self.quantity

class TM {
    self.platform
    self.stock
    # precomputed: observed_slots[eligible_index] = Some(ui_slot) if stocked
    self.observed_slots

    def __init__(self, platform, stock):
        observed_slots = vec![None; TOTAL_ELIGIBLE];
        for slot, item in enumerate(stock):
            observed_slots[item.eligible_index] = Some(slot);
        self.platform = platform
        self.stock = stock
        self.observed_slots = observed_slots
    }

    def seed_valid(self, seed):
        prng = get_prng(self.platform, seed);

        # Phase A: Object shuffle with early rejection (807 next() calls)
        min_non_obs_eligible_key = INT_MAX;
        obs_keys = [0] * STOCK_QUANTITY
        obs_seen = [False] * STOCK_QUANTITY
        obs_count = 0
        max_obs_key = 0

        for pos in range(TOTAL_OBJECTS):
            key = prng.next()
            match OBJECT_ENUMERATION[pos].class {  # TODO-hi: continue port from here!
                ObjectClass::FullyEligible(elig_idx) => {
                    if let Some(slot) = self.observed_slots[elig_idx as usize] {
                        let s = slot as usize;

                        // Check against non-observed items
                        if min_non_obs_eligible_key < key {
                            return false;
                        }

                        // Check ordering against previously-seen observed items
                        for t in 0..STOCK_QUANTITY {
                            if obs_seen[t] {
                                if t < s && obs_keys[t] > key {
                                    return false; // earlier UI slot has larger key
                                }
                                if t > s && obs_keys[t] < key {
                                    return false; // later UI slot has smaller key
                                }
                            }
                        }

                        obs_keys[s] = key;
                        obs_seen[s] = true;
                        obs_count += 1;
                        if key > max_obs_key {
                            max_obs_key = key;
                        }
                    } else {
                        // Non-observed fully eligible item
                        if key < min_non_obs_eligible_key {
                            min_non_obs_eligible_key = key;
                        }
                        if key < max_obs_key {
                            return false;
                        }
                    }
                }
                ObjectClass::Intermediate | ObjectClass::Ineligible => {
                    // Just advance RNG, no checks needed
                }
            }
        }

        // Verify all 10 observed items were encountered
        if obs_count != STOCK_QUANTITY as u8 {
            return false;
        }

        // Final check: no non-observed eligible item beat the largest observed key
        // (already checked incrementally, but verify min_non_obs > max_obs)
        if min_non_obs_eligible_key < max_obs_key {
            return false;
        }

        // Phase B: Price and quantity verification (10 items x 3 RNG calls)
        // Items are processed in sort-key order (ascending), which matches UI slot order 0..9
        for slot in 0..STOCK_QUANTITY {
            let set_idx = prng.next_max(10);
            let mult_idx = prng.next_max(3);
            let qty_roll = prng.next_double();

            let item = &self.stock[slot];
            let base_price = ELIGIBLE_OBJECTS[item.eligible_index as usize].price;

            let set_price = (set_idx as u16 + 1) * 100; // [100, 200, ..., 1000]
            let multiplied = base_price * [3u16, 4u16, 5u16][mult_idx as usize];
            let expected_price = max(set_price, multiplied);
            let expected_qty: u8 = if qty_roll < 0.1 { 5 } else { 1 };

            if expected_price != item.price || expected_qty != item.quantity {
                return false;
            }
        }

        true
    }
}

pub fn possible_prices(eligible_index: u16) -> Vec<u16> {
    let base_price = ELIGIBLE_OBJECTS[eligible_index as usize].price;
    let mut prices: BTreeSet<u16> = BTreeSet::new();

    for set_idx in 0..10u16 {
        for mult_idx in 0..3usize {
            let set_price = (set_idx + 1) * 100;
            let multiplied = base_price * [3u16, 4u16, 5u16][mult_idx];
            prices.insert(max(set_price, multiplied));
        }
    }

    prices.into_iter().collect()
}

##########
### use ssc::xxhash::s_seed;
use xxhash_rust::xxh32::xxh32;

# Compute the shop RNG seed for a given days_active and uid.
# `xxHash32(pack_le_bytes([days_played % 2147483647, (uid/2) % 2147483647, 0, 0, 0]))`
def shop_seed(days_played, uid):
    dp = (days_played as f64 % 2147483647.0) as i32;
    k = ((uid / 2) as f64 % 2147483647.0) as i32;
    buf = [0u8; 20];
    buf[0..4].copy_from_slice(&dp.to_le_bytes());
    buf[4..8].copy_from_slice(&k.to_le_bytes());
    // bytes 8..20 are already zero
    xxh32(&buf, 0) as i32
}

/// Compute the SYNCED_RANDOM seed for a given key hash, uid, and days_played.
///
/// Matches the games `CreateRandom(key_hash, uniqueIDForThisGame, DaysPlayed)`:
/// `xxHash32(pack_le_bytes([key_hash % 2147483647, uid % 2147483647, days_played % 2147483647, 0, 0]))`
///
/// Note: uses full uid (NOT uid/2), unlike shop_seed.
def synced_random_seed(key_hash, uid, days_played: i32) -> i32 {
    let kh = (key_hash as f64 % 2147483647.0) as i32;
    let u = (uid as f64 % 2147483647.0) as i32;
    let dp = (days_played as f64 % 2147483647.0) as i32;
    let mut buf = [0u8; 20];
    buf[0..4].copy_from_slice(&kh.to_le_bytes());
    buf[4..8].copy_from_slice(&u.to_le_bytes());
    buf[8..12].copy_from_slice(&dp.to_le_bytes());
    // bytes 12..20 are already zero
    xxh32(&buf, 0) as i32
}

##########

fn main() {
def main():
    uid = 0
    platform = "x86"
    day = 1
    month = 1  # caution: 0-index!
    year = 1

    # TODO: argparse
            "--seed"
                uid = args[i].parse().expect("--seed must be a non-negative integer")
            "--platform"
                "arm"
                "x86"
                other? error
            "--day"
                (check range)
            "--month"
                (get as string, check range!!)
            "--year"
                (check range)
            other? error("unknown argument")

    days_active = (year - 1) * 112 + month * 28 + day
    seed = s_seed(days_active, uid)
    stock = gen_stock(platform, seed)

    month_name = ["A", "B", "C", "D"];  # TODO
    platform_name = "x86" if True else "arm"  # TODO

    print(f"Platform  : {}", platform_name)
    print(f"Date      : Day {} of {}, Year {} (days_played={})", day, season_name, year, days_played)
    print(f"UID       : {}", uid)
    print(f"Shop seed : {}", seed)
    print("")
    print(f"{:<4}  {:<32}  {:>7}  {:>3}", "Slot", "Item", "Price", "Qty")
    print(f"{}", "-".repeat(55))

    for slot, item in enumerate(stock.items) {
        obj = eligible_objects[item.eligible_index]
        print(f"{:<4}  {:<32}  {:>6}g  {:>3}x", slot, obj.name, item.price, item.quantity)
    }
}
