__author__ = 'aarongary'

import json

class DrugSearchResult():
    def __init__(self):
        self.inferred_drugs = []

    def add_drug_item(self, drug_item):
        # Search the dictionary for the grouping term
        # if we find it we append the grouped condition
        # if we don't find it we insert the grouping term and add the grouped condition
        foundGroupedItem = False
        if(len(drug_item['drugs']) > 0):
            gene_id = drug_item['index']
            for drug_id in drug_item['drugs']:

                for grouped_item in self.inferred_drugs:
                    if(grouped_item.key == drug_item.):
                        foundGroupedItem = True
                        grouped_item.groupedItemsCosmic.append(groupedCondition)

                if(not foundGroupedItem):
                    myGroupedItem = GroupedItem()
                    myGroupedItem.groupedItemTerm = groupItemTermName
                    myGroupedItem.groupedItemsCosmic.append(groupedCondition)
                    self.grouped_items.append(myGroupedItem)



    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)