import numpy

import ROOT
TMVA_tools = ROOT.TMVA.Tools.Instance()

# mode = 'NoVertex'
mode = 'PseudoVertex'
# mode = 'RecoVertex'

tree = ROOT.TChain('CombinedSVV2{mode}'.format(mode=mode))

files = []
files = [
    'data/skimmed_20k_eachptetabin_CombinedSVV2{mode}_B.root'.format(mode=mode),
    'data/skimmed_20k_eachptetabin_CombinedSVV2{mode}_C.root'.format(mode=mode),
    'data/skimmed_20k_eachptetabin_CombinedSVV2{mode}_DUSG.root'.format(mode=mode)
]

for f in files:
    print 'Opening file', f
    tree.Add(f)


# LR training variables
training_vars = [
    'trackSip3dSig[0]',
    'trackSip3dSig[1]',
    'trackSip3dSig[2]',
    'Alt$(trackSip3dSig[3], -10.)',
    'Alt$(trackSip3dSig[4], -10.)'
    ]

if mode in ['PseudoVertex', 'RecoVertex']:
    training_vars += [
    'trackEtaRel[0]',
    'trackEtaRel[1]',
    'vertexMass', 
    'vertexNTracks', 
    'vertexEnergyRatio', 
    'trackSip2dSigAboveCharm',
    'vertexJetDeltaR'
    ]

if mode == 'RecoVertex':
    training_vars += [
    'flightDistance2dSig'
    ]

# Additional NN training variables
training_vars += [
    'jetPt',
    'abs(jetEta)',
    'jetNTracks',
    ]

if mode == 'RecoVertex':
    training_vars += [
    'jetNSecondaryVertices'
    ]

# My random selection for testing
training_vars += [
    'log10(trackPtRel[0])',
    'log10(trackPtRel[1])',
    'log10(trackPtRel[2])',
    'log10(trackPPar[0])',
    'log10(trackPPar[1])',
    'log10(trackPPar[2])',
    'muonEnergyFraction',
    'muonMultiplicity',
    'electronEnergyFraction',
    'electronMultiplicity',
    ]
if mode == 'RecoVertex':
    training_vars += [
    'log10(flightDistance2dVal)', 
    'log10(flightDistance3dVal)',
    'log10(vertexFitProb)',
    ]


def train():
    signal_selection = 'flavour==4' # b
    background_selection = 'flavour!=4' # no b

    num_pass = tree.GetEntries(signal_selection)
    num_fail = tree.GetEntries(background_selection)

    print 'N events signal', num_pass
    print 'N events background', num_fail
    outFile = ROOT.TFile('TMVA_classification.root', 'RECREATE')

    factory    = ROOT.TMVA.Factory(
        "TMVAClassification", 
        outFile, 
        "!V:!Silent:Color:DrawProgressBar:Transformations=I" ) 

    for var in training_vars:
        factory.AddVariable(var, 'F') # add float variable

    # factory.SetWeightExpression('')

    factory.AddSignalTree(tree, 1.)
    factory.AddBackgroundTree(tree, 1.)

    # import pdb; pdb.set_trace()

    factory.PrepareTrainingAndTestTree( ROOT.TCut(signal_selection), ROOT.TCut(background_selection),
                                        "nTrain_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )


    factory.BookMethod(ROOT.TMVA.Types.kBDT, "BDTG","!H:!V:NTrees=500::BoostType=Grad:Shrinkage=0.05:UseBaggedBoost:GradBaggingFraction=0.9:nCuts=500:MaxDepth=5:MinNodeSize=0.1" )


    factory.BookMethod(ROOT.TMVA.Types.kBDT, "BDT_ADA", "!H:!V:NTrees=400:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=50:AdaBoostBeta=0.2:MaxDepth=5:MinNodeSize=0.1")

    factory.BookMethod( ROOT.TMVA.Types.kFisher, "Fisher", "H:!V:Fisher:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10" )


    factory.TrainAllMethods()

    # factory.OptimizeAllMethods()

    factory.TestAllMethods()

    factory.EvaluateAllMethods()

    outFile.Close()

    ROOT.gROOT.LoadMacro('$ROOTSYS/tmva/test/TMVAGui.C')
    ROOT.TMVAGui('TMVA_classification.root')
    raw_input("Press Enter to continue...")

def trainMultiClass():
    classes = [
        ('flavour==5', 'B'),
        ('flavour==4', 'C'),
        ('flavour!=5 && flavour!=4', 'UDSG')
    ]

    for cl in classes:
        print 'N events', cl[1], tree.GetEntries(cl[0])

    outFile = ROOT.TFile('TMVA_multiclass.root', 'RECREATE')

    factory    = ROOT.TMVA.Factory(
        "TMVAClassification", 
        outFile, 
        "!V:!Silent:Color:DrawProgressBar:Transformations=I:AnalysisType=Multiclass" ) 

    for var in training_vars:
        factory.AddVariable(var, 'F') # add float variable

    # factory.SetWeightExpression('')

    for cl in classes:
        factory.AddTree(tree, cl[1], 1., ROOT.TCut(cl[0]))
    # factory.AddSignalTree(tree, 1.)
    # factory.AddBackgroundTree(tree, 1.)

    # import pdb; pdb.set_trace()

    factory.PrepareTrainingAndTestTree( ROOT.TCut(''), ROOT.TCut(''),  "SplitMode=Random:NormMode=NumEvents:!V")

    factory.BookMethod(ROOT.TMVA.Types.kBDT, "BDTG","!H:!V:NTrees=500::BoostType=Grad:Shrinkage=0.05:UseBaggedBoost:GradBaggingFraction=0.9:nCuts=500:MaxDepth=4:MinNodeSize=0.1" )

    # factory.BookMethod(ROOT.TMVA.Types.kBDT, "BDT_ADA", "!H:!V:NTrees=400:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=50:AdaBoostBeta=0.2:MaxDepth=2:MinNodeSize=6")


    factory.TrainAllMethods()

    # factory.OptimizeAllMethods()

    factory.TestAllMethods()

    factory.EvaluateAllMethods()

    outFile.Close()

    ROOT.gROOT.LoadMacro('$ROOTSYS/tmva/test/TMVAMultiClassGui.C')
    ROOT.TMVAMultiClassGui('TMVA_multiclass.root')
    raw_input("Press Enter to continue...")

def read():
    import array

    reader = ROOT.TMVA.Reader('TMVAClassification_BDTG')

    varDict = {}
    for var in training_vars:
        varDict[var] = array.array('f',[0])
        reader.AddVariable(var, varDict[var])

    reader.BookMVA("BDTG","weights/TMVAClassification_BDTG.weights.xml")

    bdtOuts = []
    flavours = []

    for jentry in xrange(tree.GetEntries()):

        ientry = tree.LoadTree(jentry)
        nb = tree.GetEntry(jentry)

        for var in varDict:
            varDict[var][0] = getattr(tree, var)

        bdtOutput = reader.EvaluateMVA("BDTG")

        flavour = tree.flavour
        bdtOuts.append(bdtOutput)
        flavours.append(flavour)

        if jentry%1000 == 0:
            print jentry, varDict['f1'], bdtOutput, flavour

    writeSmallTree = False

    if writeSmallTree:

        BDTG = numpy.zeros(1, dtype=float)
        flav = numpy.zeros(1, dtype=float)

        fout = ROOT.TFile('trainPlusBDTG.root', 'RECREATE')
        treeout = ROOT.TTree()
        treeout.Branch('BDTG', BDTG, 'BDTG/D')
        treeout.Branch('flavour', flav, 'loss/D')


        for i, bdtOut in enumerate(bdtOuts):
            BDTG[0] = bdtOut
            flav[0] = flavours[i]
            if i%1000==0:
                print i, bdtOut, flavours[i]
            treeout.Fill()
        treeout.Write()
        fout.Write()
        fout.Close()


if __name__ == '__main__':
    train()
    # trainMultiClass()
    # read()

