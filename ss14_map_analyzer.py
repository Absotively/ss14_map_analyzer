import argparse
import base64
import csv
import pathlib
import sys
import yaml

# Ignore these files
# These maps are either weird or not in rotation
ignored_files = [
    "reach.yml",
    "relic.yml",
    "saltern.yml",
    "centcomm.yml"
]

# For each prefix, group entities with names beginning with that prefix together
grouping_prefixes = [
    "Airlock",
    "Wall",
    "WindowDirectional",
    "Window",
    "PosterLegit",
    "PosterContraband",
    "SignDirectional"
]

# Entities and prefix groups for which to report the number per thousand tiles
densities = [
    "PosterLegit",
    "PosterContraband",
    "SignDirectional",
    "StationMap"
]

yaml.add_multi_constructor(u'!type:', lambda loader, suffix, node: loader.construct_mapping(node))

def analyze_map(mappath):
    if mappath.name in ignored_files:
        return None

    map_info = {
      'tile_count': 0,
      'counts': {}
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
              if prefix not in map_info['counts']:
                map_info['counts'][prefix] = 0
              map_info['counts'][prefix] += len(ent['entities'])
              added = True
              break
          if not added:
            map_info['counts'][ent['proto']] = len(ent['entities'])

    return map_info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compiles some statistics about Space Station 14 maps')
    parser.add_argument('mappath', type=pathlib.Path)

    args = parser.parse_args()

    if args.mappath.is_dir():
        map_path_list = args.mappath.glob('*.yml')
    else:
        map_path_list = [args.mappath]
    all_maps_data = {}
    counted_things = set()
    for map_path in map_path_list:
        map_data = analyze_map(map_path)
        if map_data is None:
            continue
        all_maps_data[map_data['id']] = map_data
        counted_things |= set(map_data['counts'].keys())

    map_ids = list(all_maps_data.keys())
    map_ids.sort()
    reordered_data = []
    reordered_data.append(['Map ID'] + map_ids)
    reordered_data.append(['Tiles'] + [all_maps_data[x]['tile_count'] for x in map_ids])

    for density in densities:
        count_data = [ density ]
        if density in grouping_prefixes:
            count_data[0] += '*'
        density_data = [ density + ' density']
        for map_id in map_ids:
            map_tiles = all_maps_data[map_id]['tile_count']
            map_counts = all_maps_data[map_id]['counts']
            if density in map_counts:
                count_data.append(map_counts[density])
                density_data.append(1000 * map_counts[density] / map_tiles)
            else:
                count_data.append(0)
                density_data.append(0)
        reordered_data.append(count_data)
        reordered_data.append(density_data)

    for prefix in grouping_prefixes:
        if prefix in densities:
            continue
        count_data = [ prefix + '*' ]
        for map_id in map_ids:
            if prefix in all_maps_data[map_id]['counts']:
                count_data.append(all_maps_data[map_id]['counts'][prefix])
            else:
                count_data.append(0)
        reordered_data.append(count_data)

    for counted_thing in sorted(counted_things ^ set(densities) ^ set(grouping_prefixes)):
        count_data = [ counted_thing ]
        for map_id in map_ids:
            if counted_thing in all_maps_data[map_id]['counts']:
                count_data.append(all_maps_data[map_id]['counts'][counted_thing])
            else:
                count_data.append(0)
        reordered_data.append(count_data)

    writer = csv.writer(sys.stdout)
    for r in reordered_data:
        writer.writerow(r)
