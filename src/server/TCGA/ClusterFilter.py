__author__ = 'guorongxu'

import os
import re
import sys

## deduplicate the cluster files.
def deduplicate_cluster(cluster_file_dir, combination):
    clusters = {}
    for gamma in [1, 4, 7, 11, 14, 17, 20]:
        cluster_folder = cluster_file_dir + "/" + combination + "_gamma_" + str(gamma)
        cluster_file = cluster_folder + "/" + combination + "_gamma_" + str(gamma) + ".louvain.tsv"

        if not os.path.exists(cluster_file):
            continue

        print "system is deduplicating: " + cluster_file
        with open(cluster_file) as fp:
            lines = fp.readlines()

            for line in lines:
                if line.startswith("corr"):
                    continue

                fields = re.split(r'\t', line)
                ## gamma + group_id as the key of clusters
                key = str(gamma) + "-" + fields[1]
                if key not in clusters:
                    genes = set([fields[3], fields[4][:-1]])
                    clusters.update({key:genes})
                else:
                    genes = clusters.get(key)
                    genes.add(fields[3])
                    genes.add(fields[4][:-1])
                    clusters.update({key:genes})

        fp.closed

    uniq_cluster_id = {}
    similar_cluster_id = {}

    print cluster_file_dir + ": total cluster: " + str(len(clusters))

    for index_i, cluster_i in clusters.items():
        has_similar_cluster = False
        is_min_cluster = True
        for index_j, cluster_j in clusters.items():
            if index_i == index_j:
                continue
            intersection_clusters = cluster_i.intersection(cluster_j)
            if float(len(intersection_clusters)) / float(len(cluster_i)) > 0.75 \
                    and float(len(intersection_clusters)) / float(len(cluster_j)) > 0.75:
                has_similar_cluster = True
                ## only keep the shortest cluster if has similar clusters
                if len(cluster_i) > len(cluster_j):
                    is_min_cluster = False
                    similar_cluster_id.update({index_i:index_i})

                if len(cluster_i) == len(cluster_j) and index_j not in uniq_cluster_id:
                    similar_cluster_id.update({index_j:index_j})

        if (has_similar_cluster and is_min_cluster and index_i not in similar_cluster_id) or not has_similar_cluster:
            uniq_cluster_id.update({index_i:index_i})
        if has_similar_cluster and not is_min_cluster and index_i not in similar_cluster_id:
            uniq_cluster_id.update({index_i:index_i})

    print cluster_file_dir + " " + combination + ": total similar cluster: " + str(len(similar_cluster_id))
    print cluster_file_dir + " " + combination + ": total unique cluster: " + str(len(uniq_cluster_id))
    return uniq_cluster_id

def print_unique_cluster(cluster_file_dir, unique_cluster_file_dir, combination, uniq_cluster_id):
    for gamma in [1, 4, 7, 11, 14, 17, 20]:
        cluster_folder = cluster_file_dir + "/" + combination + "_gamma_" + str(gamma)
        cluster_file = cluster_folder + "/" + combination + "_gamma_" + str(gamma) + ".louvain.tsv"
        unique_cluster_folder = unique_cluster_file_dir + "/" + combination + "_gamma_" + str(gamma)
        unique_cluster_file = unique_cluster_folder + "/" + combination + "_gamma_" + str(gamma) + ".louvain.unique.tsv"

        print "system is printing unique cluster: " + unique_cluster_file
        if not os.path.exists(os.path.dirname(unique_cluster_file)):
            os.makedirs(os.path.dirname(unique_cluster_file))

        filewriter = open(unique_cluster_file, "a")

        with open(cluster_file) as fp:
            lines = fp.readlines()

            for line in lines:
                if line.startswith("corr"):
                    filewriter.write(line)
                    continue

                fields = re.split(r'\t', line)
                ## gamma + group_id as the key of clusters
                key = str(gamma) + "-" + fields[1]
                if key in uniq_cluster_id:
                    filewriter.write(line)

        fp.closed
        filewriter.close()

## Main entry
if __name__ == "__main__":
    cluster_file_dir = sys.argv[1]
    unique_cluster_file_dir = sys.argv[2]
    combination = sys.argv[3]

    uniq_cluster_id = deduplicate_cluster(cluster_file_dir, combination)
    print_unique_cluster(cluster_file_dir, unique_cluster_file_dir, combination, uniq_cluster_id)

