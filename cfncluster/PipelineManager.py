__author__ = 'Guorong Xu<g1xu@ucsd.edu>'

import ConnectionManager

workspace = "/shared/workspace/SearchEngineProject/codes"

## run all analysis.
def run_analysis(ssh_client, disease_name, operation, s3_input_files_address, s3_output_files_address):

    print "executing pipeline..."
    ConnectionManager.execute_command(ssh_client, "sh " + workspace + "/run.sh " + disease_name + " " 
    	+ operation + " " + s3_input_files_address + " " + s3_output_files_address)

## checking disease names
def check_disease_name():
	print "AcuteMyeloidLeukemia"
	print "AdrenocorticalCancer"
	print "BladderCancer"
	print "BrainCancer"
	print "BreastCancer"
	print "CervicalCancer"
	print "CholangiocarcinomaLiver"
	print "ColonAdenocarcinoma"
	print "DiffuseLargeBCellLymphoma"
	print "EndometrialCancer"
	print "EsophagealCancer"
	print "GliomaGlioblastoma"
	print "HeadAndNeckSquamousCarcinoma"
	print "Inflammation"
	print "KidneyCancer"
	print "LiverCancer"
	print "LungCancer"
	print "OvarianCancer"
	print "PancreaticCancer"
	print "ProstateAdenocarcinoma"
	print "RectalCancer"
	print "Sarcoma"
	print "SkinMelanoma"
	print "StomachCancer"
	print "ThyroidCancer"
	print "UvealMelanoma"
    
## checking your jobs status
def check_processing_status(ssh_client):
    print "checking processing status"
    ConnectionManager.execute_command(ssh_client, "cat " + workspace + "/nohup.out")

## checking your jobs status
def check_jobs_status(ssh_client):
    print "checking jobs status"
    ConnectionManager.execute_command(ssh_client, "qstat")

## checking your host status
def check_host_status(ssh_client):
    print "checking qhost status"
    ConnectionManager.execute_command(ssh_client, "qhost")


