var app = angular.module('myApp', ['services', 'angular-clipboard']);

app.controller('myCtrl', function ($scope, $http, $log, HttpServiceJsonp) {
    $scope.useDev = true;
    //$scope.serverHost = "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com";


    //$scope.serverHost = "http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com"; //Search Engine (Dev)
    //$scope.serverHost = "http://ec2-52-36-65-220.us-west-2.compute.amazonaws.com:8181"; //Thumbnail generator
    //$scope.serverHost = "http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:8181"; //Search Engine (Prod)
    //$scope.serverHost = "http://localhost:8182";
    $scope.serverHost = python_host_global;

    $scope.projectID = "559d6a91927ec80fd6ce7129"; //PROD project
    //$scope.projectID = "55917763f6f407181fa2ec23"; //localhost project


    $scope.searchbox = "OR2J3,AANAT,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,ST14,NXF1,H3F3B,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3";
    $scope.contentString = "";
    $scope.showTerms = true;
    $scope.showCopyToClipboard = false;
    $scope.ids = {
      es_id: ""
    };

    $scope.APILinks = [
        {"address": $scope.serverHost + "/search/clusters/SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2,RGS7BP,EDIL3,PDE3A,PCDHGA12,C10orf128,ELK3,PRKG1,LPAR4,PCDHGB7,RP1L1,HTR1B,PDZD2/99?callback=JSON_CALLBACK",
        "title": "SEARCH CLUSTERS (Parameters: SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2...)", "active": 1, "directLink": false, "parameter": "term list", "required": "required"},

        {"address": $scope.serverHost + "/search/phenotypes/SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2,RGS7BP,EDIL3,PDE3A,PCDHGA12,C10orf128,ELK3,PRKG1,LPAR4,PCDHGB7,RP1L1,HTR1B,PDZD2/99?callback=JSON_CALLBACK",
        "title": "SEARCH CONDITIONS (Parameters: SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2...)", "active": 1, "directLink": false, "parameter": "search page number", "required": "optional"}
    ];



    $scope.RESTLinks = [




    {"address": $scope.serverHost + "/search/clusters/SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2,RGS7BP,EDIL3,PDE3A,PCDHGA12,C10orf128,ELK3,PRKG1,LPAR4,PCDHGB7,RP1L1,HTR1B,PDZD2/99?callback=JSON_CALLBACK",
    "title": "SEARCH CLUSTERS (Parameters: SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2...)", "active": 1, "directLink": false},

    {"address": $scope.serverHost + "/search/phenotypes/SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2,RGS7BP,EDIL3,PDE3A,PCDHGA12,C10orf128,ELK3,PRKG1,LPAR4,PCDHGB7,RP1L1,HTR1B,PDZD2/99?callback=JSON_CALLBACK",
    "title": "SEARCH CONDITIONS (Parameters: SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2...)", "active": 1, "directLink": false},

    {"address": $scope.serverHost + "/search/authors/SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2,RGS7BP,EDIL3,PDE3A,PCDHGA12,C10orf128,ELK3,PRKG1,LPAR4,PCDHGB7,RP1L1,HTR1B,PDZD2/99?callback=JSON_CALLBACK",
    "title": "SEARCH AUTHORS (Parameters: SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2...)", "active": 1, "directLink": false},

    {"address": $scope.serverHost + "/search/drugs/SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2,RGS7BP,EDIL3,PDE3A,PCDHGA12,C10orf128,ELK3,PRKG1,LPAR4,PCDHGB7,RP1L1,HTR1B,PDZD2?callback=JSON_CALLBACK",
    "title": "SEARCH DRUGS (Parameters: SMAD9,SULT1C4,KIRREL,RUNX1T1,PCSK5,LDLRAD3,ADAMTS15,CACNA2D1,CYSLTR2...)", "active": 1, "directLink": false},

    {"address": $scope.serverHost + "/search/inferred/drugs/IRGQ,EDF1,AIPL1/2040020397?callback=JSON_CALLBACK",
    "title": "SEARCH INFERRED DRUGS (Parameters: NIPAL2,STT3B,AQP10,CYP2R1 ~ 2020004787)", "active": 1, "directLink": false},







      {"address": "http://localhost:3000/getRenderedNodes/AVMGDv8uRXVvO0gLolCm?callback=JSON_CALLBACK",
      "title": "RENDERED GRAPH", "active": 1, "directLink": false},

      {"address": $scope.serverHost + "/api/getInferredDrugs/2010020613,2010004933,2010016852,2010016826,2010027950,2010020503,2010017522,2010017652,2010017527,2010020273,2010020100,2010025212?callback=JSON_CALLBACK",
      "title": "INFERRED DRUGS SEARCH (Parameters: 2010018824,2010011335,etc...)", "active": 1, "directLink": false},

      {"address": $scope.serverHost + "/api/gettabcounts/TEAD3,MYO1D,WEE1,DLL4,STIM2,CAPZA1,STK39,CNOT7,ENAH,CDH11,USP46,MTMR4,FOSB,EHF,PNLIP,EIF2S2,TRAPPC8,PITPNM2,GLTP,CLK1,PLAC8L1,CCDC158,MACC1,KRT80,AANAT,OR2J3,GPIHBP1?callback=JSON_CALLBACK",
      "title": "TAB COUNTS Search (Parameters: SMAD9,SULT1C4,KIRREL,RUNX1T1,...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/star/search/map/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "GENE TAB Search (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/star/search/map/GATA1?callback=JSON_CALLBACK",
        "title": "GENE TAB Search (Parameters: GATA1)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/star/search/map/hsa-mir-34a?callback=JSON_CALLBACK",
        "title": "MiRNA GENE TAB Search (Parameters: hsa-mir-34a,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/paged/conditions/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3/1?callback=JSON_CALLBACK",
        "title": "CONDITIONS TAB Search Simple", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/simple/conditions/search/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3/99?callback=JSON_CALLBACK",
        "title": "CONDITIONS TAB BASIC Search Simple", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/people/peoplecenter2/search/GATA1?callback=JSON_CALLBACK",
        "title": "AUTHOR TAB Search 2 (Parameters: GATA1)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/getauthor/paged/GATA1/2?callback=JSON_CALLBACK",
        "title": "AUTHOR TAB Search Paged (Parameters: GATA1)", "active": 1, "directLink": false},




        {"address": $scope.serverHost + "/nav/elasticsearch/drug_network/search/map/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3/2020014671,2020004787,2010025212,2010007504,2010020100,2010020273,2010017527,2010017652?callback=JSON_CALLBACK",
        "title": "DRUG TAB Search W/ inferred drugs (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/drug_network/search/map/SMIM12,JAM3,FAN1,KHDC3L,CFAP45,RTFDC1,AARD,WSCD1,PPIB,GNPTAB,AATK,SYNGAP1,FOXH1,CDYL2,PARD3B,SNED1,TPO,HS2ST1,KRTAP25-1,ADARB2,ZNF777,DCLK2,SEMA3G,PTPRS,DNAJB6,PDZK1,NEU1,CHRNA4,TSHZ3,CADPS2,COX7A2,HIST1H2AJ,WNT4,COTL1,PTPRE,DSCAML1,SPTBN5,SPTBN4,ENPP5,TAGAP,FASTKD2,SRRM3,ZNF468,FIGN,NRXN1,HOXB7,GNG13,NUDCD3,EPHB1,RPTOR/2020003808,2020025295?callback=JSON_CALLBACK",
        "title": "DRUG TAB Search W/ inferred drugs (Parameters: Sort order WRONG,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/experiment1/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3/2020023012,2050002211,2050002123,2050014574,2020004269,2050000752,2050014430,2020009336,2020025173,2020026243?callback=JSON_CALLBACK",
        "title": "DRUG TAB Search W/ inferred drugs (EXPERIMENT 1)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/drug_network/search/map/SLC9B1,BTNL9,RHOF,ZNF322A,DCAF4L1,RBL2,BMP4,OR14J1,BOP1,PAPPA2,MGAT1,TCEA1,ADAM12,C1QL4,PRELID2,RABEPK,SLC25A18,CD82,EIF5A2,NAP1L1,HTR1E,NFIX,SDC2,PROSER2,ELMSAN1,ZNF512B,KRT80,MRPS24,C11ORF53,SNPH,SMARCA4,RGL2,MYH10,CBFA2T3,FAM178A,FIZ1,SLCO5A1,FNBP1,ZNF354C,DLGAP3,TMEM95,ELF5,PORCN,GPR12,ANKRD22,SEPHS1,C6ORF10,NEIL2,PIGB,NLGN3,JPH2,ACTR8,PTCHD2,ENG,TBC1D4,RNASEH1,BICC1,SREBF1,ZBED5,FAM163A,CACNA1I,SLC38A10,KIAA0319,MICALL2,PNMT,SH3PXD2A,PERP,TMEM125,PARP1,H3F3B,UBLCP1,EBF3,AGO1,SNCA,SORBS2,LVRN,MRPL55,MAD1L1,ARHGAP19,LHX8,COL4A2,MTNR1A,FZR1,BANP,SLC41A3,PPP2R1B,LILRB3,MAGIX,PDZD2,IGSF9B,E4F1,RDX,VWA5A,RAP1GAP2,PGRMC1,ANO6,ZNF665,KATNB1,C9ORF69,P2RX4,MAPK11,C1QTNF8,UBE2E2,PRX,ROR2,KCNK1,MAGI3,KIAA0182,SERPINI2,ZIC4,PLEKHH2,EGFL8,MIDN,TSHR,GBA2,DKC1,NR0B1,CNNM4,NFASC,FAT1,PRRC2A,CHMP1A,EMB,FAM126A,FOXJ3,PCBP3,NRBF2,SYNJ2,VAX1,LZTR1,CHST2,MAPRE1,OBSCN,CALHM3,RAPGEF3,WDR20,BTN1A1,VCPIP1,DIP2C,TSNARE1,PSMC1,POP7,ZNF155,CIITA,SLC38A9,DLG2,BARHL2,ABT1,WNT5A,SHANK2,FYN,NSF,CFB,C2,SLC16A9,SUPV3L1,FRG2C,FBP2,URB2,TRIM26,MAGI1,ANKRD30A,ACTG1,EFCAB2,PKP4,CHRM1,RNF220,LRCH2,TNXB,PPP1R26,RNF150,PLEKHG4B,TUT1,ARHGDIG,PPIH,ACCN1,IL10RA,GSG1,RAB17,KCTD2,RNPEPL1,STEAP1,CDKN2AIP,SLC22A2,CRHR2,B3GNT4,HOXC9,WDR45,ANKRD11,KDM4B,PAX2,JPH3,TNNT3,HOXA10,HS3ST4,KIAA0232,KCNK12,SORBS1,ZNRF3,KCNE1,HCG27,DVL3,HMCN1,CNN2,BCAS4,FAM117A,SYT3,AIM1,RIMBP2,OPCML,HOXC13,SULF1,ST6GALNAC6,ASF1A,KIF21A,FAM84B,RXFP1,TAP2,NDNF,MSH5-SAPCD1,ZBTB49,CCSER2,SMCO2,SCAPER,C1GALT1C1,RERE,AKR1B1,CALCA,HMGA2,LMAN2L,APBB1IP,TRAPPC6B,TXNDC2,TMEM14A,HSPB6,SNRPE,CTDP1,IFI27L2,PACS2,ELL3,SPATA22,CYP26C1,PRDM16,SOS1,DOCK9,MPPED1,TFAP2A,CLIC5,FAM82A1,LYAR,NOL11,IDE,HEYL,NKAIN3,CNST,FBRS,EXOC7,ZNF507,SEC23B,PSMB8,ITGB2,WNT3,PACSIN3,PPP1R3C,DTNB,FLT1/2020064979,2020066557,2020064929?callback=JSON_CALLBACK",
        "title": "DRUG TAB Search W/ inferred drugs (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        //{"address": $scope.serverHost + "/api/heatProp/getInferredDrugs/CDH11,DLL4,FOSB,GPIHBP1/2020004787?callback=JSON_CALLBACK",
        {"address": $scope.serverHost + "/api/heatProp/getInferredDrugs/COL1A1,DCLK1,IL33/2040012865?callback=JSON_CALLBACK",
        "title": "INFERRED DRUGS BY HEATPROP **** Search W/ inferred drugs (Parameters: CDH11,DLL4,FOSB,GPIHBP1  ~ 2020004787)", "active": 1, "directLink": false},







        {"address": $scope.serverHost + "/nav/terms/lookup/CHR1:G.43869315C>G,CHR9:G.74860114G>T,hsa-mir-34a,hsa-mir-34b,hsa-mir-34c,ras,homo,sapiens,rattus,OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,human,ENSG00000198804,aslfdkjds?callback=JSON_CALLBACK",
        "title": "Python-based term identifier (Parameter: hsa-mir-34a,homo,sapien,rattus,OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,human,ENSG00000198804,aslfdkjds)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/term/lookup/GATA1?callback=JSON_CALLBACK",
        "title": "Python-based term identifier (Parameter: GATA1)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/getImage?callback=JSON_CALLBACK",
        "title": "GET IMAGE", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/fileByIdRaw/node/2050002123?callback=JSON_CALLBACK",
        "title": "Get document by ID (Parameter: 2050002123)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/go/genes/GO:0001944?callback=JSON_CALLBACK",
        "title": "Get genes by GO ID (Parameter: GO:0001944)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/tribe/lookup/6279,1363,5777777777777,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "TEST Tribe", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/elasticsearch/getclusterenrichmentbyid/AVKLAMW0Zi0bM3KTWa2X?callback=JSON_CALLBACK",
        "title": "Cluster Enrichment By ES ID (Parameters: AVKLAMW0Zi0bM3KTWa2X)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/dbsnp/search/map/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "DBSnp Search (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/getheatmap3/2020000463?callback=JSON_CALLBACK", //AVJhHCI9Ao6zDNWFcVcV
        "title": "GET Heatmap", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/getheatmap/filtered/2020000463/CNNM3,PRPF19,UBOX5,MRPS10,CYP2R1,SMCR8,UBOX5,MRPS10,CYP2R1,SMCR8,SCARNA23/200?callback=JSON_CALLBACK", //AVJhHCI9Ao6zDNWFcVcV
        "title": "GET Filtered Heatmap", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/getheatmapmatrix/filtered/2020000463/CNNM3,PRPF19,UBOX5,MRPS10,CYP2R1,SMCR8,UBOX5,MRPS10,CYP2R1,SMCR8,SCARNA23/200?callback=JSON_CALLBACK", //AVJhHCI9Ao6zDNWFcVcV
        "title": "GET Filtered Heatmap NEW", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/getheatmapmatrix/unfiltered/2020000463?callback=JSON_CALLBACK", //AVJhHCI9Ao6zDNWFcVcV
        "title": "GET Un-filtered Heatmap NEW", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/getheatmapmatrix/filtered/2050006141/CLK1,DLL4/200?callback=JSON_CALLBACK", //AVJhHCI9Ao6zDNWFcVcV
        "title": "GET Filtered Heatmap asymmetric", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/ds/getheatmapgraph/2020000463/AGL,ESPN,SMCR8/200?callback=JSON_CALLBACK",
        "title": "GET Network Graph", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/getheatmap/2010017751?callback=JSON_CALLBACK",
        "title": "Get Heat Map - OLD", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/getheatmap2/AVMFn1mZRXVvO0gLmUF7?callback=JSON_CALLBACK",
        "title": "Get Heat Map Plotly - OLD", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/ds/getrawcluster/2020000463/AGL,ESPN?callback=JSON_CALLBACK",
        "title": "GET Raw Cluster - OLD", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/getclinvar/AVEmratFO3XiWf9OXyWg?callback=JSON_CALLBACK",
        "title": "Get Clinvar By ES Id", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/conditions/genevariants/GATA3/ER-PR-positive carcinoma/breast?callback=JSON_CALLBACK",
        "title": "******* Get Gene info By variant collection", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/people/genecenter/lazysearch/OR2J3,AANAT,KRT80,MACC1,LOC139201?callback=JSON_CALLBACK",
        "title": "People GENE CENTERED Lazy Search (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/people/genecenter/lazysearch/hydrate/OR2J3?callback=JSON_CALLBACK",
        "title": "People GENE CENTERED Lazy Search HYDRATE (Parameters: OR2J3)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/people/genecenter/search/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "People GENE CENTERED Search (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/people/peoplecenter/search/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "People AUTHOR CENTERED Search (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/elasticsearch/getauthorcenteredbyid/AVGulTLQi9N1w84UpY-B/CGNL1,SLC1A1?callback=JSON_CALLBACK",
        "title": "People AUTHOR CENTERED Search by ID (Parameters: AVFfUtr3jNt6bOv-svw_ and FLT3,LDB1)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/people/gene/targeted/Chaum, Edward/FOSB,EGR1,JUNB?callback=JSON_CALLBACK",
        "title": "People AUTHOR GENE TARGETED Search (Parameters: Chaum, Edward - FOSB)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/coexpression_network/search/map/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "Co-expression network Search (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/coexpression_network/search/map/OR2J3,AANAT,KRT80/HUMAN?callback=JSON_CALLBACK",
        "title": "Co-expression network Search with Genome (Parameters: OR2J3,AANAT,KRT80,HUMAN,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/star/search/neighborhood/map/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "Star Search by NEIGHBORHOOD (Parameters: OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/elasticsearch/single/star/search/map/OR2J3?callback=JSON_CALLBACK",
        "title": "Star Search return whole document (Parameter: OR2J3) **NOT WORKING IN PROD", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/restbroker/entrez/CLK1?callback=JSON_CALLBACK",
        "title": "Entrez info (Parameter: CLK1)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/pubmed/genecounts/OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,PITPNM2,TRAPPC8,EIF2S2?callback=JSON_CALLBACK",
        "title": "PubMed gene counts (Parameters: OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,PITPNM2,TRAPPC8,EIF2S2)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/pubmed/genecounts/normalized/OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,PITPNM2,TRAPPC8,EIF2S2?callback=JSON_CALLBACK",
        "title": "PubMed gene counts NORMALIZED (Parameters: OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,PITPNM2,TRAPPC8,EIF2S2)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/go/enrich/CCDC158,PLAC8L1,CLK1?callback=JSON_CALLBACK",
        "title": "Gene Enrichment (Parameters: CCDC158,PLAC8L1,CLK1)", "active": 1, "directLink": false},


        {"address": $scope.serverHost + "/nav/elasticsearch/go/enrich/AU_n5pMynhwhjTnOrD7w?callback=JSON_CALLBACK",
        "title": "Gene Enrichment from ElasticSearch document (Parameter: AU_n3aS0nhwhjTnOrCfU)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/mirbase/ext/hsa-mir-27b?callback=JSON_CALLBACK",
        "title": "Mirbase search (Parameter: hsa-mir-27b)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/interpro/info/IPR000001?callback=JSON_CALLBACK",
        "title": "InterPro (Parameter: IPR000001) **NOT WORKING IN PROD", "active": 1, "directLink": false},

        {"address": "http://ec2-52-26-19-122.us-west-2.compute.amazonaws.com:8080/NLP/Classifier/get-direct-term-resolution/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,CLK1,Cholera,GLTP,Aspirin,PITPNM2,TRAPPC8,EIF2S2,adverse,ST14,NXF1,H3F3B,FOSB,MTMR4,USP46,CDH11,ENAH,transplanted,CNOT7,STK39,CAPZA1,STIM2,nasal,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        //{"address": "http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:8080/NLP/Classifier/get-direct-term-resolution/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,CLK1,Cholera,GLTP,Aspirin,PITPNM2,TRAPPC8,EIF2S2,adverse,ST14,NXF1,H3F3B,FOSB,MTMR4,USP46,CDH11,ENAH,transplanted,CNOT7,STK39,CAPZA1,STIM2,nasal,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "Term identifier (Parameters: OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,etc...)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/terms/lookup/CHR1:G.43869315C>G,CHR9:G.74860114G>T,hsa-mir-34a,hsa-mir-34b,hsa-mir-34c,ras,homo,sapiens,rattus,OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,human,ENSG00000198804,aslfdkjds?callback=JSON_CALLBACK",
        "title": "Python-based term identifier (Parameter: hsa-mir-34a,homo,sapien,rattus,OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,human,ENSG00000198804,aslfdkjds)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/terms/autocomplete/bla?callback=JSON_CALLBACK",
        "title": "Auto complete term identifier (Parameter: homo,sapien,rattus,OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,human,ENSG00000198804,aslfdkjds)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/nav/getgeneinfo/OR2J3?callback=JSON_CALLBACK",
        "title": "Information about a specific gene (Parameter: OR2J3)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/nav/networks?callback=JSON_CALLBACK",
        "title": "NAV - networks", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/nav/project/" + $scope.projectID + "?callback=JSON_CALLBACK",
        "title": "NAV - projects (Parameter: " + $scope.projectID + ")", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/nav/project/" + $scope.projectID + "/files?callback=JSON_CALLBACK",
        "title": "NAV - project files (Parameter: " + $scope.projectID + ")", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/nav/project/" + $scope.projectID + "/jobs?callback=JSON_CALLBACK",
        "title": "NAV - project jobs (Parameter: " + $scope.projectID + ")", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/nav/gene/ENSG00000012048?callback=JSON_CALLBACK",
        "title": "NAV - gene id resolution (Parameter: BRCA1)", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/ds/getbpnet/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "Author Gene Bipartite graph", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/saved/search/56732f6ff6f40715d6cc42f2?callback=JSON_CALLBACK",
        "title": "GET Saved Search", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/gettabcounts/OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3?callback=JSON_CALLBACK",
        "title": "GET Tab Counts", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/get/search/stats?callback=JSON_CALLBACK",
        "title": "GET Search Stats", "active": 1, "directLink": false},

        {"address": $scope.serverHost + "/api/gene/summary/FOSB?callback=JSON_CALLBACK",
        "title": "GET GENE Summary", "active": 1, "directLink": false},





        {"address": "http://ec2-52-41-84-103.us-west-2.compute.amazonaws.com:9200/_plugin/head",
        "title": "ElasticSearch Head Plugin (52-27-59-174 - PROD)", "active": 1, "directLink": true},

        {"address": "http://ec2-52-32-210-84.us-west-2.compute.amazonaws.com:9200/_plugin/head",
        "title": "ElasticSearch Head Plugin (52-32-210-84 - DEV REST and WEB)", "active": 1, "directLink": true},

        {"address": "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com",
        "title": "Nav server (Human 52-26-26-232)", "active": 1, "directLink": true},

        {"address": "http://ec2-52-32-210-84.us-west-2.compute.amazonaws.com:3000",
        "title": "Dev.Geneli.st (52-32-210-84)", "active": 1, "directLink": true}
       ];

    $scope.showSearchControls = function () {
        $scope.showTerms = $scope.showTerms === false ? true : false;
    };

    $scope.directLinkFilter = function (item) {
        return item.directLink;
    };

    $scope.relativeLinkFilter = function (item) {
        return !item.directLink;
    };

    $scope.content = {};

    $scope.testD3 = function() {
        var data = [4, 8, 15, 16, 23, 42];
//        var body = d3.select("body");
//        body.style("color", "black");
//        body.style("background-color", "yellow");

        d3.select(".chart")
          .selectAll("div")
            .data(data)
          .enter().append("div")
            .style("width", function(d) { return d * 10 + "px"; })
            .text(function(d) { return d; });
        };

    $scope.getRESTContent = function(myURL) {
        var url = "http://localhost:8182/nav/restbroker/entrez/CLK1?callback=JSON_CALLBACK";
        //alert(myURL);
        $scope.items = [];
        $scope.content = "";
        $scope.contentString = "";
        //alert(myURL);
        var myrequest = HttpServiceJsonp.jsonp(myURL)
            .success(function (result) {
                $scope.content = result;
                $scope.contentString = JSON.stringify(result);

                $scope.showTerms = false;
                $scope.showCopyToClipboard = true;
            }).finally(function () {

            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });

    };

    $scope.textToCopy = "I can copy by clicking!\nAnd also new lines!";

});
