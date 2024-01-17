# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""


# from itertools import prod0
from src.Card_Identification.configuration_handler import MtGOCRData, CubeCobraData
from Levenshtein import distance as levenshtein_distance

mtg_ocr_config = MtGOCRData()
scryfall_all_data= mtg_ocr_config.open_scryfall_file()


from fuzzywuzzy import fuzz

def fuzzy_match(potential_name, actual_name):
    ratio = fuzz.ratio(potential_name, actual_name)
    if ratio >= 75:
        return True
    return False

for card in scryfall_all_data:
    if fuzzy_match(pot_name, card['name']) and pot_collector_number == card['collector_number'] and pot_set == card['set_name'] and pot_rarity == card['rarity']:
        # Found a matching card!
        print(card['name'])
        print(card['set_name'])
        print(card['collector_number'])
        print(card['rarity'])
        break


pot_names = ['Visage of Dread']
pot_collector_numbers = ["123", "456"]  # Add actual collector numbers
pot_sets = ["res", "Nwi", "LCE", "weS"]
pot_sets = ['res', 'Nwi', 'LCE', 'weS']
pot_rarities = ["U"]

def find_card_by_infos(pot_collector_numbers, pot_sets, pot_rarities, pot_cardnames, scryfall_all_data, verbose=0):

    updated_pot_rarities = []
    for rarity in pot_rarities:
        if rarity == "C":
            updated_pot_rarities.append("common")
        elif rarity == "T":
            updated_pot_rarities.append("token")
        elif rarity == "U":
            updated_pot_rarities.append("uncommon")
        elif rarity == "M":
            updated_pot_rarities.append("mythic")

    # Start by filtering the scryfall_data for "name"
    possible_cards = []
    for name in pot_cardnames:
        for card in scryfall_all_data:
            name_distance = levenshtein_distance(name.lower(), card["name"].lower())
            if name_distance <= 2:
                possible_cards.append(card)
    
    print("possible cards:", possible_cards)
   
   # # filter by collector number an set, but this is not needed now as it extends the data very much 
   # for pot_collector_number in pot_collector_numbers:
   #      for pot_set in pot_sets:
   #          for card in scryfall_all_data:
   #              if (levenshtein_distance(card["collector_number"].lower(), pot_collector_number.lower()) == 1) and (
   #                            levenshtein_distance(card["set"].lower(), pot_set.lower()) == 1):
   #                                possible_cards.append(card)
                          
    # Filter cards based on the remaining criteria
    if possible_cards:
       

        def custom_sort(card):
            # Calculate a score based on the Levenshtein distance for the name, set, rarity, and collector number
            name_dist = levenshtein_distance(card["name"].lower(), " ".join(pot_cardnames).lower())
            set_dist = levenshtein_distance(card["set"].lower(), " ".join(pot_sets).lower())
            rarity_dist = levenshtein_distance(card["rarity"].lower(), " ".join(pot_rarities).lower())
            if pot_collector_numbers:
                collector_num_dist = levenshtein_distance(card["collector_number"], " ".join(pot_collector_numbers))
            else:
                collector_num_dist = 0

            score = name_dist + set_dist + rarity_dist + collector_num_dist
            return score

        # Sort the possible cards by their score
        possible_cards.sort(key=custom_sort)
        best_match = possible_cards[0]

        # Return the best matching card
        return best_match, possible_cards
    else:
        return possible_cards[0], possible_cards


# Run the function
best_match, redcards= find_card_by_infos(pot_collector_numbers, pot_sets, pot_rarities, pot_names, scryfall_all_data)

if best_match:
    print("Best match:", best_match.get('name'))
else:
    print("No matching card found.")

for card in redcards:
    print(card["name"],card["set"],card["collector_number"])


def find_card_by_infos(pot_collector_numbers, pot_sets, pot_rarities, pot_cardnames, scryfall_all_data, verbose=0):

    updated_pot_rarities = []
    for rarity in pot_rarities:
        if rarity == "C":
            updated_pot_rarities.append("common")
        elif rarity == "T":
            updated_pot_rarities.append("token")
        elif rarity == "U":
            updated_pot_rarities.append("uncommon")
        elif rarity == "M":
            updated_pot_rarities.append("mythic")           
            
    # Start by filtering the scryfall_data for "name"
    possible_cards = []
    for name in pot_cardnames:
        for card in scryfall_all_data:
            name_distance = levenshtein_distance(name.lower(), card["name"].lower())
            if name_distance <= 2:
                possible_cards.append(card)
    
  
    print(possible_cards[0].get('name'))
    # Filter cards based on the remaining criteria
    if possible_cards:
        print("possible cards")
        refined_cards = []

        for criterium_type in ["collector_number", "set", "rarity"]:
            for card in possible_cards:
                print(card["collector_number"],card["set"],card["rarity"],card["name"])
                if criterium_type == "collector_number":
                    for collector_number in pot_collector_numbers:
                        print("given ccnumber", collector_number)
                        print(card["collector_number"])
                        if collector_number and card["collector_number"] == collector_number:
                            refined_cards.append(card)
                elif criterium_type == "set":
                    for pot_set in pot_sets:
                        print("given set", pot_set.lower())
                        print(card["set"])
                        if pot_set.lower() and card["set"] == pot_set :
                            refined_cards.append(card)
                elif criterium_type == "rarity":
                    for rarity in updated_pot_rarities:
                        print("giben rarity", rarity)
                        print(card["rarity"])
                        if rarity and card["rarity"] == rarity:
                        
                            refined_cards.append(card)

        if len(refined_cards) > 0 : 
            possible_cards = refined_cards
            print("cards were refined")
        # print(refinded_cards)
        print(possible_cards[0].get('name'))

        # Return the best matching card
        if possible_cards:
            best_match = min(possible_cards, key=lambda c: levenshtein_distance(c["name"].lower(), " ".join(pot_cardnames).lower()))
            return best_match, refined_cards
        else:
            return possible_cards, refined_cards
    else:
        return possible_cards, refined_cards

# Run the function
best_match, redcards= find_card_by_infos(pot_collector_numbers, pot_sets, pot_rarities, pot_names, scryfall_all_data)

if best_match:
    print("Best match:", best_match.get('name'))
else:
    print("No matching card found.")


    # 'uncommon'
   # ' 'collector_number''
# {'object': 'card', 'id': '3d4b61c6-3e88-49f5-9e16-aa8a59653327', 'oracle_id': '7cad43df-31c9-47b5-bc05-4a0f6544b396', 'multiverse_ids': [636836, 636837], 'mtgo_id': 118068, 'arena_id': 87276, 'tcgplayer_id': 525361, 'cardmarket_id': 743210, 'name': 'Visage of Dread // Dread Osseosaur', 'lang': 'en', 'released_at': '2023-11-17', 'uri': 'https://api.scryfall.com/cards/3d4b61c6-3e88-49f5-9e16-aa8a59653327', 'scryfall_uri': 'https://scryfall.com/card/lci/129/visage-of-dread-dread-osseosaur?utm_source=api', 'layout': 'transform', 'highres_image': True, 'image_status': 'highres_scan', 'cmc': 2.0, 'type_line': 'Artifact // Creature — Dinosaur Skeleton Horror', 'color_identity': ['B'], 'keywords': ['Craft', 'Transform', 'Menace', 'Mill'], 'card_faces': [{'object': 'card_face', 'name': 'Visage of Dread', 'mana_cost': '{1}{B}', 'type_line': 'Artifact', 'oracle_text': "When Visage of Dread enters the battlefield, target opponent reveals their hand. You choose an artifact or creature card from it. That player discards that card.\nCraft with two creatures {5}{B} ({5}{B}, Exile this artifact, Exile the two from among creatures you control and/or creature cards in your graveyard: Return this card transformed under its owner's control. Craft only as a sorcery.)", 'colors': ['B'], 'artist': 'David Auden Nash', 'artist_id': '092827e0-03f2-4e73-852e-d95eba0fef20', 'illustration_id': 'fb928322-345d-4e29-91c8-ac8ff7d51bb0', 'image_uris': {'small': 'https://cards.scryfall.io/small/front/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'normal': 'https://cards.scryfall.io/normal/front/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'large': 'https://cards.scryfall.io/large/front/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'png': 'https://cards.scryfall.io/png/front/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.png?1699044214', 'art_crop': 'https://cards.scryfall.io/art_crop/front/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'border_crop': 'https://cards.scryfall.io/border_crop/front/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214'}}, {'object': 'card_face', 'name': 'Dread Osseosaur', 'flavor_name': '', 'mana_cost': '', 'type_line': 'Creature — Dinosaur Skeleton Horror', 'oracle_text': 'Menace\nWhenever Dread Osseosaur enters the battlefield or attacks, you may mill two cards. (You may put the top two cards of your library into your graveyard.)', 'colors': ['B'], 'color_indicator': ['B'], 'power': '5', 'toughness': '4', 'flavor_text': '"It\'s not my fault! The glyphs for \'blessed\' and \'cursed\' look very similar!"\n—Diego, Brazen Coalition translator', 'artist': 'David Auden Nash', 'artist_id': '092827e0-03f2-4e73-852e-d95eba0fef20', 'illustration_id': '75f231ae-b1cd-4329-a55e-a90719d7b2a8', 'image_uris': {'small': 'https://cards.scryfall.io/small/back/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'normal': 'https://cards.scryfall.io/normal/back/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'large': 'https://cards.scryfall.io/large/back/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'png': 'https://cards.scryfall.io/png/back/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.png?1699044214', 'art_crop': 'https://cards.scryfall.io/art_crop/back/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214', 'border_crop': 'https://cards.scryfall.io/border_crop/back/3/d/3d4b61c6-3e88-49f5-9e16-aa8a59653327.jpg?1699044214'}}], 'legalities': {'standard': 'legal', 'future': 'legal', 'historic': 'legal', 'timeless': 'legal', 'gladiator': 'legal', 'pioneer': 'legal', 'explorer': 'legal', 'modern': 'legal', 'legacy': 'legal', 'pauper': 'not_legal', 'vintage': 'legal', 'penny': 'legal', 'commander': 'legal', 'oathbreaker': 'legal', 'brawl': 'legal', 'historicbrawl': 'legal', 'alchemy': 'legal', 'paupercommander': 'not_legal', 'duel': 'legal', 'oldschool': 'not_legal', 'premodern': 'not_legal', 'predh': 'not_legal'}, 'games': ['paper', 'arena', 'mtgo'], 'reserved': False, 'foil': True, 'nonfoil': True, 'finishes': ['nonfoil', 'foil'], 'oversized': False, 'promo': False, 'reprint': False, 'variation': False, 'set_id': '70169a6e-89d1-4a3a-aef7-3152958d55ac', 'set': 'lci', 'set_name': 'The Lost Caverns of Ixalan', 'set_type': 'expansion', 'set_uri': 'https://api.scryfall.com/sets/70169a6e-89d1-4a3a-aef7-3152958d55ac', 'set_search_uri': 'https://api.scryfall.com/cards/search?order=set&q=e%3Alci&unique=prints', 'scryfall_set_uri': 'https://scryfall.com/sets/lci?utm_source=api', 'rulings_uri': 'https://api.scryfall.com/cards/3d4b61c6-3e88-49f5-9e16-aa8a59653327/rulings', 'prints_search_uri': 'https://api.scryfall.com/cards/search?order=released&q=oracleid%3A7cad43df-31c9-47b5-bc05-4a0f6544b396&unique=prints', 'collector_number': '129', 'digital': False, 'rarity': 'uncommon', 'artist': 'David Auden Nash', 'artist_ids': ['092827e0-03f2-4e73-852e-d95eba0fef20'], 'border_color': 'black', 'frame': '2015', 'full_art': False, 'textless': False, 'booster': True, 'story_spotlight': False, 'edhrec_rank': 20130, 'penny_rank': 5423, 'preview': {'source': 'Everyeye.it', 'source_uri': 'https://www.everyeye.it/giochi/magic-the-gathering-le-caverne-perdute-di-ixalan/', 'previewed_at': '2023-10-30'}, 'prices': {'usd': '0.05', 'usd_foil': '0.08', 'usd_etched': None, 'eur': '0.06', 'eur_foil': '0.09', 'tix': '0.01'}, 'related_uris': {'gatherer': 'https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=636836&printed=false', 'tcgplayer_infinite_articles': 'https://tcgplayer.pxf.io/c/4931599/1830156/21018?subId1=api&trafcat=infinite&u=https%3A%2F%2Finfinite.tcgplayer.com%2Fsearch%3FcontentMode%3Darticle%26game%3Dmagic%26partner%3Dscryfall%26q%3DVisage%2Bof%2BDread%2B%252F%252F%2BDread%2BOsseosaur', 'tcgplayer_infinite_decks': 'https://tcgplayer.pxf.io/c/4931599/1830156/21018?subId1=api&trafcat=infinite&u=https%3A%2F%2Finfinite.tcgplayer.com%2Fsearch%3FcontentMode%3Ddeck%26game%3Dmagic%26partner%3Dscryfall%26q%3DVisage%2Bof%2BDread%2B%252F%252F%2BDread%2BOsseosaur', 'edhrec': 'https://edhrec.com/route/?cc=Visage+of+Dread'}, 'purchase_uris': {'tcgplayer': 'https://tcgplayer.pxf.io/c/4931599/1830156/21018?subId1=api&u=https%3A%2F%2Fwww.tcgplayer.com%2Fproduct%2F525361%3Fpage%3D1', 'cardmarket': 'https://www.cardmarket.com/en/Magic/Products/Search?referrer=scryfall&searchString=Visage+of+Dread&utm_campaign=card_prices&utm_medium=text&utm_source=scryfall', 'cardhoarder': 'https://www.cardhoarder.com/cards/118068?affiliate_id=scryfall&ref=card-profile&utm_campaign=affiliate&utm_medium=card&utm_source=scryfall'}}

