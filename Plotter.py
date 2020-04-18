import warnings as wr
import os
from Selector import Selector
import ROOT as r
import copy

class Plotter:
    ''' Class to draw histograms and get info from Selector'''
    ### =============================================
    ### Constructor
    def __init__(self, backgrounds, data = '', path = "./results", selection = []):
        ''' Initialize a new plotter... give a list with all names of MC samples and the name of the data sample '''
        self.data = data
        self.backgrounds = backgrounds
        self.savepath = path
        counter = 0
        for p in self.backgrounds:
            self.listOfSelectors.append(Selector(p, selection))
            self.colors.append(counter+1)
            counter += 1

        if (self.data != ''): self.dataSelector = Selector(self.data,selection)
        return

    ### =============================================
    ### Attributes
    savepath = "."
    listOfSelectors = []
    dataSelector = Selector()
    data = ''
    colors = []

    # Default parameters
    fLegX1, fLegY1, fLegX2, fLegY2 = 0.75, 0.55, 0.89, 0.89
    LegendTextSize  = 0.035
    xtitle = ''
    ytitle = ''
    title  = ''
    LogY = False


    ### =============================================
    ### Methods
    def SetLegendPos(self, x1, y1, x2, y2):
        ''' Change the default position of the legend'''
        self.fLegX1 = x1
        self.fLegY1 = y1
        self.fLegX2 = x2
        self.fLegY2 = y2


    def SetLegendSize(self, t = 0.065):
        ''' Change the default size of the text in the legend'''
        self.LegendTextSize = t


    def SetSavePath(self, newpath):
        '''Change where plots and text dumps are going to be saved. By default: ./results'''
        self.savepath = newpath


    def SetColors(self, col):
        ''' Set the colors for each MC sample '''
        self.colors = col


    def SetTitle(self, tit):
        ''' Set title of the plot '''
        self.title = tit


    def SetXtitle(self, tit):
        ''' Set title of X axis '''
        self.xtitle = tit


    def SetYtitle(self, tit):
        ''' Set title of Y axis '''
        self.ytitle = tit

    def SetYaxislog(self):
        self.LogY = True

    def GetHisto(self, process, name):
        ''' Returns histogram 'name' for a given process '''
        for s in self.listOfSelectors:
            if name not in s.name: continue
            h = s.GetHisto(name)
            return h

        wr.warn("[Plotter::GetHisto] WARNING: histogram {h} for process {p} not found!".format(h = name, p = process))
        return r.TH1F()


    def GetEvents(self, process, name):
        ''' Returns the integral of a histogram '''
        return self.GetHisto(process, name).Integral()


    def Stack(self, name):
        ''' Produce a stack plot for a variable given '''
        if (isinstance(name, list)):
            for nam in name: self.Stack(nam)
            return

        c = r.TCanvas('c_'+name, 'c', 10, 10, 800, 600)

        upperPad = r.TPad("upperPad", "upperPad", 0.0, 0.2, 1.0, 1.0)
        upperPad.Draw()
        upperPad.cd()
        l = r.TLegend(self.fLegX1, self.fLegY1, self.fLegX2, self.fLegY2)
        l.SetTextSize(self.LegendTextSize)
        l.SetBorderSize(0)
        l.SetFillColor(10)

        hstack = r.THStack('hstack_' + name, "hstack")
        counter = 0
        for s in self.listOfSelectors:
            h = s.GetHisto(name)
            h.SetFillColor(self.colors[counter])
            h.SetLineColor(1)
            '''
            h.SetBinError(2,200)
            '''
            hstack.Add(h)
            l.AddEntry(h, s.name, "f")
            counter += 1
        hstack.Draw("hist")

        if self.title  != '': hstack.SetTitle(self.title)
        if self.xtitle != '': hstack.GetXaxis().SetTitle(self.xtitle)
        if self.ytitle != '': hstack.GetYaxis().SetTitle(self.ytitle)
        hstack.GetYaxis().SetTitleOffset(1.35)
        Max = hstack.GetStack().Last().GetMaximum()
        #Para el eje log
        if self.LogY:
            upperPad.SetLogy()
            self.LogY = False
        if self.data != '':
            hdata = self.dataSelector.GetHisto(name)
            hdata.SetMarkerStyle(20)
            hdata.SetMarkerColor(1)
            hdata.Draw("pesame")
            MaxData = hdata.GetMaximum()
            if(Max < MaxData): Max = MaxData
            l.AddEntry(hdata, self.dataSelector.name, 'p')
        #----text-----
        t= r.TLatex(0.15,0.92,"CMS #font[12]{Preliminary}")
        t.SetNDC(1)
        t.Draw()
        t2= r.TLatex(0.65,0.92,"50 pb^{-1}  (#sqrt{s} = 7 TeV)")
        t2.SetNDC(1)
        t2.Draw()
        t4 = r.TLatex(0.05,0.70,self.ytitle)
        t4.SetNDC(1)
        t4.SetTextAngle(90)
        t4.Draw()
        
        #----text-----
        
        hstack.SetMaximum(Max * 1.1)
        hstack.GetHistogram().GetXaxis().SetTickLength(0)
        hstack.GetHistogram().GetXaxis().SetLabelOffset(999)
        hstack.GetHistogram().GetYaxis().SetTitleSize(10)
        
        upperPad.SetGrid()
        #-----Canvas data/pred-------
        
        c.cd(0)
        t3 = r.TLatex(0.75,0.05,"#scale[0.9]{%2s}" %(self.xtitle))
        t3.SetNDC(1)
        t3.Draw()
        
        
        lowerPad = r.TPad("lowerPad", "lowerPad", 0.0, 0.1, 1.0, 0.278)
        lowerPad.SetFillStyle(4000)
        lowerPad.SetTopMargin(0.0)
        lowerPad.Draw()
        lowerPad.cd()
        h3 = copy.deepcopy(hdata.Clone("Datos"))
        suma = r.TH1F("Suma", '',h3.GetNbinsX(),h3.GetXaxis().GetXmin(),h3.GetBinWidth(1)*h3.GetNbinsX()+h3.GetXaxis().GetXmin())
        for s in self.listOfSelectors:
            h = s.GetHisto(name)
            suma.Add(h)
        
        linea = r.TH1F("Linea", '',h3.GetNbinsX(),h3.GetXaxis().GetXmin(),h3.GetBinWidth(1)*h3.GetNbinsX()+h3.GetXaxis().GetXmin())
        for i in range(0,h3.GetNbinsX()):
            linea.SetBinContent(i+1,1)
        h3.Divide(suma)
        h3.SetMarkerStyle(20)
        h3.SetMarkerColor(1)
        h3.SetTitle('')
        h3.GetXaxis().SetTitle('')
        h3.GetYaxis().SetTitle('Data/pred.')
        h3.Draw()
        h3.GetXaxis().SetLabelSize(0.14)
        h3.GetYaxis().SetLabelSize(0.10)
        h3.GetYaxis().SetTitleSize(10)
        h3.GetYaxis().SetRangeUser(0.6,1.8)
        linea.SetLineColor(r.kRed)
        linea.Draw("same")
        t5 = r.TLatex(0.05,0.05,"#scale[4]{Data/pred.}")
        t5.SetNDC(1)
        t5.SetTextAngle(90)
        t5.Draw()
        
        lowerPad.SetGrid()
        
        #---For NJets_NBJets---
        if name == 'NJets_NBJets':
            labels_NJetsNBJets = ['(0,0)','(1,#geq0)','(2,0)','(2,#geq1)','(3,0)','(3,#geq1)','(#geq4,0)','(#geq4,#geq1)']
            h3.GetXaxis().SetLabelSize(0.28)
            c.cd(0)
            t3 = r.TLatex(0.65,0.05,"#scale[0.9]{%2s}" %('(N_Jets,N_bJets)'))
            t3.SetNDC(1)
            t3.Draw()
            lowerPad.cd()
            for j in range(0,h3.GetNbinsX()):
                h3.GetXaxis().SetBinLabel(j+1,labels_NJetsNBJets[j]) 
        
        #---For NJets_NBJets---        
        #-----Canvas data/pred-------
        #-----Incertidumbres---------
        upperPad.cd()
        suma.Draw("E2 SAME") #E2 pinta la incertidumbre como rectangulos
        suma.SetFillColor(14)
        suma.SetFillStyle(3244)
        suma.SetLineColor(0)
        l.AddEntry(suma, "Stat unc.", "f")
        l.Draw("same")
        #-----Incertidumbres---------
        create_folder(self.savepath)
        c.Print(self.savepath + "/" + name + '.png', 'png')
        c.Print(self.savepath + "/" + name + '.pdf', 'pdf')
        c.Close()
        return

#--------Para pintar no-stack------
    def Trigger_Eff(self, name, name2, name3, name4):
        '''
        Esta funcion solo sirve para calcular la eficiencia de trigger utilizando el pt de muon. (Solo admite muestra ttbar)
        '''
        l = r.TLegend(self.fLegX1, self.fLegY1, self.fLegX2, self.fLegY2)
        l.SetTextSize(self.LegendTextSize)
        l.SetBorderSize(0)
        l.SetFillColor(10)
        l2 = r.TLegend(self.fLegX1, self.fLegY1, self.fLegX2, self.fLegY2)
        l2.SetTextSize(self.LegendTextSize)
        l2.SetBorderSize(0)
        l2.SetFillColor(10)
        
        for s in self.listOfSelectors:
            h = s.GetHisto(name)
            h2 = s.GetHisto(name2)
            h_eff = s.GetHisto(name3)
            h2_eff = s.GetHisto(name4)
            break #Solo queremos utilizar la muestra de ttbar que debe estar colocada en primera posicion en el mca


        c=r.TCanvas('c_'+name+name2, 'c', 10, 10, 800, 600)
        c.Divide(1,2) 
        c.cd(1)
        h2.SetTitle('Pt muones (Muestra t#bar{t})')
        #h.GetYaxis().SetRange(0,4000)
        #h2.GetYaxis().SetRange(0,40)
        l.AddEntry(h, 'Con trigger', "f")
        l.AddEntry(h2, 'Sin trigger', "f")
        h.SetFillColor(0)
        h.SetLineColor(20)
        h2.SetFillColor(0)
        h2.SetLineColor(800)
        #---Eficiencia---
        num = h.Integral()
        den = h2.Integral()
        eff = 1.*num/den
        print('La eficiencia de trigger para pt > 26 GeV: %3.3f' %eff)
        #---Eficiencia---
        h2.Draw("HIST")
        h.Draw("HIST SAME")
        l.Draw()
        #----text-----
        t4= r.TLatex(0.1,0.92,"CMS #font[12]{Preliminary}")
        t4.SetNDC(1)
        t4.Draw()
        t5= r.TLatex(0.75,0.92,"50 pb^{-1}  (#sqrt{s} = 7 TeV)")
        t5.SetNDC(1)
        t5.Draw()
        #----text-----
        c.cd(2)
        h3 = copy.deepcopy(h_eff.Clone("Cociente"))
        h3.Divide(h2_eff) 
        h3.SetTitle('Eficiencia trigger')
        h3.SetFillColor(46)
        h3.SetLineColor(20)
        h3.SetFillStyle(4050)
        h3.GetYaxis().SetTitle('Eficiencia')
        #h3.GetYaxis().SetRange(0,23)
        #h3.GetXaxis().SetRange(1,4)
        l2.AddEntry(h3, 'Cociente', 'f')
        h3.Draw("HIST SAME")   
        l2.Draw("SAME")
        #----text-----
        t= r.TLatex(0.1,0.92,"CMS #font[12]{Preliminary}")
        t.SetNDC(1)
        t.Draw()
        t2= r.TLatex(0.75,0.92,"50 pb^{-1}  (#sqrt{s} = 7 TeV)")
        t2.SetNDC(1)
        t2.Draw()
        t3= r.TLatex(0.14,0.82,"#epsilon_{t}=%3.3f" %eff)
        t3.SetNDC(1)
        t3.Draw()
        #----text-----
        create_folder(self.savepath)
        c.Print(self.savepath + "/" + 'Trigger_eff' + '.png', 'png')
        c.Print(self.savepath + "/" + 'Trigger_eff' + '.pdf', 'pdf')
        c.Close()
        return eff
#--------Para pintar no-stack------

    def PrintCounts(self, name):
        ''' Print the number of events for each sample in a given histogram '''
        if (isinstance(name, list)):
            for nam in name: self.PrintEvents(nam)
            return

        print "\nPrinting number of events for histogram {h}:".format(h = name)
        print '----------------------------------------------------'
        total = 0.
        for s in self.listOfSelectors:
            h = s.GetHisto(name)
            print "{nam}: {num}".format(nam = s.name, num = h.Integral())
            total += h.Integral()
            if s.name == 'ttbar':
                counts_ttbar = h.Integral()

        print 'Expected (MC): {tot}'.format(tot = total)
        print '------------------------------'
        if self.data != '':
            hdata = self.dataSelector.GetHisto(name)
            print 'Observed (data): {tot}'.format(tot = hdata.Integral())
            print '------------------------------'
        return counts_ttbar, total, hdata.Integral()

#-------------FUNCION MIA----------------------------------------------------
    def GetCounts(self, name):
        ''' Devuelve el numero de eventos  '''
        if (isinstance(name, list)):
            for nam in name: self.PrintEvents(nam)
            return
        muestras = []
        eventos = []
        total = 0.
        for s in self.listOfSelectors:
            h = s.GetHisto(name)
            total += h.Integral()
            muestras.append(s.name)
            eventos.append(h.Integral())

        if self.data != '':
            hdata = self.dataSelector.GetHisto(name)
            muestras.append('data')
            eventos.append(hdata.Integral())            
        
        return muestras,eventos
#-------------FUNCION MIA----------------------------------------------------

    def SaveCounts(self, name, overridename = ""):
        ''' Save in a text file the number of events for each sample in a given histogram '''
        if (isinstance(name, list)):
            for nam in name: self.SaveCounts(nam, overridename = overridename)
            return

        filename = "yields_{h}".format(h = name) if (overridename == "") else overridename
        create_folder(self.savepath)
        outfile = open(self.savepath + "/" + filename + (".txt" if ".txt" not in overridename else ""), "w")

        thelines = []

        thelines.append("Number of events for histogram {h}:\n".format(h = name))
        thelines.append("----------------------------------------------------\n")
        total = 0.
        for s in self.listOfSelectors:
            h = s.GetHisto(name)
            thelines.append("{nam}: {num}\n".format(nam = s.name, num = h.Integral()))
            total += h.Integral()
        thelines.append('Expected (MC): {tot}\n'.format(tot = total))
        thelines.append('------------------------------\n')
        if self.data != '':
            hdata = self.dataSelector.GetHisto(name)
            thelines.append('Observed (data): {tot}\n'.format(tot = hdata.Integral()))
            thelines.append('------------------------------\n')

        outfile.writelines(thelines)
        outfile.close()
        return

def create_folder(path):
    if not os.path.exists(path): os.system("mkdir -p " + path)
    return
