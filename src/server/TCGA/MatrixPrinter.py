__author__ = 'guorongxu'

def print_matrix(output_file_name, sample_list, sample_name_list, gene_name_list):

    filewriter = open(output_file_name, "a")

    ## Printing the header of the table
    sample_name_str = "gene_name\t"
    for sample_name in sample_name_list:
        sample_name_str = sample_name_str + sample_name + "\t"
    filewriter.write(sample_name_str[:-1] + "\n")

    for gene_name in gene_name_list:
        ## Printing the gene name in the 1st column
        ## We add a suffix "_v" to mark the mutation gene id so that to avoid the same name with gene id.
        expression_str = gene_name + "_v" + "\t"

        for sample in sample_list:
            gene_list = sample_list.get(sample)
            if gene_name in gene_list:
                expression_str = expression_str + str(gene_list.get(gene_name)) + "\t"
            else:
                expression_str = expression_str + "0\t"

        filewriter.write(expression_str[:-1] + "\n")

    filewriter.close()