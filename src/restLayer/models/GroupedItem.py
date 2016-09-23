__author__ = 'aarongary'

class GroupedItem():
    def __init__(self):
        self.groupedItemTerm = ''
        self.groupedItemsClinvar = []
        self.groupedItemsCosmic = []

    def toJson(self):
        return_value = {
            'gene_name': self.groupedItemTerm,
            'phenotypes_clinvar': self.groupedItemsClinvar,
            'phenotypes_cosmic': self.groupedItemsCosmic
        }

        return return_value

