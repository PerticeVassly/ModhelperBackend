from .mongodb_manager import metaInfosRepository

# use to match the std entity name
all_mod_names = metaInfosRepository.find_all_mod_names()
all_item_names = metaInfosRepository.find_all_item_names()
all_entity_names = metaInfosRepository.find_all_entity_names()
all_biome_names = metaInfosRepository.find_all_biome_names()
all_structure_names = metaInfosRepository.find_all_structure_names()