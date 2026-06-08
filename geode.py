def getTreasureFromGeode(Item geode):
    if not IsGeode(geode):
        return None
    try:
        geodeId = geode.QualifiedItemId
        r = CreateRandom(
                Game1.stats.Get("MysteryBoxesOpened") if "MysteryBox" in geodeId.Contains("MysteryBox") else Game1.stats.GeodesCracked,
                Game1.uniqueIDForThisGame / 2,  # TODO slash slash?
                Game1.player.uniqueMultiplayerID.Value // 2)
        prewarm_amount = r.Next(1, 10)
        for _ in range(prewarm_amount):
            r.NextDouble()
        prewarm_amount = r.Next(1, 10)
        for _ in range(prewarm_amount):
            r.NextDouble()
        if "MysteryBox" in geodeId:
            if Game1.stats.Get("MysteryBoxesOpened") > 10 or geodeId == "(O)GoldenMysteryBox":
                rareMod = 2 if geodeId == "(O)GoldenMysteryBox") else 1
                if geodeId == "(O)GoldenMysteryBox" \
                        and Game1.player.stats.Get(StatKeys.Mastery(0)) != 0 \
                        and r.NextBool(0.005):
                    return ItemRegistry.Create("(O)GoldenAnimalCracker")
                if geodeId == "(O)GoldenMysteryBox" \
                        and r.NextBool(0.005)):
                    return ItemRegistry.Create("(BC)272")  # Auto-Petter
                if r.NextBool(0.002 * rareMod):
                    return ItemRegistry.Create("(O)279")  # Magic Rock Candy
                if r.NextBool(0.004 * rareMod):
                    return ItemRegistry.Create("(O)74")  # Prismatic Shard
                if r.NextBool(0.008 * rareMod):
                    return ItemRegistry.Create("(O)166")  # Treasure Chest
                if r.NextBool(0.01 * rareMod + 0.0 if Game1.player.mailReceived.Contains("GotMysteryBook") else 0.0004 * Game1.stats.Get("MysteryBoxesOpened")):
                    if not Game1.player.mailReceived.Contains("GotMysteryBook"):
                        Game1.player.mailReceived.Add("GotMysteryBook")
                        return ItemRegistry.Create("(O)Book_Mystery")
                    return ItemRegistry.Create(r.Choose("(O)PurpleBook", "(O)Book_Mystery"))
                if r.NextBool(0.01 * rareMod):
                    return ItemRegistry.Create(r.Choose("(O)797", "(O)373"))  # Pearl / Golden Pumpkin
                if r.NextBool(0.01 * rareMod):
                    return ItemRegistry.Create("(H)MysteryHat")
                if r.NextBool(0.01 * rareMod):
                    return ItemRegistry.Create("(S)MysteryShirt")
                if r.NextBool(0.01 * rareMod):
                    return ItemRegistry.Create("(WP)MoreWalls:11")  # Mystery Wallpaper
                if r.NextBool(0.1) || geodeId == "(O)GoldenMysteryBox":
                    match r.Next(15):
                        case 0:
                            return ItemRegistry.Create("(O)288", 5)  # Mega Bomb
                        case 1:
                            return ItemRegistry.Create("(O)253", 3)  # Triple Shot Espresso
                        case 2:
                            if Game1.player.GetUnmodifiedSkillLevel(1) >= 6 and r.NextBool():
                                return ItemRegistry.Create(r.Choose("(O)687", "(O)695"))  # Dressed Spinner / Cork Bobber
                            return ItemRegistry.Create("(O)242", 2)  # Dish O' The Sea
                        case 3:
                            return ItemRegistry.Create("(O)204", 2)  # Lucky Lunch
                        case 4:
                            return ItemRegistry.Create("(O)369", 20)  # Quality Fertilizer
                        case 5:
                            return ItemRegistry.Create("(O)466", 20)  # Deluxe Speed-Gro
                        case 6:
                            return ItemRegistry.Create("(O)773", 2)  # Life Elixer
                        case 7:
                            return ItemRegistry.Create("(O)688", 3)  # Warp Totem: Farm
                        case 8:
                            return ItemRegistry.Create("(O)" + r.Next(628, 634))  # Random Sapling
                        case 9:
                            return ItemRegistry.Create("(O)" + Crop.getRandomLowGradeCropForThisSeason(Game1.season), 20)
                        case 10:
                            if r.NextBool():
                                return ItemRegistry.Create("(W)60")  # Ossified Blade
                            return ItemRegistry.Create(r.Choose("(O)533", "(O)534"))  # Emerald Ring / Ruby Ring
                        case 11:
                            return ItemRegistry.Create("(O)621")  # Quality Sprinkler
                        case 12:
                            return ItemRegistry.Create("(O)MysteryBox", r.Next(3, 5))
                        case 13:
                            return ItemRegistry.Create("(O)SkillBook_" + r.Next(5))
                        case 14:
                            return getRaccoonSeedForCurrentTimeOfYear(Game1.player, r, 8)
            # First 10 non-golden mystery boxes jump here:
            match r.Next(14):
                case 0:
                    return ItemRegistry.Create("(O)395", 3)  # Coffee
                case 1:
                    return ItemRegistry.Create("(O)287", 5)  # Bomb
                case 2:
                    return ItemRegistry.Create("(O)" + Crop.getRandomLowGradeCropForThisSeason(Game1.season), 8)
                case 3:
                    return ItemRegistry.Create("(O)" + r.Next(727, 734))  # Fish Foods + Maple Bar
                case 4:
                    return ItemRegistry.Create("(O)" + getRandomIntWithExceptions(r, 194, 240, new List<int> { 217 }))  # Foods
                case 5:
                    return ItemRegistry.Create("(O)709", 10)  # Hardwood
                case 6:
                    return ItemRegistry.Create("(O)369", 10)  # Quality Fertilizer
                case 7:
                    return ItemRegistry.Create("(O)466", 10)  # Deluxe Speed-Gro
                case 8:
                    return ItemRegistry.Create("(O)688")  # Warp Totem: Farm
                case 9:
                    return ItemRegistry.Create("(O)689")  # Warp Totem: Mountains
                case 10:
                    return ItemRegistry.Create("(O)770", 10)  # Mixed Seeds
                case 11:
                    return ItemRegistry.Create("(O)MixedFlowerSeeds", 10)
                case 12:
                    if r.NextBool(0.4):
                        match r.Next(4):
                            case 0:  return "(O)525"  # Sturdy Ring
                            case 1:  return "(O)529"  # Amethyst Ring
                            case 2:  return "(O)888"  # Glowstone Ring
                            case _:  return f"(O){r.Next(531, 533)}"  # Aquamarine Ring / Jade Ring
                    return ItemRegistry.Create("(O)MysteryBox", 2)
                case 13:
                    return ItemRegistry.Create("(O)690")  # Warp Totem: Beach
                case _:
                    return ItemRegistry.Create("(O)382")  # Coal
        if r.NextBool(0.1) and Game1.player.team.SpecialOrderRuleActive("DROP_QI_BEANS"):
            return ItemRegistry.Create("(O)890", 5 if r.NextBool(0.25) else 1)  # Qi Bean
        if (Game1.objectData.TryGetValue(geode.ItemId, out var data)):  # TODO: what is this even???
            geodeDrops = [data.GeodeDrops]
            if geodeDrops != null && geodeDrops.Count > 0 && (!data.GeodeDropsDefaultItems || r.NextBool()):  # TODO
                foreach (ObjectGeodeDropData drop in data.GeodeDrops.OrderBy((ObjectGeodeDropData p) => p.Precedence))
                    if (!r.NextBool(drop.Chance) || (drop.Condition != null && !GameStateQuery.CheckConditions(drop.Condition, null, null, null, null, r))):
                        continue
                    # TODO: figure out next line
                    Item item = ItemQueryResolver.TryResolveRandomItem(drop, new ItemQueryContext(null, null, r), avoidRepeat: false, null, null, null, delegate(string query, string error) {
                        Game1.log.Error($"Geode item '{geode.QualifiedItemId}' failed parsing item query '{query}' for {"GeodeDrops"} entry '{drop.Id}': {error}")
                    })
                    if item:
                        if drop.SetFlagOnPickup:
                            item.SetFlagOnPickup = drop.SetFlagOnPickup
                        return item
        int amount = 2 * r.Next(3) + 1
        if r.NextBool(0.1):
            amount = 10
        if r.NextBool(0.01):
            amount = 20
        if r.NextBool():
            match r.Next(4):
                case 0 | 1:
                    return ItemRegistry.Create("(O)390", amount)  # Stone
                case 2:
                    return ItemRegistry.Create("(O)330")  # Clay
                case _:
                    match geodeId:
                        case "(O)749":
                            return ItemRegistry.Create("(O)" + (82 + r.Next(3) * 2))  # Omni -> Fire Quartz / Frozen Tear / Earth Crystal
                        case "(O)535":
                            return ItemRegistry.Create("(O)86")  # Geode -> Earth Crystal
                        case "(O)536":
                            return ItemRegistry.Create("(O)84")  # Frozen Geode -> Frozen Tear
                        case _:
                            return ItemRegistry.Create("(O)82")  # Magma Geode -> Fire Quartz
        if geodeId != "(O)535":  # [not] Geode
            if geodeId == "(O)536":  # Frozen Geode
                match r.Next(4):
                    case 0:
                        return ItemRegistry.Create("(O)378", amount)  # Copper Ore
                    case 1:
                        return ItemRegistry.Create("(O)380", amount)  # Iron Ore
                    case 2:
                        return ItemRegistry.Create("(O)382", amount)  # Coal
                    case _:
                        return ItemRegistry.Create("(O)384" if Game1.player.deepestMineLevel > 75 else "(O)380", amount)  # Gold Ore / Iron Ore
            match r.Next(5):
                case 0:
                    return ItemRegistry.Create("(O)378", amount)  # Copper Ore
                case 1:
                    return ItemRegistry.Create("(O)380", amount)  # Iron Ore
                case 2:
                    return ItemRegistry.Create("(O)382", amount)  # Coal
                case 3:
                    return ItemRegistry.Create("(O)384", amount)  # Gold Ore
                case _:
                    return ItemRegistry.Create("(O)386", amount / 2 + 1)  # Iridium Ore
        match r.Next(3):
            case 0:
                return ItemRegistry.Create("(O)378", amount)  # Copper Ore
            case 1:
                return ItemRegistry.Create("(O)380" if Game1.player.deepestMineLevel > 25 else "(O)378", amount)  # Iron Ore / Copper Ore
            case _:
                return ItemRegistry.Create("(O)382", amount)  # Coal
    except Exception as e:
        Game1.log.Error("Geode '" + geode?.QualifiedItemId + "' failed creating treasure.", e)

    return ItemRegistry.Create("(O)390")  # Stone
