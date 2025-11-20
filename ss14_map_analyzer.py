import argparse
import base64
import csv
import pathlib
import sys
import yaml

yaml.add_multi_constructor(u'!type:', lambda loader, suffix, node: loader.construct_mapping(node))

def analyze_map(mappath):
    map_info = {'tile_count': 0, 'maps': 0, 'directional_signs': 0}

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
        elif ent['proto'] == 'StationMap':
            map_info['maps'] = len(ent['entities'])
        elif ent['proto'].startswith('SignDirectional'):
            map_info['directional_signs'] += len(ent['entities'])

    if 'maps' in map_info:
        map_info['maps_density'] = 1000 * map_info['maps']/map_info['tile_count']

    if 'directional_signs' in map_info:
        map_info['directional_sign_density'] = 1000 * map_info['directional_signs']/map_info['tile_count']

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

    writer = csv.DictWriter(sys.stdout, ['id', 'tile_count', 'maps', 'maps_density', 'directional_signs', 'directional_sign_density'])
    writer.writeheader()
    for m in all_maps_data:
        writer.writerow(m)
