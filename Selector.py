# -*- coding: utf-8 -*-
import os
import warnings as wr
import ROOT as r
import copy

class Selector:
    ''' Class to do an event selection'''
    ### =============================================
    ### Constructor
    def __init__(self, filename = '', selection = []):
        ''' Initialize a new Selector by giving the name of a sample.root file '''
        self.name = filename
        self.filename = self.name
        self.seleccion = selection
        if self.filename[-5:] != '.root': self.filename += '.root'
        if not os.path.exists(self.filename): self.filename = 'files/' + self.filename
        if not os.path.exists(self.filename):
            if (self.name != ''): wr.warn("[Selector::constructor] WARNING: file {f} not found".format(f = self.name))
        else:
            self.CreateHistograms()
            self.Loop()
        return

    ### =============================================
    ### Attributes
    # General
    histograms = []
    name = ""
    name = ""
    filename = ""
    seleccion = []

    # Histogram variables
    muon1_pt = -99
    invmass = -99
    weight = -99

    ### =============================================
    ### Methods
    def CreateHistograms(self):
        ''' CREATE YOUR HISTOGRAMS HERE '''
        self.histograms = []
        self.histograms.append(r.TH1F(self.name + '_MuonPt',     ';p_{T}^{#mu} (GeV);Events', 20, 0, 200))
        self.histograms.append(r.TH1F(self.name + '_MuonPt_notrigg', ';p_{T}^{#mu} (GeV);Events', 20, 0, 200))
        self.histograms.append(r.TH1F(self.name + '_MuonPt_forEff',     ';p_{T}^{#mu} (GeV);Events', 25, 15, 40))
        self.histograms.append(r.TH1F(self.name + '_MuonPt_notrigg_forEff', ';p_{T}^{#mu} (GeV);Events', 25, 15, 40))
        #self.histograms.append(r.TH1F(self.name + '_DiMuonMass', ';m^{#mu#mu} (GeV);Events',  20, 0, 200))
        self.histograms.append(r.TH1F(self.name + '_NJet', 'NJets',10,0,10))
        #-----Histogramas para varias variables----
        self.histograms.append(r.TH1F(self.name + '_MET', 'MET',30,0,200))
        self.histograms.append(r.TH1F(self.name + '_MuonPt_gen',';p_{T}^{#mu} (GeV);Events', 20, 0, 200))
        self.histograms.append(r.TH1F(self.name + '_EventWeight_gen','EventWeight',1,0,1))
        self.histograms.append(r.TH1F(self.name + '_EventWeight_gen_tot','EventWeight',1,0,1))
        self.histograms.append(r.TH1F(self.name + '_NBJets','NBjets',4,0,4))
        self.histograms.append(r.TH1F(self.name + '_EventWeight','EventWeight',1,0,1))
        self.histograms.append(r.TH1F(self.name + '_NJets_NBJets','NJets_NBJets',8,0,8))
        return


    def GetHisto(self, name):
        ''' Use this method to access to any stored histogram '''
        for h in self.histograms:
            n = h.GetName()
            if self.name + '_' + name == n: return h
        wr.warn("[Selector::GetHisto] WARNING: histogram {h} not found.".format(h = name))
        return r.TH1F()


    def FillHistograms(self):
        self.GetHisto('MuonPt_notrigg').Fill(self.muon1_pt_notrigg, self.weight)
        self.GetHisto('MuonPt_notrigg_forEff').Fill(self.muon1_pt_notrigg, self.weight)
        
        if self.trigger == 1:
            self.GetHisto('NJet').Fill(self.NJet, self.weight)
            self.GetHisto('MET').Fill(self.MET, self.weight)
            self.GetHisto('MuonPt_forEff').Fill(self.muon1_pt,    self.weight)
            self.GetHisto('MuonPt').Fill(self.muon1_pt,    self.weight)
            self.GetHisto('NBJets').Fill(self.nbjets, self.weight)
            self.GetHisto('EventWeight').Fill(0, self.weight)
            self.GetHisto('NJets_NBJets').Fill(self.NBin,self.weight)
        return


    def Loop(self):
        ''' Main method, used to loop over all the entries '''
        f = r.TFile.Open(self.filename)
        tree = f.events

        nEvents = tree.GetEntries()
        
        print "Opening file {f} and looping over {n} events...".format(f = self.filename, n = nEvents)
        
        for event in tree:
            #-----------Region fiducial------------------------
            #Voy a seleccionar muones con la distribución de pdgID y con un momento transverso igual que en mi región de señal, también tendremos en cuenta hasta donde se miden los muones en eta (eta<2.4), hasta donde se pueden identificar los jets b (eta<2.4) y también hasta donde se miden los jets ligeros (eta<5.2)
            if self.filename == 'files/ttbar.root':
                self.GetHisto('EventWeight_gen_tot').Fill(0,event.EventWeight)
                if abs(event.MCleptonPDGid) == 13: #13 es la ID del muon, los valores negativos son las antipartículas
                    muon1_gen = r.TLorentzVector()
                    energy_muon = (event.MClepton_px**2+event.MClepton_py**2+event.MClepton_pz**2+0.1056583745**2)**(0.5)
                    muon1_gen.SetPxPyPzE(event.MClepton_px,event.MClepton_py,event.MClepton_pz,energy_muon)
                    self.muon1_pt_gen = muon1_gen.Pt()
                    #----4-momento quarks b-------
                    b_hadronic = r.TLorentzVector()
                    b_hadronic.SetPx(event.MChadronicBottom_px)
                    b_hadronic.SetPy(event.MChadronicBottom_py)
                    b_hadronic.SetPz(event.MChadronicBottom_pz)
                    
                    b_leptonic = r.TLorentzVector()
                    b_leptonic.SetPx(event.MCleptonicBottom_px)
                    b_leptonic.SetPy(event.MCleptonicBottom_py)
                    b_leptonic.SetPz(event.MCleptonicBottom_pz)                    
                    #----4-momento quarks b-------
                    #----4-momento quarks ligeros-------
                    q_hadronic = r.TLorentzVector()
                    q_hadronic.SetPx(event.MChadronicWDecayQuark_px)
                    q_hadronic.SetPy(event.MChadronicWDecayQuark_py)
                    q_hadronic.SetPz(event.MChadronicWDecayQuark_pz)
                    
                    qbar_hadronic = r.TLorentzVector()
                    qbar_hadronic.SetPx(event.MChadronicWDecayQuarkBar_px)
                    qbar_hadronic.SetPy(event.MChadronicWDecayQuarkBar_py)
                    qbar_hadronic.SetPz(event.MChadronicWDecayQuarkBar_pz)                    
                    #----4-momento quarks ligeros-------
                    if self.muon1_pt_gen >= self.seleccion[0] and muon1_gen.Eta()<2.4 and b_hadronic.Eta()<2.4 and b_leptonic.Eta()<2.4 and q_hadronic.Eta()<5.2 and qbar_hadronic.Eta()<5.2:
                        self.GetHisto('MuonPt_gen').Fill(self.muon1_pt_gen,event.EventWeight) 
                        self.GetHisto('EventWeight_gen').Fill(0,event.EventWeight)
            #-----------Region fiducial------------------------        
            
            
            if event.NMuon != 1: continue         # Selecting events with 1 muon 
            #if event.NMuon < 1: continue
            #For trigger calculus
            muon1_notrigg = r.TLorentzVector()
            muon1_notrigg.SetPxPyPzE(event.Muon_Px[0], event.Muon_Py[0], event.Muon_Pz[0], event.Muon_E[0])
            
            #--Seleccion de Pt del muon, hay que situarla de manera que tambien afecte a los sucesos que no han pasado trigger--
            if muon1_notrigg.Pt()<self.seleccion[0]: continue
            #-------------------------------------------------------------------------------------------------------------------
            if event.NJet < self.seleccion[1]: continue #Selecting events with N jets
            #---------btag working point-----
            '''
            flag = 0
            bTagScaleFactor = 1
            if self.seleccion[2] == -1: #Esto es por si situamos el WP en -1, es decir, no imponemos restriccion en b-jets
                flag = 1
            else:
                for i in range(0,event.NJet):
                    if event.Jet_btag[i] >= self.seleccion[2]:
                        flag = 1
                        bTagScaleFactor = 0.9
                        break
                    else: continue
            
            if flag != 1: continue
            '''
            NbJets = 0
            bTagScaleFactor = 1
            for i in range(0,event.NJet):
                if event.Jet_btag[i] >= self.seleccion[2]:
                    NbJets = NbJets + 1
                else: continue
            
            if NbJets == 1:
                bTagScaleFactor = 0.9
            if NbJets >= 2:
                bTagScaleFactor = 0.86
             
            if NbJets < self.seleccion[3]: continue
            
            #---------btag working point-----
            
            self.weight   = event.EventWeight*bTagScaleFactor if not self.name == 'data' else 1 #Scale Factor de b-tagging
            '''
            self.weight   = event.EventWeight if not self.name == 'data' else 1 
            '''
            self.muon1_pt_notrigg = muon1_notrigg.Pt()
            self.muon1_pt_notrigg_forEff = muon1_notrigg.Pt()       
            
            
            ### Selection
            if event.triggerIsoMu24 == 1: # Events must pass the trigger
            ### Variable calculation
                muon1 = r.TLorentzVector()
                muon1.SetPxPyPzE(event.Muon_Px[0], event.Muon_Py[0], event.Muon_Pz[0], event.Muon_E[0])
                self.muon1_pt = muon1.Pt()
                self.muon1_pt_forEff = muon1.Pt()
                self.NJet = event.NJet
                self.MET = (event.MET_px*event.MET_px+event.MET_py*event.MET_py)**(0.5)
                self.nbjets = NbJets
                #---Histogram NJets_NBJets---
                if self.NJet == 0:
                    self.NBin = 0
                if self.NJet == 1:
                    self.NBin = 1
                if self.NJet == 2 and self.nbjets == 0:
                    self.NBin = 2
                if self.NJet == 2 and self.nbjets >= 1:
                    self.NBin = 3
                if self.NJet == 3 and self.nbjets == 0:
                    self.NBin = 4
                if self.NJet == 3 and self.nbjets >= 1:
                    self.NBin = 5
                if self.NJet >= 4 and self.nbjets == 0:
                    self.NBin = 6
                if self.NJet >= 4 and self.nbjets >=1:
                    self.NBin = 7
                #---Histogram NJets_NBJets--- 
            ### Filling
            self.trigger = event.triggerIsoMu24
            self.FillHistograms()
        return


































