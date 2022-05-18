from allensdk.core.structure_tree import StructureTree
from allensdk.core.reference_space_cache import ReferenceSpaceApi, ReferenceSpaceCache
from allensdk.api.queries.ontologies_api import OntologiesApi
import typing as tp
import pandas as pd
import re


# nodes = OntologiesApi().get_structures_with_sets(
#     strategy='lazy',
#     path=ReferenceSpaceCache(resolution, reference_space_key, manifest='manifest.json').get_cache_path(None, 'STRUCTURE_TREE'),
#     structure_graph_ids=1, 
#     **ReferenceSpaceCache.cache_json())
class Atlas(StructureTree):
    obsolete_parent_areas ={
            934: {
                'old_acronym' :'ENTmv',
                'new_id' :926,
                'new_acronym' :'ENTm',
                'new_acronym_list' :['ENTm'],
                'parent_id':909,
                'parent_acronym':'ENT'},
            22: {
                'old_acronym' :'PTLp',
                'new_id':22,
                'new_acronym' :'VISa-VISrl',
                'new_acronym_list' :['VISa', 'VISrl'],
                'parent_id' : 669,
                'parent_acronym':'VIS'}
                }
    obsolete_areas = {
            560 : {
                'old_acronym': 'CNspg',
                'new_id':607,
                'new_acronym' :'DCO-VCO',
                'new_acronym_list' :['DCO', 'VCO'],
                'parent_id' : 607,
                'new_parent_acronym':'CN'},
            112 : {
                'acronym': 'CNlam',
                'new_id':607,
                'new_acronym' :'DCO-VCO',
                'new_acronym_list' :['DCO', 'VCO'],
                'parent_id' : 607,
                'new_parent_acronym':'CN'}
            }
    # CONSTRUCTOR
    def __init__(self, nodes = None,resolution = 25, reference_space_key = 'annotation/ccf_2017'):
        if nodes == None:

            nodes = OntologiesApi().get_structures_with_sets(
                        strategy='lazy',
                        pre=self.clean_structures,
                        post=lambda x: self.clean_structures(x), 
                        path=ReferenceSpaceCache(resolution, reference_space_key, manifest='manifest.json').get_cache_path(None, 'STRUCTURE_TREE'),
                        structure_graph_ids=1, 
                        **ReferenceSpaceCache.cache_json())

        super().__init__(nodes)

    # converts ids into graph_orders
    def ids_to_graph_order(self, ids:tp.Sequence[int]):
        to_fn = lambda x: x['graph_order']
        graph_order = self.nodes_by_property('id', ids, to_fn)
        return graph_order

    #converts list of acronyms into ids
    def acronyms_to_ids(self, acronyms:tp.Sequence[str]):
        to_fn = lambda x: x['id']
        ids = self.nodes_by_property('acronym', acronyms, to_fn)
        return ids

    #converts list of ids into acronyms
    def ids_to_acronyms(self, ids:tp.Sequence[int]):
        to_fn = lambda x: x['acronym']
        ids = self.nodes_by_property('id', ids, to_fn)
        return ids

    #get colors from ids (rgb triplet or hex)
    def ids_to_colors(self, ids:tp.Sequence[int], color_model = "rgb") -> tp.Sequence[tuple]:
        if color_model == "hex":
            to_fn = lambda y: f"{y['rgb_triplet'][0]:02x}{y['rgb_triplet'][1]:02x}{y['rgb_triplet'][2]:02x}" 
        elif color_model == "rgb":
            to_fn = lambda x: x['rgb_triplet']
        elif color_model == "rgb_norm":
            to_fn = lambda x: [c/255 for c in x['rgb_triplet']]
        elif color_model == "rgb_plotly":
            to_fn = lambda x: f"rgb({x['rgb_triplet'][0]},{x['rgb_triplet'][1]},{x['rgb_triplet'][2]})"
        colors = self.nodes_by_property('id', ids, to_fn)
        return colors

    #get name of areas based on ids
    def ids_to_names(self, ids:tp.Sequence[int]) -> tp.Sequence[str]:
        to_fn = lambda x: x['name']
        names = self.nodes_by_property('id', ids, to_fn)
        return names
    
    #substitute area ids in pre-defined list
    def remap_area_ids(self, ids: tp.Sequence[int], newmap:tp.Mapping) -> tp.Sequence[int]:
        new_ids = [newmap[i]  if i in newmap.keys() else i for i in ids ]
        return new_ids
    
    # allign area id lists to the resolution level of another area id lists (supports conversion from a couple of obsolete ids [TO BE CHECKED AGAIN]])
    def match_structure_id_lists(self, list_to_match:tp.Sequence[int], reference_list:tp.Sequence[int], verbose:bool = False) -> tp.List[int] :
        matched_list = []
        non_matchable_ids = []
        for area in list_to_match:
            matched  = False
            for ref_area in reference_list:
                if area == ref_area:
                    matched_list.append(area)
                    matched  = True
                    break
                elif self.structure_descends_from(area, ref_area) :
                    matched_list.append(ref_area)
                    matched  = True
                    break
                elif self.structure_descends_from(ref_area, area) :
                    matched_list.append(area)
                    matched  = True
                    break
                elif self.structure_descends_from(area, 73) :
                    matched_list.append(73)
                    matched  = True
                    if verbose:                
                        print('found structures of the ventricular system in the proposed id list')
                    break
                # elif any([self.structure_descends_from(area,obsPar) for obsPar in self.obsolete_parent_areas.keys()]):
                #     # print('ok1')
                #     for obsPar in self.obsolete_parent_areas.keys():
                #         # print('ok2')
                #         if self.structure_descends_from(area,obsPar):
                #             matched_list.append(self.obsolete_parent_areas[obsPar]['new_id'])
                #             matched  = True
                #             # print('ok')
                #             if verbose:    
                #                 old_acr = self.obsolete_parent_areas[obsPar]['old_acronym']
                #                 print(f'Obsolete areas in the source list { old_acr }')
                #                 print(area, obsPar)
                #             break
                #     break
                # elif any([area == obsPar for obsPar in self.obsolete_areas.keys()]):
                #     for obsPar in self.obsolete_areas.keys():
                #         if area == obsPar :
                #             matched_list.append(self.obsolete_areas[obsPar]['new_id'])
                #             matched  = True
                #             if verbose:
                #                 old_acr = self.obsolete_areas[obsPar]['old_acronym']    
                #                 print(f'Obsolete areas in the source list { old_acr }')
                #             break
                #     break
            if matched == False:
                matched_list.append(None)
                non_matchable_ids.append(area)            
        return matched_list, non_matchable_ids

    #get list of ids of 12 major anatomical structures
    def get_major_divisions_ids(self):
        overlap = lambda x: (set([687527670]) & set(x['structure_set_ids']))
        filtered_dicts =  self.filter_nodes(overlap)
        return [x['id'] for x in filtered_dicts]

    #get list of ids of mid-ontology areas
    def get_midontology_structures_ids(self):
        overlap = lambda x: (set([167587189]) & set(x['structure_set_ids']))
        filtered_dicts =  self.filter_nodes(overlap)
        return [x['id'] for x in filtered_dicts]

    #get list of ids of cortical areas (43)
    def get_cortical_structures_ids(self):
        overlap = lambda x: (set([688152357]) & set(x['structure_set_ids']))
        filtered_dicts =  self.filter_nodes(overlap)
        return [x['id'] for x in filtered_dicts]

    # return string correspondent to the number of cortical layer (None if area id is not descendant of Isocortex)
    def get_layer_from_area_id(self, ids):
        isocrtx_ids = self.get_cortical_structures_ids()
        area_names = self.ids_to_names(ids)
        func = lambda x: self.extract_layer_number(x)
        is_isocortex = lambda x: self.structure_descends_from_any(x,isocrtx_ids)
        return list(map(lambda x: func(x) if is_isocortex else None, area_names))

    def get_hierarchy_matrix(self):
        return

    #extract layer number from name string (re module)
    def extract_layer_number(self,string):
        pattern_str = re.compile(r'Layer\w*\s*(\d\s*/*\s*\d*)', re.IGNORECASE)
        match_obj = re.search(pattern_str , repr(string) )

        return match_obj.groups()[0]

    #check if area descends from any area in a given list of candidate ids
    def structure_descends_from_any(self, area_id, list_of_parents):
        area_dict = self.nodes(area_id)
        inters = set(area_dict[0]['structure_id_path']).intersection(set(list_of_parents))
        logical = len(inters)>0
        return logical
    
    
    def multiIndexDf_from_fineDf(self, fineDf, verbose=False):

        id_list = fineDf.index.tolist()

        midOntologyIDs = self.get_midontology_structures_ids()
        # Match the fine IDs to the mid IDs
        mid, toDrop_mid = self.match_structure_id_lists(id_list, midOntologyIDs)
        if verbose:
            print(f"While matching MID ONTOLOGY structures, {len(toDrop_mid)} structures were dropped:")
            for ID in toDrop_mid:
                print(f"\t- ID: {ID} - Name: {self.get_structures_by_id([ID])[0]['name']}")
        

        # Adjust dataFrame for COARSE ontology structures
        coarseOntologyIDs = self.get_major_divisions_ids()
        coarseOntologyIDs.append(1009)     # Add Fiber tracts to the list
        # Match the fine IDs to the coarse IDs
        coarse, toDrop_coarse = self.match_structure_id_lists(id_list, coarseOntologyIDs)
        if verbose:
            print(f"While matching COARSE ONTOLOGY structures, {len(toDrop_coarse)} structures were dropped:")
            for ID in toDrop_coarse:
                print(f"\t- ID: {ID} - Name: {self.get_structures_by_id([ID])[0]['name']}")


        newIndices = [(a,b,c) for a,b,c in zip(coarse,mid,id_list)]
        
        # Mark as regions to drop those that have at lease a None in one of the 3 idexes
        toRemove = [not all(x) for x in newIndices]
        
        # Copy of the original dataframe to use as output
        df = fineDf.copy()
        # Put the multiindex
        df.index = pd.MultiIndex.from_tuples(newIndices, names=["coarse","mid","fine"])
        # Remove regions with a None
        df.drop(df[toRemove].index, inplace=True)
        
        return df

    

    

if __name__ == '__main__':

    a = Atlas()
