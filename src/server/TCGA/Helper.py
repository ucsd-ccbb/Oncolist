__author__ = 'guorongxu'

import logging

def get_abbreviation_tumor_name(short_name):
    if short_name == "LAML":
        return "Leukemia"
    elif short_name == "ACC":
        return "Adrenal"
    elif short_name == "BLCA":
        return "Bladder"
    elif short_name == "LGG":
        return "Brain"
    elif short_name == "BRCA":
        return "Breast"
    elif short_name == "CESC":
        return "Cervical"
    elif short_name == "CHOL":
        return "Bile"
    elif short_name == "COAD":
        return "Colon"
    elif short_name == "ESCA":
        return "Esophagus"
    elif short_name == "FPPP":
        return "FFPE Pilot Phase II"
    elif short_name == "GBM":
        return "Brain"
    elif short_name == "HNSC":
        return "HeadAndNeck"
    elif short_name == "KIPAN":
        return "Kidney"
    elif short_name == "KICH":
        return "Kidney"
    elif short_name == "KIRC":
        return "Kidney"
    elif short_name == "KIRP":
        return "Kidney"
    elif short_name == "LIHC":
        return "Liver"
    elif short_name == "LUAD":
        return "Lung Adenocarcinoma"
    elif short_name == "LUSC":
        return "Lung"
    elif short_name == "DLBC":
        return "Lymphoma"
    elif short_name == "MESO":
        return "Ovarian"
    elif short_name == "OV":
        return "Ovarian"
    elif short_name == "PAAD":
        return "Pancreatic"
    elif short_name == "PCPG":
        return "Adrenal"
    elif short_name == "PRAD":
        return "Prostate"
    elif short_name == "READ":
        return "Rectal"
    elif short_name == "SARC":
        return "Sarcoma"
    elif short_name == "SKCM":
        return "Skin"
    elif short_name == "STAD":
        return "Stomach"
    elif short_name == "STES":
        return "Stomach"
    elif short_name == "TGCT":
        return "Testicular"
    elif short_name == "THYM":
        return "Thymus"
    elif short_name == "THCA":
        return "Thyroida"
    elif short_name == "UCS":
        return "Uterine"
    elif short_name == "UCEC":
        return "Uterine"
    elif short_name == "UVM":
        return "Uveal"
    elif short_name == "COADREAD":
        return "Colon"
    elif short_name == "GBMLGG":
        return "Brain"
    else:
        logging.error("No Matching full name: " + short_name)

def get_full_tumor_name(short_name):
    if short_name == "LAML":
        return "Acute Myeloid Leukemia"
    elif short_name == "ACC":
        return "Adrenocortical Carcinoma"
    elif short_name == "BLCA":
        return "Bladder Urothelial Carcinoma"
    elif short_name == "LGG":
        return "Brain Lower Grade Glioma"
    elif short_name == "BRCA":
        return "Breast Invasive Carcinoma"
    elif short_name == "CESC":
        return "Cervical Squamous Cell Carcinoma and Endocervical Adenocarcinoma"
    elif short_name == "CHOL":
        return "Cholangiocarcinoma"
    elif short_name == "COAD":
        return "Colon Adenocarcinoma"
    elif short_name == "ESCA":
        return "Esophageal Carcinoma"
    elif short_name == "FPPP":
        return "FFPE Pilot Phase II"
    elif short_name == "GBM":
        return "Glioblastoma Multiforme"
    elif short_name == "HNSC":
        return "Head and Neck Squamous Cell Carcinoma"
    elif short_name == "KIPAN":
        return "Kidney Chromophobe and Kidney Renal Clear Cell Carcinoma and Kidney Renal Papillary Cell Carcinoma"
    elif short_name == "KICH":
        return "Kidney Chromophobe"
    elif short_name == "KIRC":
        return "Kidney Renal Clear Cell Carcinoma"
    elif short_name == "KIRP":
        return "Kidney Renal Papillary Cell Carcinoma"
    elif short_name == "LIHC":
        return "Liver Hepatocellular Carcinoma"
    elif short_name == "LUAD":
        return "Lung Adenocarcinoma"
    elif short_name == "LUSC":
        return "Lung Squamous Cell Carcinoma"
    elif short_name == "DLBC":
        return "Lymphoid Neoplasm Diffuse Large B-cell Lymphoma"
    elif short_name == "MESO":
        return "Mesothelioma"
    elif short_name == "OV":
        return "Ovarian Serous Cystadenocarcinoma"
    elif short_name == "PAAD":
        return "Pancreatic Adenocarcinoma"
    elif short_name == "PCPG":
        return "Pheochromocytoma and Paraganglioma"
    elif short_name == "PRAD":
        return "Prostate Adenocarcinoma"
    elif short_name == "READ":
        return "Rectum Adenocarcinoma"
    elif short_name == "SARC":
        return "Sarcoma"
    elif short_name == "SKCM":
        return "Skin Cutaneous Melanoma"
    elif short_name == "STAD":
        return "Stomach Adenocarcinoma"
    elif short_name == "STES":
        return "Stomach and Esophageal Carcinoma"
    elif short_name == "TGCT":
        return "Testicular Germ Cell Tumors"
    elif short_name == "THYM":
        return "Thymoma"
    elif short_name == "THCA":
        return "Thyroid Carcinoma"
    elif short_name == "UCS":
        return "Uterine Carcinosarcoma"
    elif short_name == "UCEC":
        return "Uterine Corpus Endometrial Carcinoma"
    elif short_name == "UVM":
        return "Uveal Melanoma"
    elif short_name == "COADREAD":
        return "Colon Adenocarcinoma and Rectum adenocarcinoma"
    elif short_name == "GBMLGG":
        return "Glioblastoma Multiforme and Brain Lower Grade Glioma"
    else:
        logging.error("No Matching full name: " + short_name)

