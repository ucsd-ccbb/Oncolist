import json

class ConditionSearchResults():
    def __init__(self):
        self.searchTab = 'PHENOTYPES'
        self.clusterNodeName = ''
        self.geneScoreRangeMax = 100
        self.geneSuperList = []
        self.items = []
        self.geneScoreRangeStep = 0.1
        self.geneScoreRangeMin = 5
        self.searchGroupTitle = ''
        self.grouped_items = []
        self.grouped_items_gene = []
        self.grouped_by_conditions = []
        self.simple_disease_tissue_group = []
        self.basic_grouped_search_results = {}

    def to_JSON(self):
        return json.dumps([self], default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

    def add_simplified_cosmic_item(self, cosmic_items):
        self.simple_disease_tissue_group = cosmic_items

    def add_basic_cosmic_list(self, basic_list):
        self.basic_grouped_search_results = basic_list

    def addGroupedCosmicConditions(self, groupItemTermName, groupedCondition):
        # Search the dictionary for the grouping term
        # if we find it we append the grouped condition
        # if we don't find it we insert the grouping term and add the grouped condition
        foundGroupedItem = False
        for grouped_item in self.grouped_items:
            if(grouped_item['group_key'] == groupItemTermName):
                foundGroupedItem = True
                grouped_item['cosmic_conditions'].append(groupedCondition)

        if(not foundGroupedItem):
            add_this_grouped_item = {
                'group_key': groupItemTermName,
                'cosmic_conditions': [groupedCondition],
                'cosmic_conditions_count': 0,
                'clinvar_conditions': [],
                'clinvar_conditions_count': 0,
                'total_counts': 0
            }
            self.grouped_items.append(add_this_grouped_item)

    def addGroupedClinvarConditions(self, groupItemTermName, groupedCondition):
        # Search the dictionary for the grouping term
        # if we find it we append the grouped condition
        # if we don't find it we insert the grouping term and add the grouped condition
        foundGroupedItem = False
        for grouped_item in self.grouped_items:
            if(grouped_item['group_key'] == groupItemTermName):
                foundGroupedItem = True
                grouped_item['clinvar_conditions'].append(groupedCondition)

        if(not foundGroupedItem):
            add_this_grouped_item = {
                'group_key': groupItemTermName,
                'cosmic_conditions': [],
                'cosmic_conditions_count': 0,
                'clinvar_conditions': [groupedCondition],
                'clinvar_conditions_count': 0,
                'total_counts': 0
            }
            self.grouped_items.append(add_this_grouped_item)


    #===========================================================
    # GROUP CONDITIONS ~ Key: CONDITION Value: GENES
    #===========================================================
    def addGroupedCosmicConditionsGene(self, groupItemTermName, groupedGene, group_info): #, variants):
        # Search the dictionary for the grouping term
        # if we find it we append the grouped condition
        # if we don't find it we insert the grouping term and add the grouped condition
        group_tissue_type = ''
        group_condition_type = ''
        group_title_split = groupItemTermName.split('|')
        if(len(group_title_split) > 1):
            group_tissue_type = group_title_split[0]
            group_condition_type = group_title_split[1]

        foundGroupedItemGene = False
        for grouped_item_gene in self.grouped_items_gene:
            if(grouped_item_gene['group_key'] == groupItemTermName):
                foundGroupedItemGene = True
                grouped_item_gene['cosmic_genes'].append(groupedGene)

                for cosmicId_item in group_info['cosmic_ids']:
                    if(cosmicId_item not in grouped_item_gene['cosmic_id']):
                        grouped_item_gene['cosmic_id'].append(cosmicId_item)

                for pubmedId_item in group_info['pubmed_ids']:
                    if(pubmedId_item not in grouped_item_gene['pubmed_ids']):
                        grouped_item_gene['pubmed_ids'].append(pubmedId_item)

                #for variant_gene in variants:
                #    if(variant_gene not in grouped_item_gene['variants']):
                #        grouped_item_gene['variants'].append(variant_gene)

        if(not foundGroupedItemGene):
            add_this_grouped_item = {
                'group_key': groupItemTermName,
                'group_condition_type': group_condition_type,
                'group_tissue_type': group_tissue_type,
                'cosmic_genes': [groupedGene],
                'cosmic_id': group_info['cosmic_ids'],
                'pubmed_ids': group_info['pubmed_ids'],
                #'variants': variants,
                'cosmic_genes_count': 0,
                'clinvar_genes': [],
                'clinvar_genes_count': 0,
                'total_counts': 0
            }
            self.grouped_items_gene.append(add_this_grouped_item)

    def addGroupedClinvarConditionsGene(self, groupItemTermName, groupedGene, resources):
        # Search the dictionary for the grouping term
        # if we find it we append the grouped condition
        # if we don't find it we insert the grouping term and add the grouped condition
        group_tissue_type = ''
        group_condition_type = ''
        group_title_split = groupItemTermName.split('|')
        if(len(group_title_split) > 1):
            group_tissue_type = group_title_split[0]
            group_condition_type = group_title_split[1]
        else:
            group_tissue_type = groupItemTermName
            group_condition_type = groupItemTermName

        foundGroupedItem = False
        for grouped_item in self.grouped_items:
            if(grouped_item['group_key'] == groupItemTermName):
                foundGroupedItem = True
                grouped_item['clinvar_genes'].append(groupedGene)
                for resource in resources:
                    grouped_item['resources'].append(resource)

        if(not foundGroupedItem):
            add_this_grouped_item = {
                'group_key': groupItemTermName,
                'group_condition_type': group_condition_type,
                'group_tissue_type': group_tissue_type,
                'cosmic_genes': [],
                'cosmic_genes_count': 0,
                'pubmed_ids': [],
                'resources': resources,
                'clinvar_genes': [groupedGene],
                'clinvar_genes_count': 0,
                'total_counts': 0
            }
            self.grouped_items_gene.append(add_this_grouped_item)

    def group_items_by_conditions(self):
        for grouped_item in self.grouped_items_gene:

            foundGroupedItem = False
            for outer_grouped_item in self.grouped_by_conditions:
                if(outer_grouped_item['group_condition_type_key'] == grouped_item['group_condition_type'].replace('(','').replace(')','')):
                    foundGroupedItem = True
                    outer_grouped_item['group_condition_type_items'].append(grouped_item)

            if(not foundGroupedItem):
                add_this_grouped_item = {
                    'group_condition_type_key': grouped_item['group_condition_type'].replace('(','').replace(')',''),
                    'group_condition_type_items': [grouped_item],
                    'grouped_by_conditions_count': 0
                }
                self.grouped_by_conditions.append(add_this_grouped_item)

    def updateCounts(self):
        for grouped_item in self.grouped_items:
            grouped_item['cosmic_conditions_count'] = len(grouped_item['cosmic_conditions'])
            grouped_item['clinvar_conditions_count'] = len(grouped_item['clinvar_conditions'])
            grouped_item['total_counts'] = grouped_item['cosmic_conditions_count'] + grouped_item['clinvar_conditions_count']

        for grouped_item in self.grouped_items_gene:
            grouped_item['cosmic_genes_count'] = len(grouped_item['cosmic_genes'])
            grouped_item['clinvar_genes_count'] = len(grouped_item['clinvar_genes'])
            grouped_item['total_counts'] = grouped_item['cosmic_genes_count'] + grouped_item['clinvar_genes_count']

        for outer_grouped_item in self.grouped_by_conditions:
            outer_grouped_item['grouped_by_conditions_count'] = len(outer_grouped_item['group_condition_type_items'])



