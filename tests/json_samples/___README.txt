This directory contains sample JSON output returned from the Scryfall API.

Almost all of them are Card data JSONs, representing different cards, tokens, emblems, game markers, etc.
Some are used stand-alone, to verify the card data importer can handle certain card types with special properties,
and some are used together to verify relationships between cards are handled properly.

The all_sets_data.json file contains the /api/sets/ API endpoint response with set-related data only present there,
like the set parent/child relationship and the set icon download URI.
