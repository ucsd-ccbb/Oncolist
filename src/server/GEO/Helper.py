__author__ = 'guorongxu'

import logging

def get_abbreviation_tumor_name(short_name):
    if short_name == "AcuteMyeloidLeukemia":
        return "Leukemia"
    elif short_name == "AdrenocorticalCancer":
        return "Adrenal"
    elif short_name == "BladderCancer":
        return "Bladder"
    elif short_name == "BrainCancer":
        return "Brain"
    elif short_name == "BreastCancer":
        return "Breast"
    elif short_name == "CervicalCancer":
        return "Cervical"
    elif short_name == "CholangiocarcinomaLiver":
        return "Bile"
    elif short_name == "ColonAdenocarcinoma":
        return "Colon"
    elif short_name == "DiffuseLargeBCellLymphoma":
        return "Lymphoma"
    elif short_name == "EndometrialCancer":
        return "Endometrial"
    elif short_name == "EsophagealCancer":
        return "Esophagus"
    elif short_name == "GliomaGlioblastoma":
        return "Brain"
    elif short_name == "HeadAndNeckSquamousCarcinoma":
        return "HeadAndNeck"
    elif short_name == "Inflammation":
        return "Colon"
    elif short_name == "InflammationBlood":
        return "Lung"
    elif short_name == "KidneyCancer":
        return "Kidney"
    elif short_name == "KidneyClearCellCarcinoma":
        return "Kidney"
    elif short_name == "LiverCancer":
        return "Liver"
    elif short_name == "LiverHepatocellularCarcinoma":
        return "Liver"
    elif short_name == "LungCancer":
        return "Lung"
    elif short_name == "OvarianCancer":
        return "Ovarian"
    elif short_name == "PancreaticAdenocarcinoma":
        return "Pancreatic"
    elif short_name == "PancreaticCancer":
        return "Pancreatic"
    elif short_name == "ProstateAdenocarcinoma":
        return "Prostate"
    elif short_name == "RectalCancer":
        return "Rectal"
    elif short_name == "Sarcoma":
        return "Sarcoma"
    elif short_name == "SkinMelanoma":
        return "Skin"
    elif short_name == "StomachCancer":
        return "Stomach"
    elif short_name == "ThyroidCancer":
        return "Thyroid"
    elif short_name == "UvealMelanoma":
        return "Uveal"
    else:
        logging.error("No Matching short name: " + short_name)

def get_full_tumor_name(short_name):
    if short_name == "AcuteMyeloidLeukemia":
        return "Acute Myeloid Leukemia"
    elif short_name == "AdrenocorticalCancer":
        return "Adrenocortical Cancer"
    elif short_name == "BladderCancer":
        return "Bladder Cancer"
    elif short_name == "BrainCancer":
        return "Glioma High Grade"
    elif short_name == "BreastCancer":
        return "Breast Tumors RNA"
    elif short_name == "CervicalCancer":
        return "Cervical Cancer ChemoradioResistant"
    elif short_name == "CholangiocarcinomaLiver":
        return "Cholangiocarcinoma"
    elif short_name == "ColonAdenocarcinoma":
        return "Colon Cancer"
    elif short_name == "DiffuseLargeBCellLymphoma":
        return "Diffuse Large B-Cell Lymphoma"
    elif short_name == "EndometrialCancer":
        return "Endometrial Cancer Stage I"
    elif short_name == "EsophagealCancer":
        return "Esophageal Cancer"
    elif short_name == "GliomaGlioblastoma":
        return "Glioblastoma"
    elif short_name == "HeadAndNeckSquamousCarcinoma":
        return "Head and Neck"
    elif short_name == "Inflammation":
        return "Ulcerative Colitis Colon Inflammation"
    elif short_name == "InflammationBlood":
        return "Blood Lung Cancer"
    elif short_name == "KidneyCancer":
        return "Renal Cell Carcinoma"
    elif short_name == "KidneyClearCellCarcinoma":
        return "Kidney Renal Clear Cell Carcinoma"
    elif short_name == "LiverCancer":
        return "Hepatocellular Carcinoma"
    elif short_name == "LiverHepatocellularCarcinoma":
        return "Liver Hepatocellular Carcinoma Early Stage Cirrhosis"
    elif short_name == "LungCancer":
        return "Blood Lung Cancer Stage I"
    elif short_name == "OvarianCancer":
        return "Ovarian Cancer"
    elif short_name == "PancreaticAdenocarcinoma":
        return "Pancreatic Ductal Adenocarcinoma"
    elif short_name == "PancreaticCancer":
        return "Pancreatic"
    elif short_name == "ProstateAdenocarcinoma":
        return "Prostate Carcinoma"
    elif short_name == "RectalCancer":
        return "Rectal Cancer"
    elif short_name == "Sarcoma":
        return "Sarcoma"
    elif short_name == "SkinMelanoma":
        return "Melanoma Malignant"
    elif short_name == "StomachCancer":
        return "Stomach Cancer 126"
    elif short_name == "ThyroidCancer":
        return "Thyroid Cancer"
    elif short_name == "UvealMelanoma":
        return "Uveal Melanoma"
    else:
        logging.error("No Matching full name: " + short_name)
