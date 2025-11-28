import argparse
import base64
import csv
import pathlib
import sys
import yaml

# Entities for which to report the number per thousand tiles
density_entities = ["StationMap"]

# For each prefix, group entities with names beginning with that prefix together
grouping_prefixes = ["SignDirectional"]

# Groups for which to report the number per thousand tiles
density_groups = ["SignDirectional"]

yaml.add_multi_constructor(u'!type:', lambda loader, suffix, node: loader.construct_mapping(node))

def analyze_map(mappath):
    map_info = {
      'tile_count': 0,
      'entity_counts': {},
      'entity_group_counts': dict.fromkeys(grouping_prefixes, 0),
      'densities': {}
    }

    with open(mappath, 'r') as mapfile:
        mapdata = yaml.load(mapfile, yaml.Loader)

    # count various things
    for k in mapdata['tilemap'].keys():
        if mapdata['tilemap'][k] == 'Space':
            space_tile_value = k
            break

    for ent in mapdata['entities']:
        if ent['proto'] == "":
            for dataent in ent['entities']:
                for comp in dataent['components']:
                    if comp['type'] == 'MapGrid':
                        for chunk in comp['chunks'].values():
                            tiles = base64.b64decode(chunk['tiles'])
                            tile_count = len(tiles) - tiles.count(space_tile_value)
                            map_info['tile_count'] += tile_count
                    elif comp['type'] == 'BecomesStation':
                        map_info['id'] = comp['id']
        else:
          added = False
          for prefix in grouping_prefixes:
            if ent['proto'].startswith(prefix):
              map_info['entity_group_counts'][prefix] += len(ent['entities'])
              added = True
              break
          if not added:
            map_info['entity_counts'][ent['proto']] = len(ent['entities'])

    for proto in density_entities:
      if proto in map_info['entity_counts']:
        map_info['densities'][proto + ' density'] = 1000 * map_info['entity_counts'][proto] / map_info['tile_count']

    for proto in density_groups:
      if proto in map_info['entity_group_counts']:
        map_info['densities'][proto + ' density'] = 1000 * map_info['entity_group_counts'][proto] / map_info['tile_count']

    return map_info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compiles some statistics about Space Station 14 maps')
    parser.add_argument('mappath', type=pathlib.Path)

    args = parser.parse_args()

    if args.mappath.is_dir():
        map_path_list = args.mappath.glob('*.yml')
    else:
        map_path_list = [args.mappath]
    all_maps_data = []
    for map_path in map_path_list:
        all_maps_data.append(analyze_map(map_path))

    print(all_maps_data)
    exit()

    writer = csv.DictWriter(sys.stdout, ['id', 'tile_count', 'maps', 'maps_density', 'directional_signs', 'directional_sign_density'])
    writer.writeheader()
    for m in all_maps_data:
        writer.writerow(m)
