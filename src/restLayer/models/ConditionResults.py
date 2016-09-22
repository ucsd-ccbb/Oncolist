__author__ = 'aarongary'
from models.SearchResult import SearchResultModel
from models.GroupedItem import GroupedItem


class ConditionResultModel(SearchResultModel):
    def __init__(self):
        self.conditionId = 'cosmic_clinvar'

    def addGroupedCosmicConditions(self, groupItemTermName, groupedCondition):
        # Search the dictionary for the grouping term
        # if we find it we append the grouped condition
        # if we don't find it we insert the grouping term and add the grouped condition
        foundGroupedItem = False
        for grouped_item in self.grouped_items:
            if(grouped_item.groupedItemTerm == groupItemTermName):
                foundGroupedItem = True
                grouped_item.groupedItemsCosmic.append(groupedCondition)

        if(not foundGroupedItem):
            myGroupedItem = GroupedItem()
            myGroupedItem.groupedItemTerm = groupItemTermName
            myGroupedItem.groupedItemsCosmic.append(groupedCondition)
            self.grouped_items.append(myGroupedItem)

    def addGroupedClinvarConditions(self, groupItemTermName, groupedCondition):
        # Search the dictionary for the grouping term
        # if we find it we append the grouped condition
        # if we don't find it we insert the grouping term and add the grouped condition
        foundGroupedItem = False
        for grouped_item in self.grouped_items:
            if(grouped_item.groupedItemTerm == groupItemTermName):
                foundGroupedItem = True
                grouped_item.groupedItemsClinvar.append(groupedCondition)

        if(not foundGroupedItem):
            myGroupedItem = GroupedItem()
            myGroupedItem.groupedItemTerm = groupItemTermName
            myGroupedItem.groupedItemsClinvar.append(groupedCondition)
            self.grouped_items.append(myGroupedItem)

    def toJson(self):
        return_value = SearchResultModel.toJson(self)

        grouped_items = return_value['grouped_items']
        grouped_items_array = []

        for grouped_item in grouped_items:
            grouped_items_array.append(grouped_item.toJson())

        return_value['grouped_items'] = grouped_items_array

        return return_value
